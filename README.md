# MODULUX BE

Dự án Backend cho hệ thống quản lý CMS nội dung của **Modulux Homes**. Dự án này cung cấp các API để giao tiếp với Frontend.

## Công nghệ sử dụng
- **Framework:** FastAPI
- **Máy chủ ASGI:** Uvicorn
- **ORM:** SQLAlchemy 2.0
- **Cơ sở dữ liệu:** PostgreSQL (sử dụng `psycopg2-binary`)
- **Ngôn ngữ:** Python 3.10+
- **Thư viện khác:** Pydantic (Validate dữ liệu), APScheduler (Lên lịch tự động - cronjob), BeautifulSoup, v.v.

## Hướng dẫn cài đặt và chạy dự án

### Yêu cầu hệ thống
- **Python**: Nên sử dụng phiên bản Python 3.10 hoặc mới hơn.
- **PostgreSQL**: Đã được cài đặt trực tiếp trên máy hoặc qua Docker.

### Các bước thực hiện

**1. Tạo và kích hoạt môi trường ảo (Virtual Environment):**
Di chuyển vào thư mục `MODULUX_BE`. Nếu thư mục `.venv` chưa có sẵn, bạn tiến hành tạo ra nó:
```bash
python -m venv .venv
```
Kích hoạt môi trường ảo:
- Trên Windows:
  ```powershell
  .venv\Scripts\activate
  ```
- Trên MacOS / Linux:
  ```bash
  source .venv/bin/activate
  ```

**2. Cài đặt các thư viện (Dependencies):**
Sau khi môi trường ảo đã kích hoạt thành công (có chữ `(.venv)` hiển thị ở terminal), chạy lệnh sau:
```bash
pip install -r requirements.txt
```

**3. Cấu hình biến môi trường (`.env`):**
Tạo file `.env` tại thư mục gốc `MODULUX_BE` và khai báo cấu hình cơ sở dữ liệu và các biến môi trường cần thiết (DB URL, CORS_ORIGINS,...).

**4. Chạy các lệnh cập nhật database / Seed dữ liệu (Nếu cần thiết):**
Trước khi chạy ứng dụng lần đầu, bạn có thể thiết lập database thông qua các script di chuyển dữ liệu có sẵn trong hệ thống:
```bash
python run_migration.py
```
*(Lưu ý: Bạn cũng có thể chạy các tool khác như `run_contacts_migration.py`, `seed_about_sections.py` tương tự nếu bạn cần đẩy data mẫu).*

**5. Khởi chạy ứng dụng Server:**
Chạy lệnh uvicorn để khởi động server (có kích hoạt auto-reload trong lúc dev):
```bash
uvicorn app.main:app --reload
```
Theo mặc định, ứng dụng FastAPI sẽ chạy ở `http://127.0.0.1:8000`.

**6. Xem tài liệu API (Swagger UI):**
FastAPI tự động tạo ra tài liệu API tương tác. Khi server đã chạy, mở trình duyệt và đi đến:
- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
