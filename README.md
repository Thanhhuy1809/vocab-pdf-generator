# Vocab PDF Generator

Generate a clean PDF table of vocabulary and grammar structures from a plain text file.

## Mô tả thuật toán (Tiếng Việt)

Chương trình sử dụng quy trình 5 bước để chuyển dữ liệu thô thành bảng PDF:

1. Đọc dữ liệu đầu vào
- Đọc toàn bộ nội dung từ file văn bản UTF-8 (mặc định: vocab_data.txt).

2. Chuẩn hóa từng dòng
- Loại bỏ khoảng trắng dư.
- Đổi ký tự gạch dài (—) về dấu gạch ngang (-).
- Gộp nhiều khoảng trắng liên tiếp thành 1 khoảng trắng.
- Cắt bớt các ký tự đầu dòng như dấu *, - nếu có.

3. Phân tích cú pháp thành bản ghi
- Bỏ qua dòng tiêu đề như "Từ vựng".
- Nhận diện các kiểu phân tách chính:
  - word = meaning
  - structure -> meaning
  - structure → meaning
  - term : meaning
- Nếu gặp dạng 2 dòng:
  - Dòng 1: "offer to V"
  - Dòng 2: "→ đề nghị làm gì"
  thì ghép thành một mục "Cấu trúc".
- Gán nhãn loại dữ liệu:
  - Dùng mũi tên (->, →) => "Cấu trúc"
  - Các dấu còn lại (=, :) => "Từ vựng"

4. Dựng bảng PDF
- Đăng ký font hỗ trợ tiếng Việt (ưu tiên Arial/Tahoma trên Windows, DejaVuSans trên Linux).
- Tạo tiêu đề và style cho header/body.
- Tạo bảng 4 cột:
  - STT
  - Loại
  - Từ/Cấu trúc
  - Nghĩa/Ghi chú
- Tô màu header, kẻ lưới, canh lề, và lặp lại hàng tiêu đề ở mỗi trang.

5. Xuất file kết quả
- Ghi PDF ra file đầu ra (mặc định: vocab_table.pdf).
- In số dòng đã xử lý để kiểm tra nhanh.

## Algorithm Description (English)

The program uses a 5-step pipeline to convert raw text into a printable PDF table:

1. Read input
- Load all text from a UTF-8 plain text file (default: vocab_data.txt).

2. Normalize each line
- Trim surrounding whitespace.
- Replace em dash (—) with regular hyphen (-).
- Collapse repeated spaces into a single space.
- Remove leading bullet-like characters such as * and -.

3. Parse lines into entries
- Skip heading-like lines such as "Từ vựng".
- Detect supported separators:
  - word = meaning
  - structure -> meaning
  - structure → meaning
  - term : meaning
- Handle two-line structure form:
  - Line 1: "offer to V"
  - Line 2: "→ ..."
  and merge them into one "Structure" entry.
- Assign category:
  - Arrow separators (->, →) => "Cấu trúc" (Structure)
  - Other separators (=, :) => "Từ vựng" (Vocabulary)

4. Build PDF table
- Register a Vietnamese-capable font (Arial/Tahoma on Windows, DejaVuSans on Linux).
- Create title/header/body styles.
- Build a 4-column table:
  - Index
  - Type
  - Word/Structure
  - Meaning/Notes
- Apply header color, grid, alignment, row striping, and repeating header rows across pages.

5. Export result
- Write PDF to output path (default: vocab_table.pdf).
- Print the number of parsed rows for quick verification.

## Run

```bash
pip install -r requirements.txt
python generate_vocab_pdf.py --input vocab_data.txt --output vocab_table.pdf
```

Optional:

```bash
python generate_vocab_pdf.py --title "TỪ VỰNG VÀ CẤU TRÚC CẦN CHÚ Ý"
```
