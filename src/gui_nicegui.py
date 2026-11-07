#!/usr/bin/env python3
"""
Mô phỏng trực quan PGP Hybrid (RSA + AES-GCM) bằng NiceGUI.
Tích hợp KaTeX & latex2mathml để render chuẩn xác các công thức LaTeX ($...$ và $$...$$).
Mặc định: "Xin chào Cô Hạnh, bọn em là nhóm 7"
"""

import os
import sys
from nicegui import ui

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if REPORT_DIR not in sys.path:
    sys.path.insert(0, REPORT_DIR)

from algorithms.rsa import generate_rsa_keys, rsa_encrypt, rsa_decrypt
from algorithms.aes_gcm import aes_gcm_encrypt, aes_gcm_decrypt

# Trạng thái phiên làm việc
state = {
    "bob_pub": None,
    "bob_priv": None,
    "session_key": None,
    "nonce": None,
    "ciphertext": None,
    "auth_tag": None,
    "enc_session_key": None,
    "recovered_key": None,
}


def notify(msg: str, color="indigo"):
    ui.notify(msg, color=color, position="bottom-right")


def show_info(title: str, content: str):
    """Hiển thị modal giải thích chi tiết, render LaTeX tự động bằng ui.markdown(extras=['latex'])."""
    with ui.dialog() as dialog, ui.card().classes("p-5 max-w-lg w-full rounded-xl shadow-lg border border-slate-200"):
        with ui.row().classes("items-center justify-between w-full pb-2 border-b border-slate-100"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("info", size="1.4rem").classes("text-indigo-600")
                ui.label(title).classes("font-bold text-slate-800 text-sm")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense").classes("text-slate-400 hover:text-slate-600")

        # extras=['latex'] chuyển đổi $...$ và $$...$$ sang MathML/KaTeX chuẩn
        ui.markdown(content, extras=["latex"]).classes("text-xs text-slate-600 leading-relaxed mt-3")

        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Đã hiểu", on_click=dialog.close).classes("bg-slate-800 text-white text-xs px-4 py-1.5 rounded")
    dialog.open()


# --- CÁC HÀM XỬ LÝ THEO BƯỚC ---
def action_generate_keys():
    state["bob_pub"], state["bob_priv"] = generate_rsa_keys(bits=256)
    e, n = state["bob_pub"]
    d, _ = state["bob_priv"]

    lbl_bob_pub.set_text(f"e={e}, n={n}")
    lbl_bob_priv.set_text(f"d={d}")
    lbl_alice_bob_pub.set_text(f"e={e}, n={n}")

    # Reset
    state["session_key"] = None
    state["nonce"] = None
    state["ciphertext"] = None
    state["auth_tag"] = None
    state["enc_session_key"] = None
    state["recovered_key"] = None

    lbl_session_key.set_text("—")
    lbl_aes_cipher.set_text("—")
    lbl_rsa_cipher.set_text("—")
    txt_network_packet.set_value("")
    lbl_recovered_key.set_text("—")
    lbl_ghash_status.set_text("Chờ xác thực")
    lbl_ghash_status.classes(replace="text-xs text-slate-400 font-mono")
    txt_decrypted_output.set_value("")

    notify("Đã sinh cặp khóa RSA Bob (256-bit)", "teal")


def action_generate_session_key():
    state["session_key"] = os.urandom(16)
    lbl_session_key.set_text(state["session_key"].hex())
    notify("Đã tạo khóa phiên K (128-bit)", "blue")


def action_aes_encrypt():
    if not state["session_key"]:
        notify("Vui lòng sinh khóa K trước", "amber")
        return

    pt = txt_plaintext_input.value.strip()
    if not pt:
        notify("Vui lòng nhập bản rõ M", "amber")
        return

    pt_bytes = pt.encode("utf-8")
    state["ciphertext"], state["nonce"], state["auth_tag"] = aes_gcm_encrypt(
        state["session_key"], pt_bytes
    )

    lbl_aes_cipher.set_text(
        f"IV  : {state['nonce'].hex()}\n"
        f"Data: {state['ciphertext'].hex()}\n"
        f"Tag : {state['auth_tag'].hex()}"
    )
    notify("AES-GCM: Mã hóa thành công", "blue")


def action_rsa_encrypt_key():
    if not state["session_key"]:
        notify("Chưa có khóa phiên K", "amber")
        return
    if not state["bob_pub"]:
        notify("Chưa có Public Key của Bob", "amber")
        return

    key_int = int.from_bytes(state["session_key"], byteorder="big")
    state["enc_session_key"] = rsa_encrypt(state["bob_pub"], key_int)
    lbl_rsa_cipher.set_text(f"0x{state['enc_session_key']:x}")
    notify("RSA: Đã mã hóa khóa K", "blue")


def action_send_packet():
    if not state["enc_session_key"] or not state["ciphertext"]:
        notify("Cần hoàn tất mã hóa trước", "amber")
        return

    packet_str = (
        "{\n"
        f'  "C_key": "0x{state["enc_session_key"]:x}",\n'
        f'  "IV": "{state["nonce"].hex()}",\n'
        f'  "C_data": "{state["ciphertext"].hex()}",\n'
        f'  "Tag": "{state["auth_tag"].hex()}"\n'
        "}"
    )
    txt_network_packet.set_value(packet_str)
    notify("Đã truyền gói tin lên mạng", "purple")


def action_simulate_tamper():
    if not state["ciphertext"]:
        notify("Chưa có gói tin", "amber")
        return

    tampered = bytearray(state["ciphertext"])
    tampered[0] ^= 0xFF
    state["ciphertext"] = bytes(tampered)

    packet_str = (
        "// [ĐÃ SỬA ĐỔI 1 BYTE TRONG C_DATA]\n"
        "{\n"
        f'  "C_key": "0x{state["enc_session_key"]:x}",\n'
        f'  "IV": "{state["nonce"].hex()}",\n'
        f'  "C_data": "{state["ciphertext"].hex()}",\n'
        f'  "Tag": "{state["auth_tag"].hex()}"\n'
        "}"
    )
    txt_network_packet.set_value(packet_str)
    notify("Đã sửa bit trong C_data", "red")


def action_rsa_decrypt_key():
    if not state["enc_session_key"]:
        notify("Chưa có gói tin", "amber")
        return

    recovered_int = rsa_decrypt(state["bob_priv"], state["enc_session_key"])
    state["recovered_key"] = (recovered_int & ((1 << 128) - 1)).to_bytes(16, byteorder="big")
    lbl_recovered_key.set_text(state["recovered_key"].hex())
    notify("RSA: Đã khôi phục khóa K", "teal")


def action_aes_decrypt_data():
    if not state["recovered_key"]:
        notify("Chưa khôi phục khóa K", "amber")
        return

    try:
        pt_bytes = aes_gcm_decrypt(
            session_key=state["recovered_key"],
            nonce_bytes=state["nonce"],
            ciphertext_bytes=state["ciphertext"],
            auth_tag_bytes=state["auth_tag"],
        )
        decrypted_text = pt_bytes.decode("utf-8")
        txt_decrypted_output.set_value(decrypted_text)

        lbl_ghash_status.set_text("HỢP LỆ (Khớp Auth Tag)")
        lbl_ghash_status.classes(replace="text-xs text-emerald-600 font-bold")
        notify("Xác thực GHASH thành công", "emerald")
    except Exception as e:
        txt_decrypted_output.set_value(f"[LỖI: {e}]")
        lbl_ghash_status.set_text(f"LỖI: {e}")
        lbl_ghash_status.classes(replace="text-xs text-rose-600 font-bold")
        notify("Kiểm tra Tag thất bại", "red")


# --- UI SETUP ---
ui.query("body").style("background-color: #f8fafc;")

# Nạp thêm KaTeX CDN để hiển thị công thức toán học sắc nét nhất trên trình duyệt
ui.add_head_html(r"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
""")

with ui.header().classes("bg-slate-900 text-white px-5 py-2.5 flex items-center justify-between shadow-sm"):
    with ui.row().classes("items-center gap-2"):
        ui.icon("lock", size="1.5rem").classes("text-indigo-400")
        ui.label("PGP Hybrid Simulator (RSA + AES-GCM)").classes("text-sm font-bold")
    with ui.row().classes("items-center gap-2"):
        ui.button(
            icon="info",
            on_click=lambda: show_info(
                "Tổng quan mô hình PGP Hybrid",
                r"""
- **Nguyên lý PGP Hybrid:** Kết hợp ưu điểm về **tốc độ** của mật mã đối xứng (AES-GCM) và khả năng **phân phối khóa an toàn** của mật mã bất đối xứng (RSA).
- **Quy trình chuẩn:**
  1. Dữ liệu lớn $M$ được mã hóa đối xứng bằng khóa phiên ngẫu nhiên $K$ (128-bit) qua AES-GCM.
  2. Khóa phiên $K$ có kích thước cố định (16 bytes) được mã hóa bằng Public Key của Bob qua RSA.
  3. Gói tin truyền qua mạng gồm: $\{C_{\text{key}}, \text{IV}, C_{\text{data}}, \text{Tag}\}$.
                """,
            ),
        ).props("flat round dense").classes("text-slate-300 hover:text-white")
        ui.button("Đổi Khóa Bob", icon="refresh", on_click=action_generate_keys).classes(
            "bg-indigo-600 text-xs px-2.5 py-1 rounded text-white"
        )

# Bố cục 3 cột đều nhau với ui.grid(columns=3)
with ui.grid(columns=3).classes("w-full max-w-7xl mx-auto p-3 gap-3 items-start"):
    # CỘT 1: ALICE
    with ui.card().classes("w-full p-3 bg-white rounded-lg shadow-xs border border-slate-200"):
        with ui.row().classes("items-center justify-between w-full pb-1 mb-2 border-b border-slate-100"):
            with ui.row().classes("items-center gap-1"):
                ui.label("1. Phía Alice (Mã Hóa)").classes("font-bold text-slate-800 text-sm")
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Bước 1: Phía Alice (Mã Hóa)",
                        r"""
- **Vai trò:** Alice là bên gửi thông điệp.
- **Tiến trình:**
  1. Nhận Public Key $(e_B, n)$ của Bob từ trước (được đối chiếu fingerprint an toàn).
  2. Sinh ngẫu nhiên Session Key $K$ (16 bytes = 128 bits) bằng bộ sinh số ngẫu nhiên an toàn (`os.urandom(16)`).
  3. Dùng $K$ mã hóa bản rõ $M$ bằng chế độ AES-GCM, nhận về: $C_{\text{data}}$, vector khởi tạo IV (12B), và mã chứng thực Auth Tag (16B).
  4. Chuyển $K$ thành số nguyên và mã hóa qua RSA Bob: $C_{\text{key}} = K^{e_B} \pmod n$.
                        """,
                    ),
                ).props("flat round dense size=xs").classes("text-slate-400 hover:text-indigo-600")
            ui.icon("send", size="1.1rem", color="blue")

        ui.label("Public Key Bob:").classes("text-xs text-slate-400 font-semibold")
        lbl_alice_bob_pub = ui.label("...").classes("text-xs font-mono text-slate-600 truncate w-full")

        ui.label("Bản rõ đầu vào (M):").classes("text-xs text-slate-400 font-semibold mt-2")
        txt_plaintext_input = ui.textarea(
            value="Xin chào Cô Hạnh, bọn em là nhóm 7"
        ).classes("w-full text-xs").props("outlined dense rows=2")

        with ui.row().classes("w-full gap-1.5 mt-2"):
            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button("1. Khóa K", on_click=action_generate_session_key).classes("flex-1 text-xs bg-slate-800 text-white")
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Sinh Khóa Phiên K (Session Key)",
                        r"""
- **Mục đích:** Tạo ra một khóa bí mật tạm thời dùng riêng cho phiên truyền thông hiện tại.
- **Cơ chế:** Gọi hàm sinh số ngẫu nhiên bảo mật `os.urandom(16)` để tạo chuỗi 16 bytes (128 bits). Khóa này không bao giờ dùng cố định hay truyền công khai dưới dạng bản rõ.
                        """,
                    ),
                ).props("flat round dense size=xs").classes("text-slate-400 hover:text-indigo-600")

            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button("2. AES-GCM", on_click=action_aes_encrypt).classes("flex-1 text-xs bg-blue-600 text-white")
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mã Hóa AES-GCM",
                        r"""
- **Mục đích:** Mã hóa nội dung $M$ với tốc độ cao, đồng thời bảo vệ tính toàn vẹn (AEAD).
- **Cơ chế:**
  - Sinh ngẫu nhiên **IV (Nonce)** 12 bytes.
  - Phép mã hóa đối xứng AES kết hợp bộ nhân GHASH trên trường Galois $GF(2^{128})$ để sinh ra **Ciphertext** và **Authentication Tag** 16 bytes.
                        """,
                    ),
                ).props("flat round dense size=xs").classes("text-slate-400 hover:text-indigo-600")

            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button("3. RSA K", on_click=action_rsa_encrypt_key).classes("flex-1 text-xs bg-indigo-600 text-white")
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mã Hóa Khóa Phiên Bằng RSA",
                        r"""
- **Mục đích:** Bảo vệ khóa đối xứng $K$ khi truyền trên mạng công cộng.
- **Cơ chế:** Chuyển 16 bytes của $K$ thành số nguyên dương $m_K < n$. Tính:
  $$C_{\text{key}} = (m_K)^e \pmod n$$
  Chỉ ai nắm giữ Private Key tương ứng $d$ của Bob mới giải mã được giá trị này.
                        """,
                    ),
                ).props("flat round dense size=xs").classes("text-slate-400 hover:text-indigo-600")

        ui.separator().classes("my-2")
        ui.label("Khóa phiên K:").classes("text-xs text-slate-400 font-semibold")
        lbl_session_key = ui.label("—").classes("text-xs font-mono text-blue-700 truncate w-full")

        ui.label("AES-GCM (IV, C_data, Tag):").classes("text-xs text-slate-400 font-semibold mt-1")
        lbl_aes_cipher = ui.label("—").classes("text-xs font-mono text-slate-700 whitespace-pre-wrap break-all w-full")

        ui.label("C_key (RSA):").classes("text-xs text-slate-400 font-semibold mt-1")
        lbl_rsa_cipher = ui.label("—").classes("text-xs font-mono text-indigo-700 truncate w-full")

    # CỘT 2: KÊNH MẠNG
    with ui.card().classes("w-full p-3 bg-white rounded-lg shadow-xs border border-slate-200"):
        with ui.row().classes("items-center justify-between w-full pb-1 mb-2 border-b border-slate-100"):
            with ui.row().classes("items-center gap-1"):
                ui.label("2. Kênh Mạng (JSON Packet)").classes("font-bold text-slate-800 text-sm")
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Bước 2: Kênh Mạng & Đóng Gói Tin",
                        r"""
- **Mục đích:** Mô phỏng dữ liệu thực tế đóng gói vào giao thức TCP Socket khi truyền giữa máy Alice và Bob.
- **Cấu trúc JSON Envelope:**
  - `C_key`: Khóa phiên $K$ đã được mã hóa bằng RSA của Bob.
  - `IV`: Vector khởi tạo 12B (công khai) cần thiết cho giải mã AES-GCM.
  - `C_data`: Bản mã nhị phân của dữ liệu $M$.
  - `Tag`: Mã xác thực toàn vẹn GHASH 16B.
- Kẻ tấn công trên mạng dù bắt được toàn bộ gói tin này cũng **không thể khôi phục** $K$ hay $M$, và mọi sửa đổi trên `C_data` sẽ bị phát hiện ngay lập tức nhờ `Tag`.
                        """,
                    ),
                ).props("flat round dense size=xs").classes("text-slate-400 hover:text-indigo-600")
            ui.icon("wifi", size="1.1rem", color="purple")

        with ui.row().classes("w-full gap-1.5 mb-2"):
            ui.button("Gửi Gói Tin", icon="forward", on_click=action_send_packet).classes("flex-1 text-xs bg-purple-600 text-white")
            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button("Sửa Bit (Tấn Công)", icon="warning", on_click=action_simulate_tamper).classes("flex-1 text-xs bg-rose-600 text-white")
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mô Phỏng Tấn Công Sửa Đổi Bit",
                        r"""
- **Mục đích:** Kiểm chứng khả năng chống giả mạo và phát hiện can thiệp của AES-GCM (Integrity & Authenticity).
- **Hành vi mô phỏng:** Thực hiện phép XOR đảo bit (`tampered[0] ^= 0xFF`) trên byte đầu tiên của bản mã `C_data`.
- **Kỳ vọng:** Khi Bob nhận được, quá trình tính lại GHASH sẽ cho ra mã băm khác với `Tag` trong gói tin dẫn tới hệ thống lập tức ném ngoại lệ và từ chối dữ liệu.
                        """,
                    ),
                ).props("flat round dense size=xs").classes("text-slate-400 hover:text-indigo-600")

        ui.label("Dữ liệu truyền trên TCP:").classes("text-xs text-slate-400 font-semibold")
        txt_network_packet = ui.textarea().classes("w-full font-mono text-xs").props("outlined dense rows=14 readonly")

    # CỘT 3: BOB
    with ui.card().classes("w-full p-3 bg-white rounded-lg shadow-xs border border-slate-200"):
        with ui.row().classes("items-center justify-between w-full pb-1 mb-2 border-b border-slate-100"):
            with ui.row().classes("items-center gap-1"):
                ui.label("3. Phía Bob (Giải Mã)").classes("font-bold text-slate-800 text-sm")
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Bước 3: Phía Bob (Giải Mã & Kiểm Tra)",
                        r"""
- **Vai trò:** Bob là bên nhận thông điệp, nắm giữ khóa bí mật $d_B$.
- **Tiến trình:**
  1. Tiếp nhận gói tin PGP từ kết nối TCP Socket.
  2. Sử dụng Private Key $d_B$ để giải mã trường `C_key`:
     $$K = (C_{\text{key}})^{d_B} \pmod n$$
  3. Dùng $K$ cùng `IV` và `Tag` để giải mã `C_data` qua AES-GCM:
     - Tính toán lại mã kiểm tra GHASH trên dữ liệu nhận được.
     - So sánh với `Tag`: Nếu khớp hoàn toàn thì khôi phục bản rõ $M'$. Nếu sai khác thì từ chối ngay lập tức.
                        """,
                    ),
                ).props("flat round dense size=xs").classes("text-slate-400 hover:text-indigo-600")
            ui.icon("security", size="1.1rem", color="teal")

        with ui.expansion("Khóa RSA Bob", icon="key").classes("w-full text-xs mb-2"):
            ui.label("Public (e, n):").classes("text-xs text-slate-400")
            lbl_bob_pub = ui.label("...").classes("font-mono text-xs text-slate-600 truncate w-full")
            ui.label("Private d:").classes("text-xs text-slate-400 mt-1")
            lbl_bob_priv = ui.label("...").classes("font-mono text-xs text-rose-600 truncate w-full")

        with ui.row().classes("w-full gap-1.5 mb-2"):
            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button("1. Giải RSA K", on_click=action_rsa_decrypt_key).classes("flex-1 text-xs bg-teal-700 text-white")
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Giải Mã RSA Khôi Phục Khóa Phiên K",
                        r"""
- **Mục đích:** Lấy lại khóa đối xứng $K$ từ trường $C_{\text{key}}$.
- **Công thức tính:**
  $$K_{\text{int}} = (C_{\text{key}})^d \pmod n$$
  Sau đó chuyển đổi số nguyên $K_{\text{int}}$ về chuỗi 16 bytes nhị phân.
                        """,
                    ),
                ).props("flat round dense size=xs").classes("text-slate-400 hover:text-indigo-600")

            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button("2. GHASH & AES", on_click=action_aes_decrypt_data).classes("flex-1 text-xs bg-emerald-600 text-white")
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Kiểm Thực GHASH & Giải Mã AES-GCM",
                        r"""
- **Mục đích:** Đảm bảo dữ liệu không bị sửa đổi trước khi trả về bản rõ.
- **Cơ chế:** Thuật toán tính lại Auth Tag dựa trên $C_{\text{data}}$ và khóa $K$.
  - Nếu `Tag` trùng khớp: giải mã Counter Mode và xuất ra $M'$.
  - Nếu `Tag` sai lệch (do bị tấn công hoặc sai khóa): ném ngoại lệ `MAC check failed`, hủy gói tin.
                        """,
                    ),
                ).props("flat round dense size=xs").classes("text-slate-400 hover:text-indigo-600")

        ui.label("Khóa K khôi phục:").classes("text-xs text-slate-400 font-semibold")
        lbl_recovered_key = ui.label("—").classes("text-xs font-mono text-teal-800 truncate w-full")

        ui.label("Kiểm thực Auth Tag:").classes("text-xs text-slate-400 font-semibold mt-1")
        lbl_ghash_status = ui.label("Chờ xác thực").classes("text-xs text-slate-400 font-mono")

        ui.label("Bản rõ nhận được (M'):").classes("text-xs text-slate-400 font-semibold mt-2")
        txt_decrypted_output = ui.textarea().classes("w-full text-xs").props("outlined dense rows=2 readonly")

action_generate_keys()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="PGP Hybrid Simulator", port=8080, reload=False, show=False)
