# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Phạm Minh Cương |
| MSSV | 2A202602825 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/mcnb2005/K4-L3L4-Track2-Day21-CI-CD-for-AI-Systems |
| Ngày nộp | 07/10/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---:|---:|---:|---:|---:|
| 1 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 2 | 100 | 0.10 | 3 | 0.7109 | 0.8780 |
| 3 | 200 | 0.10 | 5 | 0.7149 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Lần chạy 3 có F1 lớp dương cao nhất (0.7149), vượt ngưỡng triển khai 0.65. Lần chạy 2 có accuracy cao nhất (0.8780) nhưng F1 thấp hơn, cho thấy accuracy không phản ánh đầy đủ khả năng nhận diện nhóm thu nhập cao. Với learning rate 0.05 và 50 cây, mô hình học chưa đủ nên F1 chỉ đạt 0.6051; tăng số cây và độ sâu giúp mô hình tốt hơn, dù thời gian huấn luyện và nguy cơ overfit cũng tăng.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Chỉ khoảng 24.8% mẫu thuộc lớp thu nhập trên 50K nên dữ liệu mất cân bằng rõ rệt. Mô hình luôn dự đoán “thu nhập thấp” vẫn đạt accuracy khoảng 0.752 nhưng không phát hiện trường hợp thu nhập cao nào, nên F1 lớp dương bằng 0. F1 là trung bình điều hòa của precision và recall, buộc mô hình vừa hạn chế dự đoán dương sai vừa không bỏ sót quá nhiều mẫu dương. Bài dùng `f1_score(y_true, y_pred)` mặc định cho lớp dương. Không dùng `average="weighted"` hoặc `average="macro"`, vì cách tổng hợp nhiều lớp có thể làm mờ hiệu năng lớp dương và khiến ngưỡng 0.65 mất ý nghĩa.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| MLflow thiếu `pkg_resources` | Setuptools mới không còn API cũ mà MLflow 2.13 sử dụng | Khóa `setuptools<81` trong requirements |
| MLflow lỗi pool của SQLAlchemy | SQLAlchemy 2.1 thay đổi API chưa tương thích MLflow 2.13 | Khóa `SQLAlchemy<2.1` và chạy lại test |
| DVC không tạo được site cache | Thư mục mặc định `C:\ProgramData\iterative` không có quyền ghi | Chuyển site cache vào workspace bằng `DVC_SITE_CACHE_DIR` |

---

## 4. So Sánh Bước 2 và Bước 3

| | f1_score | accuracy |
|---|---:|---:|
| Bước 2 (chỉ `train_batch1`) | 0.7149 | 0.8740 |
| Bước 3 (thêm `train_batch2`) | 0.7354 | 0.8820 |

**Nhận xét:** Khi tăng dữ liệu huấn luyện từ 22.361 lên 44.722 mẫu, F1 tăng 0.0205 và accuracy tăng 0.0080. Mức tăng vừa phải là hợp lý vì hai batch được lấy ngẫu nhiên từ cùng một nguồn và có phân phối tương tự; giá trị chính của Bước 3 vẫn là kiểm chứng luồng tái huấn luyện tự động khi dữ liệu thay đổi.
