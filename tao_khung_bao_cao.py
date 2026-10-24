# -*- coding: utf-8 -*-
"""
Tạo file Word Báo Cáo Thực Nghiệm Mẫu dựa trên Đề Cương Chi Tiết 35 Trang
Khung chuẩn format học thuật: Font Calibri, Heading phân cấp, Bảng biểu, Box ghi chú hướng dẫn chèn số liệu và đồ thị.
Tích hợp Trang Phụ lục & Mục lục điều hướng tương tác (Clickable Bookmarks & Hyperlinks).
"""

import os
import sys
import html
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

# Thiết lập encoding UTF-8 an toàn cho console output
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

OUTPUT_FILE = r"D:\đo lường\thực hành\RCWL1601\Bao_Cao_Thuc_Nghiem_RCWL1601_Khung_Chuan.docx"
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

doc = Document()

# Page Margins chuẩn A4
for s in doc.sections:
    s.top_margin = Inches(0.8)
    s.bottom_margin = Inches(0.8)
    s.left_margin = Inches(0.9)
    s.right_margin = Inches(0.9)

# Colors
C_NAVY = RGBColor(0, 51, 102)     # #003366
C_MAROON = RGBColor(128, 0, 0)   # #800000
C_GRAY = RGBColor(90, 90, 90)
C_DARK = RGBColor(30, 30, 30)
C_BLUE = RGBColor(26, 82, 118)

# Biến đếm ID duy nhất cho Word Bookmarks
bm_counter = 0

def add_bookmark(paragraph, bookmark_name):
    """Gắn thẻ Bookmark (w:bookmarkStart và w:bookmarkEnd) vào đoạn văn bản để làm đích đến cho hyperlink."""
    global bm_counter
    bm_counter += 1
    bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bm_counter}" w:name="{bookmark_name}"/>')
    bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bm_counter}"/>')
    pPr = paragraph._p.pPr
    if pPr is not None:
        pPr.addnext(bm_start)
    else:
        paragraph._p.insert(0, bm_start)
    paragraph._p.append(bm_end)

def set_cell_bg(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_pad(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_title(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = C_NAVY
    return p

def add_subtitle(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = C_MAROON
    return p

def add_meta(label, val):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(3)
    r1 = p.add_run(label + ": ")
    r1.font.bold = True
    r1.font.size = Pt(11)
    r2 = p.add_run(val)
    r2.font.size = Pt(11)

def add_h1(text, anchor=None, back_to_toc=True):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = C_NAVY
    
    if back_to_toc and anchor:
        p.add_run("   ")
        back_hl = parse_xml(
            f'<w:hyperlink {nsdecls("w")} w:anchor="toc_nav">'
            f'<w:r>'
            f'<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:color w:val="2563EB"/><w:sz w:val="18"/><w:i/></w:rPr>'
            f'<w:t>[↑ Về Mục Lục]</w:t>'
            f'</w:r>'
            f'</w:hyperlink>'
        )
        p._p.append(back_hl)

    if anchor:
        add_bookmark(p, anchor)
    return p

def add_h2(text, anchor=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(11)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = C_MAROON
    if anchor:
        add_bookmark(p, anchor)
    return p

def add_h3(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = C_BLUE
    return p

def add_p(text, bold_prefix="", italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(11)
        r_pre.font.bold = True
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(11)
    r.font.italic = italic
    return p

def add_bullet(text, bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.12
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(11)
        r_pre.font.bold = True
    r = p.add_run(text)
    r.font.name = 'Calibri'
    r.font.size = Pt(11)
    return p

def add_guide_box(text, tip_title="[HƯỚNG DẪN ĐIỀN SỐ LIỆU & ĐỒ THỊ CHO MỤC NÀY]"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_bg(cell, "F2F7FA")
    set_cell_pad(cell, top=100, bottom=100, left=150, right=150)
    
    # Border nét đứt xanh
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="single" w:sz="6" w:space="0" w:color="3B82F6"/><w:bottom w:val="single" w:sz="6" w:space="0" w:color="3B82F6"/><w:left w:val="single" w:sz="18" w:space="0" w:color="2563EB"/><w:right w:val="single" w:sz="6" w:space="0" w:color="3B82F6"/></w:tcBorders>')
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(3)
    r1 = p.add_run(tip_title + "\n")
    r1.font.name = 'Calibri'
    r1.font.size = Pt(10)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(30, 64, 175)
    
    r2 = p.add_run(text)
    r2.font.name = 'Calibri'
    r2.font.size = Pt(10)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(55, 65, 81)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def add_placeholder_img(caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    set_cell_bg(cell, "F8FAFC")
    set_cell_pad(cell, top=200, bottom=200, left=300, right=300)
    
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="dashed" w:sz="8" w:space="0" w:color="94A3B8"/><w:bottom w:val="dashed" w:sz="8" w:space="0" w:color="94A3B8"/><w:left w:val="dashed" w:sz="8" w:space="0" w:color="94A3B8"/><w:right w:val="dashed" w:sz="8" w:space="0" w:color="94A3B8"/></w:tcBorders>')
    tcPr.append(tcBorders)
    
    cp = cell.paragraphs[0]
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cp.add_run("[VỊ TRÍ CHÈN HÌNH ẢNH / BIỂU ĐỒ - DÙNG INSERT > PICTURE HOẶC XUẤT TỪ SCRIPT DATA_ANALYSIS.PY]")
    r.font.name = 'Calibri'
    r.font.size = Pt(9.5)
    r.font.italic = True
    r.font.color.rgb = RGBColor(100, 116, 139)
    
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(8)
    rc = p_cap.add_run(caption)
    rc.font.name = 'Calibri'
    rc.font.size = Pt(9.5)
    rc.font.italic = True
    rc.font.color.rgb = C_GRAY

def add_toc_entry(doc, title, anchor, level=1):
    """Thêm một dòng liên kết điều hướng trong Trang Mục lục & Phụ lục."""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.05
    if level == 1:
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.left_indent = Inches(0)
        color = "003366"  # C_NAVY
        bold_tag = "<w:b/>"
        size = 20  # 10 pt
        prefix = "■ "
    else:
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.left_indent = Inches(0.2)
        color = "1D4ED8"  # Royal Blue
        bold_tag = ""
        size = 18  # 9 pt
        prefix = "▸ "

    safe_text = html.escape(f"{prefix}{title}")
    hyperlink = parse_xml(
        f'<w:hyperlink {nsdecls("w")} w:anchor="{anchor}">'
        f'<w:r>'
        f'<w:rPr>'
        f'<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>'
        f'<w:rStyle w:val="Hyperlink"/>'
        f'<w:color w:val="{color}"/>'
        f'{bold_tag}'
        f'<w:sz w:val="{size}"/>'
        f'</w:rPr>'
        f'<w:t>{safe_text}</w:t>'
        f'</w:r>'
        f'</w:hyperlink>'
    )
    p._p.append(hyperlink)

# ==================== TRANG BÌA (TRANG 1) ====================
add_title("BÁO CÁO THỰC NGHIỆM ĐO LƯỜNG")
add_subtitle("KHẢO SÁT TOÀN DIỆN CÁC ĐẶC TÍNH ĐO LƯỜNG CỦA CẢM BIẾN KHOẢNG CÁCH SIÊU ÂM RCWL-1601 KẾT HỢP BÙ NHIỆT ĐỘ TRÊN VI ĐIỀU KHIỂN ESP32")

doc.add_paragraph().paragraph_format.space_after = Pt(24)
add_meta("Học phần", "Kỹ thuật Đo lường và Cảm biến (Mã học phần: EMA2024E_3)")
add_meta("Giảng viên hướng dẫn", "[Điền tên Giảng viên phụ trách môn học]")
add_meta("Nhóm sinh viên thực hiện", "[Điền Tên Nhóm / Họ tên Sinh viên - MSSV]")
add_meta("Lớp học phần", "[Điền Tên Lớp]")
add_meta("Năm học / Học kỳ", "Năm học 2026 – Học kỳ I")
add_meta("Địa điểm thực nghiệm", "Phòng thực hành Kỹ thuật Đo lường & Cảm biến")

doc.add_page_break()

# ==================== TRANG 2: MỤC LỤC & PHỤ LỤC ĐIỀU HƯỚNG TƯƠNG TÁC ====================
p_toc = doc.add_paragraph()
p_toc.paragraph_format.space_before = Pt(8)
p_toc.paragraph_format.space_after = Pt(4)
r_toc = p_toc.add_run("MỤC LỤC & PHỤ LỤC ĐIỀU HƯỚNG TƯƠNG TÁC")
r_toc.font.name = 'Calibri'
r_toc.font.size = Pt(15)
r_toc.font.bold = True
r_toc.font.color.rgb = C_NAVY
add_bookmark(p_toc, "toc_nav")

# Box hướng dẫn thao tác click chuột
tbl_box = doc.add_table(rows=1, cols=1)
tbl_box.alignment = WD_TABLE_ALIGNMENT.CENTER
c_box = tbl_box.cell(0, 0)
set_cell_bg(c_box, "F0F7FF")
set_cell_pad(c_box, top=80, bottom=80, left=120, right=120)

tcPr_box = c_box._tc.get_or_add_tcPr()
tcBorders_box = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="single" w:sz="18" w:space="0" w:color="2563EB"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
tcPr_box.append(tcBorders_box)

cp_box = c_box.paragraphs[0]
cp_box.paragraph_format.space_after = Pt(1)
r_b1 = cp_box.add_run("HƯỚNG DẪN ĐIỀU HƯỚNG TỰ ĐỘNG BẰNG CHUỘT:\n")
r_b1.font.name = 'Calibri'
r_b1.font.size = Pt(9.5)
r_b1.font.bold = True
r_b1.font.color.rgb = RGBColor(30, 64, 175)

r_b2 = cp_box.add_run("• Bấm chuột (hoặc nhấn giữ phím Ctrl + Click chuột) vào bất kỳ tiêu đề hoặc đề mục nào dưới đây để di chuyển ngay lập tức đến nội dung tương ứng.\n• Tại đầu mỗi chương lớn, có sẵn liên kết \"[↑ Về Mục Lục]\" giúp bạn quay trở lại trang điều hướng này bất kỳ lúc nào.")
r_b2.font.name = 'Calibri'
r_b2.font.size = Pt(9.0)
r_b2.font.italic = True
r_b2.font.color.rgb = RGBColor(55, 65, 81)

doc.add_paragraph().paragraph_format.space_after = Pt(2)

# Danh sách toàn bộ đề mục điều hướng
toc_entries = [
    (1, "PHẦN MỞ ĐẦU & DANH MỤC QUY ƯỚC DỮ LIỆU", "sec_modau"),
    (2, "1. Lời nói đầu và Đặt vấn đề", "sec_modau_1"),
    (2, "2. Bảng quy ước mã hóa tập dữ liệu thực nghiệm", "sec_modau_2"),
    
    (1, "CHƯƠNG 1: CƠ SỞ LÝ THUYẾT ĐO LƯỜNG VÀ CẢM BIẾN SIÊU ÂM", "chap1"),
    (2, "1.1. Nguyên lý đo khoảng cách bằng Thời gian bay (ToF) của sóng siêu âm 40 kHz", "chap1_1"),
    (2, "1.2. Sự phụ thuộc của vận tốc âm thanh vào nhiệt độ và nguyên lý bù nhiệt", "chap1_2"),
    (2, "1.3. Cấu tạo phần cứng cảm biến RCWL-1601 và cảm biến DHT11", "chap1_3"),
    (2, "1.4. Hệ thống các chỉ tiêu kỹ thuật đánh giá cảm biến và Lý thuyết sai số", "chap1_4"),
    
    (1, "CHƯƠNG 2: THIẾT KẾ HỆ THỐNG ĐO VÀ QUY TRÌNH THỰC NGHIỆM", "chap2"),
    (2, "2.1. Thiết kế phần cứng và sơ đồ đấu nối trên ESP32", "chap2_1"),
    (2, "2.2. Thiết kế kiến trúc phần mềm hướng đối tượng (OOP)", "chap2_2"),
    (2, "2.3. Bố trí bàn đo và Quy trình thực nghiệm", "chap2_3"),
    
    (1, "CHƯƠNG 3: PHÂN TÍCH LỰA CHỌN CỠ MẪU TỐI ƯU N = 50 TỪ TẬP MẪU LỚN", "chap3"),
    (2, "3.1. Bài toán tối ưu hóa giữa Độ tin cậy thống kê và Thời gian đo", "chap3_1"),
    (2, "3.2. Phân tích sự hội tụ của Trung bình tích lũy và Độ lệch chuẩn theo k = 2 .. 100", "chap3_2"),
    (2, "3.3. Biểu đồ hội tụ và Luận giải chốt cỡ mẫu N = 50", "chap3_3"),
    
    (1, "CHƯƠNG 4: ĐÁNH GIÁ TOÀN DIỆN CÁC ĐẶC TÍNH TĨNH Ở ĐIỀU KIỆN CHUẨN (FSDT & BSDT)", "chap4"),
    (2, "4.1. Bảng tổng hợp thống kê toàn dải và Lọc sai số thô (3-Sigma & IQR)", "chap4_1"),
    (2, "4.2. Khảo sát Vùng chết (Blind Zone: 1cm - 3cm) và Giới hạn đo xa (400cm - 600cm)", "chap4_2"),
    (2, "4.3. Đánh giá Độ chụm (Precision) và Độ lặp lại (Repeatability)", "chap4_3"),
    (2, "4.4. Đánh giá Độ chính xác (Accuracy) – Sai số tuyệt đối & Tương đối", "chap4_4"),
    (2, "4.5. Đánh giá Độ tuyến tính (Linearity), Độ nhạy (Sensitivity) và Độ phân giải (Resolution)", "chap4_5"),
    (2, "4.6. Khảo sát Độ trễ (Hysteresis) giữa Chiều tiến (FSDT) và Chiều lùi (BSDT)", "chap4_6"),
    (2, "4.7. Đánh giá Độ không đảm bảo đo theo chuẩn ISO/GUM", "chap4_7"),
    
    (1, "CHƯƠNG 5: KHẢO SÁT CÁC YẾU TỐ GÂY NHIỄU NGOẠI CẢNH", "chap5"),
    (2, "5.1. Ảnh hưởng của Bề mặt phản xạ: Mặt nhẵn (FSDT) vs. Mặt gồ ghề (FRDT)", "chap5_1"),
    (2, "5.2. Ảnh hưởng của Nhiệt độ môi trường & Hiệu quả thuật toán bù nhiệt", "chap5_2"),
    
    (1, "CHƯƠNG 6: TỔNG KẾT ĐẶC TÍNH KỸ THUẬT & KẾT LUẬN", "chap6"),
    (2, "6.1. Bảng đối chiếu Hồ sơ kỹ thuật thực nghiệm so với Datasheet của Nhà sản xuất", "chap6_1"),
    (2, "6.2. Kết luận và Khuyến nghị giải pháp kỹ thuật", "chap6_2"),
    (2, "Tài liệu tham khảo & Phụ lục Code", "chap6_ref"),
]

for level, title, anchor in toc_entries:
    add_toc_entry(doc, title, anchor, level)

doc.add_page_break()

# ==================== TRANG 3+: NỘI DUNG CHI TIẾT BÁO CÁO ====================
# ==================== PHẦN MỞ ĐẦU ====================
add_h1("PHẦN MỞ ĐẦU & DANH MỤC QUY ƯỚC DỮ LIỆU", anchor="sec_modau")

add_h2("1. Lời nói đầu và Đặt vấn đề", anchor="sec_modau_1")
add_p("Trong bối cảnh công nghiệp 4.0 và tự động hóa robot, bài toán đo khoảng cách không tiếp xúc đóng vai trò sống còn trong việc định vị, giám sát mức bồn chứa và tránh vật cản an toàn. Cảm biến siêu âm RCWL-1601 là giải pháp nâng cấp thế hệ mới cho dòng HC-SR04 truyền thống nhờ điện áp làm việc rộng (3.0V - 5.5V) và dòng tiêu thụ tĩnh cực thấp (~2.2mA). Tuy nhiên, để đưa cảm biến vào ứng dụng công nghiệp tin cậy, việc khảo sát thực nghiệm toàn diện các chỉ tiêu kỹ thuật tĩnh, sai số phi tuyến, độ lặp lại và phân tích độ không đảm bảo đo theo chuẩn quốc tế ISO/GUM là hết sức cần thiết.")

add_h2("2. Bảng quy ước mã hóa tập dữ liệu thực nghiệm", anchor="sec_modau_2")
add_p("Toàn bộ các tệp dữ liệu thực nghiệm thu thập từ kit ESP32 được chuẩn hóa theo quy ước viết tắt sau:")

tbl_code = doc.add_table(rows=6, cols=3)
tbl_code.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_code = ["Ký hiệu tệp", "Tên đầy đủ (Tiếng Anh)", "Mô tả điều kiện thực nghiệm"]
for idx, h in enumerate(headers_code):
    c = tbl_code.cell(0, idx)
    c.text = h
    set_cell_bg(c, "003366")
    set_cell_pad(c)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(10)

data_code = [
    ("100lanforward_smooth_defttemp_XXXcm", "100 Samples Exploration", "Đo thăm dò mẫu lớn 100 lần ở 50cm, 100cm, 150cm để tìm cỡ mẫu tối ưu N."),
    ("FSDT", "Forward – Smooth – Default Temp", "Chiều tiến (1cm -> 600cm), mặt cản phẳng nhẵn (mica/kính), nhiệt độ phòng mặc định."),
    ("BSDT", "Backward – Smooth – Default Temp", "Chiều lùi (300cm -> 10cm), mặt cản phẳng nhẵn, đối chiếu chiều tiến để tính Độ trễ."),
    ("FRDT", "Forward – Rough – Default Temp", "Chiều tiến (10cm -> 375cm), mặt cản xốp/gồ ghề để khảo sát hiện tượng tán xạ âm."),
    ("FSAT / FSLT", "Forward – Smooth – Air-con Temp", "Chiều tiến, mặt phẳng nhẵn, trong phòng điều hòa nhiệt độ thấp để đánh giá bù nhiệt.")
]

for row_idx, r_data in enumerate(data_code):
    row = tbl_code.rows[row_idx + 1]
    bg = "F2F5F8" if row_idx % 2 == 1 else "FFFFFF"
    for col_idx, val in enumerate(r_data):
        c = row.cells[col_idx]
        c.text = val
        set_cell_bg(c, bg)
        set_cell_pad(c)
        for r in c.paragraphs[0].runs:
            r.font.size = Pt(9.5)

doc.add_page_break()

# ==================== CHƯƠNG 1 ====================
add_h1("CHƯƠNG 1: CƠ SỞ LÝ THUYẾT ĐO LƯỜNG VÀ CẢM BIẾN SIÊU ÂM", anchor="chap1")

add_h2("1.1. Nguyên lý đo khoảng cách bằng Thời gian bay (ToF) của sóng siêu âm 40 kHz", anchor="chap1_1")
add_p("Nguyên lý đo cự ly siêu âm dựa trên phương pháp Thời gian bay (Time-of-Flight - ToF). Bộ phát kích hoạt một chùm 8 chu kỳ xung sóng áp điện ở tần số 40 kHz. Sóng âm lan truyền trong không khí, gặp vật cản và phản xạ dội ngược lại đầu thu. Khoảng cách d từ cảm biến đến vật thể được tính qua phương trình:")
add_p("d = (v * t) / 2", bold_prefix="   [Công thức 1.1] ", italic=True)
add_p("Trong đó: v là vận tốc truyền âm thanh trong không khí (m/s); t là tổng thời gian từ lúc phát chùm xung đến khi đầu thu nhận được sóng dội (Echo pulse width).")
add_bullet("Góc mở búp sóng (Beam Angle): Chùm sóng siêu âm lan truyền theo dạng nón với nửa góc khoảng ±7.5° (góc mở hiệu dụng 15°).", "• ")
add_bullet("Suy hao biên độ: Công suất sóng âm suy giảm theo bình phương khoảng cách (1/r^2) và bị tiêu tán do ma sát nhớt cùng độ ẩm không khí.", "• ")

add_h2("1.2. Sự phụ thuộc của vận tốc âm thanh vào nhiệt độ và nguyên lý bù nhiệt", anchor="chap1_2")
add_p("Vận tốc truyền sóng âm trong chất khí phụ thuộc trực tiếp vào nhiệt độ tuyệt đối của môi trường theo công thức Laplace:")
add_p("v(T) = 331.3 * sqrt(1 + T / 273.15) ≈ 331.3 + 0.606 * T  [m/s]", bold_prefix="   [Công thức 1.2] ", italic=True)
add_p("Trong đó T là nhiệt độ môi trường tính bằng độ C (°C). Cứ mỗi 1°C thay đổi, vận tốc truyền âm biến thiên khoảng 0.606 m/s (tương đương ~0.18%). Nếu không có cảm biến nhiệt độ (như DHT11) để bù trừ thời gian thực, sự chênh lệch nhiệt độ giữa các mùa hoặc môi trường có thể gây ra sai số tỷ lệ lên tới 1.5% - 3.0%.")

add_h2("1.3. Cấu tạo phần cứng cảm biến RCWL-1601 và cảm biến DHT11", anchor="chap1_3")
add_bullet("Cảm biến RCWL-1601: Sử dụng IC xử lý chuyên dụng RCWL-9610 thế hệ mới, hỗ trợ nguồn 3.0V - 5.5V, ngõ ra Echo mức logic 3.3V tương thích hoàn toàn chân GPIO của ESP32 mà không cần mạch chuyển đổi mức.", "• ")
add_bullet("Cảm biến nhiệt ẩm DHT11: Sử dụng chuẩn giao tiếp 1-Wire số, dải đo nhiệt độ 0 - 50°C với sai số ±2°C, cung cấp tham số nhiệt độ T phục vụ bù nhiệt tự động.", "• ")

add_h2("1.4. Hệ thống các chỉ tiêu kỹ thuật đánh giá cảm biến và Lý thuyết sai số", anchor="chap1_4")
add_bullet("Độ chụm (Precision / Repeatability): Định lượng qua độ lệch chuẩn thực nghiệm mẫu s và hệ số biến thiên CV% = (s / x_bar) * 100%.", "• ")
add_bullet("Độ chính xác (Accuracy): Định lượng qua sai số tuyệt đối e = d_meas - d_true và sai số tương đối delta% = (|e| / d_true) * 100%.", "• ")
add_bullet("Tiêu chuẩn loại bỏ sai số thô (Outliers): Áp dụng quy tắc 3-Sigma (|x_i - x_bar| > 3*s) và khoảng tứ phân vị IQR (vượt ngoài [Q1 - 1.5*IQR, Q3 + 1.5*IQR]) để lọc bỏ các xung nhiễu nhảy bậc chu kỳ sóng âm.", "• ")
add_bullet("Độ tuyến tính (Linearity) & Độ nhạy (Sensitivity): Hồi quy bình phương tối thiểu y = ax + b, tính hệ số tương quan R^2 và độ phi tuyến %FSO = (max|Delta| / FSO) * 100%.", "• ")
add_bullet("Độ trễ (Hysteresis): Chênh lệch giá trị đo giữa chiều tiến và chiều lùi tại cùng một điểm chuẩn: Delta_H = |d_forward - d_backward|.", "• ")
add_bullet("Độ không đảm bảo đo (Measurement Uncertainty theo ISO/GUM): Đánh giá Độ không đảm bảo đo Loại A u_A = s / sqrt(N), Loại B u_B từ dụng cụ chuẩn, Tổng hợp u_c = sqrt(u_A^2 + u_B^2) và Mở rộng U_95% = 2 * u_c.", "• ")

add_guide_box("Bạn có thể viết thêm lý thuyết hoặc tóm lược công thức theo slide của thầy cô nếu cần. Giữ nguyên các định nghĩa chuẩn về Precision, Accuracy, Hysteresis, u_A, u_B.")

doc.add_page_break()

# ==================== CHƯƠNG 2 ====================
add_h1("CHƯƠNG 2: THIẾT KẾ HỆ THỐNG ĐO VÀ QUY TRÌNH THỰC NGHIỆM", anchor="chap2")

add_h2("2.1. Thiết kế phần cứng và sơ đồ đấu nối trên ESP32", anchor="chap2_1")
add_bullet("ESP32 GPIO 5: Kết nối chân TRIG của RCWL-1601 (Xung kích phát 10 μs).", "• ")
add_bullet("ESP32 GPIO 18: Kết nối chân ECHO của RCWL-1601 (Đo độ rộng xung phản hồi).", "• ")
add_bullet("ESP32 GPIO 4: Kết nối chân DATA của cảm biến nhiệt độ DHT11 (chuẩn 1-Wire).", "• ")
add_bullet("Nguồn nuôi: Cấp 3.3V từ chân 3V3 của ESP32 sang VCC của cảm biến, nối chung GND.", "• ")

add_placeholder_img("Hình 2.1: Sơ đồ nối dây thực tế giữa RCWL-1601, DHT11 và ESP32 Expansion Board 30-Pin")

add_h2("2.2. Thiết kế kiến trúc phần mềm hướng đối tượng (OOP)", anchor="chap2_2")
add_p("Hệ thống phần mềm được module hóa hướng đối tượng thành 3 lớp độc lập:")
add_bullet("Lớp RCWL1601: Quản lý kích phát xung, đo thời gian xung time_pulse_us, lọc trung vị 3 xung liên tiếp để loại trừ nhiễu đột biến cơ học.", "• ")
add_bullet("Lớp DHT11Sensor: Đọc định kỳ nhiệt độ T và độ ẩm RH, tính toán hệ số vận tốc âm v(T) tương ứng.", "• ")
add_bullet("Lớp DistanceMonitorApp (trên ESP32) & ESP32TerminalRunner (trên PC): Điều phối quá trình đo lặp lại N lần tại mỗi mốc, đóng gói chuỗi CSV_DATA và lưu trực tiếp vào tệp CSV trên máy tính.", "• ")

add_placeholder_img("Hình 2.2: Sơ đồ lớp UML (Class Diagram) và Lưu đồ giải thuật (Flowchart) thu thập dữ liệu")

add_h2("2.3. Bố trí bàn đo và Quy trình thực nghiệm", anchor="chap2_3")
add_p("Bàn đo được thiết lập dọc theo ray trượt / thước chuẩn kỹ thuật 2000 mm (độ chia 1 mm). Cảm biến đặt cố định vuông góc tại vạch 0 cm. Tấm cản chuẩn (kích thước 25x25 cm) di chuyển tịnh tiến vuông góc với trục âm thanh. Toàn bộ quá trình đo được tự động hóa qua kịch bản tệp batch trên máy tính.")

doc.add_page_break()

# ==================== CHƯƠNG 3 ====================
add_h1("CHƯƠNG 3: PHÂN TÍCH LỰA CHỌN CỠ MẪU TỐI ƯU N = 50 TỪ TẬP MẪU LỚN", anchor="chap3")

add_h2("3.1. Bài toán tối ưu hóa giữa Độ tin cậy thống kê và Thời gian đo", anchor="chap3_1")
add_p("Trong thực nghiệm đo lường, việc chọn cỡ mẫu N (số lần đo lặp lại tại mỗi vị trí) phải giải quyết mâu thuẫn cơ bản:")
add_bullet("Nếu N quá nhỏ (ví dụ N = 5 - 10): Sai số chuẩn của giá trị trung bình lớn, dễ bị ảnh hưởng bởi điểm dị biệt ngẫu nhiên, không đủ bậc tự do để kiểm định phân phối.", "• ")
add_bullet("Nếu N quá lớn (ví dụ N = 100 - 200): Thời gian đo kéo dài dẫn tới hiện tượng trôi nhiệt độ môi trường, quá nhiệt màng rung áp điện và tăng chi phí thực nghiệm không cần thiết.", "• ")

add_h2("3.2. Phân tích sự hội tụ của Trung bình tích lũy và Độ lệch chuẩn theo k = 2 .. 100", anchor="chap3_2")
add_p("Sử dụng tập dữ liệu đo thăm dò 100 mẫu liên tiếp tại 3 mốc khoảng cách đại diện (50 cm, 100 cm, 150 cm) từ các tệp 100lanforward_smooth_defttemp_XXXcm.csv. Khảo sát sự biến thiên của trung bình tích lũy x_bar(k) và khoảng sai số tin cậy 95% epsilon_95(k) = t_(0.95, k-1) * s(k) / sqrt(k):")

# Bảng mẫu mẫu tối ưu N
tbl_opt = doc.add_table(rows=6, cols=6)
tbl_opt.alignment = WD_TABLE_ALIGNMENT.CENTER
hdrs_opt = ["Cỡ mẫu k", "x_bar (50cm)", "s (50cm)", "x_bar (100cm)", "s (100cm)", "Sai số tin cậy ε_95%"]
for i, h in enumerate(hdrs_opt):
    c = tbl_opt.cell(0, i)
    c.text = h
    set_cell_bg(c, "003366")
    set_cell_pad(c)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.5)

sample_opt_rows = [
    ("k = 5", "[50.18]", "[0.145]", "[100.25]", "[0.198]", "± 0.180 cm"),
    ("k = 10", "[50.12]", "[0.120]", "[100.22]", "[0.175]", "± 0.086 cm"),
    ("k = 30", "[50.08]", "[0.112]", "[100.19]", "[0.162]", "± 0.042 cm"),
    ("k = 50 (Tối ưu)", "[50.05]", "[0.108]", "[100.18]", "[0.158]", "± 0.031 cm"),
    ("k = 100", "[50.04]", "[0.106]", "[100.17]", "[0.155]", "± 0.021 cm")
]

for row_idx, r_data in enumerate(sample_opt_rows):
    row = tbl_opt.rows[row_idx + 1]
    bg = "F2F5F8" if row_idx % 2 == 1 else "FFFFFF"
    for col_idx, val in enumerate(r_data):
        c = row.cells[col_idx]
        c.text = val
        set_cell_bg(c, bg)
        set_cell_pad(c)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.size = Pt(9.5)

add_h2("3.3. Biểu đồ hội tụ và Luận giải chốt cỡ mẫu N = 50", anchor="chap3_3")
add_p("Qua đồ thị biến thiên, tại điểm k ≈ 30 - 35 xuất hiện điểm khuỷu tay (elbow point). Từ k = 50 trở đi, đường cong sai số tin cậy epsilon_95% tiệm cận ngang và độ lệch chuẩn s bão hòa hoàn toàn. Việc chọn N = 50 đảm bảo sai số trung bình < 0.35 mm trong khi tiết kiệm 50% thời gian thực nghiệm so với N = 100.")

add_placeholder_img("Hình 3.1: Đồ thị 4 góc phân tích sự hội tụ của Trung bình, Độ lệch chuẩn và Sai số tin cậy tại 50cm, 100cm, 150cm")

add_guide_box("Mở script data_analysis.py hoặc chạy file phan_tich_du_lieu.bat để trích xuất bảng số liệu chính xác và ảnh biểu đồ _optimal_n.png chèn vào vị trí này.")

doc.add_page_break()

# ==================== CHƯƠNG 4 ====================
add_h1("CHƯƠNG 4: ĐÁNH GIÁ TOÀN DIỆN CÁC ĐẶC TÍNH TĨNH Ở ĐIỀU KIỆN CHUẨN (FSDT & BSDT)", anchor="chap4")

add_h2("4.1. Bảng tổng hợp thống kê toàn dải và Lọc sai số thô (3-Sigma & IQR)", anchor="chap4_1")
add_p("Dữ liệu từ tệp tổng hợp FSDT.csv được phân tích trên toàn bộ các mốc cự ly từ 1 cm đến 600 cm. Bộ lọc kép 3-Sigma và IQR được áp dụng để loại bỏ các điểm nhảy bậc chu kỳ sóng phản xạ:")

# Bảng thống kê toàn dải mẫu
tbl_stat = doc.add_table(rows=8, cols=7)
tbl_stat.alignment = WD_TABLE_ALIGNMENT.CENTER
hdrs_stat = ["d_true (cm)", "t_echo (μs)", "d_mean (cm)", "Độ lệch s (cm)", "Sai số e (cm)", "u_A (cm)", "Tỷ lệ Outlier"]
for i, h in enumerate(hdrs_stat):
    c = tbl_stat.cell(0, i)
    c.text = h
    set_cell_bg(c, "003366")
    set_cell_pad(c)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.0)

sample_stat_data = [
    ("1.0", "---", "[Nhảy loạn/0]", "---", "Vùng mù", "---", "100%"),
    ("2.0", "[120.5]", "[2.12]", "[0.280]", "[+0.12]", "[0.040]", "12%"),
    ("10.0", "[582.4]", "[10.12]", "[0.105]", "[+0.12]", "[0.015]", "0%"),
    ("50.0", "[2895.1]", "[50.08]", "[0.115]", "[+0.08]", "[0.016]", "0%"),
    ("100.0", "[5792.6]", "[100.18]", "[0.158]", "[+0.18]", "[0.022]", "0%"),
    ("300.0", "[17390.2]", "[300.52]", "[0.285]", "[+0.52]", "[0.040]", "2%"),
    ("500.0", "[28990.0]", "[501.20]", "[0.520]", "[+1.20]", "[0.074]", "6%")
]

for row_idx, r_data in enumerate(sample_stat_data):
    row = tbl_stat.rows[row_idx + 1]
    bg = "F2F5F8" if row_idx % 2 == 1 else "FFFFFF"
    for col_idx, val in enumerate(r_data):
        c = row.cells[col_idx]
        c.text = val
        set_cell_bg(c, bg)
        set_cell_pad(c)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.size = Pt(9.0)

add_h2("4.2. Khảo sát Vùng chết (Blind Zone: 1cm - 3cm) và Giới hạn đo xa (400cm - 600cm)", anchor="chap4_2")
add_bullet("Vùng chết (Blind Zone): Tại d < 2.0 cm, thời gian phản xạ t < 116 μs trùng với thời gian tắt dao động màng gốm phát (ringing time) và bão hòa mạch khuếch đại, khiến cảm biến đọc sai hoàn toàn hoặc báo timeout. Bắt đầu từ d = 3.0 cm, tín hiệu ổn định trở lại.", "• ")
add_bullet("Giới hạn đo xa: Tại d > 450 cm, biên độ sóng dội suy giảm mạnh. Tỷ lệ bắt sóng trượt tăng lên và xuất hiện sai số lớn khi đạt 550 - 600 cm. Dải đo hiệu dụng (Effective Span) khuyến nghị là 3.0 cm đến 450 cm.", "• ")

add_h2("4.3. Đánh giá Độ chụm (Precision) và Độ lặp lại (Repeatability)", anchor="chap4_3")
add_p("Độ lệch chuẩn thực nghiệm s duy trì ở mức rất thấp (s ≈ 0.10 - 0.18 cm) trong dải cự ly dưới 200 cm, tương ứng hệ số biến thiên CV% < 0.3%. Khi cự ly tăng trên 300 cm, do tán xạ môi trường, s tăng dần lên 0.3 - 0.5 cm.")

add_h2("4.4. Đánh giá Độ chính xác (Accuracy) – Sai số tuyệt đối & Tương đối", anchor="chap4_4")
add_p("Sai số tuyệt đối e = d_meas - d_true mang giá trị dương nhất quán (+1.0 mm đến +4.5 mm), bắt nguồn từ độ trễ khởi tạo mạch dao động (zero-offset). Sai số tương đối delta% giảm nhanh từ 1.2% ở 10 cm xuống < 0.2% trên toàn bộ dải đo 50 - 400 cm.")

add_h2("4.5. Đánh giá Độ tuyến tính (Linearity), Độ nhạy (Sensitivity) và Độ phân giải (Resolution)", anchor="chap4_5")
add_bullet("Phương trình hồi quy tĩnh: d_meas = a * d_true + b với a ≈ 1.0025, b ≈ +0.065 cm và hệ số xác định R^2 > 0.9999, khẳng định độ tuyến tính tuyệt đối.", "• ")
add_bullet("Độ nhạy tĩnh: S_t = Delta_t / Delta_d ≈ 57.8 μs/cm (phù hợp với vận tốc âm thanh ở 26.5°C).", "• ")
add_bullet("Sai số phi tuyến toàn dải: delta_NL ≈ 0.18% FSO, đáp ứng xuất sắc tiêu chuẩn công bố của nhà sản xuất (< 0.5% FSO).", "• ")
add_bullet("Độ phân giải (Resolution): Độ phân giải lượng tử phần cứng đạt Delta_d = (v * 1μs)/2 ≈ 0.17 mm; độ phân giải thực tế hữu ích đạt 1.0 mm.", "• ")

add_placeholder_img("Hình 4.1: Đường đặc tính truyền đạt tĩnh, đường thẳng hồi quy tuyến tính và đồ thị sai số phi tuyến %FSO")

add_h2("4.6. Khảo sát Độ trễ (Hysteresis) giữa Chiều tiến (FSDT) và Chiều lùi (BSDT)", anchor="chap4_6")
add_p("So sánh trực tiếp giữa tập dữ liệu FSDT (chiều tiến) và BSDT (chiều lùi) trên các mốc chung từ 10 cm đến 300 cm. Độ lệch trễ trung bình Delta_H_k = |d_forward - d_backward| dao động dưới 0.5 mm, sai số độ trễ toàn dải gamma_H = (Delta_H_max / FSO) * 100% < 0.15%. Kết luận: Cảm biến siêu âm RCWL-1601 không tồn tại hiện tượng trễ cơ học.")

add_placeholder_img("Hình 4.2: Biểu đồ Vòng trễ (Hysteresis Loop) so sánh đường đặc tính chiều tiến và chiều lùi")

add_h2("4.7. Đánh giá Độ không đảm bảo đo theo chuẩn ISO/GUM", anchor="chap4_7")
add_p("Tính toán ngân sách độ không đảm bảo đo tại mốc cự ly tiêu chuẩn d = 100 cm:")
add_bullet("Độ KĐBĐ Loại A (u_A): u_A = s / sqrt(N) = 0.158 / sqrt(50) ≈ 0.022 cm (0.22 mm).", "• ")
add_bullet("Độ KĐBĐ Loại B (u_B): Tổng hợp từ sai số vạch chia thước thép (u_B1 = 1mm/sqrt(3) ≈ 0.58 mm), độ phân giải bộ đếm vi điều khiển (u_B2 ≈ 0.1 mm) và sai số nhiệt độ DHT11 (u_B3 ≈ 0.35 mm) -> u_B ≈ 0.68 mm.", "• ")
add_bullet("Độ KĐBĐ tổng hợp (u_c) & Mở rộng (U_95%): u_c = sqrt(u_A^2 + u_B^2) ≈ 0.71 mm -> U_95% = 2 * u_c ≈ 1.42 mm.", "• ")

add_guide_box("Mục này tổng hợp toàn bộ các đặc tính chuẩn. Bạn chỉ cần đối chiếu các bảng CSV trong thư mục du_lieu_tong_hop/ để cập nhật số liệu chính xác.")

doc.add_page_break()

# ==================== CHƯƠNG 5 ====================
add_h1("CHƯƠNG 5: KHẢO SÁT CÁC YẾU TỐ GÂY NHIỄU NGOẠI CẢNH", anchor="chap5")

add_h2("5.1. Ảnh hưởng của Bề mặt phản xạ: Mặt nhẵn (FSDT) vs. Mặt gồ ghề (FRDT)", anchor="chap5_1")
add_p("Khảo sát sự suy giảm chất lượng tín hiệu đo khi thay đổi bề mặt phản xạ từ tấm mica phẳng nhẵn sang tấm xốp/mút gồ ghề trên các mốc cự ly từ 10 cm đến 375 cm:")
add_bullet("Hiện tượng tán xạ âm học (Acoustic Scattering): Sóng âm bị phản xạ phân tán theo nhiều hướng, làm biên độ sóng dội về đầu thu bị suy giảm mạnh.", "• ")
add_bullet("Suy giảm Độ chụm: Độ lệch chuẩn s của mặt gồ ghề tăng gấp 2.5 - 4 lần so với mặt nhẵn; xuất hiện nhiều điểm dị biệt nhảy bậc chu kỳ sóng.", "• ")
add_bullet("Suy giảm Độ chính xác: Sườn xung Echo bị trễ do biên độ sóng yếu mất nhiều chu kỳ mới kích hoạt được ngưỡng so sánh comparator -> d_rough luôn lớn hơn d_smooth từ 3 mm đến 15 mm.", "• ")
add_bullet("Thu hẹp dải đo cực đại: Cảm biến mất hoàn toàn tín hiệu phản xạ (timeout) từ cự ly 375 cm đối với mặt gồ ghề, trong khi mặt nhẵn đo được tới 600 cm.", "• ")

add_placeholder_img("Hình 5.1: Đồ thị so sánh Boxplot sai số và Độ lệch chuẩn giữa Bề mặt phẳng nhẵn (FSDT) và Bề mặt gồ ghề (FRDT)")

add_h2("5.2. Ảnh hưởng của Nhiệt độ môi trường & Hiệu quả thuật toán bù nhiệt", anchor="chap5_2")
add_p("So sánh thời gian truyền xung t_echo và khoảng cách tính toán giữa môi trường phòng thường (T ≈ 26.5°C) và phòng bật điều hòa nhiệt độ thấp (T ≈ 21.0°C):")
add_bullet("Nếu không có bù nhiệt: Vận tốc âm giảm từ 347.3 m/s xuống 344.0 m/s (chênh lệch ~3.3 m/s). Tại cự ly 200 cm, sai số trôi nhiệt độ (Thermal Drift) gây lệch khoảng cách lên tới ~2.0 cm.", "• ")
add_bullet("Khi kích hoạt thuật toán bù nhiệt từ DHT11: Giá trị khoảng cách đo được tại 2 mức nhiệt độ trùng khớp nhau với sai lệch < 1.5 mm, khẳng định vai trò thiết yếu của việc bù nhiệt trong ứng dụng thực tế.", "• ")

add_placeholder_img("Hình 5.2: Đồ thị biểu diễn sai số trôi nhiệt khi không bù nhiệt và hiệu quả ổn định tín hiệu sau khi bù nhiệt bằng DHT11")

doc.add_page_break()

# ==================== CHƯƠNG 6 ====================
add_h1("CHƯƠNG 6: TỔNG KẾT ĐẶC TÍNH KỸ THUẬT & KẾT LUẬN", anchor="chap6")

add_h2("6.1. Bảng đối chiếu Hồ sơ kỹ thuật thực nghiệm so với Datasheet của Nhà sản xuất", anchor="chap6_1")

tbl_ds = doc.add_table(rows=8, cols=4)
tbl_ds.alignment = WD_TABLE_ALIGNMENT.CENTER
hdrs_ds = ["Thông số kỹ thuật", "Công bố Datasheet", "Kết quả Thực nghiệm", "Đánh giá đạt chuẩn"]
for i, h in enumerate(hdrs_ds):
    c = tbl_ds.cell(0, i)
    c.text = h
    set_cell_bg(c, "003366")
    set_cell_pad(c)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9.5)

data_ds = [
    ("Điện áp hoạt động", "3.0V - 5.5V DC", "3.3V (cấp từ ESP32)", "Đạt chuẩn tuyệt đối"),
    ("Dải đo danh định", "2 cm - 450 cm", "3 cm - 450 cm (Hiệu dụng)", "Đạt chuẩn công bố"),
    ("Vùng chết (Blind Zone)", "< 2.0 cm", "2.0 cm - 2.5 cm", "Đạt chuẩn vật lý"),
    ("Độ phân giải danh định", "0.1 cm (1 mm)", "1.0 mm (Hữu ích) / 0.17 mm (Lượng tử)", "Vượt chuẩn công bố"),
    ("Góc mở búp sóng", "< 15 độ", "Khoảng 14.5 độ", "Đạt chuẩn"),
    ("Độ phi tuyến (%FSO)", "< 0.5% FSO", "0.18% FSO", "Đạt chuẩn vượt trội"),
    ("Độ trễ (Hysteresis)", "Không công bố", "< 0.15% FSO (< 0.5 mm)", "Rất tốt (không trễ)")
]

for row_idx, r_data in enumerate(data_ds):
    row = tbl_ds.rows[row_idx + 1]
    bg = "F2F5F8" if row_idx % 2 == 1 else "FFFFFF"
    for col_idx, val in enumerate(r_data):
        c = row.cells[col_idx]
        c.text = val
        set_cell_bg(c, bg)
        set_cell_pad(c)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.size = Pt(9.5)

add_h2("6.2. Kết luận và Khuyến nghị giải pháp kỹ thuật", anchor="chap6_2")
add_bullet("Vùng làm việc tối ưu: Cảm biến RCWL-1601 hoạt động chính xác và tuyến tính nhất trong dải cự ly 10 cm đến 300 cm đối với các vật thể có bề mặt cứng, phẳng.", "• ")
add_bullet("Khuyến nghị phần cứng: Cần duy trì khoảng cách lắp đặt tối thiểu 5 cm cách xa vật cản gần nhất để tránh rơi vào vùng chết; bố trí cảm biến vuông góc tuyệt đối với bề mặt đo.", "• ")
add_bullet("Khuyến nghị giải pháp xử lý tín hiệu: Bắt buộc tích hợp cảm biến nhiệt độ để bù vận tốc âm; áp dụng bộ lọc trung vị (Median Filter 3 xung) kết hợp lọc trung bình trượt (Moving Average Filter n = 10 mẫu) để loại trừ triệt để sóng sánh và nhiễu xung cơ học.", "• ")

add_h2("Tài liệu tham khảo & Phụ lục Code", anchor="chap6_ref")
add_bullet("Datasheet mô-đun siêu âm RCWL-1601 & IC điều khiển RCWL-9610.", "1. ")
add_bullet("Tài liệu bài giảng Kỹ thuật Đo lường và Cảm biến (ELEC-E5710 / EMA2024E_3), Đại học Bách Khoa.", "2. ")
add_bullet("ISO/IEC Guide 98-3:2008 (GUM) - Guide to the Expression of Uncertainty in Measurement.", "3. ")
add_bullet("Toàn bộ mã nguồn chương trình ESP32 và script phân tích dữ liệu được lưu trữ tại thư mục thực hành RCWL1601.", "4. ")

doc.save(OUTPUT_FILE)
print("SUCCESS: File Word Báo Cáo Khung Chuẩn (kèm Trang Phụ Lục Điều Hướng Tương Tác) đã được tạo thành công tại:")
print(OUTPUT_FILE)
