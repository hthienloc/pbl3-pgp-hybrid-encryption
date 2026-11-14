#import "template.typ": project

#show: project.with(
  institution: "TRƯỜNG ĐẠI HỌC BÁCH KHOA – ĐẠI HỌC ĐÀ NẴNG\nKHOA ĐIỆN TỬ VÀ TRÍ TUỆ NHÂN TẠO",
  doc-category: "BÁO CÁO ĐỒ ÁN HỌC PHẦN – NHÓM 7",
  main-title: "PGP / OPENPGP",
  sub-title: "Nghiên cứu và mô phỏng cơ chế mã hóa lai (Hybrid Encryption) kết hợp RSA và AES-GCM",
  author-str: "Sinh viên thực hiện:\n- Vũ Duy Dương (106230007)\n- Huỳnh Thiện Lộc (106230052)\n- Phan Vĩnh Sơn (106230059)",
  affiliation-str: "Học phần: PBL3: Mạng máy tính\nGVHD: TS. Trần Thị Minh Hạnh\nĐà Nẵng, 2026",
  heading-color: rgb("#1e40af"),
  heading-font: "Times New Roman",
  body-font: "Times New Roman",
)

#include "sections/00_abstract.typ"
#include "sections/01_introduction.typ"
#include "sections/02_related_work.typ"
#include "sections/03_methodology.typ"
#include "sections/04_experiments_results.typ"
#include "sections/05_conclusion.typ"

#pagebreak()
#bibliography("references.bib", title: [TÀI LIỆU THAM KHẢO], style: "ieee")

#include "sections/06_appendix.typ"
