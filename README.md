# HashIndex — Hệ Thống So Sánh Thuật Toán Tìm Kiếm

So sánh hiệu năng **Hash Table, Linear Search, Binary Search** trên dataset sinh viên giả lập, qua 3 scenario thực tế.

## Tính năng

- **Scenario 1:** Tra cứu sinh viên theo MSSV
- **Scenario 2A:** Lọc theo GPA + mã khoa
- **Scenario 2B:** Lọc theo khoảng GPA thuần
- **Scenario 3:** Tìm kiếm tên mờ (fuzzy, bỏ dấu tiếng Việt)
- Dataset: 1K / 5K / 10K records sinh viên giả lập
- **Giao diện:** Web UI chạy local (FastAPI + HTML/JS)

## Cài đặt

### 1. Clone repo
```bash
git clone https://github.com/khiemtrancong26-tech/Project_DSA_PTTKGT.git
cd Project_DSA_PTTKGT
```

### 2. Tạo môi trường ảo
```bash
python -m venv venv
```

### 3. Kích hoạt môi trường ảo

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Cài thư viện
```bash
pip install -r requirements.txt
```

## Chạy chương trình

### Bước 1 — Sinh dataset (bắt buộc trước khi chạy)
```bash
python data/generator.py
```
Tạo 3 file `students_1K.xlsx`, `students_5K.xlsx`, `students_10K.xlsx` trong thư mục `data/`.

---

### Bước 2 — Khởi động Web UI
```bash
python web.py
```
Mở trình duyệt và truy cập:
```
http://localhost:8000
```

**Tính năng Web UI:**
- Chọn dataset và load bằng nút bấm
- Chạy từng thuật toán, xem thời gian thực thi ngay trên giao diện
- Scenario 2 & 3: hiển thị toàn bộ kết quả dưới dạng bảng có thể cuộn
- Terminal log theo dõi từng thao tác

> Web UI chỉ chạy local (`localhost`) — không cần HTTPS, không expose ra ngoài internet.

## Cấu trúc project

```
Project_DSA_PTTKGT/
├── data/
│   ├── generator.py               # Sinh dataset giả — CCCD-based student_id
│   └── loader.py                  # Đọc xlsx, build hash tables
├── engine/
│   ├── linear_search.py           # Linear Search — O(n) duyệt tuần tự
│   ├── binary_search.py           # Binary Search + bisect helpers — O(log n)
│   ├── fuzzy_search.py            # NFKD normalize → substring match bỏ dấu
│   ├── inverted_index.py          # Inverted Index — token → danh sách record
│   ├── benchmark.py               # Đo avg 10 lần bằng perf_counter()
│   ├── scenario.py                # Ráp logic đầy đủ từng scenario, gọi benchmark
│   ├── hash_table.py              # Base class — Polynomial Rolling Hash (base=31)
│   └── collision/                 # ← Các lớp con kế thừa trực tiếp từ hash_table.py
│       ├── chaining.py            # Separate Chaining — 1 key → 1 value
│       ├── chaining_multi.py      # Chaining Multi   — 1 key → list value
│       ├── open_addressing.py     # Double Hashing   — 1 key → 1 value
│       └── open_addressing_multi.py  # Double Hashing — 1 key → list value
├── web/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── web.py                         # FastAPI server + REST API
└── requirements.txt
```

## Công nghệ sử dụng

- Python 3.11
- pandas, openpyxl — đọc/ghi xlsx
- FastAPI, uvicorn — Web UI server
- HTML / CSS / JavaScript — frontend