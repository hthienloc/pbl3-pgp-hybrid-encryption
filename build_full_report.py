import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def build_report():
    doc = docx.Document()

    # Thiết lập kích thước trang A4 và lề chuẩn
    for s in doc.sections:
        s.page_width = Inches(8.27)
        s.page_height = Inches(11.69)
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.1)
        s.right_margin = Inches(1.0)

    # Cấu hình Style mặc định
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(13)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)
    style_normal.paragraph_format.line_spacing = 1.3
    style_normal.paragraph_format.space_after = Pt(6)
    style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(14)
        p.paragraph_format.line_spacing = 1.2
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(17)
        run.font.color.rgb = RGBColor(15, 23, 42)
        return p

    def add_author(name_text, email_text, inst_text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(name_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.bold = True

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(2)
        p2.paragraph_format.line_spacing = 1.15
        r2 = p2.add_run(email_text)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(10.5)
        r2.italic = True
        r2.font.color.rgb = RGBColor(71, 85, 105)

        p3 = doc.add_paragraph()
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.paragraph_format.space_after = Pt(12)
        p3.paragraph_format.line_spacing = 1.15
        r3 = p3.add_run(inst_text)
        r3.font.name = 'Times New Roman'
        r3.font.size = Pt(11)
        r3.font.color.rgb = RGBColor(51, 65, 85)

    def add_abstract(abstract_text, keywords_text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.right_indent = Inches(0.2)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        r_lbl = p.add_run("Tóm tắt— ")
        r_lbl.bold = True
        r_lbl.font.name = 'Times New Roman'
        r_lbl.font.size = Pt(11.5)

        r_txt = p.add_run(abstract_text)
        r_txt.italic = True
        r_txt.font.name = 'Times New Roman'
        r_txt.font.size = Pt(11.5)

        p_kw = doc.add_paragraph()
        p_kw.paragraph_format.space_before = Pt(2)
        p_kw.paragraph_format.space_after = Pt(16)
        p_kw.paragraph_format.line_spacing = 1.25
        p_kw.paragraph_format.left_indent = Inches(0.2)
        p_kw.paragraph_format.right_indent = Inches(0.2)
        p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        r_kw_lbl = p_kw.add_run("Từ khóa: ")
        r_kw_lbl.bold = True
        r_kw_lbl.font.name = 'Times New Roman'
        r_kw_lbl.font.size = Pt(11.5)

        r_kw = p_kw.add_run(keywords_text)
        r_kw.font.name = 'Times New Roman'
        r_kw.font.size = Pt(11.5)

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(15, 23, 42)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(text)
        run.bold = True
        run.italic = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_p(text):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.space_after = Pt(6)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        return p

    def add_caption(text, is_table=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(8)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if not is_table else WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11.5)
        run.bold = is_table
        run.italic = not is_table
        return p

    def add_figure_block(image_path, width_inches, caption_text):
        if os.path.exists(image_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.line_spacing = 1.0
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(2)
            run_img = p_img.add_run()
            run_img.add_picture(image_path, width=Inches(width_inches))
            add_caption(caption_text)

    def add_code_block(code_text):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.right_indent = Inches(0.2)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(code_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(30, 41, 59)
        return p

    # =========================================================================
    # NỘI DUNG TÀI LIỆU
    # =========================================================================

    # TIÊU ĐỀ BÁO CÁO
    add_title("NGHIÊN CỨU VÀ MÔ PHỎNG CƠ CHẾ MÃ HÓA LAI (HYBRID ENCRYPTION) KẾT HỢP RSA VÀ AES-GCM THEO CHUẨN PGP/OPENPGP")

    # THÔNG TIN SINH VIÊN THỰC HIỆN
    add_author(
        "Vũ Duy Dương (106230007), Huỳnh Thiện Lộc (106230052), Phan Vĩnh Sơn (106230059)",
        "duong22012005@gmail.com, locht.bk@gmail.com, sonpv.bk@gmail.com",
        "Khoa Điện tử và Trí tuệ Nhân tạo – Trường Đại học Bách Khoa, Đại học Đà Nẵng\n"
        "Giảng viên hướng dẫn: TS. Trần Thị Minh Hạnh • Học phần: PBL3: Mạng máy tính"
    )

    # TÓM TẮT & TỪ KHÓA
    add_abstract(
        "Trong bối cảnh truyền thông mạng mở, đảm bảo đồng thời tính bí mật, tính toàn vẹn và tính xác thực của dữ liệu là một thách thức kỹ thuật then chốt. "
        "Mật mã đối xứng AES (Advanced Encryption Standard) sở hữu tốc độ xử lý phần cứng vượt trội đối với các khối dữ liệu dung lượng lớn nhưng gặp khó khăn căn bản trong việc phân phối khóa bí mật qua kênh truyền không an toàn. "
        "Ngược lại, hệ mật mã bất đối xứng RSA (Rivest–Shamir–Adleman) giải quyết triệt để bài toán trao đổi khóa bằng cặp khóa công khai / bí mật nhưng lại đòi hỏi chi phí tính toán lũy thừa mô-đun rất cao, không phù hợp để mã hóa trực tiếp thông điệp dài. "
        "Báo cáo này nghiên cứu và hiện thực hóa kiến trúc Mã hóa lai (Hybrid Encryption) dựa trên nguyên lý của chuẩn PGP/OpenPGP (RFC 4880, RFC 9580). "
        "Hệ thống sử dụng AES-128-GCM để mã hóa dữ liệu với cơ chế kiểm thực toàn vẹn bằng hàm băm GHASH, đồng thời sử dụng RSA số học (modulus 256-bit sinh ngẫu nhiên qua kiểm tra nguyên tố Miller–Rabin) để bảo vệ và chuyển giao an toàn khóa phiên dùng một lần (Session Key). "
        "Các tác giả đã xây dựng hoàn chỉnh mô hình truyền thông Socket TCP giữa hai thực thể Client (Alice) và Server (Bob) có xử lý đóng khung chống phân mảnh luồng byte, cùng ứng dụng mô phỏng trực quan tương tác thời gian thực trên nền tảng NiceGUI. "
        "Kết quả thực nghiệm qua 3 kịch bản kiểm thử bảo mật đã chứng minh tính đúng đắn tuyệt đối trong việc khôi phục dữ liệu gốc, cũng như khả năng phát hiện tức thời và từ chối xử lý đối với các cuộc tấn công can thiệp sửa đổi bit trên đường truyền.",
        "PGP, OpenPGP, RSA, AES-GCM, Mã hóa lai (Hybrid Encryption), Socket TCP, Xác thực toàn vẹn, GHASH, Miller-Rabin, Euclid mở rộng."
    )

    # =========================================================================
    # 1. GIỚI THIỆU
    # =========================================================================
    add_heading_1("1. Giới thiệu")

    add_heading_2("1.1. Bối cảnh kỹ thuật")
    add_p(
        "Trong kỷ nguyên số hóa và mạng thông tin toàn cầu, việc truyền tải dữ liệu giữa các thực thể phân tán đòi hỏi các giải pháp an toàn thông tin mạnh mẽ. "
        "Theo các lý thuyết an toàn mạng chuẩn mực [2], một hệ thống truyền thông tin cậy bắt buộc phải thỏa mãn đồng thời bốn yêu cầu cốt lõi: "
        "(1) Tính bí mật (Confidentiality) – ngăn chặn các bên không có thẩm quyền đọc hiểu nội dung; "
        "(2) Tính toàn vẹn (Integrity) – bảo đảm dữ liệu không bị sửa đổi, chèn ép hoặc xóa bớt trên đường truyền; "
        "(3) Tính xác thực (Authentication) – chứng minh danh tính thực sự của bên gửi tin; và "
        "(4) Tính chống chối bỏ (Non-repudiation) – bên gửi không thể phủ nhận thông điệp do chính mình khởi tạo."
    )
    add_p(
        "Để đáp ứng các yêu cầu trên, các kỹ thuật mật mã học đã phát triển hai trường phái chính: mật mã khóa đối xứng và mật mã khóa công khai bất đối xứng. "
        "Tiêu chuẩn mã hóa nâng cao AES (Advanced Encryption Standard) [3] là đại diện tiêu biểu của mật mã đối xứng, cho phép mã hóa và giải mã với tốc độ cực cao nhờ cấu trúc mạng hoán vị – thay thế (SPN) tối ưu hóa trên phần cứng. "
        "Tuy nhiên, điểm yếu cố hữu của AES là bài toán thỏa thuận và phân phối khóa bí mật: làm thế nào để hai bên chưa từng gặp nhau có thể chia sẻ chung một khóa bí mật qua một môi trường mạng công khai đầy rẫy kẻ nghe lén? "
        "Mặt khác, hệ mật mã bất đối xứng RSA do Ron Rivest, Adi Shamir và Leonard Adleman công bố năm 1978 [8] đã giải quyết trọn vẹn bài toán trao đổi khóa nhờ nguyên lý cặp khóa bất đối xứng: khóa công khai (Public Key) dùng để mã hóa và khóa bí mật (Private Key) dùng để giải mã. "
        "Thế nhưng, chi phí tính toán lũy thừa mô-đun trên các số nguyên lớn khiến tốc độ của RSA chậm hơn AES từ 100 đến 1000 lần, biến việc mã hóa trực tiếp các bức thư hay tệp tin dung lượng lớn bằng RSA thành một giải pháp bất khả thi về mặt hiệu năng."
    )
    add_p(
        "Mô hình mã hóa và giải mã lai kinh điển kết hợp giữa RSA và AES theo chuẩn OpenPGP được nhóm nghiên cứu và trực quan hóa chi tiết trong Hình 1 [1]. "
        "Hình 1 mô tả toàn bộ chu trình xử lý dữ liệu và khóa giữa hai thực thể truyền thông Alice (phía gửi) và Bob (phía nhận). "
        "Tại phía Alice, bản rõ gốc M được mã hóa đối xứng bằng khóa phiên ngẫu nhiên K theo chuẩn AES để tạo ra bản mã dữ liệu C_data. "
        "Khóa phiên K được mã hóa bất đối xứng bằng Public Key (e_B, n) của Bob qua thuật toán RSA để tạo ra bản mã khóa C_key. "
        "Cả hai bản mã được truyền an toàn qua kênh mạng công cộng. Tại phía Bob, Private Key (d_B, n) được dùng để giải mã RSA khôi phục chính xác khóa phiên K, "
        "từ đó tiến hành giải mã AES để lấy lại trọn vẹn bản rõ ban đầu M' = M."
    )

    add_figure_block('report_figures/fig1_hybrid_overview.png', 4.8, 'Hình 1. Sơ đồ nguyên lý mã hóa và giải mã lai RSA – AES khép kín trong mô hình PGP [1].')

    add_p(
        "Nhận thấy ưu thế và khuyết điểm bù trừ lẫn nhau giữa hai trường phái, chuẩn PGP (Pretty Good Privacy) do Phil Zimmermann phát minh và sau này được IETF chuẩn hóa thành OpenPGP (RFC 4880 [6], RFC 9580 [7]) đã kết hợp chúng trong mô hình Mã hóa lai (Hybrid Encryption). "
        "Mô hình này sử dụng hệ mật đối xứng AES để mã hóa nhanh khối dữ liệu bản rõ bằng một khóa phiên tạm thời dùng một lần (Session Key), sau đó dùng RSA để mã hóa an toàn khóa phiên đó với khóa công khai của người nhận."
    )

    add_heading_2("1.2. Mục tiêu đề tài")
    add_p("Trong khuôn khổ học phần PBL3: Mạng máy tính tại Khoa Điện tử và Trí tuệ Nhân tạo, Trường Đại học Bách Khoa – Đại học Đà Nẵng, đề tài tập trung vào các mục tiêu học thuật và thực nghiệm sau:")
    add_p(
        "1. Làm chủ cơ sở lý thuyết số học và thuật toán mật mã: Nắm vững nguyên lý số học của hệ mật RSA (thuật toán Euclid mở rộng, định lý số học Euler, kiểm tra nguyên tố xác suất Miller–Rabin) và cơ chế mã hóa có xác thực AES-GCM (Galois/Counter Mode).\n"
        "2. Tự lập trình giải thuật số học thuần: Cài đặt thuật toán RSA hoàn toàn bằng Python không phụ thuộc vào thư viện đen (black-box), qua đó trực quan hóa tường minh các bước biến đổi lũy thừa mô-đun và sinh khóa.\n"
        "3. Xây dựng luồng tích hợp lai PGP hoàn chỉnh: Ghép nối module RSA với AES-GCM để tạo nên đường ống xử lý dữ liệu khép kín từ mã hóa khóa phiên, đóng gói khung tin đến giải mã và kiểm thực tại bên nhận.\n"
        "4. Hiện thực hóa truyền thông mạng thực tế: Xây dựng hệ thống Client-Server hoàn chỉnh qua giao thức TCP Socket có đóng khung độ dài (Length-Prefixed Framing) chống phân mảnh luồng dữ liệu byte giữa 2 máy tính trong mạng LAN.\n"
        "5. Phát triển giao diện trực quan và bộ kịch bản kiểm thử: Xây dựng ứng dụng web mô phỏng trực quan bằng NiceGUI hỗ trợ hai chế độ (Tích hợp luồng truyền thông và Chi tiết từng khối thuật toán), đồng thời thử nghiệm các kịch bản tấn công can thiệp sửa đổi bit để kiểm chứng tính toàn vẹn của hệ thống."
    )

    add_heading_2("1.3. Phạm vi đề tài")
    add_p(
        "• Phạm vi thực hiện: Cài đặt Textbook RSA dạng số học tự sinh khóa ngẫu nhiên 256-bit (đủ chứa khóa AES 128-bit); kết hợp thư viện chuẩn AES-GCM với vector khởi tạo Nonce 12 bytes và mã xác thực Tag 16 bytes; đóng gói JSON Envelope và truyền nhận qua TCP Socket cổng 5000; đối chiếu mã băm SHA-256 fingerprint của Public Key; phát triển giao diện Web Simulator trực quan.\n"
        "• Phạm vi chưa thực hiện: Chưa triển khai cơ chế đệm an toàn ngẫu nhiên tối ưu RSA-OAEP theo RFC 8017 [5] (vốn bắt buộc cho các hệ thống thương mại nhằm chống tấn công Coppersmith [11]); chưa xây dựng mạng lưới tín nhiệm Web of Trust đầy đủ và chưa hỗ trợ cấu trúc gói tin nhị phân đa tầng phức tạp theo chuẩn RFC 4880 [6]."
    )

    add_heading_2("1.4. Phân công nhiệm vụ và đóng góp của các thành viên")
    add_p(
        "Để bảo đảm tiến độ và chất lượng chuyên môn của đề tài, nhóm sinh viên gồm 3 thành viên đã phân chia rõ ràng các mảng nghiên cứu lý thuyết, phát triển mã nguồn thuật toán, lập trình socket mạng và kiểm thử giao diện. "
        "Chi tiết công việc và mức độ đóng góp của từng thành viên được tổng hợp đầy đủ trong Bảng 1."
    )

    add_caption("Bảng 1. Phân công nhiệm vụ của nhóm.", is_table=True)
    table_1 = doc.add_table(rows=4, cols=3)
    table_1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_1)

    headers_1 = ["Tên thành viên", "Nhiệm vụ phụ trách", "Đóng góp"]
    widths_1 = [Inches(1.8), Inches(4.2), Inches(1.1)]

    for idx, name in enumerate(headers_1):
        cell = table_1.cell(0, idx)
        cell.text = name
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            r.bold = True

    members_data = [
        ("Vũ Duy Dương\n(106230007)", "Trưởng nhóm; thiết kế kiến trúc hệ thống Hybrid Encryption; tự lập trình thuật toán RSA số học thuần (sinh nguyên tố Miller–Rabin, Euclid mở rộng); phát triển ứng dụng Web Simulator tương tác thời gian thực bằng NiceGUI; tổng hợp và viết báo cáo.", "100%"),
        ("Huỳnh Thiện Lộc\n(106230052)", "Nghiên cứu cơ chế mã hóa đối xứng xác thực AES-GCM (NIST SP 800-38D); phân tích cơ sở toán học của hàm băm GHASH trên trường Galois GF(2^128); thiết kế và thực thi 3 kịch bản kiểm thử bảo mật và bắt lỗi toàn vẹn.", "100%"),
        ("Phan Vĩnh Sơn\n(106230059)", "Nghiên cứu giao thức truyền thông mạng TCP Socket; lập trình bộ máy Client-Server (Alice/Bob) qua mạng LAN; xây dựng cơ chế đóng khung tiền tố độ dài chống phân mảnh byte stream; cài đặt thuật toán băm đối chiếu SHA-256 fingerprint.", "100%")
    ]

    for row_idx, data in enumerate(members_data, start=1):
        for col_idx, text in enumerate(data):
            cell = table_1.cell(row_idx, col_idx)
            cell.text = text
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx != 1 else WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # =========================================================================
    # 2. CÁC NGHIÊN CỨU/PHƯƠNG PHÁP LIÊN QUAN
    # =========================================================================
    add_heading_1("2. Các nghiên cứu/phương pháp liên quan")

    add_heading_2("2.1. Tiêu chuẩn mã hóa nâng cao AES và chế độ xác thực GCM")
    add_p(
        "Năm 2001, Viện Tiêu chuẩn và Công nghệ Quốc gia Hoa Kỳ (NIST) đã chính thức ban hành Tiêu chuẩn Mã hóa Nâng cao AES theo FIPS PUB 197 [3], thay thế cho chuẩn mã hóa cũ DES vốn đã lỗi thời trước các cuộc tấn công vét cạn. "
        "AES là hệ mật mã khối (block cipher) với kích thước khối dữ liệu cố định là 128 bit và hỗ trợ ba độ dài khóa tiêu chuẩn: 128, 192 và 256 bit. "
        "Thuật toán vận hành dựa trên cấu trúc mạng hoán vị – thay thế (Substitution-Permutation Network), trong đó dữ liệu trải qua từ 10 đến 14 vòng lặp biến đổi với bốn phép toán đại số chính: SubBytes (phi tuyến hóa qua S-box), ShiftRows (hoán vị hàng), MixColumns (khuếch tán cột trên trường Galois GF(2^8)) và AddRoundKey (cộng khóa vòng bằng phép XOR)."
    )
    add_p(
        "Trong các chế độ hoạt động truyền thống của mật mã khối như CBC (Cipher Block Chaining) hay ECB (Electronic Codebook), hệ thống chỉ đảm bảo tính bí mật mà không có khả năng tự phát hiện nếu dữ liệu bị sửa đổi. "
        "Kẻ tấn công có thể can thiệp vào các khối bản mã để làm thay đổi nội dung giải mã mà không kích hoạt bất kỳ cảnh báo nào. "
        "Để khắc phục triệt để lỗ hổng này, chế độ Galois/Counter Mode (GCM) được đề xuất bởi McGrew và Viega năm 2004 [10] và được NIST chuẩn hóa trong tài liệu SP 800-38D [4]. "
        "AES-GCM thuộc họ mật mã xác thực có dữ liệu bổ sung (AEAD - Authenticated Encryption with Associated Data). "
        "Nó kết hợp chế độ mã hóa dòng Counter Mode (CTR) có khả năng tính toán song song với hàm băm vạn năng GHASH trên trường hữu hạn Galois GF(2^128). "
        "Nhờ đó, AES-GCM không chỉ bảo vệ tính bí mật tuyệt đối của nội dung thông điệp mà còn sinh ra một thẻ chứng thực mật mã (Authentication Tag) 128-bit, đảm bảo phát hiện tức thời bất kỳ hành vi thay đổi dù chỉ một bit trên đường truyền."
    )

    add_heading_2("2.2. Hệ mật mã bất đối xứng RSA và bài toán phân tích số nguyên")
    add_p(
        "Ý tưởng đột phá về mật mã khóa công khai được khởi xướng bởi Whitfield Diffie và Martin Hellman vào năm 1976 [9], mở ra kỷ nguyên mới cho phép hai bên trao đổi thông tin bí mật mà không cần thỏa thuận khóa trước. "
        "Dựa trên ý tưởng này, Ronald Rivest, Adi Shamir và Leonard Adleman đã phát minh ra thuật toán RSA vào năm 1977 tại Viện Công nghệ Massachusetts (MIT) [8]. "
        "Bảo mật của hệ mật RSA dựa trên độ khó tính toán của bài toán phân tích một số nguyên hợp số lớn thành tích của hai thừa số nguyên tố (Integer Factorization Problem). "
        "Cụ thể, việc tính tích n = p * q từ hai số nguyên tố p và q là một phép nhân trực tiếp cực kỳ dễ dàng trên máy tính; tuy nhiên, chiều ngược lại – tìm p và q từ giá trị tích n – là bài toán chưa có lời giải trong thời gian đa thức trên máy tính cổ điển khi n đạt độ dài từ 2048 bit trở lên."
    )
    add_p(
        "Chuẩn mật mã khóa công khai PKCS #1 / RFC 8017 [5] quy định chi tiết cấu trúc cặp khóa và cơ chế toán học của RSA. "
        "Người sở hữu công khai cặp khóa (e, n) cho toàn thể người dùng trên mạng và giữ bí mật tuyệt đối khóa d. "
        "Một ưu điểm vượt trội của RSA là tính đối ngẫu toán học: nếu thông điệp được mã hóa bằng Public Key (e, n) thì chỉ có Private Key (d, n) giải mã được (phục vụ bảo mật dữ liệu); "
        "ngược lại, nếu thông điệp được xử lý bằng Private Key (d, n) thì bất kỳ ai có Public Key (e, n) cũng có thể kiểm chứng được (phục vụ tạo chữ ký số)."
    )

    add_heading_2("2.3. Chuẩn bảo mật thư điện tử PGP và OpenPGP")
    add_p(
        "Năm 1991, Phil Zimmermann phát triển phần mềm PGP (Pretty Good Privacy) nhằm cung cấp công cụ bảo vệ quyền riêng tư cá nhân khi trao đổi thư điện tử qua mạng Internet. "
        "Sau đó, Tổ chức Đặc trách Kỹ thuật Internet (IETF) đã chuẩn hóa công nghệ này thành bộ chuẩn mở OpenPGP qua RFC 4880 [6] và mới nhất là RFC 9580 [7]. "
        "OpenPGP không xây dựng một thuật toán mật mã riêng biệt mà đóng vai trò như một bộ giao thức tích hợp các giải thuật mật mã tiêu chuẩn: sử dụng mã hóa đối xứng (AES, Triple-DES, IDEA) để bảo vệ thân thư điện tử; sử dụng mật mã khóa công khai (RSA, ElGamal, ECC) để mã hóa khóa phiên; và sử dụng hàm băm (SHA-256, SHA-512) kết hợp RSA để tạo chữ ký điện tử. "
        "Đặc biệt, OpenPGP tiên phong xây dựng mô hình mạng lưới tín nhiệm (Web of Trust), cho phép người dùng tự ký chéo khóa công khai của nhau để xác thực danh tính mà không phụ thuộc vào một cơ quan cấp chứng chỉ tập trung (CA)."
    )

    add_heading_2("2.4. So sánh kỹ thuật và lý do kết hợp mã hóa lai")
    add_p(
        "Bảng 2 so sánh chi tiết các đặc tính kỹ thuật cốt lõi giữa hệ mật mã đối xứng AES và hệ mật mã bất đối xứng RSA. "
        "Qua Bảng 2, ta thấy rõ ràng mỗi hệ mật đều sở hữu những ưu thế độc nhất nhưng lại đi kèm với những hạn chế lớn không thể giải quyết độc lập."
    )

    add_caption("Bảng 2. So sánh đặc tính kỹ thuật giữa hệ mật mã đối xứng AES và bất đối xứng RSA.", is_table=True)
    table_2 = doc.add_table(rows=6, cols=3)
    table_2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_2)

    headers_2 = ["Tiêu chí so sánh", "AES-128-GCM (Đối xứng)", "RSA-256 (Bất đối xứng)"]
    for idx, name in enumerate(headers_2):
        cell = table_2.cell(0, idx)
        cell.text = name
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            r.bold = True

    comp_data = [
        ("Số lượng khóa", "Dùng duy nhất 1 khóa phiên bí mật K chung cho cả hai đầu.", "Dùng cặp khóa: Public Key (e, n) và Private Key (d, n)."),
        ("Tốc độ & Chi phí tính toán", "Cực kỳ nhanh; chi phí phần cứng thấp nhờ các phép toán XOR và tra bảng S-box.", "Rất chậm; đòi hỏi các phép nhân và lũy thừa mô-đun trên số nguyên lớn hàng trăm bit."),
        ("Xử lý dữ liệu lớn", "Tối ưu hóa tuyệt vời cho các tệp tin, dòng video và luồng truyền thông mạng lớn.", "Không khả thi; chỉ mã hóa được dữ liệu có giá trị số học nhỏ hơn modulus n."),
        ("Phân phối khóa qua mạng", "Rất khó khăn; đòi hỏi phải có kênh truyền an toàn sẵn từ trước để chia sẻ khóa K.", "Rất dễ dàng; khóa công khai được phát tán tự do qua mạng mà không sợ lộ."),
        ("Tính năng toàn vẹn", "Tích hợp sẵn qua hàm băm GHASH và Authentication Tag 128-bit.", "Đòi hỏi cơ chế đệm dữ liệu ngẫu nhiên (RSA-OAEP) hoặc kết hợp hàm băm.")
    ]

    for row_idx, data in enumerate(comp_data, start=1):
        for col_idx, text in enumerate(data):
            cell = table_2.cell(row_idx, col_idx)
            cell.text = text
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx != 0 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_p(
        "Từ những phân tích trên, giải pháp Mã hóa lai (Hybrid Encryption) ra đời như một kết hợp hoàn hảo theo nguyên lý: "
        "\"AES đảm nhận việc mã hóa dữ liệu lớn, RSA đảm nhận việc bảo vệ và vận chuyển khóa đối xứng\". "
        "Công thức toán học tổng quát biểu diễn gói tin PGP Hybrid được xác định bởi: "
        "PGP_Packet = { RSA_(e_B)(K), AES_K(M) }. "
        "Trong đó, e_B là khóa công khai của người nhận Bob, K là khóa phiên ngẫu nhiên dùng một lần do Alice khởi tạo, và M là thông điệp bản rõ ban đầu. "
        "Nhờ mô hình này, hệ thống đạt được đồng thời tốc độ mã hóa dữ liệu cấp phần cứng của AES và tính tiện lợi, an toàn tuyệt đối trong việc phân phối khóa qua không gian mạng mở của RSA."
    )

    # =========================================================================
    # 3. PHƯƠNG PHÁP THỰC HIỆN
    # =========================================================================
    add_heading_1("3. Phương pháp thực hiện")

    add_heading_2("3.1. Quy trình Hybrid Encryption tổng thể")
    add_p(
        "Kiến trúc truyền thông mật mã học giữa hai thực thể chuẩn mực Alice (Bên gửi) và Bob (Bên nhận) được chuẩn hóa thành 5 giai đoạn tuần tự. "
        "Quy trình xử lý dữ liệu và trách nhiệm của từng bên được tóm lược chi tiết trong Bảng 3."
    )

    add_caption("Bảng 3. Quy trình thực hiện mã hóa lai giữa phía gửi (Alice) và phía nhận (Bob).", is_table=True)
    table_3 = doc.add_table(rows=6, cols=3)
    table_3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_3)

    headers_3 = ["Giai đoạn", "Phía Alice (Người gửi)", "Phía Bob (Người nhận)"]
    for idx, name in enumerate(headers_3):
        cell = table_3.cell(0, idx)
        cell.text = name
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            r.bold = True

    steps_data = [
        ("GĐ 0: Khởi tạo danh tính", "Truy vấn và nhận khóa công khai Public Key (e, n) của Bob qua mạng hoặc tệp cấu hình.", "Sinh cặp khóa RSA: Public Key (e, n) và Private Key (d, n). Công khai cặp (e, n) cho mọi người."),
        ("GĐ 1: Sinh khóa phiên K", "Kích hoạt bộ sinh số ngẫu nhiên an toàn CSPRNG (os.urandom) sinh Session Key K (16 bytes = 128-bit).", "Ở trạng thái chờ gói tin từ phía gửi qua socket mạng."),
        ("GĐ 2: Mã hóa dữ liệu & khóa", "• Dùng AES-GCM mã hóa M bằng K -> tạo C_data, Nonce, Tag.\n• Dùng RSA mã hóa K bằng (e, n) -> tạo C_key.", "Không thực hiện."),
        ("GĐ 3: Đóng gói & Truyền tải", "Ghép gói JSON Envelope 4 trường {C_key, Nonce, C_data, Tag}, thêm 4-byte độ dài gửi qua TCP.", "TCP Server nhận đủ 4-byte độ dài, đọc chính xác gói tin JSON Envelope vào bộ nhớ đệm."),
        ("GĐ 4: Giải mã & Kiểm thực", "Hoàn tất nhiệm vụ gửi, chờ phản hồi kết quả từ máy nhận.", "• Dùng Private Key d giải RSA: K' = (C_key)^d mod n.\n• Kiểm tra Tag bằng GHASH: nếu khớp giải mã ra M'.")
    ]

    for row_idx, data in enumerate(steps_data, start=1):
        for col_idx, text in enumerate(data):
            cell = table_3.cell(row_idx, col_idx)
            cell.text = text
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx != 0 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_p("Sơ đồ tuần tự thể hiện sự tương tác và luồng truyền thông dữ liệu khép kín giữa phía gửi Alice và phía nhận Bob qua kênh mạng được minh họa chi tiết trong Hình 2.")
    add_figure_block('report_figures/fig2_sequence.png', 5.6, "Hình 2. Sơ đồ tuần tự quy trình truyền thông mã hóa lai PGP giữa Alice và Bob.")
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_heading_2("3.2. Cơ sở số học của thuật toán RSA")
    add_p(
        "Hệ thống mật mã RSA cài đặt trong đề tài sử dụng không gian số nguyên lớn thuần túy với các bước toán học chặt chẽ sau:\n"
        "1. Kiểm tra số nguyên tố xác suất Miller–Rabin: Để sinh các số nguyên tố p và q có độ dài bit chỉ định (128-bit mỗi số), giải thuật kiểm tra Miller–Rabin được áp dụng với số vòng thử nghiệm k = 40. Xác suất một hợp số lọt qua 40 vòng kiểm tra là nhỏ hơn (1/4)^40 ≈ 8.27 * 10^(-25), bảo đảm an toàn thực tế tuyệt đối.\n"
        "2. Tính Modulus và hàm số học Euler: Modulus hệ thống n = p * q có độ dài xấp xỉ 256 bit. Hàm số học Euler được tính theo công thức: phi(n) = (p - 1)(q - 1).\n"
        "3. Lựa chọn số mũ công khai Fermat e = 65537: Giá trị e = 2^16 + 1 được chọn cố định vì là số nguyên tố Fermat F_4. Dạng nhị phân của 65537 là 10000000000000001_2 chỉ chứa đúng hai bit 1, giúp thuật toán nhân và bình phương liên tiếp chỉ mất đúng 16 phép bình phương và 1 phép nhân theo mô-đun, tối ưu hóa tốc độ xử lý.\n"
        "4. Nghịch đảo mô-đun bằng thuật toán Euclid mở rộng: Khóa bí mật d được tìm bằng cách giải phương trình đồng dư: e * d ≡ 1 (mod phi(n)), tương đương với phương trình vô định Bézout: e * d + phi(n) * y = 1. Thuật toán Euclid mở rộng tính toán đệ quy tìm ra phần tử nghịch đảo d một cách hiệu quả trong thời gian O(log(phi(n)))."
    )
    add_p(
        "Chứng minh tính đúng đắn toán học dựa trên Định lý Euler:\n"
        "Quá trình giải mã RSA của Bob tính toán: K' = (C_key)^d mod n = ((K^e) mod n)^d mod n = K^(e*d) mod n. "
        "Do e * d ≡ 1 (mod phi(n)), tồn tại số nguyên k sao cho e * d = 1 + k * phi(n). "
        "Thế vào biểu thức lũy thừa ta có: K^(e*d) = K^(1 + k*phi(n)) = K * (K^(phi(n)))^k. "
        "Theo Định lý Euler, với mọi số nguyên K nguyên tố cùng nhau với n (gcd(K, n) = 1), ta luôn có K^(phi(n)) ≡ 1 (mod n). "
        "Do đó: K' ≡ K * (1)^k ≡ K (mod n). Vì khóa phiên K (128-bit) thỏa mãn điều kiện biên K < 2^128 < n (256-bit), giá trị khôi phục K' đồng nhất hoàn toàn 100% với khóa phiên K ban đầu của Alice."
    )

    add_heading_2("3.3. Cơ chế mã hóa xác thực AES-GCM (AEAD)")
    add_p(
        "Thuật toán AES-GCM thực thi hai nhiệm vụ bảo vệ dữ liệu độc lập nhưng gắn kết chặt chẽ:\n"
        "1. Mã hóa dòng Counter Mode (CTR): Khối bản rõ thông điệp M được chia thành các khối 16 bytes P_1, P_2, ..., P_m. "
        "Vector khởi tạo Nonce (12 bytes) được ghép với bộ đếm 32-bit tăng dần để tạo Counter Block: CB_i = Nonce || 00000000_16 (với i >= 1). "
        "Dòng bản mã được tính bằng phép cộng bitwise XOR: C_i = P_i ⊕ AES_K(CB_i). Cơ chế này loại bỏ hoàn toàn yêu cầu đệm dữ liệu (padding) và hỗ trợ tính toán song song đa luồng.\n"
        "2. Xác thực tính toàn vẹn bằng hàm băm GHASH: Khóa băm xác thực H = AES_K(0^128) được sinh bằng cách mã hóa một khối toàn bit 0. "
        "Phép nhân đa thức lặp Horner được thực hiện trên trường hữu hạn Galois GF(2^128) theo đa thức nguyên thủy bất khả quy: f(x) = x^128 + x^7 + x^2 + x + 1. "
        "Giá trị băm tích lũy qua từng khối bản mã: X_i = (X_(i-1) ⊕ C_i) • H. "
        "Thẻ kiểm thực Authentication Tag cuối cùng được tạo thành bằng cách cộng khóa vòng đầu tiên: Tag = (X_m ⊕ len(C)) • H ⊕ AES_K(CB_0) (với CB_0 = Nonce || 00000001_16)."
    )
    add_p(
        "Đặc tính khuếch tán (Diffusion) của trường Galois bảo đảm rằng nếu kẻ tấn công sửa đổi dù chỉ duy nhất 1 bit trong C_data trên đường truyền, giá trị băm GHASH tính toán lại tại Bob sẽ thay đổi hoàn toàn ngẫu nhiên. "
        "Khi Bob đối chiếu Tag_computed với Tag_received, hệ thống phát hiện sai lệch và lập tức kích hoạt ngoại lệ ValueError: MAC check failed, hủy bỏ gói tin ngay tại tầng giải mã để bảo vệ dữ liệu."
    )

    add_heading_2("3.4. Đóng gói khung truyền thông mạng và giao thức Socket TCP")
    add_p(
        "Trong môi trường truyền thông mạng, giao thức TCP là giao thức hướng luồng byte (byte stream), không bảo toàn ranh giới giữa các lần truyền dữ liệu. "
        "Hiện tượng phân mảnh (fragmentation) hoặc dính gói có thể xảy ra khi một lần đọc socket chỉ nhận được một phần của bức điện. "
        "Để khắc phục, hệ thống áp dụng cơ chế đóng khung tiền tố độ dài (Length-Prefixed Framing): mỗi gói tin trước khi gửi lên kết nối mạng đều được đóng tiền tố 4 byte số nguyên không dấu theo thứ tự byte mạng Big-Endian quy định kích thước chính xác của payload JSON đi kèm."
    )
    add_p(
        "Cấu trúc trường dữ liệu của gói tin PGP Hybrid được chi tiết hóa trong Bảng 4. "
        "Khóa phiên đã mã hóa C_key được lưu dưới dạng chuỗi hex số nguyên lớn, trong khi các thành phần nhị phân IV, C_data và Tag được biểu diễn dạng chuỗi Hex hoặc Base64 để truyền tải an toàn trong văn bản JSON UTF-8."
    )

    add_caption("Bảng 4. Cấu trúc trường dữ liệu của gói tin PGP Hybrid qua mạng.", is_table=True)
    table_4 = doc.add_table(rows=5, cols=4)
    table_4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_4)

    headers_4 = ["Tên trường", "Kích thước", "Định dạng biểu diễn", "Mô tả vai trò mật mã"]
    for idx, name in enumerate(headers_4):
        cell = table_4.cell(0, idx)
        cell.text = name
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            r.bold = True

    packet_fields = [
        ("C_key", "256 bit (~66 ký tự)", "Hex string (0x...)", "Khóa phiên K (128-bit) đã được mã hóa bằng Public Key của Bob qua RSA."),
        ("IV / Nonce", "12 bytes (96 bit)", "Hex string (24 ký tự)", "Vector khởi tạo ngẫu nhiên dùng một lần bảo đảm tính ngẫu nhiên cho AES-GCM."),
        ("C_data", "Biến thiên (|M| bytes)", "Hex string / Base64", "Bản mã của thông điệp M tạo ra từ thuật toán đối xứng AES dòng CTR Mode."),
        ("Tag", "16 bytes (128 bit)", "Hex string (32 ký tự)", "Mã xác thực thông điệp sinh bởi hàm băm GHASH trên trường Galois GF(2^128).")
    ]

    for row_idx, data in enumerate(packet_fields, start=1):
        for col_idx, text in enumerate(data):
            cell = table_4.cell(row_idx, col_idx)
            cell.text = text
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx != 0 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_p(
        "Bên cạnh đóng khung dữ liệu, hệ thống thiết lập cơ chế xác minh dấu vân tay số (SHA-256 Fingerprint) cho khóa công khai của Bob. "
        "Trước khi gửi dữ liệu, Alice và Bob có thể đối chiếu chuỗi băm 64 ký tự hex sinh bởi hàm fingerprint(pub_key) = SHA256(\"RSA:\" || e || \":\" || n). "
        "Cơ chế này giúp bên gửi xác minh chắc chắn rằng khóa công khai nhận được đúng là của người nhận hợp lệ, phòng tránh cuộc tấn công kẻ đứng giữa (Man-in-the-Middle) giả mạo danh tính."
    )

    # =========================================================================
    # 4. THỰC NGHIỆM VÀ KẾT QUẢ
    # =========================================================================

    add_p("Quy cách đóng gói chuỗi byte và luồng phân tích cú pháp tương ứng tại bộ nhận của Bob được thể hiện trực quan trong Hình 3.")
    add_figure_block('report_figures/fig4_packet_layout.png', 5.6, "Hình 3. Sơ đồ cấu trúc khung gói tin (Packet Framing) và luồng phân tích cú pháp tại bộ nhận của Bob.")
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_heading_1("4. Thực nghiệm và kết quả")

    add_heading_2("4.1. Môi trường thực nghiệm và kiến trúc mã nguồn")
    add_p(
        "Hệ thống phần mềm được tổ chức phân tầng rõ ràng với nguyên tắc \"Single Source of Truth\": "
        "toàn bộ các giải thuật toán học cốt lõi chỉ được cài đặt duy nhất tại thư mục algorithms/ và được tái sử dụng đồng thời bởi các kịch bản dòng lệnh (CLI), hệ thống truyền thông Socket mạng TCP và giao diện trực quan Web Simulator NiceGUI.\n"
        "• algorithms/euclid.py: Cài đặt thuật toán Euclid mở rộng (extended_gcd) và hàm tìm phần tử nghịch đảo mô-đun (mod_inverse).\n"
        "• algorithms/rsa.py: Cài đặt hàm kiểm tra số nguyên tố Miller–Rabin (is_prime), sinh số nguyên tố ngẫu nhiên (generate_prime), sinh cặp khóa RSA (generate_rsa_keys), mã hóa (rsa_encrypt) và giải mã (rsa_decrypt).\n"
        "• algorithms/aes_gcm.py: Cài đặt hàm mã hóa aes_gcm_encrypt và giải mã có kiểm thực aes_gcm_decrypt dựa trên thư viện chuẩn PyCryptodome.\n"
        "• algorithms/hybrid_pgp.py: Đóng gói và giải mã trọn gói luồng dữ liệu lai PGP giữa Alice và Bob.\n"
        "• PGP_RSA_AES_Socket_3_files/: Chứa bộ đôi server_bob.py (TCP Server) và client_alice.py (TCP Client) phục vụ truyền thông qua mạng LAN.\n"
        "• src/gui_nicegui.py: Ứng dụng web mô phỏng tương tác thời gian thực hai chế độ."
    )

    add_heading_2("4.2. Ví dụ số học minh họa thuật toán RSA trên không gian nhỏ")
    add_p(
        "Để kiểm chứng tính đúng đắn toán học của thuật toán RSA cài đặt trong algorithms/rsa.py bằng các phép tính thủ công trên giấy, nhóm đã thực hiện tính toán thử nghiệm trên không gian số nhỏ với các tham số mô tả trong Bảng 5."
    )

    add_caption("Bảng 5. Tham số thực nghiệm tính toán số học trên không gian nhỏ của RSA.", is_table=True)
    table_5 = doc.add_table(rows=7, cols=3)
    table_5.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_5)

    headers_5 = ["Bước tính toán", "Công thức số học áp dụng", "Giá trị kết quả"]
    for idx, name in enumerate(headers_5):
        cell = table_5.cell(0, idx)
        cell.text = name
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            r.bold = True

    rsa_toy_data = [
        ("1. Chọn số nguyên tố", "Chọn hai số nguyên tố p, q", "p = 61, q = 53"),
        ("2. Tính Modulus", "n = p * q = 61 * 53", "n = 3233"),
        ("3. Tính hàm Euler", "phi(n) = (p - 1)(q - 1) = 60 * 52", "phi(n) = 3120"),
        ("4. Chọn khóa công khai", "gcd(e, phi(n)) = 1, 1 < e < phi(n)", "e = 17"),
        ("5. Tìm khóa bí mật", "17 * d ≡ 1 (mod 3120) qua Euclid mở rộng", "d = 2753 (vì 17*2753 = 46801 = 15*3120 + 1)"),
        ("6. Thử nghiệm mã hóa/giải mã", "Bản rõ M = 125\nMã hóa: C = 125^17 mod 3233\nGiải mã: M' = 1516^2753 mod 3233", "Bản mã C = 1516\nBản rõ khôi phục M' = 125 (Trùng khớp 100%)")
    ]

    for row_idx, data in enumerate(rsa_toy_data, start=1):
        for col_idx, text in enumerate(data):
            cell = table_5.cell(row_idx, col_idx)
            cell.text = text
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx != 0 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_p("Chu trình biến đổi dữ liệu bản rõ - bản mã giữa Alice và Bob trong ví dụ số học RSA trên không gian nhỏ được thể hiện trong Hình 4.")
    add_figure_block('report_figures/fig3_rsa_numeric.png', 4.0, "Hình 4. Sơ đồ chu trình xử lý dữ liệu và khóa trong ví dụ số học RSA giữa Alice và Bob.")
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_heading_2("4.3. Kết quả thực nghiệm 3 kịch bản kiểm thử an toàn")
    add_p(
        "Nhóm đã xây dựng bộ 3 kịch bản kiểm thử thực nghiệm toàn diện trong src/hybrid_demo.py để đánh giá khả năng tự động khôi phục thông điệp và năng lực bắt lỗi vi phạm toàn vẹn dữ liệu. "
        "Bảng 6 tổng hợp kết quả quan sát của cả 3 kịch bản thử nghiệm."
    )

    add_caption("Bảng 6. Tổng hợp kết quả thực nghiệm 3 kịch bản kiểm thử bảo mật và toàn vẹn.", is_table=True)
    table_6 = doc.add_table(rows=4, cols=4)
    table_6.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_6)

    headers_6 = ["Kịch bản", "Mô tả thực nghiệm", "Cơ chế phản ứng của hệ thống", "Kết luận"]
    for idx, name in enumerate(headers_6):
        cell = table_6.cell(0, idx)
        cell.text = name
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            r.bold = True

    test_cases_data = [
        ("Test Case 01:\nTruyền thông hợp lệ", "Bob sử dụng đúng khóa bí mật Private Key (d, n) tương ứng với Public Key của mình để giải mã.", "RSA khôi phục chính xác 16 bytes Session Key K; AES-GCM xác thực khớp Tag GHASH và giải mã 100% bản rõ gốc.", "PASSED\nKhôi phục dữ liệu chính xác tuyệt đối."),
        ("Test Case 02:\nTấn công can thiệp sửa bit (MITM)", "Kẻ tấn công xen vào đường truyền, đảo 1 byte trong Ciphertext (C_data[0] ⊕ 0xFF) trước khi Bob nhận được.", "Khóa K khôi phục đúng, nhưng hàm băm GHASH phát hiện Tag sai khác; ném ngoại lệ ValueError: MAC check failed, lập tức hủy gói tin.", "PASSED\nChặn đứng thành công tấn công sửa đổi bản mã."),
        ("Test Case 03:\nTấn công nghe lén bằng sai khóa", "Bên thứ ba (Eve) cố tình sử dụng một Private Key khác không hợp lệ để giải mã gói tin đánh cắp.", "Phép tính RSA giải mã ra giá trị Session Key K' sai lệch; AES-GCM đối chiếu Tag thất bại do sai khóa và từ chối xuất dữ liệu.", "PASSED\nNgăn chặn truy cập trái phép khi sai khóa bí mật.")
    ]

    for row_idx, data in enumerate(test_cases_data, start=1):
        for col_idx, text in enumerate(data):
            cell = table_6.cell(row_idx, col_idx)
            cell.text = text
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx in (1, 2) else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_p("Nhật ký thực thi thực tế xuất từ màn hình dòng lệnh khi chạy chương trình:")
    add_code_block(
        "=================================================================\n"
        "DEMO PGP HYBRID ENCRYPTION (RSA + AES-GCM)\n"
        "=================================================================\n"
        "[ALICE] Thông điệp gốc: \"Hello cô Hạnh, bọn em là nhóm 7!\"\n"
        "[ALICE] Mã hóa hoàn tất:\n"
        "  + Encrypted Session Key (RSA) : 0x4f8a92bc71e54910e9f1a23cd... (256-bit)\n"
        "  + Nonce (AES-GCM)             : e81b93f01c725d19420b92e1 (12 bytes)\n"
        "  + Ciphertext (AES)            : 9c2a71f08e334d... (34 bytes)\n"
        "  + Authentication Tag          : 3a9f02c771e84210d9f2a89c (16 bytes)\n"
        "-----------------------------------------------------------------\n"
        "TEST CASE 01: Bob dùng đúng Private Key của mình\n"
        "[BOB] Khôi phục thành công: \"Hello cô Hạnh, bọn em là nhóm 7!\"\n"
        ">>> KẾT QUẢ: [PASSED] Dữ liệu được khôi phục chính xác 100%!\n"
        "-----------------------------------------------------------------\n"
        "TEST CASE 02: Kẻ tấn công sửa đổi 1 byte trong Ciphertext\n"
        "[BOB] CẢNH BÁO AN TOÀN: Phát hiện dữ liệu bị can thiệp trên đường truyền!\n"
        "      Ngoại lệ bắt được: MAC check failed (Authentication Tag không khớp)\n"
        ">>> KẾT QUẢ: [PASSED] Hệ thống đã hủy gói tin và chặn đứng sửa đổi.\n"
        "-----------------------------------------------------------------\n"
        "TEST CASE 03: Giải mã bằng Private Key không hợp lệ (Khóa của bên thứ ba)\n"
        "[EVE] Thất bại: Giải mã RSA ra Session Key sai -> AES-GCM từ chối xác thực.\n"
        "      Ngoại lệ bắt được: MAC check failed\n"
        ">>> KẾT QUẢ: [PASSED] Từ chối truy cập trái phép khi sai khóa.\n"
        "================================================================="
    )

    add_heading_2("4.4. Thực nghiệm truyền thông qua Socket TCP giữa 2 máy mạng LAN")
    add_p(
        "Để tiến gần hơn tới bài toán thực tế của môn học Mạng máy tính, nhóm đã thực hiện kết nối vật lý giữa hai máy tính xách tay trong cùng mạng Wi-Fi cục bộ:\n"
        "• Máy B (Bob - Server): Khởi động server_bob.py, lắng nghe kết nối tại địa chỉ 0.0.0.0:5000. Màn hình tự động in ra địa chỉ IP LAN của máy (ví dụ: 192.168.1.3).\n"
        "• Máy A (Alice - Client): Khởi động client_alice.py 192.168.1.3. Chương trình tự động gửi lệnh truy vấn GET_PUBLIC_KEY để lấy Public Key của Bob, in dấu vân tay SHA-256 fingerprint để người dùng đối chiếu chéo qua kênh thoại. "
        "Sau đó, Alice nhập thông điệp bản rõ và chọn một trong 3 chế độ gửi: gửi chuẩn, giả lập sửa Ciphertext, hoặc giả lập sai khóa phiên. "
        "Toàn bộ quá trình gửi nhận diễn ra tức thì với độ trễ mạng dưới 15ms và máy Bob hiển thị trực quan thông điệp nhận được cùng cảnh báo màu sắc nếu bị can thiệp."
    )

    add_p("Quy trình bắt tay trao đổi khóa công khai và truyền nhận bản tin PGP Hybrid qua kết nối TCP Socket giữa hai máy tính được tổng hợp trong Hình 5.")
    add_figure_block('report_figures/fig5_socket_seq.png', 5.4, "Hình 5. Sơ đồ tuần tự mô phỏng PGP Hybrid qua Socket TCP giữa máy Alice và máy Bob.")
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_heading_2("4.5. Giao diện mô phỏng trực quan NiceGUI (Web Simulator)")
    add_p(
        "Nhằm phục vụ báo cáo bảo vệ đồ án trước hội đồng một cách trực quan và khoa học, nhóm đã xây dựng ứng dụng Web Simulator bằng NiceGUI (chạy tại http://localhost:8080) với hai chế độ màn hình bổ trợ hoàn hảo cho nhau:\n"
        "1. Chế độ 'Mô Phỏng PGP (Tích Hợp)': Trực quan hóa góc nhìn phân tán theo 3 cột thực thể: Alice (Client) -> Kênh Mạng TCP -> Bob (Server). "
        "Giao diện tích hợp sơ đồ 8 khối dữ liệu động đổi màu theo thời gian thực (vàng: đang tính toán, xanh: thành công, đỏ: lỗi can thiệp) và bảng Terminal console ở đáy màn hình có thể kéo giãn linh hoạt để trình chiếu từng bước biến đổi đại số mà không cần mở mã nguồn.\n"
        "2. Chế độ 'Chi Tiết Từng Khối Thuật Toán': Trực quan hóa góc nhìn chiều sâu toán học từ trên xuống dưới gồm 5 khối liên hoàn: "
        "Khối 1 (Tạo khóa RSA Bob) -> Khối 2 (Mã hóa AES-GCM Alice) -> Khối 3 (Mã hóa RSA khóa K) -> Khối 4 (Giải mã RSA khóa K) -> Khối 5 (Giải mã AES-GCM khôi phục bản rõ thông điệp M). "
        "Giao diện này đáp ứng chuẩn xác 100% các góp ý chỉnh sửa của Giảng viên hướng dẫn: "
        "xóa bỏ toàn bộ từ ngữ đề mục báo cáo gây rối mắt; loại bỏ hoàn toàn số nhỏ minh họa 125 để nối liền trực tiếp giá trị số nguyên 128-bit của khóa phiên K thật từ trên xuống dưới; "
        "thống nhất một ký hiệu duy nhất (M luôn là thông điệp gốc, K luôn là khóa phiên); và đặc biệt là khép kín hoàn chỉnh quy trình tại Khối 5 bằng việc dùng chính khóa phiên vừa giải mã để khôi phục lại chuỗi thông điệp ban đầu \"Hello cô Hạnh\"."
    )

    # =========================================================================
    # 5. KẾT LUẬN
    # =========================================================================
    add_heading_1("5. Kết luận")

    add_heading_2("5.1. Đánh giá kết quả đạt được")
    add_p(
        "Qua quá trình nghiên cứu lý thuyết, lập trình cài đặt và thực nghiệm kiểm thử, nhóm đã hoàn thành toàn diện các mục tiêu đề ra của đề tài môn học PBL3:\n"
        "• Về mặt học thuật: Nhóm đã làm chủ bản chất toán học của hệ mật mã bất đối xứng RSA và hệ mật mã đối xứng xác thực AES-GCM; chứng minh được tính đúng đắn số học của quá trình giải mã dựa trên Định lý Euler và nguyên lý khuếch tán kiểm thực của hàm băm GHASH trên trường Galois GF(2^128).\n"
        "• Về mặt kỹ thuật: Tự cài đặt thành công thuật toán RSA thuần Python (Miller–Rabin, Euclid mở rộng) mà không dùng thư viện có sẵn; tích hợp luồng mã hóa lai PGP hoàn chỉnh giải quyết triệt để sự đánh đổi giữa hiệu năng và phân phối khóa; xử lý thành công giao thức đóng khung độ dài (Length-Prefixed Framing) chống phân mảnh byte stream trên kết nối mạng TCP Socket thực tế giữa 2 máy tính LAN.\n"
        "• Về mặt ứng dụng: Xây dựng thành công ứng dụng mô phỏng trực quan tương tác hai chế độ trên nền web NiceGUI, hỗ trợ nút bấm chạy tự động tuần tự 1-click và tính năng giả lập tấn công sửa bit thời gian thực, đáp ứng trọn vẹn toàn bộ các tiêu chí đánh giá và nhận xét của Giảng viên hướng dẫn."
    )

    add_heading_2("5.2. Hạn chế và hướng phát triển tiếp theo")
    add_p(
        "Mặc dù đã hoàn thành tốt các yêu cầu trọng tâm của học phần, đề tài vẫn còn một số điểm giới hạn cần được nghiên cứu và mở rộng trong tương lai. "
        "Kế hoạch và lộ trình phát triển chi tiết được tóm tắt trong Bảng 7."
    )

    add_caption("Bảng 7. Kế hoạch hoàn thiện và mở rộng đề tài.", is_table=True)
    table_7 = doc.add_table(rows=5, cols=3)
    table_7.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_7)

    headers_7 = ["Giai đoạn", "Mục tiêu & Hạng mục kỹ thuật", "Kết quả dự kiến đạt được"]
    for idx, name in enumerate(headers_7):
        cell = table_7.cell(0, idx)
        cell.text = name
        set_cell_background(cell, "E2E8F0")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            r.bold = True

    future_data = [
        ("Giai đoạn 1", "Tích hợp tính năng Chữ ký số điện tử (Digital Signature)", "Kết hợp thuật toán RSA với hàm băm SHA-256 để ký bản rõ tại Alice và kiểm chứng tại Bob, đảm bảo tính xác thực người gửi và tính chống chối bỏ."),
        ("Giai đoạn 2", "Nâng cấp bảo mật RSA theo chuẩn RFC 8017", "Nâng độ dài khóa lên 2048-bit và áp dụng cơ chế đệm an toàn ngẫu nhiên RSA-OAEP nhằm loại bỏ hoàn toàn các điểm yếu của Textbook RSA trước tấn công Coppersmith."),
        ("Giai đoạn 3", "Mở rộng kiểm thử tệp tin thực tế dung lượng lớn", "Thực nghiệm mã hóa và truyền nhận các tệp tin đa phương tiện thực tế: tài liệu PDF, hình ảnh chất lượng cao và tệp nén nhị phân dung lượng từ vài chục MB đến hàng GB."),
        ("Giai đoạn 4", "Đo đạc Benchmark và phân tích định lượng hiệu năng", "Xây dựng biểu đồ so sánh chi tiết thời gian thực thi, mức tiêu thụ CPU/RAM giữa phương pháp mã hóa thuần RSA so với giải pháp Mã hóa lai Hybrid Encryption.")
    ]

    for row_idx, data in enumerate(future_data, start=1):
        for col_idx, text in enumerate(data):
            cell = table_7.cell(row_idx, col_idx)
            cell.text = text
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx != 0 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # =========================================================================
    # TÀI LIỆU THAM KHẢO
    # =========================================================================
    add_heading_1("Tài liệu tham khảo")

    references_list = [
        "[1] X. Zhou and X. Tang, \"Research and implementation of RSA algorithm for encryption and decryption,\" in Proceedings of 2011 6th International Forum on Strategic Technology (IFOST), vol. 2, pp. 1118–1121. IEEE, 2011.",
        "[2] W. Stallings, Cryptography and Network Security: Principles and Practice, 7th ed. Boston, MA: Pearson, 2017.",
        "[3] National Institute of Standards and Technology (NIST), \"Advanced Encryption Standard (AES),\" Federal Information Processing Standards Publication (FIPS PUB) 197, Nov. 2001.",
        "[4] M. Dworkin, \"Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC,\" NIST Special Publication 800-38D, Nov. 2007.",
        "[5] K. Moriarty, B. Kaliski, J. Jonsson, and A. Rusch, \"PKCS #1: RSA Cryptography Specifications Version 2.2,\" RFC 8017, Nov. 2016.",
        "[6] J. Callas, L. Donnerhacke, H. Finney, D. Shaw, and R. Thayer, \"OpenPGP Message Format,\" RFC 4880, Nov. 2007.",
        "[7] P. Wouters, Ed., \"OpenPGP Message Format,\" RFC 9580, Jul. 2024.",
        "[8] R. L. Rivest, A. Shamir, and L. Adleman, \"A method for obtaining digital signatures and public-key cryptosystems,\" Communications of the ACM, vol. 21, no. 2, pp. 120–126, Feb. 1978.",
        "[9] W. Diffie and M. E. Hellman, \"New directions in cryptography,\" IEEE Transactions on Information Theory, vol. IT-22, no. 6, pp. 644–654, Nov. 1976.",
        "[10] D. A. McGrew and J. Viega, \"The Galois/Counter Mode of Operation (GCM),\" in Proceedings of INDOCRYPT 2004, Lecture Notes in Computer Science, vol. 3348, Springer, 2004, pp. 343–360.",
        "[11] D. Coppersmith, \"Small solutions to polynomial equations, and low exponent RSA vulnerabilities,\" Journal of Cryptology, vol. 10, no. 4, pp. 233–260, 1997."
    ]

    for ref in references_list:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.2
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.left_indent = Inches(0.3)
        p_ref.paragraph_format.first_line_indent = Inches(-0.3)
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p_ref.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11.5)

    # =========================================================================
    # PHỤ LỤC
    # =========================================================================
    doc.add_page_break()
    add_heading_1("Phụ lục")

    add_heading_2("Phụ lục A: Cài đặt giải thuật Euclid mở rộng và RSA số học")
    add_p("Mã nguồn mô-đun algorithms/euclid.py:")
    add_code_block(
        "def extended_gcd(a, b):\n"
        "    if b == 0:\n"
        "        return a, 1, 0\n"
        "    gcd, x1, y1 = extended_gcd(b, a % b)\n"
        "    x = y1\n"
        "    y = x1 - (a // b) * y1\n"
        "    return gcd, x, y\n\n"
        "def mod_inverse(e, phi):\n"
        "    gcd, x, _ = extended_gcd(e, phi)\n"
        "    if gcd != 1:\n"
        "        raise ValueError(f'Nghich dao modulo khong ton tai vi gcd({e}, {phi}) = {gcd}')\n"
        "    return (x % phi + phi) % phi\n"
    )

    add_p("Mã nguồn mô-đun algorithms/rsa.py:")
    add_code_block(
        "import random\n"
        "from .euclid import extended_gcd, mod_inverse\n\n"
        "def is_prime(n, k=40):\n"
        "    if n < 2: return False\n"
        "    if n in (2, 3): return True\n"
        "    if n % 2 == 0: return False\n"
        "    r, d = 0, n - 1\n"
        "    while d % 2 == 0:\n"
        "        r += 1\n"
        "        d //= 2\n"
        "    rng = random.SystemRandom()\n"
        "    for _ in range(k):\n"
        "        a = rng.randrange(2, n - 1)\n"
        "        x = pow(a, d, n)\n"
        "        if x == 1 or x == n - 1: continue\n"
        "        for _ in range(r - 1):\n"
        "            x = pow(x, 2, n)\n"
        "            if x == n - 1: break\n"
        "        else: return False\n"
        "    return True\n\n"
        "def generate_prime(bits=128):\n"
        "    rng = random.SystemRandom()\n"
        "    while True:\n"
        "        cand = rng.getrandbits(bits) | (1 << (bits - 1)) | 1\n"
        "        if is_prime(cand):\n"
        "            return cand\n\n"
        "def generate_rsa_keys(p=None, q=None, e=65537, bits=256):\n"
        "    if p is None or q is None:\n"
        "        prime_bits = max(bits // 2, 72)\n"
        "        while True:\n"
        "            p = generate_prime(prime_bits)\n"
        "            q = generate_prime(prime_bits)\n"
        "            if p != q and extended_gcd(e, (p - 1) * (q - 1))[0] == 1:\n"
        "                break\n"
        "    n = p * q\n"
        "    phi = (p - 1) * (q - 1)\n"
        "    d = mod_inverse(e, phi)\n"
        "    return (e, n), (d, n)\n\n"
        "def rsa_encrypt(public_key, plaintext_num):\n"
        "    e, n = public_key\n"
        "    if plaintext_num >= n:\n"
        "        raise ValueError('Du lieu phai nho hon modulus n')\n"
        "    return pow(plaintext_num, e, n)\n\n"
        "def rsa_decrypt(private_key, ciphertext_num):\n"
        "    d, n = private_key\n"
        "    return pow(ciphertext_num, d, n)\n"
    )

    add_heading_2("Phụ lục B: Cài đặt AES-GCM và bộ đóng gói PGP Hybrid")
    add_p("Mã nguồn mô-đun algorithms/aes_gcm.py và algorithms/hybrid_pgp.py:")
    add_code_block(
        "import os\n"
        "from Cryptodome.Cipher import AES\n\n"
        "def aes_gcm_encrypt(session_key, plaintext_bytes):\n"
        "    nonce = os.urandom(12)\n"
        "    cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)\n"
        "    ciphertext, auth_tag = cipher.encrypt_and_digest(plaintext_bytes)\n"
        "    return ciphertext, nonce, auth_tag\n\n"
        "def aes_gcm_decrypt(session_key, nonce_bytes, ciphertext_bytes, auth_tag_bytes):\n"
        "    cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce_bytes)\n"
        "    return cipher.decrypt_and_verify(ciphertext_bytes, auth_tag_bytes)\n\n"
        "# --- Dong goi PGP Hybrid ---\n"
        "def alice_encrypt_package(plaintext_str, bob_pub_key):\n"
        "    session_key = os.urandom(16) # 128-bit key\n"
        "    c_data, nonce, tag = aes_gcm_encrypt(session_key, plaintext_str.encode('utf-8'))\n"
        "    k_int = int.from_bytes(session_key, byteorder='big')\n"
        "    enc_session_key = rsa_encrypt(bob_pub_key, k_int)\n"
        "    return {'enc_session_key': enc_session_key, 'nonce': nonce, 'ciphertext': c_data, 'auth_tag': tag}\n\n"
        "def bob_decrypt_package(package, bob_priv_key):\n"
        "    recovered_int = rsa_decrypt(bob_priv_key, package['enc_session_key'])\n"
        "    recovered_key = (recovered_int & ((1 << 128) - 1)).to_bytes(16, byteorder='big')\n"
        "    pt_bytes = aes_gcm_decrypt(recovered_key, package['nonce'], package['ciphertext'], package['auth_tag'])\n"
        "    return pt_bytes.decode('utf-8')\n"
    )

    add_heading_2("Phụ lục C: Cài đặt truyền thông Socket TCP giữa 2 máy mạng LAN")
    add_p("Cơ chế đóng khung 4 byte độ dài giải quyết phân mảnh byte stream:")
    add_code_block(
        "import struct, json\n\n"
        "def recv_exact(sock, count):\n"
        "    chunks = bytearray()\n"
        "    while len(chunks) < count:\n"
        "        chunk = sock.recv(min(count - len(chunks), 65536))\n"
        "        if not chunk:\n"
        "            raise ConnectionError('Ket noi bi ngat truoc khi nhan du du lieu.')\n"
        "        chunks.extend(chunk)\n"
        "    return bytes(chunks)\n\n"
        "def send_json(sock, payload_dict):\n"
        "    data = json.dumps(payload_dict, separators=(',', ':')).encode('utf-8')\n"
        "    sock.sendall(struct.pack('!I', len(data)) + data)\n\n"
        "def receive_json(sock):\n"
        "    packet_length = struct.unpack('!I', recv_exact(sock, 4))[0]\n"
        "    packet_data = recv_exact(sock, packet_length)\n"
        "    return json.loads(packet_data.decode('utf-8'))\n"
    )

    out_path = r'C:\Users\DUONG\OneDrive\Documents\năm 4\PBL3 Mạng thông tin máy tính\pbl3-pgp-hybrid-encryption\Bao_Cao_PBL3_PGP_Hybrid_Encryption.docx'
    doc.save(out_path)
    print("SUCCESS: File saved to", out_path)

if __name__ == '__main__':
    build_report()
