# Hướng dẫn Compile Báo Cáo LaTeX

Đây là báo cáo LaTeX cho bài tập lớn "Ứng dụng Chỉ Đường Metro Thượng Hải dùng Thuật toán Tìm Kiếm".

## Yêu cầu

### Cài đặt TeX Live / MiKTeX

**Windows (TeX Live):**

1. Download TeX Live ISO từ https://tug.org/texlive/
2. Cài đặt đầy đủ (chọn install all packages).
3. Thêm bin folder vào PATH:
   ```
   C:\texlive\2024\bin\windows
   ```
   (thay năm tương ứng nếu khác)

**macOS (MacTeX):**

```bash
brew install --cask mactex
```

**Linux (Debian/Ubuntu):**

```bash
sudo apt-get update
sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra biber
```

### Yêu cầu các component

- **pdfLaTeX:** Engine mặc định của TeX Live / MiKTeX (không cần cài thêm)
- **Biber:** Bibliography backend (đi kèm TeX Live / MiKTeX)
- **vntex / babel-vietnamese:** Cho chữ tiếng Việt (thường đã cài sẵn)

## Compile

Từ thư mục `docs/report/`:

```bash
pdflatex -interaction=nonstopmode main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

Hoặc một lệnh:

```bash
pdflatex -interaction=nonstopmode main.tex && biber main && pdflatex main.tex && pdflatex main.tex
```

**Output:** `main.pdf`

## Cấu trúc thư mục

```
docs/report/
├── main.tex                # Entry point chính
├── preamble.tex            # Packages + setup
├── titlepage.tex           # Trang bìa (edit tên sinh viên ở đây)
├── chapters/
│   ├── 01-mo-dau.tex       # Chương 1: Mở đầu
│   ├── 02-co-so-ly-thuyet.tex    # Chương 2: Cơ sở lý thuyết
│   ├── 03-phan-tich-thiet-ke.tex # Chương 3: Phân tích & Thiết kế
│   ├── 04-thuc-hien-va-ket-qua.tex # Chương 4: Thực hiện & Kết quả
│   └── 05-ket-luan.tex     # Chương 5: Kết luận
├── refs.bib                # Bibliography (BibTeX)
├── figures/                # Thư mục chứa hình ảnh
│   └── .gitkeep            # Placeholder
├── README.md               # File này
└── main.pdf                # Output PDF (sau compile)
```

## Tùy chỉnh

### Chỉnh sửa tên sinh viên, MSSV, lớp, GV

Mở file `titlepage.tex` và sửa:

```latex
\newcommand{\svname}{HỌ VÀ TÊN SINH VIÊN}
\newcommand{\svid}{MSSV}
\newcommand{\svclass}{LỚP}
\newcommand{\gvname}{TS. TÊN GIẢNG VIÊN}
```

### Thêm hình ảnh

Các placeholder hình được đánh dấu `% TODO:` trong các file chương. Để thêm hình thật:

1. Đặt file ảnh vào thư mục `figures/` (ví dụ `figures/architecture.png`)
2. Uncomment dòng `\includegraphics{figures/architecture.png}`
3. Comment lại dòng `\fbox{...}` placeholder
4. Compile lại

Ví dụ:

```latex
% Trước (placeholder):
% \includegraphics[width=0.8\textwidth]{figures/architecture.png}
\fbox{\begin{minipage}{0.8\textwidth}\centering\vspace{3cm}%
  \textit{[Placeholder: Architecture diagram]}%
\vspace{3cm}\end{minipage}}

% Sau (hình thật):
\includegraphics[width=0.8\textwidth]{figures/architecture.png}
% \fbox{\begin{minipage}{0.8\textwidth}\centering\vspace{3cm}%
%   \textit{[Placeholder: Architecture diagram]}%
% \vspace{3cm}\end{minipage}}
```

### Đổi font

Nếu không có Times New Roman, mở `preamble.tex` và đổi:

```latex
% Thay từ:
\setmainfont[Extension = .ttf, BoldFont = *b, ItalicFont = *i, BoldItalicFont = *bi]{times}

% Sang một trong:
\setmainfont{Liberation Serif}
% hoặc
\setmainfont{TeX Gyre Termes}
% hoặc
\setmainfont{DejaVu Serif}
```

## Online (Overleaf)

Nếu không cài TeX Live cục bộ:

1. Zip toàn bộ thư mục `docs/report/`
2. Vào https://www.overleaf.com
3. Click "New Project" → "Upload Project"
4. Chọn file zip
5. Compiler mặc định là **pdfLaTeX** — đúng, không cần đổi
6. Bấm "Recompile"

## Troubleshooting

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-----------|---------|
| `Package babel Error: Unknown language vietnamese` | vntex/babel-vietnamese chưa cài | MiKTeX Console → Packages → install `vntex` hoặc `babel-vietnamese` |
| `T5 encoding not found` | Thiếu `vntex` fontenc | MiKTeX Console → install `vntex` |
| `biber not found` | Biber chưa cài hoặc không trong PATH | Cài `biber` package, hoặc thêm bin path |
| PDF hiển thị ô vuông ở chữ Việt | Font/encoding mismatch | Đảm bảo `\usepackage[utf8]{inputenc}` + `\usepackage[T5]{fontenc}` + `\usepackage[vietnamese]{babel}` |
| Lỗi `Unknown option utf8` với inputenc | inputenc version cũ | TeX Live >= 2018 mặc định đã đúng; nếu MiKTeX cũ → update |
| Blank page sau trang bìa | `\cleardoublepage` có thể tạo page thừa | Xoá hoặc comment lại dòng trong `titlepage.tex` |
| Code listing line overlap | Margin code listing sai | Sửa `xleftmargin` từ 15pt → 25pt trong `preamble.tex` |

## Tips

- **First time compile:** Chạy XeLaTeX lần 1, biber, rồi XeLaTeX 2 lần nữa để sync references.
- **Cập nhật tài liệu tham khảo:** Edit `refs.bib`, compile lại, biber sẽ pick up entries mới.
- **Xem PDF output nhanh:** Dùng editor có preview tích hợp (VS Code + LaTeX Workshop extension, Overleaf, TeXstudio).
- **Kiểm tra syntax:** Chạy `xelatex -interaction=nonstopmode` để xem lỗi chi tiết.

## Liên hệ

Nếu gặp vấn đề không giải quyết được, kiểm tra:
- Phiên bản TeX Live (tối thiểu 2019)
- XeLaTeX + Biber đều được cài
- Path của fonts (nếu dùng custom fonts)
- Encoding của `.tex` files (phải là UTF-8)

## Tài liệu thêm

- TeX Live: https://tug.org/texlive/
- Overleaf guides: https://www.overleaf.com/learn
- XeLaTeX documentation: https://ctan.org/pkg/xetex
- Polyglossia: https://ctan.org/pkg/polyglossia
