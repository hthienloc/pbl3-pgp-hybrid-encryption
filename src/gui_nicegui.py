#!/usr/bin/env python3
"""
Mô phỏng trực quan PGP Hybrid (RSA + AES-GCM) bằng NiceGUI.
- Tích hợp giải thích chi tiết thuật toán trong Info popup (mapping với báo cáo PBL3).
- Bổ sung sơ đồ trực quan đường đi dữ liệu (Dataflow Diagram) ở phía dưới,
  tự động cập nhật trạng thái hoạt động theo từng bước phía trên.
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
    # Trạng thái tiến trình cho sơ đồ động (None | 'running' | 'success' | 'error')
    "step_status": {
        "m": "ready",
        "k": "waiting",
        "aes_enc": "waiting",
        "rsa_enc": "waiting",
        "network": "waiting",
        "rsa_dec": "waiting",
        "ghash": "waiting",
        "aes_dec": "waiting",
        "m_out": "waiting",
    },
}


def notify(msg: str, color="indigo"):
    ui.notify(msg, color=color, position="bottom-right")


def show_info(title: str, content: str):
    """Hiển thị modal giải thích chi tiết thuật toán, render LaTeX qua latex2mathml."""
    with ui.dialog() as dialog, ui.card().classes(
        "p-5 max-w-2xl w-full rounded-xl shadow-xl border border-slate-200"
    ):
        with ui.row().classes(
            "items-center justify-between w-full pb-2 border-b border-slate-100"
        ):
            with ui.row().classes("items-center gap-2"):
                ui.icon("info", size="1.4rem").classes("text-indigo-600")
                ui.label(title).classes("font-bold text-slate-800 text-sm")
            ui.button(icon="close", on_click=dialog.close).props(
                "flat round dense"
            ).classes("text-slate-400 hover:text-slate-600")

        ui.markdown(content, extras=["latex"]).classes(
            "text-xs text-slate-600 leading-relaxed mt-3"
        )

        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Đã hiểu", on_click=dialog.close).classes(
                "bg-slate-800 text-white text-xs px-4 py-1.5 rounded"
            )
    dialog.open()


# --- CẬP NHẬT GIAO DIỆN SƠ ĐỒ ĐƯỜNG ĐI DỮ LIỆU ---
def update_diagram():
    """Cập nhật màu sắc, badge và giá trị tóm tắt trên sơ đồ trực quan luồng dữ liệu."""
    st = state["step_status"]

    def style_node(status):
        if status == "success":
            return "border-emerald-500 bg-emerald-50 text-emerald-900 shadow-sm"
        elif status == "active":
            return "border-blue-500 bg-blue-50 text-blue-900 shadow-md ring-2 ring-blue-300"
        elif status == "error":
            return "border-rose-500 bg-rose-50 text-rose-900 shadow-sm"
        return "border-slate-200 bg-slate-50 text-slate-400 opacity-60"

    card_node_m.classes(
        replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['m'])}"
    )
    card_node_k.classes(
        replace=f"p-2.5 rounded-lg border-2 border-dashed text-center transition-all {style_node(st['k'])}"
    )
    card_node_aes_enc.classes(
        replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['aes_enc'])}"
    )
    card_node_rsa_enc.classes(
        replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['rsa_enc'])}"
    )
    card_node_net.classes(
        replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['network'])}"
    )
    card_node_rsa_dec.classes(
        replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['rsa_dec'])}"
    )
    card_node_aes_dec.classes(
        replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['aes_dec'])}"
    )
    card_node_m_out.classes(
        replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['m_out'])}"
    )

    # Cập nhật nhãn phụ tóm tắt dưới mỗi khối
    lbl_flow_k.set_text(
        state["session_key"].hex()[:10] + "..." if state["session_key"] else "(chưa có)"
    )
    lbl_flow_cdata.set_text(
        f"C_data ({len(state['ciphertext'])}B)" if state["ciphertext"] else "(chưa có)"
    )
    lbl_flow_ckey.set_text(
        f"C_key: 0x{state['enc_session_key']:x}"[:14] + "..."
        if state["enc_session_key"]
        else "(chưa có)"
    )
    lbl_flow_net.set_text(
        "Payload 4 trường PGP" if state["step_status"]["network"] != "waiting" else "(chờ gửi)"
    )
    lbl_flow_rec_k.set_text(
        state["recovered_key"].hex()[:10] + "..." if state["recovered_key"] else "(chưa có)"
    )


# --- CÁC HÀM XỬ LÝ THEO BƯỚC ---
def action_generate_keys():
    state["bob_pub"], state["bob_priv"] = generate_rsa_keys(bits=256)
    e, n = state["bob_pub"]
    d, _ = state["bob_priv"]

    lbl_bob_pub.set_text(f"e={e}, n={n}")
    lbl_bob_priv.set_text(f"d={d}")
    lbl_alice_bob_pub.set_text(f"e={e}, n={n}")

    # Reset toàn bộ trạng thái dữ liệu
    state["session_key"] = None
    state["nonce"] = None
    state["ciphertext"] = None
    state["auth_tag"] = None
    state["enc_session_key"] = None
    state["recovered_key"] = None

    state["step_status"] = {
        "m": "ready",
        "k": "waiting",
        "aes_enc": "waiting",
        "rsa_enc": "waiting",
        "network": "waiting",
        "rsa_dec": "waiting",
        "ghash": "waiting",
        "aes_dec": "waiting",
        "m_out": "waiting",
    }

    lbl_session_key.set_text("—")
    lbl_aes_cipher.set_text("—")
    lbl_rsa_cipher.set_text("—")
    txt_network_packet.set_value("")
    lbl_recovered_key.set_text("—")
    lbl_ghash_status.set_text("Chờ xác thực")
    lbl_ghash_status.classes(replace="text-xs text-slate-400 font-mono")
    txt_decrypted_output.set_value("")

    update_diagram()
    notify("Đã sinh cặp khóa RSA Bob (256-bit)", "teal")


def action_generate_session_key():
    state["session_key"] = os.urandom(16)
    lbl_session_key.set_text(state["session_key"].hex())

    state["step_status"]["k"] = "success"
    update_diagram()
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

    state["step_status"]["m"] = "success"
    state["step_status"]["aes_enc"] = "success"
    update_diagram()
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

    state["step_status"]["rsa_enc"] = "success"
    update_diagram()
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

    state["step_status"]["network"] = "success"
    update_diagram()
    notify("Đã truyền gói tin lên mạng", "purple")


def action_simulate_tamper():
    if not state["ciphertext"]:
        notify("Chưa có gói tin", "amber")
        return

    # Sửa 1 byte đầu tiên của bản mã Ciphertext
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

    state["step_status"]["network"] = "error"
    update_diagram()
    notify("Đã sửa bit trong C_data", "red")


def action_rsa_decrypt_key():
    if not state["enc_session_key"]:
        notify("Chưa có gói tin", "amber")
        return

    recovered_int = rsa_decrypt(state["bob_priv"], state["enc_session_key"])
    state["recovered_key"] = (recovered_int & ((1 << 128) - 1)).to_bytes(16, byteorder="big")
    lbl_recovered_key.set_text(state["recovered_key"].hex())

    state["step_status"]["rsa_dec"] = "success"
    update_diagram()
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

        state["step_status"]["aes_dec"] = "success"
        state["step_status"]["m_out"] = "success"
        update_diagram()
        notify("Xác thực GHASH thành công", "emerald")
    except Exception as e:
        txt_decrypted_output.set_value(f"[LỖI: {e}]")
        lbl_ghash_status.set_text(f"LỖI: {e}")
        lbl_ghash_status.classes(replace="text-xs text-rose-600 font-bold")

        state["step_status"]["aes_dec"] = "error"
        state["step_status"]["m_out"] = "error"
        update_diagram()
        notify("Kiểm tra Tag thất bại", "red")


# --- XÂY DỰNG GIAO DIỆN (UI SETUP) ---
ui.query("body").style("background-color: #f8fafc;")

ui.add_head_html(r"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
""")

with ui.header().classes(
    "bg-slate-900 text-white px-5 py-2.5 flex items-center justify-between shadow-sm"
):
    with ui.row().classes("items-center gap-2"):
        ui.icon("lock", size="1.5rem").classes("text-indigo-400")
        ui.label("PGP Hybrid Simulator (RSA + AES-GCM)").classes("text-sm font-bold")
    with ui.row().classes("items-center gap-2"):
        ui.button(
            icon="info",
            on_click=lambda: show_info(
                "Mục 2 & Mục 7: Tổng Quan Kiến Trúc Mã Hóa Lai PGP",
                r"""
### 1. Bài toán và Động lực thiết kế (Mục 2 trong báo cáo)
- **Mã hóa đối xứng (AES-128):** Tốc độ phần cứng cực nhanh, xử lý dữ liệu lớn không giới hạn nhưng tồn tại nghịch lý **phải chia sẻ khóa bí mật $K$ từ trước qua kênh bảo mật**.
- **Mã hóa bất đối xứng (RSA):** Cho phép trao đổi dữ liệu an toàn qua kênh công khai nhờ cặp khóa $(e, d)$, nhưng thuật toán tính lũy thừa mô-đun trên số nguyên lớn $C = M^e \pmod n$ tốn nhiều tài nguyên tính toán (chậm gấp ~1000 lần AES), không khả thi cho dữ liệu dung lượng lớn.
- **Giải pháp Hybrid PGP:** 
  $$\text{PGP Packet} = \{\text{RSA}_{e_B}(K), \quad \text{AES-GCM}_K(M)\}$$
  Alice sinh khóa phiên ngẫu nhiên $K$ 128-bit. AES dùng $K$ mã hóa nội dung $M$, còn RSA Bob bảo vệ duy nhất 16 bytes của $K$.

### 2. Định dạng gói tin trên mạng (Mục 7.1 - Packet Framing)
Gói tin JSON Envelope đóng gói 4 trường độc lập:
1. $C_{\text{key}}$: Khóa đối xứng $K$ đã được mã hóa bằng Public Key của Bob.
2. $\text{IV}$ (Nonce): Vector 12 bytes ngẫu nhiên, không lặp lại theo chuẩn NIST SP 800-38D.
3. $C_{\text{data}}$: Bản mã dữ liệu kích thước tùy ý sinh bởi bộ mã hóa CTR Mode.
4. $\text{Tag}$: Mã chứng thực toàn vẹn GHASH 16 bytes.
                """,
            ),
        ).props("flat round dense").classes("text-slate-300 hover:text-white")
        ui.button("Đổi Khóa Bob", icon="refresh", on_click=action_generate_keys).classes(
            "bg-indigo-600 text-xs px-2.5 py-1 rounded text-white"
        )

# BỐ CỤC 3 CỘT ĐỀU NHAU (GRID COLUMNS = 3)
with ui.grid(columns=3).classes("w-full max-w-7xl mx-auto p-3 gap-3 items-start"):
    # CỘT 1: ALICE
    with ui.card().classes(
        "w-full p-3 bg-white rounded-lg shadow-xs border border-slate-200"
    ):
        with ui.row().classes(
            "items-center justify-between w-full pb-1 mb-2 border-b border-slate-100"
        ):
            with ui.row().classes("items-center gap-1"):
                ui.label("1. Phía Alice (Mã Hóa)").classes(
                    "font-bold text-slate-800 text-sm"
                )
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mục 3.1 & 7.3: Quy Trình Mã Hóa Phía Alice",
                        r"""
Theo quy trình chuẩn tại Mục 3 và hàm `alice_encrypt_package` (Mục 7.3):

1. **Khởi tạo và đối chiếu khóa:** Alice nhận Public Key $(e_B, n)$ của Bob, tiến hành kiểm tra Fingerprint SHA-256 qua kênh xác thực ngoại vi (Out-of-Band) để chống giả mạo (Man-in-the-Middle).
2. **Sinh Session Key $K$:** Tạo 16 bytes dữ liệu ngẫu nhiên giả định với entropy cao bằng `os.urandom(16)`.
3. **Mã hóa AES-GCM:** 
   $$(C_{\text{data}}, \text{Tag}) = \text{AES-GCM}_K(M, \text{IV})$$
   Đồng thời sinh ra vector $\text{IV}$ (12B) và mã kiểm tra tính toàn vẹn $\text{Tag}$ (16B).
4. **Mã hóa khóa RSA:** Chuyển $K$ thành số nguyên và mã hóa bảo vệ:
   $$C_{\text{key}} = K^{e_B} \pmod n$$
5. **Đóng gói:** Tạo envelope gồm 4 trường $\{C_{\text{key}}, \text{IV}, C_{\text{data}}, \text{Tag}\}$.
                        """,
                    ),
                ).props("flat round dense size=xs").classes(
                    "text-slate-400 hover:text-indigo-600"
                )
            ui.icon("send", size="1.1rem", color="blue")

        ui.label("Public Key Bob:").classes("text-xs text-slate-400 font-semibold")
        lbl_alice_bob_pub = ui.label("...").classes(
            "text-xs font-mono text-slate-600 truncate w-full"
        )

        ui.label("Bản rõ đầu vào (M):").classes(
            "text-xs text-slate-400 font-semibold mt-2"
        )
        txt_plaintext_input = ui.textarea(
            value="Xin chào Cô Hạnh, bọn em là nhóm 7"
        ).classes("w-full text-xs").props("outlined dense rows=2")

        with ui.row().classes("w-full gap-1.5 mt-2"):
            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button("1. Khóa K", on_click=action_generate_session_key).classes(
                    "flex-1 text-xs bg-slate-800 text-white"
                )
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mục 7.3: Sinh Khóa Phiên K (Session Key)",
                        r"""
- **Mục đích mật mã:** Tạo khóa phiên ngắn hạn (ephemeral key) độc lập cho từng phiên giao tiếp, bảo đảm tính chất bí mật chuyển tiếp (PFS - Perfect Forward Secrecy).
- **Thuật toán sinh:** Sử dụng nguồn entropy CSPRNG an toàn từ hệ điều hành (`os.urandom(16)`), tạo chuỗi nhị phân 128-bit:
  $$K \in \{0, 1\}^{128}$$
- **Tính toán:** Khóa $K$ được nạp trực tiếp vào động cơ AES-128 và không lưu trữ trên ổ đĩa cố định của Alice.
                        """,
                    ),
                ).props("flat round dense size=xs").classes(
                    "text-slate-400 hover:text-indigo-600"
                )

            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button("2. AES-GCM", on_click=action_aes_encrypt).classes(
                    "flex-1 text-xs bg-blue-600 text-white"
                )
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mục 7.2: Cơ Sở Toán Học AES-GCM (AEAD)",
                        r"""
AES-GCM kết hợp hai kỹ thuật số học chính xác (Mục 7.2 trong báo cáo):

1. **Mã hóa dòng CTR Mode:** Bản rõ $P_i$ được XOR với dòng khóa giả ngẫu nhiên:
   $$C_i = P_i \oplus \text{AES}_K(\text{CB}_i)$$
   với $\text{CB}_i$ là Counter Block ghép từ Nonce 12 bytes và biến đếm 32-bit tăng dần.
2. **Xác thực toàn vẹn bằng GHASH:** Tính toán hàm băm trên trường hữu hạn Galois $GF(2^{128})$ theo đa thức bất khả quy:
   $$f(x) = x^{128} + x^7 + x^2 + x + 1$$
   Dùng khóa băm $H = \text{AES}_K(0^{128})$ để thực hiện phép nhân Horner liên tiếp:
   $$X_i = (X_{i-1} \oplus C_i) \cdot H$$
   $$\text{Tag} = X_m \oplus \text{AES}_K(\text{CB}_0)$$
Nếu bất kỳ bit nào của $C_i$ bị thay đổi, $X_m$ sẽ biến đổi hoàn toàn và phép xác thực tại Bob sẽ thất bại lập tức.
                        """,
                    ),
                ).props("flat round dense size=xs").classes(
                    "text-slate-400 hover:text-indigo-600"
                )

            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button("3. RSA K", on_click=action_rsa_encrypt_key).classes(
                    "flex-1 text-xs bg-indigo-600 text-white"
                )
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mục 4 & 5: Mã Hóa Khóa Phiên Bằng RSA",
                        r"""
Dựa trên giải thuật RSA tự lập trình trong `algorithms/rsa.py` (Mục 5):

1. **Chuyển đổi dữ liệu:** Chuyển 16 bytes Session Key $K$ thành số nguyên lớn:
   $$m_K = \text{int.from\_bytes}(K, \text{byteorder}='big') < n$$
   (Độ dài modulus $n$ là 256-bit, lớn hơn độ dài 128-bit của $K$, bảo đảm $m_K < n$).
2. **Thuật toán lũy thừa mô-đun:** Sử dụng phương pháp bình phương và nhân liên tiếp (Square-and-Multiply) để tính:
   $$C_{\text{key}} = (m_K)^{e_B} \pmod n$$
   với $e_B = 65537$ là số mũ Fermat $F_4$ tối ưu tốc độ tính toán.
                        """,
                    ),
                ).props("flat round dense size=xs").classes(
                    "text-slate-400 hover:text-indigo-600"
                )

        ui.separator().classes("my-2")
        ui.label("Khóa phiên K:").classes("text-xs text-slate-400 font-semibold")
        lbl_session_key = ui.label("—").classes(
            "text-xs font-mono text-blue-700 truncate w-full"
        )

        ui.label("AES-GCM (IV, C_data, Tag):").classes(
            "text-xs text-slate-400 font-semibold mt-1"
        )
        lbl_aes_cipher = ui.label("—").classes(
            "text-xs font-mono text-slate-700 whitespace-pre-wrap break-all w-full"
        )

        ui.label("C_key (RSA):").classes("text-xs text-slate-400 font-semibold mt-1")
        lbl_rsa_cipher = ui.label("—").classes(
            "text-xs font-mono text-indigo-700 truncate w-full"
        )

    # CỘT 2: KÊNH MẠNG
    with ui.card().classes(
        "w-full p-3 bg-white rounded-lg shadow-xs border border-slate-200"
    ):
        with ui.row().classes(
            "items-center justify-between w-full pb-1 mb-2 border-b border-slate-100"
        ):
            with ui.row().classes("items-center gap-1"):
                ui.label("2. Kênh Mạng (JSON Packet)").classes(
                    "font-bold text-slate-800 text-sm"
                )
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mục 7.1 & 9: Đóng Gói Và Truyền Tin Qua Socket TCP",
                        r"""
Theo kiến trúc giao thức truyền thông trong `PGP_RSA_AES_Socket_3_files` (Mục 9):

- **Framing giao thức:** Sử dụng kỹ thuật Length-Prefixed Framing:
  `[4 Bytes Header độ dài Payload] + [JSON Envelope utf-8]`
  giúp bên nhận Bob giải quyết triệt để bài toán phân mảnh byte stream (TCP Fragmentation).
- **Tính an toàn trên đường truyền:**
  Kẻ tấn công thụ động (Sniffing) chỉ nhìn thấy $C_{\text{key}}$, Nonce, $C_{\text{data}}$ và $\text{Tag}$. Do bài toán RSA phân tích thừa số nguyên tố lớn, không thể suy ra $K$; do bảo mật AES-GCM, không thể suy ra $M$.
                        """,
                    ),
                ).props("flat round dense size=xs").classes(
                    "text-slate-400 hover:text-indigo-600"
                )
            ui.icon("wifi", size="1.1rem", color="purple")

        with ui.row().classes("w-full gap-1.5 mb-2"):
            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button("Gửi Gói Tin", icon="forward", on_click=action_send_packet).classes(
                    "flex-1 text-xs bg-purple-600 text-white"
                )
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mục 7.1 & 9: Gửi Gói Tin Qua Kênh Mạng (JSON Packet)",
                        r"""
Theo kiến trúc giao thức truyền thông tại Mục 7.1 và Mục 9 trong báo cáo:

- **Cơ chế đóng gói:** Gói tin PGP Envelope được cấu trúc thành định dạng JSON chuẩn gồm 4 trường mật mã độc lập:
  $$\text{Payload} = \{C_{\text{key}}, \text{IV}, C_{\text{data}}, \text{Tag}\}$$
- **Đóng khung TCP (Framing):** Dữ liệu được nạp vào kênh Socket TCP dưới dạng chuỗi byte với cơ chế Length-Prefixed:
  $$\text{Frame} = [4 \text{ bytes Header độ dài}] + [\text{JSON Payload (utf-8)}]$$
- **Truyền dẫn:** Gói tin an toàn truyền qua môi trường mạng không tin cậy. Dù đối phương nghe lén (Sniffing), không thể đọc được $K$ hay $M$.
                        """,
                    ),
                ).props("flat round dense size=xs").classes(
                    "text-slate-400 hover:text-indigo-600"
                )

            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button(
                    "Sửa Bit (Tấn Công)", icon="warning", on_click=action_simulate_tamper
                ).classes("flex-1 text-xs bg-rose-600 text-white")
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mục 8 - Test 02: Mô Phỏng Tấn Công Sửa Đổi Dữ Liệu",
                        r"""
Minh họa kịch bản kiểm thử Test Case 02 trong báo cáo (Mục 8):

- **Kịch bản tấn công:** Kẻ tấn công can thiệp vào giữa đường truyền (Man-in-the-Middle) và thực hiện phép đảo bit (Bit-Flipping Attack) trên bản mã:
  $$C'_0 = C_0 \oplus \text{0xFF}$$
- **Nguyên lý phát hiện:** Trong chế độ CTR thuần túy, việc đảo bit chỉ làm sai lệch byte tương ứng của bản rõ. Tuy nhiên, trong **AES-GCM**, sự biến đổi của $C'_0$ khiến phép nhân trên trường Galois:
  $$X'_m \neq X_m$$
  khiến $\text{Tag}' \neq \text{Tag}$. Bộ giải mã của Bob sẽ phát hiện ngay sự sai khác và lập tức ném lỗi ngoại lệ, bảo vệ tuyệt đối tính toàn vẹn.
                        """,
                    ),
                ).props("flat round dense size=xs").classes(
                    "text-slate-400 hover:text-indigo-600"
                )

        ui.label("Dữ liệu truyền trên TCP:").classes(
            "text-xs text-slate-400 font-semibold"
        )
        txt_network_packet = ui.textarea().classes(
            "w-full font-mono text-xs"
        ).props("outlined dense rows=14 readonly")

    # CỘT 3: BOB
    with ui.card().classes(
        "w-full p-3 bg-white rounded-lg shadow-xs border border-slate-200"
    ):
        with ui.row().classes(
            "items-center justify-between w-full pb-1 mb-2 border-b border-slate-100"
        ):
            with ui.row().classes("items-center gap-1"):
                ui.label("3. Phía Bob (Giải Mã)").classes(
                    "font-bold text-slate-800 text-sm"
                )
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mục 3.2 & 7.3: Quy Trình Giải Mã Phía Bob",
                        r"""
Theo thiết kế hàm `bob_decrypt_package` tại Mục 7.3:

1. **Tách gói tin:** Trích xuất 4 trường $\{C_{\text{key}}, \text{IV}, C_{\text{data}}, \text{Tag}\}$.
2. **Khôi phục khóa phiên RSA:**
   $$K_{\text{int}} = (C_{\text{key}})^{d_B} \pmod n$$
   chuyển số nguyên khôi phục về chuỗi 16 bytes khóa $K$.
3. **Đối chiếu Auth Tag GHASH:** Tái tính toán thẻ xác thực trên $C_{\text{data}}$ nhận được và so sánh thời gian thực với $\text{Tag}$ đính kèm.
4. **Giải mã nội dung:** Nếu hợp lệ, đưa vào giải mã Counter Mode để thu lại thông điệp nguyên bản $M' = M$.
                        """,
                    ),
                ).props("flat round dense size=xs").classes(
                    "text-slate-400 hover:text-indigo-600"
                )
            ui.icon("security", size="1.1rem", color="teal")

        with ui.expansion("Khóa RSA Bob", icon="key").classes(
            "w-full text-xs mb-2"
        ):
            ui.label("Public (e, n):").classes("text-xs text-slate-400")
            lbl_bob_pub = ui.label("...").classes(
                "font-mono text-xs text-slate-600 truncate w-full"
            )
            ui.label("Private d:").classes("text-xs text-slate-400 mt-1")
            lbl_bob_priv = ui.label("...").classes(
                "font-mono text-xs text-rose-600 truncate w-full"
            )

        with ui.row().classes("w-full gap-1.5 mb-2"):
            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button("1. Giải RSA K", on_click=action_rsa_decrypt_key).classes(
                    "flex-1 text-xs bg-teal-700 text-white"
                )
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mục 4.2: Cơ Sở Toán Học Giải Mã RSA",
                        r"""
Chứng minh tính đúng đắn dựa trên Định lý Euler (Mục 4.2):

1. Bob sở hữu khóa bí mật $d_B$ thỏa mãn:
   $$e_B \cdot d_B \equiv 1 \pmod{\phi(n)} \implies e_B d_B = 1 + k \phi(n)$$
2. Thực hiện tính lũy thừa mô-đun:
   $$m_K' = (C_{\text{key}})^{d_B} \pmod n = (m_K^{e_B})^{d_B} \pmod n = m_K^{1 + k \phi(n)} \pmod n$$
3. Theo Định lý Euler, $m_K^{\phi(n)} \equiv 1 \pmod n$, do đó:
   $$m_K' \equiv m_K \cdot (1)^k \equiv m_K \pmod n$$
Khóa phiên $K$ được khôi phục chính xác 100%.
                        """,
                    ),
                ).props("flat round dense size=xs").classes(
                    "text-slate-400 hover:text-indigo-600"
                )

            with ui.row().classes("flex-1 items-center gap-0.5"):
                ui.button(
                    "2. GHASH & AES", on_click=action_aes_decrypt_data
                ).classes("flex-1 text-xs bg-emerald-600 text-white")
                ui.button(
                    icon="info",
                    on_click=lambda: show_info(
                        "Mục 7.2: Xác Thực GHASH Và Giải Mã AES",
                        r"""
Cơ chế kiểm soát lỗi nghiêm ngặt:

- Bộ giải mã AES-GCM không tiến hành trả về bản rõ trước khi vượt qua kiểm tra thẻ chứng thực $\text{Tag}$.
- Nếu dữ liệu bị sửa đổi (như trong nút tấn công), hàm giải mã ném ngoại lệ `ValueError: MAC check failed`.
- Nhờ vậy, phía nhận Bob được đảm bảo 2 tầng an ninh:
  1. **Confidentiality (Tính bí mật):** Kẻ nghe trộm không đọc được dữ liệu.
  2. **Integrity (Tính toàn vẹn):** Kẻ can thiệp không thể giả mạo gói tin mà không bị phát hiện.
                        """,
                    ),
                ).props("flat round dense size=xs").classes(
                    "text-slate-400 hover:text-indigo-600"
                )

        ui.label("Khóa K khôi phục:").classes("text-xs text-slate-400 font-semibold")
        lbl_recovered_key = ui.label("—").classes(
            "text-xs font-mono text-teal-800 truncate w-full"
        )

        ui.label("Kiểm thực Auth Tag:").classes(
            "text-xs text-slate-400 font-semibold mt-1"
        )
        lbl_ghash_status = ui.label("Chờ xác thực").classes(
            "text-xs text-slate-400 font-mono"
        )

        ui.label("Bản rõ nhận được (M'):").classes(
            "text-xs text-slate-400 font-semibold mt-2"
        )
        txt_decrypted_output = ui.textarea().classes("w-full text-xs").props(
            "outlined dense rows=2 readonly"
        )


# --- KHU VỰC DƯỚI: SƠ ĐỒ ĐƯỜNG ĐI VÀ BIẾN ĐỔI DỮ LIỆU ĐỘNG (DATAFLOW DIAGRAM) ---
with ui.card().classes(
    "w-full max-w-7xl mx-auto mt-2 mb-6 p-4 bg-white rounded-xl shadow-sm border border-slate-200"
):
    with ui.row().classes(
        "items-center justify-between w-full pb-2 mb-3 border-b border-slate-100"
    ):
        with ui.row().classes("items-center gap-2"):
            ui.icon("schema", size="1.4rem").classes("text-indigo-600")
            ui.label(
                "Sơ đồ tổng quan luồng dữ liệu & trạng thái biến đổi thời gian thực"
            ).classes("text-sm font-bold text-slate-800")
            ui.badge("Tương tác đồng bộ", color="indigo").classes("text-xs")
        ui.label(
            "Quy ước: Viền xanh = Đã hoàn thành | Viền nét đứt = Khóa | Viền đỏ = Lỗi can thiệp"
        ).classes("text-xs text-slate-400")

    # GRID CÁC KHỐI SƠ ĐỒ LUỒNG DỮ LIỆU
    with ui.grid(columns=8).classes("w-full gap-2 items-center"):
        # Khối 1: Bản rõ M
        with ui.column().classes("w-full items-center gap-1"):
            ui.label("1. Dữ liệu gốc").classes("text-[10px] font-bold text-slate-500 uppercase")
            card_node_m = ui.card().classes(
                "w-full p-2.5 rounded-lg border-2 text-center transition-all border-emerald-500 bg-emerald-50 text-emerald-900"
            )
            with card_node_m:
                ui.label("Bản rõ M").classes("text-xs font-bold")
                ui.label("Input rõ").classes("text-[10px] text-slate-500")

        # Khối 2: Khóa phiên K
        with ui.column().classes("w-full items-center gap-1"):
            ui.label("2. Khóa phiên").classes("text-[10px] font-bold text-slate-500 uppercase")
            card_node_k = ui.card().classes(
                "w-full p-2.5 rounded-lg border-2 border-dashed text-center transition-all border-slate-200 bg-slate-50 opacity-60"
            )
            with card_node_k:
                ui.label("Khóa K").classes("text-xs font-bold")
                lbl_flow_k = ui.label("(chưa có)").classes(
                    "text-[10px] font-mono text-blue-700 truncate w-full"
                )

        # Khối 3: Mã hóa AES-GCM
        with ui.column().classes("w-full items-center gap-1"):
            ui.label("3. AES-GCM").classes("text-[10px] font-bold text-slate-500 uppercase")
            card_node_aes_enc = ui.card().classes(
                "w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60"
            )
            with card_node_aes_enc:
                ui.label("Mã hóa AES").classes("text-xs font-bold")
                lbl_flow_cdata = ui.label("(chưa có)").classes(
                    "text-[10px] font-mono text-slate-600 truncate w-full"
                )

        # Khối 4: Mã hóa RSA
        with ui.column().classes("w-full items-center gap-1"):
            ui.label("4. RSA Enc").classes("text-[10px] font-bold text-slate-500 uppercase")
            card_node_rsa_enc = ui.card().classes(
                "w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60"
            )
            with card_node_rsa_enc:
                ui.label("Mã hóa K").classes("text-xs font-bold")
                lbl_flow_ckey = ui.label("(chưa có)").classes(
                    "text-[10px] font-mono text-indigo-700 truncate w-full"
                )

        # Khối 5: Kênh mạng TCP
        with ui.column().classes("w-full items-center gap-1"):
            ui.label("5. Kênh mạng").classes("text-[10px] font-bold text-slate-500 uppercase")
            card_node_net = ui.card().classes(
                "w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60"
            )
            with card_node_net:
                ui.label("Gói TCP").classes("text-xs font-bold")
                lbl_flow_net = ui.label("(chờ gửi)").classes(
                    "text-[10px] text-purple-700 truncate w-full"
                )

        # Khối 6: Giải mã RSA Bob
        with ui.column().classes("w-full items-center gap-1"):
            ui.label("6. RSA Dec").classes("text-[10px] font-bold text-slate-500 uppercase")
            card_node_rsa_dec = ui.card().classes(
                "w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60"
            )
            with card_node_rsa_dec:
                ui.label("Giải mã K").classes("text-xs font-bold")
                lbl_flow_rec_k = ui.label("(chưa có)").classes(
                    "text-[10px] font-mono text-teal-800 truncate w-full"
                )

        # Khối 7: Xác thực GHASH & AES Dec
        with ui.column().classes("w-full items-center gap-1"):
            ui.label("7. GHASH + Dec").classes("text-[10px] font-bold text-slate-500 uppercase")
            card_node_aes_dec = ui.card().classes(
                "w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60"
            )
            with card_node_aes_dec:
                ui.label("Xác thực & Dec").classes("text-xs font-bold")
                ui.label("Kiểm Tag").classes("text-[10px] text-slate-500")

        # Khối 8: Bản rõ khôi phục M'
        with ui.column().classes("w-full items-center gap-1"):
            ui.label("8. Đầu ra").classes("text-[10px] font-bold text-slate-500 uppercase")
            card_node_m_out = ui.card().classes(
                "w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60"
            )
            with card_node_m_out:
                ui.label("Bản rõ M'").classes("text-xs font-bold")
                ui.label("M' = M").classes("text-[10px] text-slate-500")


action_generate_keys()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="PGP Hybrid Simulator", port=8080, reload=False, show=False)
