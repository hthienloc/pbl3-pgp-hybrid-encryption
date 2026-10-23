#import "template.typ": project

#show: project.with(
  institution: "TRƯỜNG ĐẠI HỌC BÁCH KHOA – ĐẠI HỌC ĐÀ NẴNG\nKHOA ĐIỆN TỬ VÀ TRÍ TUỆ NHÂN TẠO",
  doc-category: "BÁO CÁO TIẾN ĐỘ – NHÓM 7",
  main-title: "PGP",
  sub-title: "Nguyên lý RSA và mô hình mã hóa lai RSA – AES",
  author-str: "Sinh viên thực hiện:\n- Vũ Duy Dương (106230007)\n- Huỳnh Thiện Lộc (106230052)\n- Phan Vinh Sơn (106230059)",
  affiliation-str: "Học phần: PBL3: Mạng máy tính\nGVHD: TS. Trần Thị Minh Hạnh\nĐà Nẵng, 2026",
  heading-color: rgb("#1e40af"),
  heading-font: "Liberation Sans",
  body-font: "Liberation Sans",
)

#include "sections/00_glossary.typ"
#include "sections/01_introduction.typ"
#include "sections/02_hybrid_concept.typ"
#include "sections/03_process.typ"
#include "sections/04_rsa_keygen.typ"
#include "sections/05_rsa_implementation.typ"
#include "sections/06_rsa_example.typ"
#include "sections/07_integration.typ"
#include "sections/08_testing.typ"
#include "sections/09_conclusion.typ"
#include "sections/10_qa.typ"
