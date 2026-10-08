import importlib
import shutil
import sys

import boto3
import joblib
import numpy as np
from fastapi.testclient import TestClient
from sklearn.dummy import DummyClassifier


def test_api_downloads_model_from_s3_and_scores(monkeypatch, tmp_path):
    """Kiem tra luong tai model tu S3 va hai endpoint ma khong goi AWS that."""
    source_model = tmp_path / "source-model.joblib"
    model = DummyClassifier(strategy="constant", constant=0)
    model.fit(np.zeros((2, 10)), np.array([0, 1]))
    joblib.dump(model, source_model)

    calls = {}

    class FakeS3Client:
        def download_file(self, bucket, key, filename):
            calls.update(bucket=bucket, key=key, filename=filename)
            shutil.copyfile(source_model, filename)

    monkeypatch.setattr(boto3, "client", lambda service, **kwargs: FakeS3Client())
    monkeypatch.setenv("ARTIFACT_BUCKET", "test-income-bucket")
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    sys.modules.pop("src.serve", None)

    serve = importlib.import_module("src.serve")
    client = TestClient(serve.app)

    assert calls["bucket"] == "test-income-bucket"
    assert calls["key"] == "artifacts/current/model.joblib"
    assert client.get("/healthz").json() == {"status": "ok"}

    response = client.post("/score", json={"features": [0.0] * 10})
    assert response.status_code == 200
    assert response.json() == {"prediction": 0, "label": "thu_nhap_thap"}

    invalid = client.post("/score", json={"features": [0.0, 1.0]})
    assert invalid.status_code == 400
