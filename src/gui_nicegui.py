#!/usr/bin/env python3
"""
Mô phỏng trực quan PGP Hybrid (RSA + AES-GCM) bằng NiceGUI.
Hỗ trợ 2 trang chính qua thanh điều hướng Header:
  1. Trang 'Mô Phỏng PGP (Tích Hợp)': Luồng truyền thông hoàn chỉnh Alice -> Network -> Bob.
  2. Trang 'Chi Tiết Từng Thuật Toán': Tách biệt độc lập từng thuật toán (RSA KeyGen, AES-GCM, RSA Enc/Dec)
     chỉ tập trung vào Input -> Quá trình xử lý nội bộ (Internal Logic) -> Output.
Mặc định input: "Xin chào Cô Hạnh, bọn em là nhóm 7"
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

# Trạng thái phiên làm việc cho trang tích hợp
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

# --- CÁC HÀM TIỆN ÍCH DÙNG CHUNG ---
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


# --- THIẾT LẬP GIAO DIỆN HEAD & CSS ---
def setup_page_head():
    ui.query("body").style("background-color: #f8fafc;")
    ui.add_head_html(r"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <style>
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
            const delta = startY - e.clientY;
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


def render_header(current_page: str):
    with ui.header().classes(
        "bg-slate-900 text-white px-5 py-2.5 flex items-center justify-between shadow-sm sticky top-0 z-40"
    ):
        with ui.row().classes("items-center gap-3"):
            ui.icon("lock", size="1.5rem").classes("text-indigo-400")
            ui.label("PGP Hybrid Simulator (RSA + AES-GCM)").classes("text-sm font-bold")
            with ui.row().classes("gap-1 ml-4 bg-slate-800 p-1 rounded-lg border border-slate-700"):
                ui.button(
                    "Mô Phỏng PGP (Tích Hợp)",
                    on_click=lambda: ui.navigate.to("/"),
                ).props(f"{'unelevated' if current_page == 'integrated' else 'flat'} dense").classes(
                    f"text-xs px-3 py-1 rounded {'bg-indigo-600 text-white' if current_page == 'integrated' else 'text-slate-300 hover:text-white'}"
                )
                ui.button(
                    "Chi Tiết Từng Thuật Toán (Tách Riêng)",
                    on_click=lambda: ui.navigate.to("/algorithms"),
                ).props(f"{'unelevated' if current_page == 'isolated' else 'flat'} dense").classes(
                    f"text-xs px-3 py-1 rounded {'bg-indigo-600 text-white' if current_page == 'isolated' else 'text-slate-300 hover:text-white'}"
                )


# =========================================================================
# TRANG 1: MÔ PHỎNG PGP TÍCH HỢP (ALICE -> NETWORK -> BOB)
# =========================================================================
@ui.page("/")
def page_integrated():
    setup_page_head()
    ui.query("body").style("padding-bottom: 22rem;")
    render_header("integrated")

    def log_math(message: str):
        lines = message.strip().split("\n")
        for line in lines:
            if line.strip():
                state["log_history"].append(line)
        if len(state["log_history"]) > 20:
            state["log_history"] = state["log_history"][-20:]
        lbl_math_console.set_text("\n".join(state["log_history"]))
        ui.run_javascript(
            "const el = document.getElementById('math-log-scroll'); if (el) { el.scrollTop = el.scrollHeight; }"
        )

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

        card_node_m.classes(replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['m'])}")
        card_node_k.classes(replace=f"p-2.5 rounded-lg border-2 border-dashed text-center transition-all {style_node(st['k'])}")
        card_node_aes_enc.classes(replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['aes_enc'])}")
        card_node_rsa_enc.classes(replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['rsa_enc'])}")
        card_node_net.classes(replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['network'])}")
        card_node_rsa_dec.classes(replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['rsa_dec'])}")
        card_node_aes_dec.classes(replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['aes_dec'])}")
        card_node_m_out.classes(replace=f"p-2.5 rounded-lg border-2 text-center transition-all {style_node(st['m_out'])}")

        lbl_flow_k.set_text(state["session_key"].hex()[:10] + "..." if state["session_key"] else "(chưa có)")
        lbl_flow_cdata.set_text(f"C_data ({len(state['ciphertext'])}B)" if state["ciphertext"] else "(chưa có)")
        lbl_flow_ckey.set_text(f"C_key: 0x{state['enc_session_key']:x}"[:14] + "..." if state["enc_session_key"] else "(chưa có)")
        lbl_flow_net.set_text("Payload 4 trường PGP" if state["step_status"]["network"] != "waiting" else "(chờ gửi)")
        lbl_flow_rec_k.set_text(state["recovered_key"].hex()[:10] + "..." if state["recovered_key"] else "(chưa có)")

    def set_busy(busy: bool, action_name=""):
        state["is_busy"] = busy
        if busy:
            progress_bar.set_visibility(True)
            lbl_exec_status.set_text(f"Đang xử lý: {action_name}...")
        else:
            progress_bar.set_visibility(False)
            lbl_exec_status.set_text("Hệ thống sẵn sàng cho bước tiếp theo.")

    async def action_generate_keys():
        if state["is_busy"]: return
        set_busy(True, "Sinh cặp khóa RSA Bob (Miller-Rabin & Euclid mở rộng)")
        state["step_status"] = {"m": "ready", "k": "waiting", "aes_enc": "waiting", "rsa_enc": "waiting", "network": "waiting", "rsa_dec": "waiting", "ghash": "waiting", "aes_dec": "waiting", "m_out": "waiting"}
        update_diagram()
        log_math("[RSA KeyGen] 1. Sinh số nguyên tố p, q (128 bits) qua Miller-Rabin test...")
        await asyncio.sleep(0.3)
        state["bob_pub"], state["bob_priv"] = generate_rsa_keys(bits=256)
        e, n = state["bob_pub"]
        d, _ = state["bob_priv"]
        log_math(f"[RSA KeyGen] 2. Tính modulus n = p * q = {n}\n[RSA KeyGen] 3. Chọn số mũ Fermat e = {e}\n[RSA KeyGen] 4. Euclid mở rộng -> d = {d}\n[Hoàn tất] Public Key Bob: (e={e}, n) | Private Key Bob: d")
        lbl_bob_pub.set_text(f"e={e}, n={n}")
        lbl_bob_priv.set_text(f"d={d}")
        lbl_alice_bob_pub.set_text(f"e={e}, n={n}")
        state["session_key"], state["nonce"], state["ciphertext"], state["auth_tag"], state["enc_session_key"], state["recovered_key"] = None, None, None, None, None, None
        lbl_session_key.set_text("—"); lbl_aes_cipher.set_text("—"); lbl_rsa_cipher.set_text("—"); txt_network_packet.set_value(""); lbl_recovered_key.set_text("—"); lbl_ghash_status.set_text("Chờ xác thực"); lbl_ghash_status.classes(replace="text-xs text-slate-400 font-mono"); txt_decrypted_output.set_value("")
        set_busy(False); notify("Đã sinh cặp khóa RSA Bob (256-bit)", "teal")

    async def action_generate_session_key():
        if state["is_busy"]: return
        set_busy(True, "Sinh khóa phiên K qua CSPRNG")
        state["step_status"]["k"] = "active"; update_diagram()
        log_math("[K-Gen] Thu thập entropy /dev/urandom cho 16 bytes (128 bits)...")
        accumulated = bytearray()
        for b_idx in range(16):
            byte_val = os.urandom(1)
            accumulated.extend(byte_val)
            lbl_session_key.set_text(accumulated.hex() + " _" * (16 - len(accumulated)))
            if (b_idx + 1) % 4 == 0 or b_idx == 15:
                log_math(f"[K-Gen] Đang nạp block {b_idx+1}/16 bytes: {accumulated.hex()}")
            await asyncio.sleep(0.04)
        state["session_key"] = bytes(accumulated)
        lbl_session_key.set_text(state["session_key"].hex())
        log_math(f"[K-Gen Hoàn tất] Session Key K (128-bit): {state['session_key'].hex()}")
        log_math(f"[K-Gen] Giá trị nguyên m_K = int(K) = {int.from_bytes(state['session_key'], 'big')}")
        state["step_status"]["k"] = "success"; update_diagram(); set_busy(False); notify("Đã tạo khóa phiên K (128-bit)", "blue")

    async def action_aes_encrypt():
        if state["is_busy"]: return
        if not state["session_key"]: notify("Vui lòng sinh khóa K trước", "amber"); return
        pt = txt_plaintext_input.value.strip()
        if not pt: notify("Vui lòng nhập bản rõ M", "amber"); return
        set_busy(True, "Mã hóa AES-GCM (CTR Mode + GHASH)")
        state["step_status"]["aes_enc"] = "active"; update_diagram()
        pt_bytes = pt.encode("utf-8")
        log_math(f"[AES-GCM] Khởi tạo: Bản rõ |M| = {len(pt_bytes)} bytes. Sinh Nonce 12B...")
        await asyncio.sleep(0.15)
        state["ciphertext"], state["nonce"], state["auth_tag"] = aes_gcm_encrypt(state["session_key"], pt_bytes)
        log_math(f"[AES-CTR] Ghép Counter Block CB_0 = Nonce(12B) || 00000001(4B)\n[AES-CTR] Mã hóa dòng: C_i = P_i ⊕ AES_K(CB_i) -> C_data ({len(state['ciphertext'])}B)")
        await asyncio.sleep(0.2)
        log_math(f"[GHASH] Khóa băm xác thực H = AES_K(0^128)\n[GHASH] Phép nhân Horner trên GF(2^128): f(x) = x^128 + x^7 + x^2 + x + 1\n[GHASH] Thẻ chứng thực Tag = X_m ⊕ AES_K(CB_0) = {state['auth_tag'].hex()}")
        await asyncio.sleep(0.15)
        lbl_aes_cipher.set_text(f"IV  : {state['nonce'].hex()}\nData: {state['ciphertext'].hex()}\nTag : {state['auth_tag'].hex()}")
        state["step_status"]["m"] = "success"; state["step_status"]["aes_enc"] = "success"; update_diagram(); set_busy(False); notify("AES-GCM: Mã hóa thành công", "blue")

    async def action_rsa_encrypt_key():
        if state["is_busy"]: return
        if not state["session_key"]: notify("Chưa có khóa phiên K", "amber"); return
        if not state["bob_pub"]: notify("Chưa có Public Key của Bob", "amber"); return
        set_busy(True, "Mã hóa RSA khóa K (Square-and-Multiply)")
        state["step_status"]["rsa_enc"] = "active"; update_diagram()
        e, n = state["bob_pub"]
        key_int = int.from_bytes(state["session_key"], byteorder="big")
        log_math(f"[RSA Enc] Chuyển đổi khóa 16B: m_K = {key_int}\n[RSA Enc] Kiểm tra m_K < n: {key_int < n}")
        await asyncio.sleep(0.2)
        e_bin = bin(e)[2:]
        log_math(f"[Square-and-Multiply] Số mũ Fermat e={e} ({len(e_bin)} bits): {e_bin}")
        await asyncio.sleep(0.2)
        state["enc_session_key"] = rsa_encrypt(state["bob_pub"], key_int)
        lbl_rsa_cipher.set_text(f"0x{state['enc_session_key']:x}")
        log_math(f"[RSA Enc Hoàn tất] C_key = (m_K)^{e} mod n -> 0x{state['enc_session_key']:x}")
        state["step_status"]["rsa_enc"] = "success"; update_diagram(); set_busy(False); notify("RSA: Đã mã hóa khóa K", "blue")

    async def action_send_packet():
        if state["is_busy"]: return
        if not state["enc_session_key"] or not state["ciphertext"]: notify("Cần hoàn tất mã hóa trước", "amber"); return
        set_busy(True, "Đóng gói JSON Envelope & nạp vào TCP Socket")
        state["step_status"]["network"] = "active"; update_diagram()
        packet_str = ("{\n" f'  "C_key": "0x{state["enc_session_key"]:x}",\n' f'  "IV": "{state["nonce"].hex()}",\n' f'  "C_data": "{state["ciphertext"].hex()}",\n' f'  "Tag": "{state["auth_tag"].hex()}"\n' "}")
        payload_len = len(packet_str.encode("utf-8"))
        log_math(f"[TCP Framing] JSON payload: {payload_len} bytes\n[TCP Framing] Header độ dài: [4B Header: 0x{payload_len:08x}] + [Payload]\n[Network] Đang truyền qua TCP Socket: Alice:Client -> :5000 -> Bob:Server...")
        await asyncio.sleep(0.3)
        txt_network_packet.set_value(packet_str)
        log_math(f"[Network Hoàn tất] Gói tin đã truyền an toàn trên kênh mạng TCP.")
        state["step_status"]["network"] = "success"; update_diagram(); set_busy(False); notify("Đã truyền gói tin lên mạng", "purple")

    async def action_simulate_tamper():
        if state["is_busy"]: return
        if not state["ciphertext"]: notify("Chưa có gói tin", "amber"); return
        tampered = bytearray(state["ciphertext"])
        tampered[0] ^= 0xFF
        state["ciphertext"] = bytes(tampered)
        packet_str = ("// [ĐÃ SỬA ĐỔI 1 BYTE TRONG C_DATA: BIT-FLIP ATTACK]\n{\n" f'  "C_key": "0x{state["enc_session_key"]:x}",\n' f'  "IV": "{state["nonce"].hex()}",\n' f'  "C_data": "{state["ciphertext"].hex()}",\n' f'  "Tag": "{state["auth_tag"].hex()}"\n' "}")
        txt_network_packet.set_value(packet_str)
        log_math("[Tấn công MITM] Kẻ tấn công can thiệp trên đường truyền! Bit-Flipping: C_data[0] ⊕ 0xFF -> Ciphertext bị sai lệch.")
        state["step_status"]["network"] = "error"; update_diagram(); notify("Đã sửa bit trong C_data", "red")

    async def action_rsa_decrypt_key():
        if state["is_busy"]: return
        if not state["enc_session_key"]: notify("Chưa có gói tin", "amber"); return
        set_busy(True, "Giải mã RSA Bob: (C_key)^d mod n")
        state["step_status"]["rsa_dec"] = "active"; update_diagram()
        d, n = state["bob_priv"]
        log_math(f"[RSA Dec] Trích xuất C_key = 0x{state['enc_session_key']:x}\n[RSA Dec] Khóa bí mật Bob: d = {d}\n[RSA Dec] Lũy thừa mô-đun: m_K' = (C_key)^d mod n...")
        await asyncio.sleep(0.3)
        recovered_int = rsa_decrypt(state["bob_priv"], state["enc_session_key"])
        state["recovered_key"] = (recovered_int & ((1 << 128) - 1)).to_bytes(16, byteorder="big")
        log_math(f"[Định lý Euler] (C_key)^d = m_K^(1 + k*φ(n)) ≡ m_K mod n\n[RSA Dec Hoàn tất] Khôi phục Session Key K: {state['recovered_key'].hex()}")
        lbl_recovered_key.set_text(state["recovered_key"].hex())
        state["step_status"]["rsa_dec"] = "success"; update_diagram(); set_busy(False); notify("RSA: Đã khôi phục khóa K", "teal")

    async def action_aes_decrypt_data():
        if state["is_busy"]: return
        if not state["recovered_key"]: notify("Chưa khôi phục khóa K", "amber"); return
        set_busy(True, "Đối chiếu GHASH Tag & Giải mã AES-GCM")
        state["step_status"]["aes_dec"] = "active"; update_diagram()
        log_math(f"[Xác thực AEAD] Nạp khóa phiên K: {state['recovered_key'].hex()}\n[Xác thực AEAD] Tính lại mã kiểm tra GHASH_computed trên GF(2^128)...")
        await asyncio.sleep(0.3)
        try:
            pt_bytes = aes_gcm_decrypt(session_key=state["recovered_key"], nonce_bytes=state["nonce"], ciphertext_bytes=state["ciphertext"], auth_tag_bytes=state["auth_tag"])
            decrypted_text = pt_bytes.decode("utf-8")
            txt_decrypted_output.set_value(decrypted_text)
            lbl_ghash_status.set_text("HỢP LỆ (Khớp Auth Tag)")
            lbl_ghash_status.classes(replace="text-xs text-emerald-600 font-bold")
            log_math(f"[GHASH Xác thực] GHASH_computed == Tag ({state['auth_tag'].hex()}) -> TRÙNG KHỚP!\n[AES-CTR Dec] P_i = C_i ⊕ AES_K(CB_i) -> Khôi phục chuỗi byte UTF-8\n[Kết quả] Bản rõ M' = \"{decrypted_text}\"")
            state["step_status"]["aes_dec"] = "success"; state["step_status"]["m_out"] = "success"; update_diagram(); set_busy(False); notify("Xác thực GHASH thành công", "emerald")
        except Exception as e:
            txt_decrypted_output.set_value(f"[LỖI: {e}]")
            lbl_ghash_status.set_text(f"LỖI: {e}")
            lbl_ghash_status.classes(replace="text-xs text-rose-600 font-bold")
            log_math(f"[CẢNH BÁO TOÀN VẸN] GHASH_computed != Tag_received! Lỗi: {e} -> Hủy gói tin.")
            state["step_status"]["aes_dec"] = "error"; state["step_status"]["m_out"] = "error"; update_diagram(); set_busy(False); notify("Kiểm tra Tag thất bại", "red")

    # BỐ CỤC 3 CỘT ĐỀU NHAU (GRID COLUMNS = 3)
    with ui.grid(columns=3).classes("w-full max-w-7xl mx-auto p-3 gap-3 items-start"):
        # CỘT 1: ALICE
        with ui.card().classes("w-full p-3 bg-white rounded-lg shadow-xs border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full pb-1 mb-2 border-b border-slate-100"):
                with ui.row().classes("items-center gap-1"):
                    ui.label("1. Phía Alice (Mã Hóa)").classes("font-bold text-slate-800 text-sm")
                ui.icon("send", size="1.1rem", color="blue")
            ui.label("Public Key Bob:").classes("text-xs text-slate-400 font-semibold")
            lbl_alice_bob_pub = ui.label("...").classes("text-xs font-mono text-slate-600 truncate w-full")
            ui.label("Bản rõ đầu vào (M):").classes("text-xs text-slate-400 font-semibold mt-2")
            txt_plaintext_input = ui.textarea(value="Xin chào Cô Hạnh, bọn em là nhóm 7").classes("w-full text-xs").props("outlined dense rows=2")
            with ui.row().classes("w-full gap-1.5 mt-2"):
                ui.button("1. Khóa K", on_click=action_generate_session_key).classes("flex-1 text-xs bg-slate-800 text-white")
                ui.button("2. AES-GCM", on_click=action_aes_encrypt).classes("flex-1 text-xs bg-blue-600 text-white")
                ui.button("3. RSA K", on_click=action_rsa_encrypt_key).classes("flex-1 text-xs bg-indigo-600 text-white")
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
                ui.icon("wifi", size="1.1rem", color="purple")
            with ui.row().classes("w-full gap-1.5 mb-2"):
                ui.button("Gửi Gói Tin", icon="forward", on_click=action_send_packet).classes("flex-1 text-xs bg-purple-600 text-white")
                ui.button("Sửa Bit (Tấn Công)", icon="warning", on_click=action_simulate_tamper).classes("flex-1 text-xs bg-rose-600 text-white")
            ui.label("Dữ liệu truyền trên TCP:").classes("text-xs text-slate-400 font-semibold")
            txt_network_packet = ui.textarea().classes("w-full font-mono text-xs").props("outlined dense rows=14 readonly")

        # CỘT 3: BOB
        with ui.card().classes("w-full p-3 bg-white rounded-lg shadow-xs border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full pb-1 mb-2 border-b border-slate-100"):
                with ui.row().classes("items-center gap-1"):
                    ui.label("3. Phía Bob (Giải Mã)").classes("font-bold text-slate-800 text-sm")
                ui.icon("security", size="1.1rem", color="teal")
            with ui.expansion("Khóa RSA Bob", icon="key").classes("w-full text-xs mb-2"):
                ui.label("Public (e, n):").classes("text-xs text-slate-400")
                lbl_bob_pub = ui.label("...").classes("font-mono text-xs text-slate-600 truncate w-full")
                ui.label("Private d:").classes("text-xs text-slate-400 mt-1")
                lbl_bob_priv = ui.label("...").classes("font-mono text-xs text-rose-600 truncate w-full")
            with ui.row().classes("w-full gap-1.5 mb-2"):
                ui.button("1. Giải RSA K", on_click=action_rsa_decrypt_key).classes("flex-1 text-xs bg-teal-700 text-white")
                ui.button("2. GHASH & AES", on_click=action_aes_decrypt_data).classes("flex-1 text-xs bg-emerald-600 text-white")
            ui.label("Khóa K khôi phục:").classes("text-xs text-slate-400 font-semibold")
            lbl_recovered_key = ui.label("—").classes("text-xs font-mono text-teal-800 truncate w-full")
            ui.label("Kiểm thực Auth Tag:").classes("text-xs text-slate-400 font-semibold mt-1")
            lbl_ghash_status = ui.label("Chờ xác thực").classes("text-xs text-slate-400 font-mono")
            ui.label("Bản rõ nhận được (M'):").classes("text-xs text-slate-400 font-semibold mt-2")
            txt_decrypted_output = ui.textarea().classes("w-full text-xs").props("outlined dense rows=2 readonly")

    # SƠ ĐỒ ĐƯỜNG ĐI DỮ LIỆU ĐỘNG (DATAFLOW DIAGRAM)
    with ui.card().classes("w-full max-w-7xl mx-auto mt-2 mb-4 p-4 bg-white rounded-xl shadow-sm border border-slate-200"):
        with ui.row().classes("items-center justify-between w-full pb-2 mb-3 border-b border-slate-100"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("schema", size="1.4rem").classes("text-indigo-600")
                ui.label("Sơ đồ tổng quan luồng dữ liệu & trạng thái biến đổi thời gian thực").classes("text-sm font-bold text-slate-800")
                ui.badge("Tương tác đồng bộ", color="indigo").classes("text-xs")
            ui.label("Quy ước: Vàng = Đang xử lý | Xanh lá = Đã hoàn thành | Viền nét đứt = Khóa | Viền đỏ = Lỗi can thiệp").classes("text-xs text-slate-400")

        with ui.grid(columns=8).classes("w-full gap-2 items-center"):
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("1. Dữ liệu gốc").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_m = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-emerald-500 bg-emerald-50 text-emerald-900")
                with card_node_m: ui.label("Bản rõ M").classes("text-xs font-bold"); ui.label("Input rõ").classes("text-[10px] text-slate-500")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("2. Khóa phiên").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_k = ui.card().classes("w-full p-2.5 rounded-lg border-2 border-dashed text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_k: ui.label("Khóa K").classes("text-xs font-bold"); lbl_flow_k = ui.label("(chưa có)").classes("text-[10px] font-mono text-blue-700 truncate w-full")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("3. AES-GCM").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_aes_enc = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_aes_enc: ui.label("Mã hóa AES").classes("text-xs font-bold"); lbl_flow_cdata = ui.label("(chưa có)").classes("text-[10px] font-mono text-slate-600 truncate w-full")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("4. RSA Enc").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_rsa_enc = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_rsa_enc: ui.label("Mã hóa K").classes("text-xs font-bold"); lbl_flow_ckey = ui.label("(chưa có)").classes("text-[10px] font-mono text-indigo-700 truncate w-full")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("5. Kênh mạng").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_net = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_net: ui.label("Gói TCP").classes("text-xs font-bold"); lbl_flow_net = ui.label("(chờ gửi)").classes("text-[10px] text-purple-700 truncate w-full")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("6. RSA Dec").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_rsa_dec = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_rsa_dec: ui.label("Giải mã K").classes("text-xs font-bold"); lbl_flow_rec_k = ui.label("(chưa có)").classes("text-[10px] font-mono text-teal-800 truncate w-full")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("7. GHASH + Dec").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_aes_dec = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_aes_dec: ui.label("Xác thực & Dec").classes("text-xs font-bold"); ui.label("Kiểm Tag").classes("text-[10px] text-slate-500")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("8. Đầu ra").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_m_out = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_m_out: ui.label("Bản rõ M'").classes("text-xs font-bold"); ui.label("M' = M").classes("text-[10px] text-slate-500")

    # BẢNG CONSOLE RESIZABLE ĐÁY
    with ui.card().classes(
        "fixed bottom-0 left-0 right-0 z-50 w-full max-w-7xl mx-auto px-3 pb-2 pt-1 bg-slate-900 text-white rounded-t-xl shadow-2xl border-t-2 border-indigo-500 transition-none"
    ).style("height: 220px; min-height: 120px; max-height: 650px;").props("id=resizable-terminal-panel"):
        with ui.element("div").classes("resize-bar").props("id=console-resize-handle title='Kéo lên hoặc xuống để thay đổi kích thước terminal'"):
            ui.element("div").classes("resize-line")
        with ui.row().classes("items-center justify-between w-full pb-1 border-b border-slate-800"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("terminal", size="1.2rem").classes("text-emerald-400")
                ui.label("Nhật ký tiến trình số học thời gian thực (Lịch sử 20 sự kiện gần nhất)").classes("text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider")
            with ui.row().classes("items-center gap-2"):
                ui.icon("unfold_more", size="1rem").classes("text-slate-500")
                lbl_exec_status = ui.label("Hệ thống sẵn sàng cho bước tiếp theo.").classes("text-xs font-mono text-slate-400")
        progress_bar = ui.linear_progress().props("indeterminate").classes("w-full my-1")
        progress_bar.set_visibility(False)
        with ui.scroll_area().classes("w-full pr-2").style("height: 145px;").props("id=math-log-scroll"):
            lbl_math_console = ui.label("\n".join(state["log_history"])).classes("text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed")

    # Khởi tạo cặp khóa ban đầu
    state["bob_pub"], state["bob_priv"] = generate_rsa_keys(bits=256)
    e, n = state["bob_pub"]; d, _ = state["bob_priv"]
    lbl_bob_pub.set_text(f"e={e}, n={n}"); lbl_bob_priv.set_text(f"d={d}"); lbl_alice_bob_pub.set_text(f"e={e}, n={n}")


# =========================================================================
# TRANG 2: CHI TIẾT TỪNG THUẬT TOÁN ĐỘC LẬP (I/O VÀ QUÁ TRÌNH NỘI BỘ)
# =========================================================================
@ui.page("/algorithms")
def page_algorithms():
    setup_page_head()
    ui.query("body").style("padding-bottom: 5rem;")
    render_header("isolated")

    with ui.column().classes("w-full max-w-7xl mx-auto p-4 gap-6"):
        # Header giới thiệu trang
        with ui.row().classes("items-center justify-between w-full pb-2 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("analytics", size="1.8rem").classes("text-indigo-600")
                with ui.column().classes("gap-0"):
                    ui.label("Mô Phỏng Độc Lập Từng Khối Thuật Toán (Isolated Algorithm Engines)").classes("text-base font-bold text-slate-800")
                    ui.label("Tập trung vào: Input đầu vào -> Quá trình xử lý logic nội bộ -> Output đầu ra của từng thuật toán").classes("text-xs text-slate-500")
            ui.button("Về Trang Mô Phỏng PGP", icon="arrow_back", on_click=lambda: ui.navigate.to("/")).classes("bg-slate-800 text-white text-xs px-3 py-1.5 rounded")

        # -------------------------------------------------------------
        # KHỐI 1: THUẬT TOÁN SINH CẶP KHÓA RSA (RSA KEY GENERATION)
        # -------------------------------------------------------------
        with ui.card().classes("w-full p-4 bg-white rounded-xl shadow-sm border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full pb-2 mb-3 border-b border-slate-100"):
                with ui.row().classes("items-center gap-2"):
                    ui.badge("Thuật toán 1", color="teal").classes("text-xs font-bold")
                    ui.label("RSA Key Generation (Mục 4 trong Báo cáo)").classes("text-sm font-bold text-slate-800")
                ui.button(
                    "Thực Thi Sinh Khóa", icon="play_arrow",
                    on_click=lambda: execute_rsa_keygen()
                ).classes("bg-teal-600 text-white text-xs px-3 py-1.5 rounded")

            with ui.grid(columns=3).classes("w-full gap-3 items-stretch"):
                # Cột Input
                with ui.card().classes("p-3 bg-slate-50 rounded-lg border border-slate-200 flex flex-col justify-between"):
                    ui.label("INPUT (Tham Số Đầu Vào)").classes("text-xs font-bold text-slate-600 uppercase border-b border-slate-200 pb-1")
                    with ui.column().classes("gap-2 my-2 text-xs text-slate-700"):
                        ui.label("• Độ dài Modulus mong muốn: 256 bits")
                        ui.label("• Độ dài số nguyên tố p, q: 128 bits")
                        ui.label("• Số mũ công khai Fermat: e = 65537")
                        ui.label("• Vòng lặp Miller-Rabin: k = 40 vòng")
                    ui.label("Nguồn entropy: os.urandom(16)").classes("text-[11px] text-slate-400 font-mono")

                # Cột Quá Trình Xử Lý Logic (Internal Process)
                with ui.card().classes("p-3 bg-indigo-50/60 rounded-lg border border-indigo-200 flex flex-col justify-between"):
                    ui.label("QUÁ TRÌNH XỬ LÝ (Processing Logic)").classes("text-xs font-bold text-indigo-900 uppercase border-b border-indigo-200 pb-1")
                    txt_rsa_keygen_process = ui.label(
                        "1. Chọn p, q ngẫu nhiên 128-bit qua Miller-Rabin\n"
                        "2. Tính Modulus: n = p * q\n"
                        "3. Tính phi(n) = (p - 1) * (q - 1)\n"
                        "4. Euclid mở rộng tìm d: e * d ≡ 1 mod phi(n)"
                    ).classes("text-xs font-mono text-slate-700 leading-relaxed whitespace-pre-wrap my-2")
                    ui.label("Định lý: Euler phi-function").classes("text-[11px] text-indigo-700 font-semibold")

                # Cột Output
                with ui.card().classes("p-3 bg-emerald-50/60 rounded-lg border border-emerald-200 flex flex-col justify-between"):
                    ui.label("OUTPUT (Cặp Khóa Đầu Ra)").classes("text-xs font-bold text-emerald-900 uppercase border-b border-emerald-200 pb-1")
                    txt_rsa_keygen_output = ui.label("Nhấn 'Thực Thi Sinh Khóa' để tính toán...").classes(
                        "text-xs font-mono text-slate-700 whitespace-pre-wrap break-all leading-relaxed my-2"
                    )
                    ui.label("Cặp: Public (e, n) & Private (d, n)").classes("text-[11px] text-emerald-700 font-semibold")

            def execute_rsa_keygen():
                pub, priv = generate_rsa_keys(bits=256)
                e_val, n_val = pub; d_val, _ = priv
                txt_rsa_keygen_process.set_text(
                    f"✓ Sinh thành công số nguyên tố p, q (128-bit)\n"
                    f"✓ Tính n = p * q (256-bit Modulus)\n"
                    f"✓ Chọn Fermat e = {e_val} (gcd(e, φ(n)) = 1)\n"
                    f"✓ Euclid mở rộng: e*d ≡ 1 mod φ(n)"
                )
                txt_rsa_keygen_output.set_text(
                    f"• Public Key (e, n):\n  e = {e_val}\n  n = {n_val}\n\n"
                    f"• Private Key (d, n):\n  d = {d_val}"
                )
                notify("RSA KeyGen: Đã sinh cặp khóa 256-bit", "teal")

        # -------------------------------------------------------------
        # KHỐI 2: THUẬT TOÁN MÃ HÓA & XÁC THỰC AES-GCM (AEAD)
        # -------------------------------------------------------------
        with ui.card().classes("w-full p-4 bg-white rounded-xl shadow-sm border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full pb-2 mb-3 border-b border-slate-100"):
                with ui.row().classes("items-center gap-2"):
                    ui.badge("Thuật toán 2", color="blue").classes("text-xs font-bold")
                    ui.label("AES-GCM Authenticated Encryption (Mục 7.2 trong Báo cáo)").classes("text-sm font-bold text-slate-800")
                ui.button(
                    "Thực Thi AES-GCM", icon="play_arrow",
                    on_click=lambda: execute_aes_gcm()
                ).classes("bg-blue-600 text-white text-xs px-3 py-1.5 rounded")

            with ui.grid(columns=3).classes("w-full gap-3 items-stretch"):
                # Input
                with ui.card().classes("p-3 bg-slate-50 rounded-lg border border-slate-200 flex flex-col justify-between"):
                    ui.label("INPUT (Dữ Liệu & Khóa)").classes("text-xs font-bold text-slate-600 uppercase border-b border-slate-200 pb-1")
                    with ui.column().classes("gap-1 my-2"):
                        ui.label("Bản rõ đầu vào M:").classes("text-xs text-slate-500 font-semibold")
                        inp_aes_msg = ui.input(value="Xin chào Cô Hạnh, bọn em là nhóm 7").classes("w-full text-xs").props("outlined dense")
                        ui.label("Session Key K (16B hex):").classes("text-xs text-slate-500 font-semibold mt-1")
                        inp_aes_key = ui.input(value=os.urandom(16).hex()).classes("w-full font-mono text-xs").props("outlined dense")
                    ui.button("Sinh Khóa Mới", icon="refresh", on_click=lambda: inp_aes_key.set_value(os.urandom(16).hex())).props("flat dense").classes("text-xs text-blue-600")

                # Quá trình xử lý
                with ui.card().classes("p-3 bg-blue-50/60 rounded-lg border border-blue-200 flex flex-col justify-between"):
                    ui.label("QUÁ TRÌNH XỬ LÝ (Processing Logic)").classes("text-xs font-bold text-blue-900 uppercase border-b border-blue-200 pb-1")
                    txt_aes_process = ui.label(
                        "1. Sinh IV/Nonce ngẫu nhiên 12 bytes (96 bits)\n"
                        "2. CTR Mode: CB_i = IV || Counter(32-bit)\n"
                        "   C_i = P_i ⊕ AES_K(CB_i)\n"
                        "3. GHASH: H = AES_K(0^128)\n"
                        "   Nhân Horner trên trường Galois GF(2^128)\n"
                        "   Tag = X_m ⊕ AES_K(CB_0)"
                    ).classes("text-xs font-mono text-slate-700 leading-relaxed whitespace-pre-wrap my-2")
                    ui.label("Trường hữu hạn: GF(2^128)").classes("text-[11px] text-blue-700 font-semibold")

                # Output
                with ui.card().classes("p-3 bg-emerald-50/60 rounded-lg border border-emerald-200 flex flex-col justify-between"):
                    ui.label("OUTPUT (Bộ Ba Ciphertext, IV, Tag)").classes("text-xs font-bold text-emerald-900 uppercase border-b border-emerald-200 pb-1")
                    txt_aes_output = ui.label("Nhấn 'Thực Thi AES-GCM' để mã hóa...").classes(
                        "text-xs font-mono text-slate-700 whitespace-pre-wrap break-all leading-relaxed my-2"
                    )
                    ui.label("Định dạng: Authenticated Ciphertext").classes("text-[11px] text-emerald-700 font-semibold")

            def execute_aes_gcm():
                try:
                    k_bytes = bytes.fromhex(inp_aes_key.value.strip())
                    if len(k_bytes) != 16:
                        notify("Session Key phải đúng 16 bytes (32 hex characters)", "amber")
                        return
                    m_bytes = inp_aes_msg.value.strip().encode("utf-8")
                    c_data, iv, tag = aes_gcm_encrypt(k_bytes, m_bytes)

                    txt_aes_process.set_text(
                        f"✓ Nạp khóa K 128-bit: {k_bytes.hex()[:8]}...\n"
                        f"✓ Sinh Nonce 12B: {iv.hex()}\n"
                        f"✓ Phép XOR dòng CTR Mode hoàn tất (|M|={len(m_bytes)}B)\n"
                        f"✓ Tính băm GHASH Horner trên GF(2^128)\n"
                        f"✓ Tạo Authentication Tag 16B chống sửa đổi"
                    )
                    txt_aes_output.set_text(
                        f"• Nonce / IV (12B):\n  {iv.hex()}\n\n"
                        f"• Ciphertext ({len(c_data)}B):\n  {c_data.hex()}\n\n"
                        f"• Auth Tag GHASH (16B):\n  {tag.hex()}"
                    )
                    notify("AES-GCM: Đã mã hóa và sinh Tag GHASH", "blue")
                except Exception as e:
                    notify(f"Lỗi: {e}", "red")

        # -------------------------------------------------------------
        # KHỐI 3: THUẬT TOÁN MÃ HÓA & GIẢI MÃ RSA (SQUARE-AND-MULTIPLY & EULER)
        # -------------------------------------------------------------
        with ui.card().classes("w-full p-4 bg-white rounded-xl shadow-sm border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full pb-2 mb-3 border-b border-slate-100"):
                with ui.row().classes("items-center gap-2"):
                    ui.badge("Thuật toán 3", color="indigo").classes("text-xs font-bold")
                    ui.label("RSA Encryption & Decryption (Mục 5 trong Báo cáo)").classes("text-sm font-bold text-slate-800")
                with ui.row().classes("gap-2"):
                    ui.button(
                        "1. Mã Hóa C = M^e mod n", icon="lock",
                        on_click=lambda: execute_rsa_enc()
                    ).classes("bg-indigo-600 text-white text-xs px-3 py-1.5 rounded")
                    ui.button(
                        "2. Giải Mã M' = C^d mod n", icon="lock_open",
                        on_click=lambda: execute_rsa_dec()
                    ).classes("bg-teal-700 text-white text-xs px-3 py-1.5 rounded")

            with ui.grid(columns=3).classes("w-full gap-3 items-stretch"):
                # Input
                with ui.card().classes("p-3 bg-slate-50 rounded-lg border border-slate-200 flex flex-col justify-between"):
                    ui.label("INPUT (Số Nguyên Bản Rõ M & Khóa)").classes("text-xs font-bold text-slate-600 uppercase border-b border-slate-200 pb-1")
                    with ui.column().classes("gap-1 my-2"):
                        ui.label("Số nguyên M (hoặc Session Key nguyên):").classes("text-xs text-slate-500 font-semibold")
                        inp_rsa_m = ui.input(value="125").classes("w-full font-mono text-xs").props("outlined dense")
                        ui.label("Số mũ Fermat e:").classes("text-xs text-slate-500 font-semibold mt-1")
                        inp_rsa_e = ui.input(value="17").classes("w-full font-mono text-xs").props("outlined dense")
                        ui.label("Modulus n:").classes("text-xs text-slate-500 font-semibold mt-1")
                        inp_rsa_n = ui.input(value="3233").classes("w-full font-mono text-xs").props("outlined dense")
                        ui.label("Private Key d:").classes("text-xs text-slate-500 font-semibold mt-1")
                        inp_rsa_d = ui.input(value="2753").classes("w-full font-mono text-xs").props("outlined dense")
                    with ui.row().classes("gap-1"):
                        ui.button("Nạp ví dụ số nhỏ (Hình 3)", on_click=lambda: load_small_example()).props("flat dense").classes("text-xs text-indigo-600")
                        ui.button("Nạp Session Key (256-bit)", on_click=lambda: load_session_example()).props("flat dense").classes("text-xs text-indigo-600")

                # Quá trình xử lý
                with ui.card().classes("p-3 bg-indigo-50/60 rounded-lg border border-indigo-200 flex flex-col justify-between"):
                    ui.label("QUÁ TRÌNH XỬ LÝ (Processing Logic)").classes("text-xs font-bold text-indigo-900 uppercase border-b border-indigo-200 pb-1")
                    txt_rsa_calc_process = ui.label(
                        "• Mã hóa:\n"
                        "  C = M^e mod n qua Square-and-Multiply\n\n"
                        "• Giải mã:\n"
                        "  M' = C^d mod n qua Định lý Euler\n"
                        "  (M^e)^d = M^(1 + k*φ(n)) ≡ M mod n"
                    ).classes("text-xs font-mono text-slate-700 leading-relaxed whitespace-pre-wrap my-2")
                    ui.label("Thuật toán: Square-and-Multiply").classes("text-[11px] text-indigo-700 font-semibold")

                # Output
                with ui.card().classes("p-3 bg-emerald-50/60 rounded-lg border border-emerald-200 flex flex-col justify-between"):
                    ui.label("OUTPUT (Bản Mã C & Bản Rõ M')").classes("text-xs font-bold text-emerald-900 uppercase border-b border-emerald-200 pb-1")
                    txt_rsa_calc_output = ui.label("Nhấn nút Mã hóa hoặc Giải mã để quan sát...").classes(
                        "text-xs font-mono text-slate-700 whitespace-pre-wrap break-all leading-relaxed my-2"
                    )
                    ui.label("Khôi phục: M' ≡ M mod n").classes("text-[11px] text-emerald-700 font-semibold")

            rsa_state = {"last_cipher": None}

            def load_small_example():
                inp_rsa_m.set_value("125")
                inp_rsa_e.set_value("17")
                inp_rsa_n.set_value("3233")
                inp_rsa_d.set_value("2753")
                notify("Đã nạp ví dụ số học mẫu (M=125, p=61, q=53)", "blue")

            def load_session_example():
                sample_k = int.from_bytes(os.urandom(16), "big")
                pub_256, priv_256 = generate_rsa_keys(bits=256)
                inp_rsa_m.set_value(str(sample_k))
                inp_rsa_e.set_value(str(pub_256[0]))
                inp_rsa_n.set_value(str(pub_256[1]))
                inp_rsa_d.set_value(str(priv_256[0]))
                notify("Đã nạp khóa phiên 128-bit và cặp khóa RSA 256-bit", "blue")

            def execute_rsa_enc():
                try:
                    m_val = int(inp_rsa_m.value.strip())
                    e_val = int(inp_rsa_e.value.strip())
                    n_val = int(inp_rsa_n.value.strip())
                    if m_val >= n_val:
                        notify("Lỗi: Giá trị M phải nhỏ hơn Modulus n (M < n)!", "red")
                        return

                    c_val = rsa_encrypt((e_val, n_val), m_val)
                    rsa_state["last_cipher"] = c_val

                    e_bin = bin(e_val)[2:]
                    txt_rsa_calc_process.set_text(
                        f"[MÃ HÓA RSA]\n"
                        f"1. Kiểm tra biên: M < n ({m_val < n_val})\n"
                        f"2. Biểu diễn nhị phân e={e_val}: {e_bin}\n"
                        f"3. Square-and-Multiply tính C = {m_val}^{e_val} mod {n_val}\n"
                        f"-> Bản mã C = {c_val}"
                    )
                    txt_rsa_calc_output.set_text(
                        f"• Bản mã C (hệ thập phân):\n  {c_val}\n\n"
                        f"• Bản mã C (hệ Hex):\n  0x{c_val:x}\n\n"
                        f"(Sẵn sàng bấm '2. Giải Mã M' = C^d mod n')"
                    )
                    notify("RSA Enc: Đã mã hóa bản rõ M thành C", "indigo")
                except Exception as ex:
                    notify(f"Lỗi: {ex}", "red")

            def execute_rsa_dec():
                try:
                    if rsa_state["last_cipher"] is None:
                        notify("Vui lòng thực hiện mã hóa trước!", "amber")
                        return
                    c_val = rsa_state["last_cipher"]
                    d_val = int(inp_rsa_d.value.strip())
                    n_val = int(inp_rsa_n.value.strip())

                    m_recovered = rsa_decrypt((d_val, n_val), c_val)
                    m_original = int(inp_rsa_m.value.strip())

                    txt_rsa_calc_process.set_text(
                        f"[GIẢI MÃ RSA]\n"
                        f"1. Nạp bản mã C = {c_val}\n"
                        f"2. Dùng Private Key d = {d_val}\n"
                        f"3. Lũy thừa mô-đun: M' = {c_val}^{d_val} mod {n_val}\n"
                        f"4. Theo Định lý Euler: M' = {m_recovered}\n"
                        f"-> Kết quả: M' == M ({m_recovered == m_original})"
                    )
                    txt_rsa_calc_output.set_text(
                        f"• Bản mã giải mã C:\n  {c_val}\n\n"
                        f"• Bản rõ khôi phục M':\n  {m_recovered}\n\n"
                        f"• Trạng thái đối chiếu:\n  {'✓ TRÙNG KHỚP 100%' if m_recovered == m_original else '✗ THẤT BẠI'}"
                    )
                    notify("RSA Dec: Đã giải mã thành công", "teal")
                except Exception as ex:
                    notify(f"Lỗi: {ex}", "red")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="PGP Hybrid Simulator & Algorithms", port=8080, reload=False, show=False)
