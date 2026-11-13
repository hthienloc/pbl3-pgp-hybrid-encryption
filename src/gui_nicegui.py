#!/usr/bin/env python3
"""
Mô phỏng trực quan PGP Hybrid (RSA + AES-GCM) bằng NiceGUI.
Hỗ trợ 2 trang chính qua thanh điều hướng Header:
  1. Trang 'Mô Phỏng PGP (Tích Hợp)': Luồng truyền thông hoàn chỉnh Alice -> Network -> Bob
     với 3 cột song song, sơ đồ 8 khối dữ liệu và bảng console dán đáy.
  2. Trang 'Chi Tiết Từng Khối Thuật Toán': Nối liền dữ liệu thật từ trên xuống dưới
     (Khối 1 -> Khối 5), không dùng số nhỏ 125, thống nhất ký hiệu M (thông điệp) & K (khóa phiên),
     và khép kín bằng bước giải mã AES-GCM khôi phục bản rõ thông điệp ban đầu.
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

# -----------------------------------------------------------------------------
# TRẠNG THÁI PHIÊN LÀM VIỆC DÙNG CHUNG
# -----------------------------------------------------------------------------
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
            with ui.column().classes("gap-0"):
                ui.label("PGP Hybrid Simulator (RSA + AES-GCM)").classes("text-sm font-bold leading-tight")
                ui.label("Học phần PBL3: Mạng máy tính • Nhóm 7").classes("text-[11px] text-slate-400")
            with ui.row().classes("gap-1 ml-4 bg-slate-800 p-1 rounded-lg border border-slate-700"):
                ui.button(
                    "Mô Phỏng PGP (Tích Hợp)",
                    on_click=lambda: ui.navigate.to("/"),
                ).props(f"{'unelevated' if current_page == 'integrated' else 'flat'} dense").classes(
                    f"text-xs px-3 py-1 rounded {'bg-indigo-600 text-white font-semibold' if current_page == 'integrated' else 'text-slate-300 hover:text-white'}"
                )
                ui.button(
                    "Chi Tiết Từng Khối Thuật Toán",
                    on_click=lambda: ui.navigate.to("/algorithms"),
                ).props(f"{'unelevated' if current_page == 'algorithms' else 'flat'} dense").classes(
                    f"text-xs px-3 py-1 rounded {'bg-indigo-600 text-white font-semibold' if current_page == 'algorithms' else 'text-slate-300 hover:text-white'}"
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
        log_math("[RSA KeyGen] 1. Sinh số nguyên tố p, q (128 bits) qua Miller-Rabin test...")
        await asyncio.sleep(0.3)
        state["bob_pub"], state["bob_priv"] = generate_rsa_keys(bits=256)
        e, n = state["bob_pub"]
        d, _ = state["bob_priv"]
        log_math(
            f"[RSA KeyGen] 2. Tính modulus n = p * q = {n}\n"
            f"[RSA KeyGen] 3. Chọn số mũ Fermat e = {e}\n"
            f"[RSA KeyGen] 4. Euclid mở rộng -> d = {d}\n"
            f"[Hoàn tất] Public Key Bob: (e={e}, n) | Private Key Bob: d"
        )
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
            lbl_session_key.set_text(accumulated.hex() + " _" * (16 - len(accumulated)))
            if (b_idx + 1) % 4 == 0 or b_idx == 15:
                log_math(f"[K-Gen] Đang nạp block {b_idx+1}/16 bytes: {accumulated.hex()}")
            await asyncio.sleep(0.04)
        state["session_key"] = bytes(accumulated)
        lbl_session_key.set_text(state["session_key"].hex())
        log_math(f"[K-Gen Hoàn tất] Session Key K (128-bit): {state['session_key'].hex()}")
        log_math(f"[K-Gen] Giá trị nguyên K = int(K) = {int.from_bytes(state['session_key'], 'big')}")
        state["step_status"]["k"] = "success"
        update_diagram()
        set_busy(False)
        notify("Đã tạo khóa phiên K (128-bit)", "blue")

    async def action_aes_encrypt():
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
        state["ciphertext"], state["nonce"], state["auth_tag"] = aes_gcm_encrypt(state["session_key"], pt_bytes)
        log_math(
            f"[AES-CTR] Ghép Counter Block CB_0 = Nonce(12B) || 00000001(4B)\n"
            f"[AES-CTR] Mã hóa dòng: C_i = P_i ⊕ AES_K(CB_i) -> C_data ({len(state['ciphertext'])}B)"
        )
        await asyncio.sleep(0.2)
        log_math(
            f"[GHASH] Khóa băm xác thực H = AES_K(0^128)\n"
            f"[GHASH] Phép nhân Horner trên GF(2^128): f(x) = x^128 + x^7 + x^2 + x + 1\n"
            f"[GHASH] Thẻ chứng thực Tag = X_m ⊕ AES_K(CB_0) = {state['auth_tag'].hex()}"
        )
        await asyncio.sleep(0.15)
        lbl_aes_cipher.set_text(
            f"IV  : {state['nonce'].hex()}\nData: {state['ciphertext'].hex()}\nTag : {state['auth_tag'].hex()}"
        )
        state["step_status"]["m"] = "success"
        state["step_status"]["aes_enc"] = "success"
        update_diagram()
        set_busy(False)
        notify("AES-GCM: Mã hóa thành công", "blue")

    async def action_rsa_encrypt_key():
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
        log_math(f"[RSA Enc] Chuyển đổi khóa 16B: K = {key_int}\n[RSA Enc] Kiểm tra K < n: {key_int < n}")
        await asyncio.sleep(0.2)
        e_bin = bin(e)[2:]
        log_math(f"[Square-and-Multiply] Số mũ Fermat e={e} ({len(e_bin)} bits): {e_bin}")
        await asyncio.sleep(0.2)
        state["enc_session_key"] = rsa_encrypt(state["bob_pub"], key_int)
        lbl_rsa_cipher.set_text(f"0x{state['enc_session_key']:x}")
        log_math(f"[RSA Enc Hoàn tất] C_key = K^{e} mod n -> 0x{state['enc_session_key']:x}")
        state["step_status"]["rsa_enc"] = "success"
        update_diagram()
        set_busy(False)
        notify("RSA: Đã mã hóa khóa K", "blue")

    async def action_send_packet():
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
        log_math(
            f"[TCP Framing] JSON payload: {payload_len} bytes\n"
            f"[TCP Framing] Header độ dài: [4B Header: 0x{payload_len:08x}] + [Payload]\n"
            f"[Network] Đang truyền qua TCP Socket: Alice:Client -> :5000 -> Bob:Server..."
        )
        await asyncio.sleep(0.3)
        txt_network_packet.set_value(packet_str)
        log_math("[Network Hoàn tất] Gói tin đã truyền an toàn trên kênh mạng TCP.")
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
        log_math("[Tấn công MITM] Kẻ tấn công can thiệp trên đường truyền! Bit-Flipping: C_data[0] ⊕ 0xFF -> Ciphertext bị sai lệch.")
        state["step_status"]["network"] = "error"
        update_diagram()
        notify("Đã sửa bit trong C_data", "red")

    async def action_rsa_decrypt_key():
        if state["is_busy"]:
            return
        if not state["enc_session_key"]:
            notify("Chưa có gói tin", "amber")
            return
        set_busy(True, "Giải mã RSA Bob: (C_key)^d mod n")
        state["step_status"]["rsa_dec"] = "active"
        update_diagram()
        d, n = state["bob_priv"]
        log_math(
            f"[RSA Dec] Trích xuất C_key = 0x{state['enc_session_key']:x}\n"
            f"[RSA Dec] Khóa bí mật Bob: d = {d}\n"
            f"[RSA Dec] Lũy thừa mô-đun: K' = (C_key)^d mod n..."
        )
        await asyncio.sleep(0.3)
        recovered_int = rsa_decrypt(state["bob_priv"], state["enc_session_key"])
        state["recovered_key"] = (recovered_int & ((1 << 128) - 1)).to_bytes(16, byteorder="big")
        log_math(
            f"[Định lý Euler] (C_key)^d = K^(1 + k*phi(n)) ≡ K mod n\n"
            f"[RSA Dec Hoàn tất] Khôi phục Session Key K': {state['recovered_key'].hex()}"
        )
        lbl_recovered_key.set_text(state["recovered_key"].hex())
        state["step_status"]["rsa_dec"] = "success"
        update_diagram()
        set_busy(False)
        notify("RSA: Đã khôi phục khóa K", "teal")

    async def action_aes_decrypt_data():
        if state["is_busy"]:
            return
        if not state["recovered_key"]:
            notify("Chưa khôi phục khóa K", "amber")
            return
        set_busy(True, "Đối chiếu GHASH Tag & Giải mã AES-GCM")
        state["step_status"]["aes_dec"] = "active"
        update_diagram()
        log_math(
            f"[Xác thực AEAD] Nạp khóa phiên K': {state['recovered_key'].hex()}\n"
            f"[Xác thực AEAD] Tính lại mã kiểm tra GHASH_computed trên GF(2^128)..."
        )
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
            log_math(
                f"[GHASH Xác thực] GHASH_computed == Tag ({state['auth_tag'].hex()}) -> TRÙNG KHỚP!\n"
                f"[AES-CTR Dec] P_i = C_i ⊕ AES_K'(CB_i) -> Khôi phục chuỗi byte UTF-8\n"
                f"[Kết quả] Bản rõ M' = \"{decrypted_text}\""
            )
            state["step_status"]["aes_dec"] = "success"
            state["step_status"]["m_out"] = "success"
            update_diagram()
            set_busy(False)
            notify("Xác thực GHASH thành công", "emerald")
        except Exception as e:
            txt_decrypted_output.set_value(f"[LỖI: {e}]")
            lbl_ghash_status.set_text(f"LỖI: {e}")
            lbl_ghash_status.classes(replace="text-xs text-rose-600 font-bold")
            log_math(f"[CẢNH BÁO TOÀN VẸN] GHASH_computed != Tag_received! Lỗi: {e} -> Hủy gói tin.")
            state["step_status"]["aes_dec"] = "error"
            state["step_status"]["m_out"] = "error"
            update_diagram()
            set_busy(False)
            notify("Kiểm tra Tag thất bại", "red")

    # BỐ CỤC 3 CỘT ĐỀU NHAU (GRID COLUMNS = 3)
    with ui.grid(columns=3).classes("w-full max-w-7xl mx-auto p-3 gap-3 items-start"):
        # CỘT 1: ALICE
        with ui.card().classes("w-full p-3 bg-white rounded-lg shadow-xs border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full pb-1 mb-2 border-b border-slate-100"):
                ui.label("1. Phía Alice (Mã Hóa)").classes("font-bold text-slate-800 text-sm")
                ui.icon("send", size="1.1rem", color="blue")
            ui.label("Public Key Bob:").classes("text-xs text-slate-400 font-semibold")
            lbl_alice_bob_pub = ui.label("...").classes("text-xs font-mono text-slate-600 truncate w-full")
            ui.label("Bản rõ đầu vào (M):").classes("text-xs text-slate-400 font-semibold mt-2")
            txt_plaintext_input = ui.textarea(value="Hello cô Hạnh").classes("w-full text-xs").props("outlined dense rows=2")
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
            txt_decrypted_output = ui.textarea().classes("w-full text-xs font-bold").props("outlined dense rows=2 readonly")

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
                with card_node_m:
                    ui.label("Bản rõ M").classes("text-xs font-bold")
                    ui.label("Input rõ").classes("text-[10px] text-slate-500")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("2. Khóa phiên").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_k = ui.card().classes("w-full p-2.5 rounded-lg border-2 border-dashed text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_k:
                    ui.label("Khóa K").classes("text-xs font-bold")
                    lbl_flow_k = ui.label("(chưa có)").classes("text-[10px] font-mono text-blue-700 truncate w-full")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("3. AES-GCM").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_aes_enc = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_aes_enc:
                    ui.label("Mã hóa AES").classes("text-xs font-bold")
                    lbl_flow_cdata = ui.label("(chưa có)").classes("text-[10px] font-mono text-slate-600 truncate w-full")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("4. RSA Enc").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_rsa_enc = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_rsa_enc:
                    ui.label("Mã hóa K").classes("text-xs font-bold")
                    lbl_flow_ckey = ui.label("(chưa có)").classes("text-[10px] font-mono text-indigo-700 truncate w-full")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("5. Kênh mạng").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_net = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_net:
                    ui.label("Gói TCP").classes("text-xs font-bold")
                    lbl_flow_net = ui.label("(chờ gửi)").classes("text-[10px] text-purple-700 truncate w-full")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("6. RSA Dec").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_rsa_dec = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_rsa_dec:
                    ui.label("Giải mã K").classes("text-xs font-bold")
                    lbl_flow_rec_k = ui.label("(chưa có)").classes("text-[10px] font-mono text-teal-800 truncate w-full")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("7. GHASH + Dec").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_aes_dec = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_aes_dec:
                    ui.label("Xác thực & Dec").classes("text-xs font-bold")
                    ui.label("Kiểm Tag").classes("text-[10px] text-slate-500")
            with ui.column().classes("w-full items-center gap-1"):
                ui.label("8. Đầu ra").classes("text-[10px] font-bold text-slate-500 uppercase")
                card_node_m_out = ui.card().classes("w-full p-2.5 rounded-lg border-2 text-center transition-all border-slate-200 bg-slate-50 opacity-60")
                with card_node_m_out:
                    ui.label("Bản rõ M'").classes("text-xs font-bold")
                    ui.label("M' = M").classes("text-[10px] text-slate-500")

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
    e, n = state["bob_pub"]
    d, _ = state["bob_priv"]
    lbl_bob_pub.set_text(f"e={e}, n={n}")
    lbl_bob_priv.set_text(f"d={d}")
    lbl_alice_bob_pub.set_text(f"e={e}, n={n}")


# =========================================================================
# TRANG 2: CHI TIẾT TỪNG KHỐI THUẬT TOÁN (NỐI LIỀN DỮ LIỆU THẬT & KHÉP KÍN LUỒNG)
# =========================================================================
@ui.page("/algorithms")
def page_algorithms():
    setup_page_head()
    ui.query("body").style("padding-bottom: 5rem;")
    render_header("algorithms")

    # Bộ trạng thái cục bộ cho luồng dữ liệu thật của trang Chi tiết
    alg_data = {
        "pub": None,
        "priv": None,
        "k_bytes": None,
        "iv": None,
        "c_data": None,
        "tag": None,
        "c_key": None,
        "recovered_k": None,
        "recovered_m": None,
    }

    # -------------------------------------------------------------------------
    # CÁC HÀM THỰC THI NỐI LIỀN DỮ LIỆU
    # -------------------------------------------------------------------------
    def execute_rsa_keygen(silent=False):
        pub, priv = generate_rsa_keys(bits=256)
        alg_data["pub"] = pub
        alg_data["priv"] = priv
        e_val, n_val = pub
        d_val, _ = priv

        txt_rsa_keygen_process.set_text(
            f"1. Sinh p, q (128-bit) qua kiểm tra nguyên tố xác suất Miller-Rabin\n"
            f"2. Tính Modulus: n = p * q (256-bit)\n"
            f"3. Hàm Euler: phi(n) = (p - 1)(q - 1)\n"
            f"4. Chọn Fermat e = {e_val} (gcd(e, phi(n)) = 1)\n"
            f"5. Euclid mở rộng tìm khóa bí mật d: e*d ≡ 1 mod phi(n)"
        )
        txt_rsa_keygen_output.set_text(
            f"• Public Key (e, n):\n  e = {e_val}\n  n = {n_val}\n\n"
            f"• Private Key (d, n):\n  d = {d_val}\n\n"
            f"-> Đã chuyển Public Key xuống Khối 3 và Private Key xuống Khối 4."
        )

        # Nối liền dữ liệu: chuyển thẳng (e, n) xuống Khối 3 và (d, n) xuống Khối 4
        lbl_k3_pub.set_text(f"e={e_val}, n={n_val}")
        lbl_k4_priv.set_text(f"d={d_val}, n={n_val}")

        if not silent:
            notify("Tạo khóa RSA: Đã sinh cặp khóa 256-bit", "teal")

    def execute_aes_gcm(silent=False):
        msg = inp_aes_msg.value.strip()
        if not msg:
            notify("Vui lòng nhập thông điệp M", "amber")
            return False

        # Tự động sinh khóa phiên K 128-bit ngẫu nhiên từ CSPRNG
        k_bytes = os.urandom(16)
        alg_data["k_bytes"] = k_bytes
        m_bytes = msg.encode("utf-8")

        c_data, iv, tag = aes_gcm_encrypt(k_bytes, m_bytes)
        alg_data["c_data"] = c_data
        alg_data["iv"] = iv
        alg_data["tag"] = tag

        lbl_k2_key_hex.set_text(k_bytes.hex())
        txt_aes_process.set_text(
            f"1. Sinh khóa phiên K ngẫu nhiên 128-bit (16B) bằng CSPRNG\n"
            f"2. Sinh vector khởi tạo Nonce / IV 12 bytes (96-bit)\n"
            f"3. Mã hóa dòng Counter Mode: C_i = P_i ⊕ AES_K(CB_i)\n"
            f"4. Nhân đa thức lặp Horner trên GF(2^128) sinh Auth Tag (16B)"
        )
        txt_aes_output.set_text(
            f"• Khóa phiên K (16B Hex):\n  {k_bytes.hex()}\n\n"
            f"• Nonce / IV (12B):\n  {iv.hex()}\n\n"
            f"• Ciphertext C_data ({len(c_data)}B):\n  {c_data.hex()}\n\n"
            f"• Auth Tag GHASH (16B):\n  {tag.hex()}"
        )

        # NỐI LIỀN DỮ LIỆU THẬT: ĐẨY THẲNG KHÓA PHIÊN K (128-bit) XUỐNG KHỐI 3 ĐỂ MÃ HÓA RSA
        # (Không còn dùng số nhỏ 125 nữa!)
        k_int = int.from_bytes(k_bytes, "big")
        lbl_k3_k_hex.set_text(k_bytes.hex())
        lbl_k3_k_int.set_text(str(k_int))

        # Đồng thời chuẩn bị dữ liệu cho Khối 5 giải mã AES
        lbl_k5_data_info.set_text(f"• IV: {iv.hex()[:16]}...\n• C_data: {c_data.hex()[:16]}... ({len(c_data)}B)\n• Tag: {tag.hex()}")

        if not silent:
            notify("Mã hóa AES-GCM: Đã sinh khóa phiên K và mã hóa thông điệp", "blue")
        return True

    def execute_rsa_enc(silent=False):
        if not alg_data["k_bytes"]:
            notify("Vui lòng thực hiện Khối 2 để có khóa phiên K trước", "amber")
            return False
        if not alg_data["pub"]:
            notify("Vui lòng thực hiện Khối 1 để có Public Key Bob trước", "amber")
            return False

        e_val, n_val = alg_data["pub"]
        k_int = int.from_bytes(alg_data["k_bytes"], "big")
        if k_int >= n_val:
            notify("Lỗi: Giá trị khóa phiên K vượt quá Modulus n", "red")
            return False

        c_key = rsa_encrypt(alg_data["pub"], k_int)
        alg_data["c_key"] = c_key

        e_bin = bin(e_val)[2:]
        txt_rsa_enc_process.set_text(
            f"1. Nhận khóa phiên K (128-bit) từ Khối 2, chuyển thành số nguyên: K = {k_int}\n"
            f"2. Kiểm tra biên mật mã: K < n ({k_int < n_val})\n"
            f"3. Biểu diễn nhị phân Fermat e = {e_val}: {e_bin}\n"
            f"4. Thuật toán Square-and-Multiply tính C_key = K^e mod n"
        )
        txt_rsa_enc_output.set_text(
            f"• Bản mã khóa phiên C_key (hệ Hex):\n  0x{c_key:x}\n\n"
            f"• Bản mã khóa phiên C_key (hệ Thập phân):\n  {c_key}\n\n"
            f"-> Đã chuyển C_key xuống Khối 4 để giải mã."
        )

        # NỐI LIỀN DỮ LIỆU: ĐẨY THẲNG C_KEY XUỐNG KHỐI 4
        lbl_k4_ckey.set_text(f"0x{c_key:x}")

        if not silent:
            notify("Mã hóa RSA: Đã mã hóa khóa phiên K thành C_key", "indigo")
        return True

    def execute_rsa_dec(silent=False):
        if not alg_data["c_key"]:
            notify("Vui lòng thực hiện Khối 3 để có C_key trước", "amber")
            return False
        if not alg_data["priv"]:
            notify("Vui lòng thực hiện Khối 1 để có Private Key Bob trước", "amber")
            return False

        d_val, n_val = alg_data["priv"]
        c_key = alg_data["c_key"]

        # Lũy thừa mô-đun: K' = (C_key)^d mod n
        k_rec_int = rsa_decrypt(alg_data["priv"], c_key)
        k_rec_bytes = (k_rec_int & ((1 << 128) - 1)).to_bytes(16, "big")
        alg_data["recovered_k"] = k_rec_bytes

        is_matched = (k_rec_bytes == alg_data["k_bytes"])

        txt_rsa_dec_process.set_text(
            f"1. Nạp bản mã khóa phiên C_key = 0x{c_key:x}\n"
            f"2. Nạp khóa bí mật Bob: d = {d_val}\n"
            f"3. Lũy thừa mô-đun theo Định lý Euler:\n"
            f"   K' = (C_key)^d mod n = K^(e*d) ≡ K mod n\n"
            f"4. Khôi phục số nguyên K' = {k_rec_int}\n"
            f"5. Chuyển đổi về 16 bytes khóa đối xứng AES"
        )
        txt_rsa_dec_output.set_text(
            f"• Khóa phiên khôi phục K' (16B Hex):\n  {k_rec_bytes.hex()}\n\n"
            f"• Khóa phiên K ban đầu (từ Khối 2):\n  {alg_data['k_bytes'].hex()}\n\n"
            f"• Trạng thái đối chiếu K' == K:\n  {'✓ TRÙNG KHỚP 100%' if is_matched else '✗ THẤT BẠI'}\n\n"
            f"-> Đã chuyển khóa K' xuống Khối 5 để giải mã thông điệp gốc."
        )

        # NỐI LIỀN DỮ LIỆU: ĐẨY THẲNG KHÓA K' VỪA GIẢI MÃ XUỐNG KHỐI 5
        lbl_k5_rec_k.set_text(k_rec_bytes.hex())

        if not silent:
            notify("Giải mã RSA: Đã khôi phục khóa phiên K'", "teal")
        return True

    def execute_aes_dec(silent=False):
        """
        KHỐI 5 (TRỌNG TÂM CÔ NHẬN XÉT):
        Dùng chính khóa K' vừa giải mã ở Khối 4 để giải mã AES-GCM,
        khép kín quy trình và khôi phục lại chuỗi thông điệp ban đầu M.
        """
        if not alg_data["recovered_k"]:
            notify("Vui lòng thực hiện Khối 4 để giải mã lấy khóa K' trước", "amber")
            return False
        if not alg_data["c_data"] or not alg_data["iv"] or not alg_data["tag"]:
            notify("Thiếu dữ liệu mã hóa từ Khối 2", "amber")
            return False

        try:
            pt_bytes = aes_gcm_decrypt(
                session_key=alg_data["recovered_k"],
                nonce_bytes=alg_data["iv"],
                ciphertext_bytes=alg_data["c_data"],
                auth_tag_bytes=alg_data["tag"],
            )
            msg_recovered = pt_bytes.decode("utf-8")
            alg_data["recovered_m"] = msg_recovered

            txt_aes_dec_process.set_text(
                f"1. Nạp khóa phiên K' (128-bit) vừa khôi phục ở Khối 4\n"
                f"2. Nạp IV (12B), C_data ({len(alg_data['c_data'])}B) và Tag (16B) từ Khối 2\n"
                f"3. XÁC THỰC GHASH TRÊN GF(2^128):\n"
                f"   Tag_computed == Tag_received -> TRÙNG KHỚP!\n"
                f"4. GIẢI MÃ CTR MODE:\n"
                f"   P_i = C_i ⊕ AES_K'(CB_i)\n"
                f"5. Chuyển đổi byte UTF-8 ra lại chuỗi thông điệp ban đầu"
            )
            txt_aes_dec_output.set_text(
                f"• Bản rõ thông điệp khôi phục M':\n"
                f"  \"{msg_recovered}\"\n\n"
                f"• Thông điệp gốc ban đầu M:\n"
                f"  \"{inp_aes_msg.value.strip()}\"\n\n"
                f"• Kết quả khép kín luồng:\n"
                f"  ✓ KHÔI PHỤC HOÀN TOÀN CHÍNH XÁC (M' == M)"
            )
            card_k5.classes(replace="w-full p-4 bg-emerald-50/70 rounded-xl shadow-md border-2 border-emerald-600 transition-all")
            badge_k5.set_text("ĐÃ KHÔI PHỤC BẢN RÕ")
            badge_k5.props("color=emerald")

            if not silent:
                notify("Giải mã AES-GCM: Đã khôi phục trọn vẹn thông điệp gốc!", "emerald")
            return True

        except Exception as e:
            txt_aes_dec_process.set_text(f"Lỗi xác thực hoặc giải mã: {e}")
            txt_aes_dec_output.set_text(f"✗ Thất bại: {e}")
            card_k5.classes(replace="w-full p-4 bg-rose-50/70 rounded-xl shadow-md border-2 border-rose-600 transition-all")
            badge_k5.set_text("LỖI TOÀN VẸN")
            badge_k5.props("color=rose")
            if not silent:
                notify(f"Lỗi: {e}", "red")
            return False

    async def run_all_blocks():
        btn_run_all.props("loading")
        execute_rsa_keygen(silent=True)
        await asyncio.sleep(0.2)
        if not execute_aes_gcm(silent=True):
            btn_run_all.props(remove="loading")
            return
        await asyncio.sleep(0.2)
        if not execute_rsa_enc(silent=True):
            btn_run_all.props(remove="loading")
            return
        await asyncio.sleep(0.2)
        if not execute_rsa_dec(silent=True):
            btn_run_all.props(remove="loading")
            return
        await asyncio.sleep(0.2)
        execute_aes_dec(silent=True)
        btn_run_all.props(remove="loading")
        notify("Đã hoàn tất tuần tự toàn bộ 5 khối thuật toán!", "emerald")

    def reset_blocks():
        execute_rsa_keygen(silent=True)
        lbl_k2_key_hex.set_text("—")
        txt_aes_process.set_text("Nhấn 'Mã Hóa AES-GCM' để bắt đầu...")
        txt_aes_output.set_text("Nhấn 'Mã Hóa AES-GCM' để tính toán...")

        lbl_k3_k_hex.set_text("(chưa có)")
        lbl_k3_k_int.set_text("(chưa có)")
        txt_rsa_enc_process.set_text("Chờ nhận khóa phiên K từ Khối 2...")
        txt_rsa_enc_output.set_text("Chưa có kết quả...")

        lbl_k4_ckey.set_text("(chưa có)")
        txt_rsa_dec_process.set_text("Chờ nhận C_key từ Khối 3...")
        txt_rsa_dec_output.set_text("Chưa có kết quả...")

        lbl_k5_rec_k.set_text("(chưa có)")
        lbl_k5_data_info.set_text("• IV, C_data, Tag sẽ lấy từ Khối 2")
        txt_aes_dec_process.set_text("Chờ nhận khóa K' từ Khối 4...")
        txt_aes_dec_output.set_text("Chờ thực thi để khôi phục bản rõ...")
        card_k5.classes(replace="w-full p-4 bg-white rounded-xl shadow-sm border border-slate-200 transition-all")
        badge_k5.set_text("CHỜ KHÓA K'")
        badge_k5.props("color=slate")

        notify("Đã làm mới dữ liệu các khối", "blue")

    # -------------------------------------------------------------------------
    # GIAO DIỆN BỐ CỤC CHÍNH CỦA TRANG CHI TIẾT
    # -------------------------------------------------------------------------
    with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-4"):
        # BANNER TIÊU ĐỀ & ĐIỀU KHIỂN (GỌN GÀNG, KHÔNG CÓ TỪ NGỮ ĐỀ MỤC BÁO CÁO)
        with ui.card().classes("w-full p-4 bg-white rounded-xl shadow-sm border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full flex-wrap gap-2 pb-2 border-b border-slate-100"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("tune", size="1.6rem").classes("text-indigo-600")
                    with ui.column().classes("gap-0"):
                        ui.label("Chi Tiết Từng Khối Thuật Toán (Nối Liền Dữ Liệu Thật)").classes("text-base font-bold text-slate-800")
                        ui.label("Dữ liệu đầu ra của khối trên tự động chuyển xuống khối dưới • M là Thông điệp gốc • K là Khóa phiên").classes("text-xs text-slate-500")
                with ui.row().classes("items-center gap-2"):
                    btn_run_all = ui.button("▶ Chạy Tuần Tự Tất Cả Khối", on_click=run_all_blocks).classes("bg-indigo-600 text-white text-xs font-semibold px-3 py-1.5 rounded-lg shadow-sm")
                    ui.button("↺ Làm Mới", on_click=reset_blocks).classes("bg-slate-700 text-white text-xs px-3 py-1.5 rounded-lg")
                    ui.button("Về Trang Tích Hợp", icon="arrow_back", on_click=lambda: ui.navigate.to("/")).classes("bg-slate-800 text-white text-xs px-3 py-1.5 rounded-lg")

            with ui.row().classes("w-full items-center gap-2 pt-2 flex-wrap"):
                ui.label("Thông điệp gốc M:").classes("text-xs font-semibold text-slate-600")
                inp_aes_msg = ui.input(value="Hello cô Hạnh").classes("flex-1 min-w-[260px] text-xs font-medium").props("outlined dense")
                with ui.row().classes("gap-1"):
                    ui.button("Mẫu: Hello cô Hạnh", on_click=lambda: inp_aes_msg.set_value("Hello cô Hạnh")).props("flat dense").classes("text-xs text-indigo-600")
                    ui.button("Mẫu: Nhóm 7", on_click=lambda: inp_aes_msg.set_value("Xin chào Cô Hạnh, bọn em là nhóm 7")).props("flat dense").classes("text-xs text-indigo-600")

        # ---------------------------------------------------------------------
        # KHỐI 1: TẠO KHÓA RSA (BOB)
        # ---------------------------------------------------------------------
        with ui.card().classes("w-full p-4 bg-white rounded-xl shadow-sm border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full pb-2 mb-2 border-b border-slate-100"):
                with ui.row().classes("items-center gap-2"):
                    ui.label("1").classes("w-6 h-6 rounded-full bg-teal-600 text-white flex items-center justify-center text-xs font-bold")
                    ui.label("Tạo Khóa RSA (Phía Bob)").classes("text-sm font-bold text-slate-800")
                    ui.badge("RSA-256", color="teal").classes("text-[10px]")
                ui.button("Tạo Cặp Khóa", icon="refresh", on_click=lambda: execute_rsa_keygen()).classes("bg-teal-600 text-white text-xs px-3 py-1 rounded")

            with ui.grid(columns=3).classes("w-full gap-3 items-stretch"):
                with ui.card().classes("p-3 bg-slate-50 rounded-lg border border-slate-200"):
                    ui.label("INPUT (THAM SỐ)").classes("text-[11px] font-bold text-slate-600 uppercase border-b pb-1")
                    ui.label("• Modulus n: 256 bits\n• Số nguyên tố p, q: 128 bits\n• Fermat: e = 65537\n• Miller-Rabin: k = 40 vòng").classes("text-xs font-mono text-slate-700 whitespace-pre-wrap leading-relaxed mt-2")
                with ui.card().classes("p-3 bg-teal-50/50 rounded-lg border border-teal-200"):
                    ui.label("QUÁ TRÌNH XỬ LÝ SỐ HỌC").classes("text-[11px] font-bold text-teal-800 uppercase border-b border-teal-200 pb-1")
                    txt_rsa_keygen_process = ui.label("Nhấn 'Tạo Cặp Khóa' để tính toán...").classes("text-xs font-mono text-slate-700 whitespace-pre-wrap leading-relaxed mt-2")
                with ui.card().classes("p-3 bg-emerald-50/50 rounded-lg border border-emerald-200"):
                    ui.label("OUTPUT (CẶP KHÓA XUẤT RA)").classes("text-[11px] font-bold text-emerald-800 uppercase border-b border-emerald-200 pb-1")
                    txt_rsa_keygen_output = ui.label("Chưa có khóa...").classes("text-xs font-mono text-slate-700 whitespace-pre-wrap break-all leading-relaxed mt-2")

        # Mũi tên dòng chảy
        with ui.row().classes("w-full justify-center -my-2"):
            with ui.row().classes("items-center gap-1 bg-teal-50 px-3 py-0.5 rounded-full border border-teal-200"):
                ui.icon("arrow_downward", size="1rem").classes("text-teal-600")
                ui.label("Public Key (e, n) chuyển xuống Khối 3 • Private Key (d, n) chuyển xuống Khối 4").classes("text-[10px] font-semibold text-teal-700")

        # ---------------------------------------------------------------------
        # KHỐI 2: MÃ HÓA AES-GCM (ALICE)
        # ---------------------------------------------------------------------
        with ui.card().classes("w-full p-4 bg-white rounded-xl shadow-sm border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full pb-2 mb-2 border-b border-slate-100"):
                with ui.row().classes("items-center gap-2"):
                    ui.label("2").classes("w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold")
                    ui.label("Mã Hóa AES-GCM (Phía Alice)").classes("text-sm font-bold text-slate-800")
                    ui.badge("AES-128-GCM", color="blue").classes("text-[10px]")
                ui.button("Mã Hóa AES-GCM", icon="lock", on_click=lambda: execute_aes_gcm()).classes("bg-blue-600 text-white text-xs px-3 py-1 rounded")

            with ui.grid(columns=3).classes("w-full gap-3 items-stretch"):
                with ui.card().classes("p-3 bg-slate-50 rounded-lg border border-slate-200"):
                    ui.label("INPUT (DỮ LIỆU & KHÓA)").classes("text-[11px] font-bold text-slate-600 uppercase border-b pb-1")
                    ui.label("Thông điệp gốc M:").classes("text-xs text-slate-500 font-semibold mt-1")
                    ui.label("Lấy từ ô nhập trên cùng").classes("text-xs font-mono text-slate-700")
                    ui.label("Khóa phiên K (128-bit):").classes("text-xs text-slate-500 font-semibold mt-2")
                    lbl_k2_key_hex = ui.label("—").classes("text-xs font-mono text-blue-700 break-all")
                    ui.label("(Tự động sinh ngẫu nhiên dùng một lần)").classes("text-[10px] text-slate-400 italic")
                with ui.card().classes("p-3 bg-blue-50/50 rounded-lg border border-blue-200"):
                    ui.label("QUÁ TRÌNH XỬ LÝ (CTR MODE & GHASH)").classes("text-[11px] font-bold text-blue-800 uppercase border-b border-blue-200 pb-1")
                    txt_aes_process = ui.label("Nhấn 'Mã Hóa AES-GCM' để bắt đầu...").classes("text-xs font-mono text-slate-700 whitespace-pre-wrap leading-relaxed mt-2")
                with ui.card().classes("p-3 bg-emerald-50/50 rounded-lg border border-emerald-200"):
                    ui.label("OUTPUT (BỘ DỮ LIỆU MÃ HÓA)").classes("text-[11px] font-bold text-emerald-800 uppercase border-b border-emerald-200 pb-1")
                    txt_aes_output = ui.label("Nhấn 'Mã Hóa AES-GCM' để tính toán...").classes("text-xs font-mono text-slate-700 whitespace-pre-wrap break-all leading-relaxed mt-2")

        # Mũi tên dòng chảy (Nhấn mạnh việc nối liền khóa K thật)
        with ui.row().classes("w-full justify-center -my-2"):
            with ui.row().classes("items-center gap-1 bg-indigo-50 px-3 py-0.5 rounded-full border border-indigo-200 shadow-xs"):
                ui.icon("arrow_downward", size="1rem").classes("text-indigo-600")
                ui.label("Đẩy trực tiếp Khóa phiên K (128-bit thật) từ Khối 2 xuống Khối 3 để mã hóa RSA").classes("text-[10px] font-bold text-indigo-700")

        # ---------------------------------------------------------------------
        # KHỐI 3: MÃ HÓA RSA KHÓA PHIÊN K (ALICE)
        # (Không còn dùng số 125, nối liền Khóa phiên K thật)
        # ---------------------------------------------------------------------
        with ui.card().classes("w-full p-4 bg-white rounded-xl shadow-sm border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full pb-2 mb-2 border-b border-slate-100"):
                with ui.row().classes("items-center gap-2"):
                    ui.label("3").classes("w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold")
                    ui.label("Mã Hóa Khóa Phiên K Bằng RSA (Phía Alice)").classes("text-sm font-bold text-slate-800")
                    ui.badge("C_key = K^e mod n", color="indigo").classes("text-[10px]")
                ui.button("Mã Hóa RSA Khóa K", icon="vpn_key", on_click=lambda: execute_rsa_enc()).classes("bg-indigo-600 text-white text-xs px-3 py-1 rounded")

            with ui.grid(columns=3).classes("w-full gap-3 items-stretch"):
                with ui.card().classes("p-3 bg-slate-50 rounded-lg border border-slate-200"):
                    ui.label("INPUT (NHẬN TRỰC TIẾP TỪ KHỐI 2)").classes("text-[11px] font-bold text-slate-600 uppercase border-b pb-1")
                    ui.label("Khóa phiên K (16B Hex từ Khối 2):").classes("text-xs text-slate-500 font-semibold mt-1")
                    lbl_k3_k_hex = ui.label("(chưa có)").classes("text-xs font-mono text-blue-700 break-all")
                    ui.label("Khóa K (Dạng số nguyên 128-bit):").classes("text-xs text-slate-500 font-semibold mt-1")
                    lbl_k3_k_int = ui.label("(chưa có)").classes("text-xs font-mono text-slate-700 truncate w-full")
                    ui.label("Public Key Bob (e, n từ Khối 1):").classes("text-xs text-slate-500 font-semibold mt-1")
                    lbl_k3_pub = ui.label("...").classes("text-xs font-mono text-teal-700 truncate w-full")
                with ui.card().classes("p-3 bg-indigo-50/50 rounded-lg border border-indigo-200"):
                    ui.label("QUÁ TRÌNH XỬ LÝ SỐ HỌC").classes("text-[11px] font-bold text-indigo-800 uppercase border-b border-indigo-200 pb-1")
                    txt_rsa_enc_process = ui.label("Chờ nhận khóa phiên K từ Khối 2...").classes("text-xs font-mono text-slate-700 whitespace-pre-wrap leading-relaxed mt-2")
                with ui.card().classes("p-3 bg-emerald-50/50 rounded-lg border border-emerald-200"):
                    ui.label("OUTPUT (BẢN MÃ KHÓA C_key)").classes("text-[11px] font-bold text-emerald-800 uppercase border-b border-emerald-200 pb-1")
                    txt_rsa_enc_output = ui.label("Chưa có kết quả...").classes("text-xs font-mono text-slate-700 whitespace-pre-wrap break-all leading-relaxed mt-2")

        # Mũi tên dòng chảy
        with ui.row().classes("w-full justify-center -my-2"):
            with ui.row().classes("items-center gap-1 bg-purple-50 px-3 py-0.5 rounded-full border border-purple-200"):
                ui.icon("arrow_downward", size="1rem").classes("text-purple-600")
                ui.label("Chuyển Bản mã khóa phiên C_key xuống Khối 4 để Bob giải mã").classes("text-[10px] font-semibold text-purple-700")

        # ---------------------------------------------------------------------
        # KHỐI 4: GIẢI MÃ RSA KHÔI PHỤC KHÓA PHIÊN K (BOB)
        # ---------------------------------------------------------------------
        with ui.card().classes("w-full p-4 bg-white rounded-xl shadow-sm border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full pb-2 mb-2 border-b border-slate-100"):
                with ui.row().classes("items-center gap-2"):
                    ui.label("4").classes("w-6 h-6 rounded-full bg-teal-700 text-white flex items-center justify-center text-xs font-bold")
                    ui.label("Giải Mã RSA Khôi Phục Khóa Phiên K (Phía Bob)").classes("text-sm font-bold text-slate-800")
                    ui.badge("K' = (C_key)^d mod n", color="teal").classes("text-[10px]")
                ui.button("Giải Mã RSA Khóa K", icon="lock_open", on_click=lambda: execute_rsa_dec()).classes("bg-teal-700 text-white text-xs px-3 py-1 rounded")

            with ui.grid(columns=3).classes("w-full gap-3 items-stretch"):
                with ui.card().classes("p-3 bg-slate-50 rounded-lg border border-slate-200"):
                    ui.label("INPUT (BẢN MÃ KHÓA & PRIVATE KEY)").classes("text-[11px] font-bold text-slate-600 uppercase border-b pb-1")
                    ui.label("Bản mã C_key (từ Khối 3):").classes("text-xs text-slate-500 font-semibold mt-1")
                    lbl_k4_ckey = ui.label("(chưa có)").classes("text-xs font-mono text-indigo-700 truncate w-full")
                    ui.label("Private Key Bob (d, n từ Khối 1):").classes("text-xs text-slate-500 font-semibold mt-1")
                    lbl_k4_priv = ui.label("...").classes("text-xs font-mono text-rose-600 truncate w-full")
                with ui.card().classes("p-3 bg-teal-50/50 rounded-lg border border-teal-200"):
                    ui.label("QUÁ TRÌNH XỬ LÝ (ĐỊNH LÝ EULER)").classes("text-[11px] font-bold text-teal-800 uppercase border-b border-teal-200 pb-1")
                    txt_rsa_dec_process = ui.label("Chờ nhận C_key từ Khối 3...").classes("text-xs font-mono text-slate-700 whitespace-pre-wrap leading-relaxed mt-2")
                with ui.card().classes("p-3 bg-emerald-50/50 rounded-lg border border-emerald-200"):
                    ui.label("OUTPUT (KHÓA K' KHÔI PHỤC)").classes("text-[11px] font-bold text-emerald-800 uppercase border-b border-emerald-200 pb-1")
                    txt_rsa_dec_output = ui.label("Chưa có kết quả...").classes("text-xs font-mono text-slate-700 whitespace-pre-wrap break-all leading-relaxed mt-2")

        # Mũi tên dòng chảy (Khép kín sang bước giải mã thông điệp)
        with ui.row().classes("w-full justify-center -my-2"):
            with ui.row().classes("items-center gap-1 bg-emerald-50 px-3 py-0.5 rounded-full border border-emerald-300 shadow-xs"):
                ui.icon("arrow_downward", size="1rem").classes("text-emerald-700")
                ui.label("Nối Khóa phiên K' vừa khôi phục vào Khối 5 để giải mã AES-GCM (Khép kín luồng Bob)").classes("text-[10px] font-bold text-emerald-800")

        # ---------------------------------------------------------------------
        # KHỐI 5: GIẢI MÃ AES-GCM KHÔI PHỤC BẢN RÕ M (KHÉP KÍN LUỒNG BOB)
        # (YÊU CẦU 1 TRỌNG TÂM CỦA CÔ)
        # ---------------------------------------------------------------------
        card_k5 = ui.card().classes("w-full p-4 bg-white rounded-xl shadow-sm border border-slate-200 transition-all")
        with card_k5:
            with ui.row().classes("items-center justify-between w-full pb-2 mb-2 border-b border-slate-100"):
                with ui.row().classes("items-center gap-2"):
                    ui.label("5").classes("w-6 h-6 rounded-full bg-emerald-700 text-white flex items-center justify-center text-xs font-bold")
                    ui.label("Giải Mã AES-GCM Khôi Phục Thông Điệp M (Khép Kín Luồng Bob)").classes("text-sm font-bold text-slate-800")
                    badge_k5 = ui.badge("CHỜ KHÓA K'", color="slate").classes("text-[10px]")
                ui.button("Giải Mã Thông Điệp M", icon="task_alt", on_click=lambda: execute_aes_dec()).classes("bg-emerald-600 text-white text-xs font-bold px-4 py-1.5 rounded shadow-xs")

            with ui.grid(columns=3).classes("w-full gap-3 items-stretch"):
                with ui.card().classes("p-3 bg-slate-50 rounded-lg border border-slate-200"):
                    ui.label("INPUT (DỮ LIỆU ĐẦU VÀO)").classes("text-[11px] font-bold text-slate-600 uppercase border-b pb-1")
                    ui.label("Khóa phiên K' (từ Khối 4):").classes("text-xs text-slate-500 font-semibold mt-1")
                    lbl_k5_rec_k = ui.label("(chưa có)").classes("text-xs font-mono text-teal-700 break-all")
                    ui.label("Dữ liệu bản mã (từ Khối 2):").classes("text-xs text-slate-500 font-semibold mt-2")
                    lbl_k5_data_info = ui.label("• IV, C_data, Tag sẽ lấy từ Khối 2").classes("text-xs font-mono text-slate-600 leading-relaxed")
                with ui.card().classes("p-3 bg-emerald-50/50 rounded-lg border border-emerald-200"):
                    ui.label("KIỂM THỰC GHASH & GIẢI MÃ").classes("text-[11px] font-bold text-emerald-800 uppercase border-b border-emerald-200 pb-1")
                    txt_aes_dec_process = ui.label("Chờ nhận khóa K' từ Khối 4...").classes("text-xs font-mono text-slate-700 whitespace-pre-wrap leading-relaxed mt-2")
                with ui.card().classes("p-3 bg-white rounded-lg border-2 border-emerald-500 flex flex-col justify-between"):
                    with ui.column().classes("gap-1"):
                        ui.label("OUTPUT (THÔNG ĐIỆP GỐC KHÔI PHỤC M')").classes("text-[11px] font-bold text-emerald-900 uppercase border-b border-emerald-200 pb-1")
                        txt_aes_dec_output = ui.label("Chờ thực thi để khôi phục bản rõ...").classes("text-xs font-mono text-slate-800 whitespace-pre-wrap leading-relaxed mt-1")

    # Khởi tạo cặp khóa ban đầu cho trang
    execute_rsa_keygen(silent=True)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="PGP Hybrid Simulator & Algorithms", port=8080, reload=False, show=False)
