#!/usr/bin/env python3
"""
Mô phỏng trực quan PGP Hybrid (RSA + AES-GCM) bằng NiceGUI.
- Bố cục:
  1. 3 cột xử lý chính (Alice -> Kênh mạng -> Bob).
  2. Sơ đồ tổng quan luồng dữ liệu 8 khối (đặt bên dưới các card).
  3. Bảng điều khiển tiến trình số học dán chặt đáy màn hình (Fixed Bottom Bar):
     - Có thanh kéo thả (Resize Handle) cho phép kéo thay đổi chiều cao tự do (100px - 600px).
     - Giữ lịch sử 20 dòng gần nhất.
     - Tự động cuộn xuống dòng mới nhất (auto-scroll).
- Mặc định: "Xin chào Cô Hạnh, bọn em là nhóm 7"
"""

import os
import sys
import asyncio
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
    "is_busy": False,
    "log_history": [
        "Hệ thống khởi tạo thành công. Nhấn vào các nút thao tác phía trên để quan sát tiến trình tính toán..."
    ],
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


def log_math(message: str):
    """Ghi thêm thông điệp vào lịch sử tối đa 20 dòng và cuộn xuống đáy."""
    lines = message.strip().split("\n")
    for line in lines:
        if line.strip():
            state["log_history"].append(line)
    # Giữ tối đa 20 dòng
    if len(state["log_history"]) > 20:
        state["log_history"] = state["log_history"][-20:]

    full_log_text = "\n".join(state["log_history"])
    lbl_math_console.set_text(full_log_text)
    # Tự động cuộn xuống đáy container log
    ui.run_javascript(
        "const el = document.getElementById('math-log-scroll'); if (el) { el.scrollTop = el.scrollHeight; }"
    )


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
    st = state["step_status"]

    def style_node(status):
        if status == "success":
            return "border-emerald-500 bg-emerald-50 text-emerald-900 shadow-sm"
        elif status == "active":
            return "border-amber-500 bg-amber-50 text-amber-900 shadow-md ring-2 ring-amber-300"
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


def set_busy(busy: bool, action_name=""):
    state["is_busy"] = busy
    if busy:
        progress_bar.set_visibility(True)
        lbl_exec_status.set_text(f"Đang xử lý: {action_name}...")
    else:
        progress_bar.set_visibility(False)
        lbl_exec_status.set_text("Hệ thống sẵn sàng cho bước tiếp theo.")


# --- CÁC HÀM XỬ LÝ THEO BƯỚC TOÁN HỌC ---
async def action_generate_keys():
    if state["is_busy"]:
        return
    set_busy(True, "Sinh cặp khóa RSA Bob (Miller-Rabin & Euclid mở rộng)")

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
    update_diagram()

    log_math("[RSA KeyGen] 1. Sinh số nguyên tố lớn p, q (128 bits) qua Miller-Rabin test...")
    await asyncio.sleep(0.3)

    state["bob_pub"], state["bob_priv"] = generate_rsa_keys(bits=256)
    e, n = state["bob_pub"]
    d, _ = state["bob_priv"]

    log_math(f"[RSA KeyGen] 2. Tính modulus n = p * q = {n}")
    log_math(f"[RSA KeyGen] 3. Chọn số mũ Fermat e = {e}")
    log_math(f"[RSA KeyGen] 4. Thuật toán Euclid mở rộng: e * d ≡ 1 mod φ(n) -> d = {d}")
    log_math(f"[Hoàn tất] Public Key Bob: (e={e}, n) | Private Key Bob: d")

    lbl_bob_pub.set_text(f"e={e}, n={n}")
    lbl_bob_priv.set_text(f"d={d}")
    lbl_alice_bob_pub.set_text(f"e={e}, n={n}")

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

    set_busy(False)
    notify("Đã sinh cặp khóa RSA Bob (256-bit)", "teal")


async def action_generate_session_key():
    """Thu thập entropy hệ thống và tạo chuỗi 128-bit khóa K."""
    if state["is_busy"]:
        return
    set_busy(True, "Sinh khóa phiên K qua CSPRNG")

    state["step_status"]["k"] = "active"
    update_diagram()

    log_math("[K-Gen] Thu thập entropy /dev/urandom cho 16 bytes (128 bits)...")
    accumulated = bytearray()
    for b_idx in range(16):
        byte_val = os.urandom(1)
        accumulated.extend(byte_val)
        hex_preview = accumulated.hex() + " _" * (16 - len(accumulated))
        lbl_session_key.set_text(hex_preview)
        if (b_idx + 1) % 4 == 0 or b_idx == 15:
            log_math(f"[K-Gen] Đang nạp block {b_idx+1}/16 bytes: {accumulated.hex()}")
        await asyncio.sleep(0.04)

    state["session_key"] = bytes(accumulated)
    lbl_session_key.set_text(state["session_key"].hex())
    log_math(f"[K-Gen Hoàn tất] Session Key K (128-bit): {state['session_key'].hex()}")
    log_math(f"[K-Gen] Giá trị nguyên m_K = int(K) = {int.from_bytes(state['session_key'], 'big')}")

    state["step_status"]["k"] = "success"
    update_diagram()
    set_busy(False)
    notify("Đã tạo khóa phiên K (128-bit)", "blue")


async def action_aes_encrypt():
    """Mã hóa dòng CTR Mode và tính băm GHASH trên trường Galois GF(2^128)."""
    if state["is_busy"]:
        return
    if not state["session_key"]:
        notify("Vui lòng sinh khóa K trước", "amber")
        return

    pt = txt_plaintext_input.value.strip()
    if not pt:
        notify("Vui lòng nhập bản rõ M", "amber")
        return

    set_busy(True, "Mã hóa AES-GCM (CTR Mode + GHASH)")
    state["step_status"]["aes_enc"] = "active"
    update_diagram()

    pt_bytes = pt.encode("utf-8")
    log_math(f"[AES-GCM] Khởi tạo: Bản rõ |M| = {len(pt_bytes)} bytes. Sinh Nonce 12B...")
    await asyncio.sleep(0.15)

    state["ciphertext"], state["nonce"], state["auth_tag"] = aes_gcm_encrypt(
        state["session_key"], pt_bytes
    )

    log_math(f"[AES-CTR] Ghép Counter Block CB_0 = Nonce(12B) || 00000001(4B)")
    log_math(f"[AES-CTR] Mã hóa dòng: C_i = P_i ⊕ AES_K(CB_i) -> C_data ({len(state['ciphertext'])}B)")
    await asyncio.sleep(0.2)

    log_math(f"[GHASH] Khóa băm xác thực H = AES_K(0^128)")
    log_math(f"[GHASH] Phép nhân Horner trên GF(2^128): f(x) = x^128 + x^7 + x^2 + x + 1")
    log_math(f"[GHASH] Thẻ chứng thực Tag = X_m ⊕ AES_K(CB_0) = {state['auth_tag'].hex()}")
    await asyncio.sleep(0.15)

    lbl_aes_cipher.set_text(
        f"IV  : {state['nonce'].hex()}\n"
        f"Data: {state['ciphertext'].hex()}\n"
        f"Tag : {state['auth_tag'].hex()}"
    )

    state["step_status"]["m"] = "success"
    state["step_status"]["aes_enc"] = "success"
    update_diagram()
    set_busy(False)
    notify("AES-GCM: Mã hóa thành công", "blue")


async def action_rsa_encrypt_key():
    """Thuật toán bình phương và nhân liên tiếp (Square-and-Multiply)."""
    if state["is_busy"]:
        return
    if not state["session_key"]:
        notify("Chưa có khóa phiên K", "amber")
        return
    if not state["bob_pub"]:
        notify("Chưa có Public Key của Bob", "amber")
        return

    set_busy(True, "Mã hóa RSA khóa K (Square-and-Multiply)")
    state["step_status"]["rsa_enc"] = "active"
    update_diagram()

    e, n = state["bob_pub"]
    key_int = int.from_bytes(state["session_key"], byteorder="big")

    log_math(f"[RSA Enc] Chuyển đổi khóa 16B: m_K = {key_int}")
    log_math(f"[RSA Enc] Kiểm tra m_K < n: {key_int < n} (128 bits < 256 bits)")
    await asyncio.sleep(0.2)

    e_bin = bin(e)[2:]
    log_math(f"[Square-and-Multiply] Số mũ Fermat e={e} ({len(e_bin)} bits): {e_bin}")
    await asyncio.sleep(0.2)

    state["enc_session_key"] = rsa_encrypt(state["bob_pub"], key_int)
    lbl_rsa_cipher.set_text(f"0x{state['enc_session_key']:x}")

    log_math(f"[RSA Enc Hoàn tất] C_key = (m_K)^{e} mod n -> 0x{state['enc_session_key']:x}")

    state["step_status"]["rsa_enc"] = "success"
    update_diagram()
    set_busy(False)
    notify("RSA: Đã mã hóa khóa K", "blue")


async def action_send_packet():
    """Đóng khung TCP và truyền dẫn qua mạng."""
    if state["is_busy"]:
        return
    if not state["enc_session_key"] or not state["ciphertext"]:
        notify("Cần hoàn tất mã hóa trước", "amber")
        return

    set_busy(True, "Đóng gói JSON Envelope & nạp vào TCP Socket")
    state["step_status"]["network"] = "active"
    update_diagram()

    packet_str = (
        "{\n"
        f'  "C_key": "0x{state["enc_session_key"]:x}",\n'
        f'  "IV": "{state["nonce"].hex()}",\n'
        f'  "C_data": "{state["ciphertext"].hex()}",\n'
        f'  "Tag": "{state["auth_tag"].hex()}"\n'
        "}"
    )
    payload_len = len(packet_str.encode("utf-8"))

    log_math(f"[TCP Framing] JSON payload: {payload_len} bytes")
    log_math(f"[TCP Framing] Header độ dài: [4B Header: 0x{payload_len:08x}] + [Payload]")
    log_math(f"[Network] Đang truyền qua TCP Socket: Alice:Client -> :5000 -> Bob:Server...")
    await asyncio.sleep(0.3)

    txt_network_packet.set_value(packet_str)
    log_math(f"[Network Hoàn tất] Gói tin đã truyền an toàn trên kênh mạng TCP.")

    state["step_status"]["network"] = "success"
    update_diagram()
    set_busy(False)
    notify("Đã truyền gói tin lên mạng", "purple")


async def action_simulate_tamper():
    if state["is_busy"]:
        return
    if not state["ciphertext"]:
        notify("Chưa có gói tin", "amber")
        return

    tampered = bytearray(state["ciphertext"])
    tampered[0] ^= 0xFF
    state["ciphertext"] = bytes(tampered)

    packet_str = (
        "// [ĐÃ SỬA ĐỔI 1 BYTE TRONG C_DATA: BIT-FLIP ATTACK]\n"
        "{\n"
        f'  "C_key": "0x{state["enc_session_key"]:x}",\n'
        f'  "IV": "{state["nonce"].hex()}",\n'
        f'  "C_data": "{state["ciphertext"].hex()}",\n'
        f'  "Tag": "{state["auth_tag"].hex()}"\n'
        "}"
    )
    txt_network_packet.set_value(packet_str)

    log_math("[Tấn công MITM] Kẻ tấn công can thiệp trên đường truyền!")
    log_math("Thực hiện phép Bit-Flipping: C_data[0] = C_data[0] ⊕ 0xFF")
    log_math("Ciphertext đã bị sửa đổi. Tag GHASH vẫn giữ nguyên.")

    state["step_status"]["network"] = "error"
    update_diagram()
    notify("Đã sửa bit trong C_data", "red")


async def action_rsa_decrypt_key():
    """Giải mã RSA bằng Private Key của Bob theo Định lý Euler."""
    if state["is_busy"]:
        return
    if not state["enc_session_key"]:
        notify("Chưa có gói tin", "amber")
        return

    set_busy(True, "Giải mã RSA Bob: (C_key)^d mod n")
    state["step_status"]["rsa_dec"] = "active"
    update_diagram()

    d, n = state["bob_priv"]
    log_math(f"[RSA Dec] Trích xuất C_key = 0x{state['enc_session_key']:x}")
    log_math(f"[RSA Dec] Khóa bí mật Bob: d = {d}")
    log_math(f"[RSA Dec] Lũy thừa mô-đun: m_K' = (C_key)^d mod n qua Square-and-Multiply...")
    await asyncio.sleep(0.3)

    recovered_int = rsa_decrypt(state["bob_priv"], state["enc_session_key"])
    state["recovered_key"] = (recovered_int & ((1 << 128) - 1)).to_bytes(16, byteorder="big")

    log_math(f"[Định lý Euler] (C_key)^d = m_K^(1 + k*φ(n)) ≡ m_K mod n")
    log_math(f"[RSA Dec] Giá trị số học: {recovered_int}")
    log_math(f"[RSA Dec Hoàn tất] Khôi phục Session Key K: {state['recovered_key'].hex()}")

    lbl_recovered_key.set_text(state["recovered_key"].hex())

    state["step_status"]["rsa_dec"] = "success"
    update_diagram()
    set_busy(False)
    notify("RSA: Đã khôi phục khóa K", "teal")


async def action_aes_decrypt_data():
    """Đối chiếu GHASH Tag trên trường Galois và giải mã bản rõ."""
    if state["is_busy"]:
        return
    if not state["recovered_key"]:
        notify("Chưa khôi phục khóa K", "amber")
        return

    set_busy(True, "Đối chiếu GHASH Tag & Giải mã AES-GCM")
    state["step_status"]["aes_dec"] = "active"
    update_diagram()

    log_math(f"[Xác thực AEAD] Nạp khóa phiên K: {state['recovered_key'].hex()}")
    log_math(f"[Xác thực AEAD] Tính lại mã kiểm tra GHASH_computed trên GF(2^128)...")
    await asyncio.sleep(0.3)

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

        log_math(f"[GHASH Xác thực] GHASH_computed == Tag ({state['auth_tag'].hex()}) -> TRÙNG KHỚP!")
        log_math(f"[AES-CTR Dec] P_i = C_i ⊕ AES_K(CB_i) -> Khôi phục chuỗi byte UTF-8")
        log_math(f"[Kết quả] Bản rõ M' = \"{decrypted_text}\"")

        state["step_status"]["aes_dec"] = "success"
        state["step_status"]["m_out"] = "success"
        update_diagram()
        set_busy(False)
        notify("Xác thực GHASH thành công", "emerald")
    except Exception as e:
        txt_decrypted_output.set_value(f"[LỖI: {e}]")
        lbl_ghash_status.set_text(f"LỖI: {e}")
        lbl_ghash_status.classes(replace="text-xs text-rose-600 font-bold")

        log_math(f"[CẢNH BÁO TOÀN VẸN] GHASH_computed != Tag_received!")
        log_math(f"Ngoại lệ phát hiện: {e} -> Hủy gói tin, không xuất bản rõ.")

        state["step_status"]["aes_dec"] = "error"
        state["step_status"]["m_out"] = "error"
        update_diagram()
        set_busy(False)
        notify("Kiểm tra Tag thất bại", "red")


# --- XÂY DỰNG GIAO DIỆN (UI SETUP) ---
ui.query("body").style("background-color: #f8fafc; padding-bottom: 22rem;")

ui.add_head_html(r"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<style>
/* CSS cho thanh kéo thả resize console ở đáy */
.resize-bar {
    width: 100%;
    height: 8px;
    cursor: ns-resize;
    background: transparent;
    display: flex;
    justify-content: center;
    align-items: center;
    user-select: none;
    touch-action: none;
}
.resize-bar:hover .resize-line {
    background-color: #818cf8;
}
.resize-line {
    width: 48px;
    height: 4px;
    border-radius: 9999px;
    background-color: #64748b;
    transition: background-color 0.2s;
}
</style>
<script>
// Logic JavaScript kéo thả thay đổi chiều cao của Terminal Panel
window.initConsoleResize = function() {
    const handle = document.getElementById('console-resize-handle');
    const panel = document.getElementById('resizable-terminal-panel');
    const scrollContainer = document.getElementById('math-log-scroll');
    if (!handle || !panel || !scrollContainer) return;

    let isResizing = false;
    let startY = 0;
    let startHeight = 0;

    handle.addEventListener('mousedown', function(e) {
        isResizing = true;
        startY = e.clientY;
        startHeight = panel.offsetHeight;
        document.body.style.cursor = 'ns-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;
        const delta = startY - e.clientY; // Kéo lên là tăng chiều cao
        let newHeight = startHeight + delta;
        if (newHeight < 120) newHeight = 120;
        if (newHeight > 650) newHeight = 650;
        panel.style.height = newHeight + 'px';
        scrollContainer.style.height = (newHeight - 75) + 'px';
        document.body.style.paddingBottom = (newHeight + 30) + 'px';
    });

    document.addEventListener('mouseup', function() {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
};
window.addEventListener('DOMContentLoaded', window.initConsoleResize);
setTimeout(window.initConsoleResize, 800);
</script>
""")

with ui.header().classes(
    "bg-slate-900 text-white px-5 py-2.5 flex items-center justify-between shadow-sm sticky top-0 z-40"
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
- **Mã hóa đối xứng (AES-128):** Tốc độ xử lý cao, phù hợp với dữ liệu lớn nhưng yêu cầu chia sẻ trước khóa bí mật $K$ qua kênh an toàn.
- **Mã hóa bất đối xứng (RSA):** Trao đổi dữ liệu an toàn qua kênh công khai bằng cặp khóa $(e, d)$, nhưng phép tính lũy thừa mô-đun trên số nguyên lớn $C = M^e \pmod n$ tiêu tốn tài nguyên, không phù hợp để mã hóa trực tiếp khối dữ liệu dung lượng lớn.
- **Giải pháp Hybrid PGP:** 
  $$\text{PGP Packet} = \{\text{RSA}_{e_B}(K), \quad \text{AES-GCM}_K(M)\}$$
  Alice sinh khóa phiên ngẫu nhiên $K$ 128-bit. AES dùng $K$ mã hóa nội dung $M$, còn RSA phía Bob bảo vệ 16 bytes của $K$.

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
AES-GCM kết hợp hai kỹ thuật số học (Mục 7.2 trong báo cáo):

1. **Mã hóa dòng CTR Mode:** Bản rõ $P_i$ được XOR với dòng khóa giả ngẫu nhiên:
   $$C_i = P_i \oplus \text{AES}_K(\text{CB}_i)$$
   với $\text{CB}_i$ là Counter Block ghép từ Nonce 12 bytes và biến đếm 32-bit tăng dần.
2. **Xác thực toàn vẹn bằng GHASH:** Tính toán hàm băm trên trường hữu hạn Galois $GF(2^{128})$ theo đa thức bất khả quy:
   $$f(x) = x^{128} + x^7 + x^2 + x + 1$$
   Dùng khóa băm $H = \text{AES}_K(0^{128})$ để thực hiện phép nhân Horner liên tiếp:
   $$X_i = (X_{i-1} \oplus C_i) \cdot H$$
   $$\text{Tag} = X_m \oplus \text{AES}_K(\text{CB}_0)$$
Nếu bất kỳ bit nào của $C_i$ bị thay đổi, giá trị $X_m$ sẽ thay đổi và phép kiểm tra Tag tại Bob sẽ thất bại.
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
  giúp bên nhận Bob xử lý hiện tượng phân mảnh byte stream (TCP Fragmentation).
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
- **Truyền dẫn:** Gói tin truyền an toàn qua môi trường mạng không tin cậy. Dù đối phương nghe lén (Sniffing), không thể đọc được $K$ hay $M$.
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
  khiến $\text{Tag}' \neq \text{Tag}$. Bộ giải mã của Bob sẽ phát hiện sự sai khác và ném ngoại lệ, bảo đảm tính toàn vẹn dữ liệu.
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
Khóa phiên $K$ được khôi phục chính xác.
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
Cơ chế kiểm soát lỗi:

- Bộ giải mã AES-GCM chỉ trả về bản rõ khi giá trị $\text{Tag}$ hợp lệ.
- Nếu dữ liệu bị sửa đổi (như trong nút tấn công), hàm giải mã ném ngoại lệ `ValueError: MAC check failed`.
- Nhờ vậy, phía nhận Bob đảm bảo 2 thuộc tính:
  1. **Tính bí mật (Confidentiality):** Kẻ nghe trộm không đọc được dữ liệu.
  2. **Tính toàn vẹn (Integrity):** Phát hiện can thiệp hoặc sửa đổi dữ liệu trên đường truyền.
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


# --- KHU VỰC DƯỚI 1: SƠ ĐỒ ĐƯỜNG ĐI VÀ BIẾN ĐỔI DỮ LIỆU ĐỘNG (DATAFLOW DIAGRAM) ---
with ui.card().classes(
    "w-full max-w-7xl mx-auto mt-2 mb-4 p-4 bg-white rounded-xl shadow-sm border border-slate-200"
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
            "Quy ước: Vàng = Đang xử lý | Xanh lá = Đã hoàn thành | Viền nét đứt = Khóa | Viền đỏ = Lỗi can thiệp"
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


# --- KHU VỰC DƯỚI 2: BẢNG TIẾN TRÌNH TOÁN HỌC CÓ KHẢ NĂNG KÉO THẢ RESIZE (RESIZABLE BOTTOM CONSOLE) ---
with ui.card().classes(
    "fixed bottom-0 left-0 right-0 z-50 w-full max-w-7xl mx-auto px-3 pb-2 pt-1 bg-slate-900 text-white rounded-t-xl shadow-2xl border-t-2 border-indigo-500 transition-none"
).style("height: 220px; min-height: 120px; max-height: 650px;").props("id=resizable-terminal-panel"):

    # Thanh tay cầm (Drag Handle) để rê chuột kéo lên/xuống thay đổi chiều cao
    with ui.element("div").classes("resize-bar").props("id=console-resize-handle title='Kéo lên hoặc xuống để thay đổi kích thước terminal'"):
        ui.element("div").classes("resize-line")

    with ui.row().classes("items-center justify-between w-full pb-1 border-b border-slate-800"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("terminal", size="1.2rem").classes("text-emerald-400")
            ui.label("Nhật ký tiến trình số học thời gian thực (Lịch sử 20 sự kiện gần nhất)").classes(
                "text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider"
            )
        with ui.row().classes("items-center gap-2"):
            ui.icon("unfold_more", size="1rem").classes("text-slate-500")
            lbl_exec_status = ui.label("Hệ thống sẵn sàng cho bước tiếp theo.").classes(
                "text-xs font-mono text-slate-400"
            )

    progress_bar = ui.linear_progress().props("indeterminate").classes("w-full my-1")
    progress_bar.set_visibility(False)

    # Container cuộn co giãn linh hoạt theo chiều cao cha
    with ui.scroll_area().classes("w-full pr-2").style("height: 145px;").props("id=math-log-scroll"):
        lbl_math_console = ui.label("\n".join(state["log_history"])).classes(
            "text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed"
        )


# Chạy hàm khởi tạo cặp khóa ban đầu đồng bộ
state["bob_pub"], state["bob_priv"] = generate_rsa_keys(bits=256)
e, n = state["bob_pub"]
d, _ = state["bob_priv"]
lbl_bob_pub.set_text(f"e={e}, n={n}")
lbl_bob_priv.set_text(f"d={d}")
lbl_alice_bob_pub.set_text(f"e={e}, n={n}")

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="PGP Hybrid Simulator", port=8080, reload=False, show=False)
