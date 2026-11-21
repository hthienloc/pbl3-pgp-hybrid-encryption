#!/usr/bin/env python3
"""
Mô phỏng trực quan PGP Hybrid (RSA-512 + AES-128-GCM) bằng NiceGUI.
- Trang '/'           : Sơ đồ kiến trúc SVG tương tác (click node/link để xem giải thích & dữ liệu thật).
- Trang '/algorithms' : Chi tiết 5 khối thuật toán nối liền dữ liệu thật từ trên xuống dưới.
"""

import os
import sys
import re
import asyncio
import html
from nicegui import ui

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if REPORT_DIR not in sys.path:
    sys.path.insert(0, REPORT_DIR)

from algorithms.rsa import generate_rsa_keys, rsa_encrypt, rsa_decrypt
from algorithms.aes_gcm import aes_gcm_encrypt, aes_gcm_decrypt


# -----------------------------------------------------------------------------
# TRẠNG THÁI & DỮ LIỆU GIẢI THÍCH CHO SƠ ĐỒ TƯƠNG TÁC
# -----------------------------------------------------------------------------
def create_initial_state():
    return {
        "bob_pub": None,
        "bob_priv": None,
        "eve_priv": None,
        "key_mode": "auto",  # 'auto' | 'custom'
        "custom_p": None,
        "custom_q": None,
        "session_key": None,
        "nonce": None,
        "ciphertext": None,
        "auth_tag": None,
        "enc_session_key": None,
        "recovered_key": None,
        "decrypted_text": None,
        "decrypt_error": None,
        "is_tampered": False,
        "use_wrong_key": False,
        "is_busy": False,
        "selected_id": "node_m",
        "log_history": [
            "Hệ thống sẵn sàng. Click vào bất kỳ khối hoặc mũi tên trên sơ đồ để xem chi tiết."
        ],
        "step_status": {
            "keygen": "success",
            "m": "ready",
            "k": "waiting",
            "aes_enc": "waiting",
            "rsa_enc": "waiting",
            "network": "waiting",
            "rsa_dec": "waiting",
            "aes_dec": "waiting",
            "m_out": "waiting",
        },
    }


DIAGRAM_META = {
    # NODES
    "node_m": {
        "title": "Bản rõ M (Plaintext)",
        "kind": "Khối dữ liệu đầu vào",
        "desc": "Chuỗi thông điệp gốc của Alice được mã hóa UTF-8 thành mảng byte trước khi đưa vào AES-GCM.",
        "formula": "M_bytes = encode_utf8(M)",
    },
    "node_k": {
        "title": "Khóa phiên K (Session Key)",
        "kind": "Khối sinh khóa CSPRNG",
        "desc": "Khóa đối xứng 128-bit (16 bytes) sinh ngẫu nhiên dùng một lần cho mỗi phiên truyền tin.",
        "formula": "K = os.urandom(16)  (128 bits)",
    },
    "node_aes_enc": {
        "title": "Mã hóa AES-128-GCM",
        "kind": "Khối xử lý phía Alice",
        "desc": "Mã hóa M bằng AES-CTR với Nonce 12B và tính thẻ xác thực GHASH trên trường GF(2^128).",
        "formula": "C_i = P_i ⊕ AES_K(CB_i)  |  Tag = X_m ⊕ AES_K(J_0)",
    },
    "node_rsa_enc": {
        "title": "Mã hóa RSA khóa K",
        "kind": "Khối xử lý phía Alice",
        "desc": "Chuyển khóa K 16B thành số nguyên (K < n) rồi mã hóa bằng Public Key (e, n) của Bob.",
        "formula": "C_key = K^e mod n  (Square-and-Multiply)",
    },
    "node_keygen": {
        "title": "Cặp khóa RSA-512 (Bob)",
        "kind": "Khối sinh khóa bất đối xứng",
        "desc": "Sinh hai số nguyên tố p, q (256-bit, Miller-Rabin k=20), tính n = p·q, e = 65537 và d = e⁻¹ mod φ(n).",
        "formula": "Pub = (e, n)  |  Priv = (d, n)",
    },
    "node_net": {
        "title": "Kênh mạng TCP (:5000)",
        "kind": "Kênh truyền không tin cậy",
        "desc": "Đóng gói JSON gồm C_key, IV, C_data, Tag kèm 4-byte header độ dài. Kẻ tấn công MITM có thể sửa bit trên kênh này.",
        "formula": "Frame = [4B Length] || JSON(C_key, IV, C_data, Tag)",
    },
    "node_rsa_dec": {
        "title": "Giải mã RSA khóa K'",
        "kind": "Khối xử lý phía Bob",
        "desc": "Dùng Private Key d tính (C_key)^d mod n để khôi phục khóa phiên K'. Nếu dùng sai khóa (Eve), K' sẽ sai lệch.",
        "formula": "K' = (C_key)^d mod n ≡ K mod n",
    },
    "node_aes_dec": {
        "title": "Kiểm thực GHASH & Giải mã AES",
        "kind": "Khối xử lý phía Bob",
        "desc": "Tính lại GHASH_computed từ C_data và K'. Chỉ giải mã CTR nếu GHASH khớp Tag; ngược lại hủy gói tin.",
        "formula": "Verify(GHASH(C_data) == Tag) → P_i = C_i ⊕ AES_K'(CB_i)",
    },
    "node_m_out": {
        "title": "Bản rõ khôi phục M'",
        "kind": "Khối dữ liệu đầu ra",
        "desc": "Thông điệp thu được sau khi xác thực toàn vẹn thành công. Đảm bảo M' == M.",
        "formula": "M' = decode_utf8(P_bytes)",
    },
    # LINKS
    "link_m_aes": {
        "title": "Luồng M → AES-128-GCM",
        "kind": "Liên kết dữ liệu",
        "desc": "Đưa chuỗi byte bản rõ M vào bộ mã hóa dòng AES-CTR và bộ băm xác thực GHASH.",
        "formula": "Input: M_bytes → AES-128-GCM",
    },
    "link_k_aes": {
        "title": "Luồng K → AES-128-GCM",
        "kind": "Liên kết khóa đối xứng",
        "desc": "Cung cấp khóa phiên K (128-bit) để sinh keystream AES_K(CB_i) và khóa băm H = AES_K(0^128).",
        "formula": "Key: K (16B) → AES-128-GCM",
    },
    "link_k_rsa": {
        "title": "Luồng K → RSA Encrypt",
        "kind": "Liên kết khóa phiên",
        "desc": "Chuyển đổi 16 bytes khóa K sang số nguyên big-endian để mã hóa bất đối xứng (yêu cầu K < n).",
        "formula": "K_int = int.from_bytes(K, 'big') < n",
    },
    "link_pub_rsa": {
        "title": "Luồng Public Key (e, n) → RSA Encrypt",
        "kind": "Liên kết khóa công khai",
        "desc": "Alice dùng khóa công khai (e, n) của Bob để khóa chặt K, chỉ Bob có d mới mở được.",
        "formula": "Pub(e, n) → C_key = K^e mod n",
    },
    "link_aes_net": {
        "title": "Luồng (IV, C_data, Tag) → Kênh TCP",
        "kind": "Liên kết bản mã dữ liệu",
        "desc": "Đẩy Nonce 12B, bản mã dữ liệu C_data và thẻ chứng thực Tag 16B vào gói JSON.",
        "formula": "{ IV, C_data, Tag } → TCP Payload",
    },
    "link_rsa_net": {
        "title": "Luồng C_key → Kênh TCP",
        "kind": "Liên kết bản mã khóa",
        "desc": "Đẩy bản mã khóa phiên C_key (512-bit) vào cùng phong bì JSON để gửi tới Bob.",
        "formula": "{ C_key } → TCP Payload",
    },
    "link_net_rsa": {
        "title": "Luồng Kênh TCP → RSA Decrypt",
        "kind": "Liên kết tách gói tin",
        "desc": "Bob tách trường C_key từ JSON nhận được qua socket TCP để đưa vào bộ giải mã RSA.",
        "formula": "JSON['C_key'] → RSA Decrypt",
    },
    "link_priv_rsa": {
        "title": "Luồng Private Key (d, n) → RSA Decrypt",
        "kind": "Liên kết khóa bí mật",
        "desc": "Nạp số mũ bí mật d của Bob (hoặc khóa giả của Eve nếu bật mô phỏng sai khóa) để giải mã C_key.",
        "formula": "Priv(d, n) → K' = (C_key)^d mod n",
    },
    "link_k_dec": {
        "title": "Luồng K' → GHASH & AES Decrypt",
        "kind": "Liên kết khóa khôi phục",
        "desc": "Chuyển khóa phiên K' vừa giải mã từ RSA sang bộ giải mã AES-128-GCM để kiểm tra Tag và giải mã.",
        "formula": "K' (16B) → AES-128-GCM Decrypt",
    },
    "link_net_aes": {
        "title": "Luồng (IV, C_data, Tag) → GHASH & AES Decrypt",
        "kind": "Liên kết bản mã nhận",
        "desc": "Bob lấy trực tiếp IV, C_data và Tag từ gói tin TCP (có thể đã bị MITM sửa bit) để đối chiếu GHASH.",
        "formula": "JSON['IV', 'C_data', 'Tag'] → GHASH Verify",
    },
    "link_aes_mout": {
        "title": "Luồng AES Decrypt → Bản rõ M'",
        "kind": "Liên kết đầu ra",
        "desc": "Nếu Tag hợp lệ, bản rõ P_bytes được giải mã UTF-8 thành M'; nếu sai Tag hoặc sai K', luồng bị chặn.",
        "formula": "P_bytes → M' (hoặc Raise ValueError)",
    },
}


def notify(msg: str, color="indigo"):
    ui.notify(msg, color=color, position="bottom-right")


def short_hex(b: bytes | None, limit: int = 16) -> str:
    if not b:
        return "—"
    h = b.hex()
    return h if len(h) <= limit else f"{h[:limit]}…"


_MATH_SUB_MAP = {
    "C_key": ("C", "key"),
    "C_data": ("C", "data"),
    "K_int": ("K", "int"),
    "M_bytes": ("M", "bytes"),
    "P_bytes": ("P", "bytes"),
    "GHASH_computed": ("GHASH", "computed"),
    "d_eve": ("d", "eve"),
    "CB_{i-1}": ("CB", "i-1"),
    "CB_i": ("CB", "i"),
    "CB_0": ("CB", "0"),
    "CB_1": ("CB", "1"),
    "P_i": ("P", "i"),
    "C_i": ("C", "i"),
    "J_0": ("J", "0"),
    "X_m": ("X", "m"),
    "X_i": ("X", "i"),
    "AES_K'": ("AES", "K'"),
    "AES_K": ("AES", "K"),
    "inc_32": ("inc", "32"),
}
_MATH_SUB_RE = re.compile(
    "|".join(re.escape(k) for k in sorted(_MATH_SUB_MAP, key=len, reverse=True))
)
_MATH_SUP_RE = re.compile(r"\^(128|-1|e|d)\b")


def _format_math(text: str, sub_fmt, sup_fmt) -> str:
    escaped = html.escape(text)
    escaped = _MATH_SUB_RE.sub(
        lambda m: f"{_MATH_SUB_MAP[m.group(0)][0]}{sub_fmt(_MATH_SUB_MAP[m.group(0)][1])}",
        escaped,
    )
    return _MATH_SUP_RE.sub(lambda m: sup_fmt(m.group(1)), escaped)


def format_math_html(text: str) -> str:
    """Định dạng chỉ số trên/dưới bằng thẻ HTML <sub>/<sup> cho các ký hiệu mật mã."""
    return _format_math(
        text,
        lambda s: f'<sub class="text-[0.75em] leading-none">{s}</sub>',
        lambda s: f'<sup class="text-[0.75em] leading-none">{s}</sup>',
    )


def format_math_svg(text: str) -> str:
    """Định dạng chỉ số trên/dưới bằng <tspan> cho nhãn trong SVG."""
    return _format_math(
        text,
        lambda s: f'<tspan baseline-shift="sub" font-size="75%">{s}</tspan>',
        lambda s: f'<tspan baseline-shift="super" font-size="75%">{s}</tspan>',
    )


def setup_page_head():
    ui.query("body").style("background-color: #f8fafc;")
    ui.add_head_html(r"""
    <style>
    .dot-grid-bg {
        background-color: #f8fafc;
        background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
        background-size: 18px 18px;
    }
    .svg-node { cursor: pointer; transition: filter 0.15s ease; }
    .svg-node:hover { filter: drop-shadow(0 3px 6px rgba(79, 70, 229, 0.25)); }
    .svg-edge-hit { cursor: pointer; }
    .svg-edge-hit:hover + .svg-edge-vis { stroke-width: 3.5 !important; filter: drop-shadow(0 0 4px rgba(79, 70, 229, 0.45)); }
    @keyframes dashFlow {
        to { stroke-dashoffset: -24; }
    }
    .edge-animated {
        stroke-dasharray: 6 6;
        animation: dashFlow 0.9s linear infinite;
    }
    .resize-bar {
        width: 100%; height: 8px; cursor: ns-resize;
        display: flex; justify-content: center; align-items: center;
        user-select: none; touch-action: none;
    }
    .resize-bar:hover .resize-line { background-color: #818cf8; }
    .resize-line {
        width: 48px; height: 4px; border-radius: 9999px;
        background-color: #64748b; transition: background-color 0.2s;
    }
    </style>
    <script>
    window.initConsoleResize = function() {
        const handle = document.getElementById('console-resize-handle');
        const panel = document.getElementById('resizable-terminal-panel');
        const scrollContainer = document.getElementById('math-log-scroll');
        if (!handle || !panel || !scrollContainer || handle.dataset.bound) return;
        handle.dataset.bound = '1';

        let isResizing = false, startY = 0, startHeight = 0;
        handle.addEventListener('mousedown', function(e) {
            isResizing = true; startY = e.clientY; startHeight = panel.offsetHeight;
            document.body.style.cursor = 'ns-resize';
            document.body.style.userSelect = 'none';
            e.preventDefault();
        });
        document.addEventListener('mousemove', function(e) {
            if (!isResizing) return;
            let newHeight = Math.max(110, Math.min(580, startHeight + (startY - e.clientY)));
            panel.style.height = newHeight + 'px';
            scrollContainer.style.height = (newHeight - 65) + 'px';
            document.body.style.paddingBottom = (newHeight + 24) + 'px';
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
    setTimeout(window.initConsoleResize, 600);
    </script>
    """)


def render_header(current_page: str):
    with ui.header().classes(
        "bg-slate-900 text-white px-5 py-2 flex items-center justify-between shadow-sm sticky top-0 z-40"
    ):
        with ui.row().classes("items-center gap-3"):
            ui.icon("hub", size="1.4rem").classes("text-indigo-400")
            with ui.column().classes("gap-0"):
                ui.label("PGP Hybrid Simulator (RSA-512 + AES-128-GCM)").classes("text-sm font-bold leading-tight")
                ui.label("PBL3: Mạng máy tính • Nhóm 7").classes("text-[11px] text-slate-400")
            with ui.row().classes("gap-1 ml-4 bg-slate-800 p-1 rounded-lg border border-slate-700"):
                ui.button(
                    "Sơ Đồ Tương Tác",
                    on_click=lambda: ui.navigate.to("/"),
                ).props(f"{'unelevated' if current_page == 'integrated' else 'flat'} dense").classes(
                    f"text-xs px-3 py-1 rounded {'bg-indigo-600 text-white font-semibold' if current_page == 'integrated' else 'text-slate-300 hover:text-white'}"
                )
                ui.button(
                    "Chi Tiết Thuật Toán",
                    on_click=lambda: ui.navigate.to("/algorithms"),
                ).props(f"{'unelevated' if current_page == 'algorithms' else 'flat'} dense").classes(
                    f"text-xs px-3 py-1 rounded {'bg-indigo-600 text-white font-semibold' if current_page == 'algorithms' else 'text-slate-300 hover:text-white'}"
                )


# =========================================================================
# TRANG 1: SƠ ĐỒ KIẾN TRÚC SVG TƯƠNG TÁC + INSPECTOR PANEL
# =========================================================================
@ui.page("/")
def page_integrated():
    setup_page_head()
    ui.query("body").style("padding-bottom: 11.5rem;")
    render_header("integrated")
    state = create_initial_state()

    # Khởi tạo cặp khóa RSA-512 mặc định cho Bob và 1 cặp khóa giả cho Eve
    state["bob_pub"], state["bob_priv"] = generate_rsa_keys(bits=512)
    _, state["eve_priv"] = generate_rsa_keys(bits=512)

    def log_math(message: str):
        for line in message.strip().split("\n"):
            if line.strip():
                state["log_history"].append(line)
        if len(state["log_history"]) > 24:
            state["log_history"] = state["log_history"][-24:]
        lbl_math_console.set_text("\n".join(state["log_history"]))
        ui.run_javascript(
            "const el = document.getElementById('math-log-scroll'); if (el) { el.scrollTop = el.scrollHeight; }"
        )

    def set_busy(busy: bool, action_name: str = ""):
        state["is_busy"] = busy
        progress_bar.set_visibility(busy)
        lbl_exec_status.set_text(
            f"Đang xử lý: {action_name}..." if busy else "Sẵn sàng. Click node/mũi tên để kiểm tra dữ liệu."
        )

    # -------------------------------------------------------------------------
    # RENDER SVG ARCHITECTURE DIAGRAM (CLICKABLE NODES & LINKS)
    # -------------------------------------------------------------------------
    def _node_palette(status: str, selected: bool):
        if status == "error":
            fill, stroke, title_col = "#fff1f2", "#e11d48", "#881337"
        elif status == "active":
            fill, stroke, title_col = "#fffbeb", "#f59e0b", "#78350f"
        elif status == "success":
            fill, stroke, title_col = "#ecfdf5", "#10b981", "#064e3b"
        elif status == "ready":
            fill, stroke, title_col = "#eff6ff", "#3b82f6", "#1e3a8a"
        else:
            fill, stroke, title_col = "#f8fafc", "#cbd5e1", "#475569"

        if selected:
            stroke = "#4f46e5"
        return fill, stroke, title_col

    def _edge_style(active_cond: bool, err_cond: bool, selected: bool):
        if selected:
            return "#4f46e5", "3.2", "edge-animated" if active_cond else ""
        if err_cond:
            return "#e11d48", "2.4", ""
        if active_cond:
            return "#10b981", "2.2", ""
        return "#94a3b8", "1.6", ""

    def build_svg() -> str:
        st = state["step_status"]
        sel = state["selected_id"]

        def edge(eid: str, d: str, active: bool, err: bool = False, label: str = "", lx: int = 0, ly: int = 0, dashed: bool = False):
            is_sel = (sel == eid)
            col, sw, anim = _edge_style(active, err, is_sel)
            dash_attr = 'stroke-dasharray="5 4"' if (dashed and not anim) else ""
            marker = "url(#arr-err)" if err else ("url(#arr-sel)" if is_sel else ("url(#arr-ok)" if active else "url(#arr-idle)"))
            lbl_html = (
                f'<rect x="{lx-28}" y="{ly-9}" width="56" height="16" rx="4" fill="#ffffff" stroke="{col}" stroke-width="1"/>'
                f'<text x="{lx}" y="{ly+3}" text-anchor="middle" font-size="9.5" font-family="monospace" font-weight="700" fill="{col}">{format_math_svg(label)}</text>'
            ) if label else ""
            return f"""
            <g onclick="emitEvent('diagram_select', '{eid}')">
              <path d="{d}" fill="none" stroke="transparent" stroke-width="18" class="svg-edge-hit"/>
              <path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" {dash_attr} class="svg-edge-vis {anim}" marker-end="{marker}"/>
              {lbl_html}
            </g>"""

        def node(nid: str, x: int, y: int, w: int, h: int, title: str, sub: str, status: str, badge: str = "", dashed: bool = False):
            is_sel = (sel == nid)
            fill, stroke, tcol = _node_palette(status, is_sel)
            sw = "2.8" if is_sel else "1.6"
            dash = 'stroke-dasharray="5 3"' if dashed else ""
            halo = f'<rect x="{x-4}" y="{y-4}" width="{w+8}" height="{h+8}" rx="12" fill="none" stroke="#6366f1" stroke-width="2" opacity="0.45"/>' if is_sel else ""
            badge_html = (
                f'<rect x="{x+w-54}" y="{y-8}" width="50" height="15" rx="7" fill="{stroke}"/>'
                f'<text x="{x+w-29}" y="{y+2}" text-anchor="middle" font-size="8.5" font-weight="700" fill="#ffffff">{html.escape(badge)}</text>'
            ) if badge else ""
            return f"""
            <g class="svg-node" onclick="emitEvent('diagram_select', '{nid}')">
              {halo}
              <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {dash}/>
              <text x="{x + w/2}" y="{y + 22}" text-anchor="middle" font-size="11.5" font-weight="700" fill="{tcol}">{format_math_svg(title)}</text>
              <text x="{x + w/2}" y="{y + 39}" text-anchor="middle" font-size="9.5" font-family="monospace" fill="#475569">{format_math_svg(sub)}</text>
              {badge_html}
            </g>"""

        m_val = (txt_plaintext_input.value or "").strip()
        m_sub = (m_val[:15] + "…") if len(m_val) > 15 else (m_val or "(trống)")
        k_sub = short_hex(state["session_key"], 12)
        aes_sub = f"C_data ({len(state['ciphertext'])}B)" if state["ciphertext"] else "CTR + GHASH"
        rsa_enc_sub = f"0x{state['enc_session_key']:x}"[:13] + "…" if state["enc_session_key"] else "K^e mod n"
        net_sub = "BIT-FLIPPED!" if state["is_tampered"] else ("Đã truyền TCP" if st["network"] == "success" else "JSON 4 trường")
        rsa_dec_sub = ("Khóa giả Eve!" if state["use_wrong_key"] else short_hex(state["recovered_key"], 12)) if state["recovered_key"] else "(C_key)^d mod n"
        aes_dec_sub = "Tag HỢP LỆ" if st["aes_dec"] == "success" else ("LỖI TAG!" if st["aes_dec"] == "error" else "GHASH + CTR")
        m_out_sub = (state["decrypted_text"][:14] + "…") if state["decrypted_text"] and len(state["decrypted_text"]) > 14 else (state["decrypted_text"] or ("BỊ HỦY" if st["m_out"] == "error" else "Chờ giải mã"))

        e_val, n_val = state["bob_pub"]
        keygen_sub = f"n: {n_val.bit_length()}b | e={e_val}"

        # Edges
        edges_svg = "".join([
            edge("link_m_aes", "M 155 95 L 195 95", st["aes_enc"] == "success", label="M", lx=175, ly=84),
            edge("link_k_aes", "M 95 190 L 95 155 L 250 155 L 250 125", st["aes_enc"] == "success", label="K", lx=172, ly=146, dashed=True),
            edge("link_k_rsa", "M 155 218 L 195 218", st["rsa_enc"] == "success", label="K_int", lx=175, ly=207, dashed=True),
            edge("link_pub_rsa", "M 420 345 L 255 345 L 255 248", st["rsa_enc"] == "success", label="(e,n)", lx=330, ly=335, dashed=True),
            edge("link_aes_net", "M 315 95 L 380 95 L 380 152 L 410 152", st["network"] in ("success", "error"), err=state["is_tampered"], label="C_data", lx=355, ly=85),
            edge("link_rsa_net", "M 315 218 L 380 218 L 380 178 L 410 178", st["network"] in ("success", "error"), label="C_key", lx=355, ly=230),
            edge("link_net_rsa", "M 550 178 L 580 178 L 580 218 L 645 218", st["rsa_dec"] in ("success", "error"), label="C_key", lx=605, ly=230),
            edge("link_priv_rsa", "M 540 345 L 705 345 L 705 248", st["rsa_dec"] in ("success", "error"), err=state["use_wrong_key"], label="d_eve" if state["use_wrong_key"] else "(d,n)", lx=625, ly=335, dashed=True),
            edge("link_net_aes", "M 550 152 L 580 152 L 580 95 L 645 95", st["aes_dec"] in ("success", "error"), err=state["is_tampered"], label="IV,C,Tag", lx=608, ly=85),
            edge("link_k_dec", "M 705 188 L 705 125", st["aes_dec"] in ("success", "error"), err=state["use_wrong_key"], label="K'", lx=720, ly=158, dashed=True),
            edge("link_aes_mout", "M 765 95 L 805 95", st["m_out"] == "success", err=st["m_out"] == "error", label="M'", lx=785, ly=84),
        ])

        # Nodes
        nodes_svg = "".join([
            node("node_m", 35, 66, 120, 56, "Bản rõ M", m_sub, st["m"], "INPUT"),
            node("node_k", 35, 190, 120, 56, "Khóa phiên K", k_sub, st["k"], "128b", dashed=True),
            node("node_aes_enc", 195, 66, 120, 56, "AES-128-GCM", aes_sub, st["aes_enc"], "ALICE"),
            node("node_rsa_enc", 195, 190, 120, 56, "RSA Encrypt", rsa_enc_sub, st["rsa_enc"], "ALICE"),
            node("node_net", 410, 130, 140, 68, "Kênh TCP :5000", net_sub, st["network"], "MITM!" if state["is_tampered"] else "TCP"),
            node("node_keygen", 415, 316, 130, 56, "Cặp khóa RSA", keygen_sub, st["keygen"], "512b", dashed=True),
            node("node_rsa_dec", 645, 190, 120, 56, "RSA Decrypt", rsa_dec_sub, st["rsa_dec"], "EVE!" if state["use_wrong_key"] else "BOB"),
            node("node_aes_dec", 645, 66, 120, 56, "GHASH & AES", aes_dec_sub, st["aes_dec"], "BOB"),
            node("node_m_out", 805, 66, 120, 56, "Bản rõ M'", m_out_sub, st["m_out"], "OUTPUT"),
        ])

        return f"""
        <svg viewBox="0 0 960 395" class="w-full h-auto select-none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <marker id="arr-idle" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#94a3b8"/>
            </marker>
            <marker id="arr-ok" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981"/>
            </marker>
            <marker id="arr-err" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#e11d48"/>
            </marker>
            <marker id="arr-sel" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#4f46e5"/>
            </marker>
          </defs>

          <!-- Zone containers -->
          <rect x="16" y="16" width="318" height="260" rx="12" fill="#ffffff" fill-opacity="0.72" stroke="#cbd5e1" stroke-dasharray="4 3"/>
          <text x="30" y="38" font-size="11" font-weight="800" fill="#1e40af" letter-spacing="0.6">ALICE (BÊN GỬI)</text>

          <rect x="392" y="88" width="176" height="145" rx="12" fill="#faf5ff" fill-opacity="0.78" stroke="#d8b4fe" stroke-dasharray="4 3"/>
          <text x="480" y="110" text-anchor="middle" font-size="11" font-weight="800" fill="#6b21a8" letter-spacing="0.6">KÊNH MẠNG</text>

          <rect x="626" y="16" width="318" height="260" rx="12" fill="#ffffff" fill-opacity="0.72" stroke="#cbd5e1" stroke-dasharray="4 3"/>
          <text x="640" y="38" font-size="11" font-weight="800" fill="#0f766e" letter-spacing="0.6">BOB (BÊN NHẬN)</text>

          {edges_svg}
          {nodes_svg}
        </svg>
        """

    # -------------------------------------------------------------------------
    # INSPECTOR DATA BUILDER (LIVE VALUES FOR SELECTED NODE / LINK)
    # -------------------------------------------------------------------------
    def get_live_values_for(item_id: str) -> str:
        e_val, n_val = state["bob_pub"]
        d_val, _ = state["bob_priv"]
        m_val = (txt_plaintext_input.value or "").strip()

        if item_id in ("node_m", "link_m_aes"):
            b = m_val.encode("utf-8")
            return f"M = \"{m_val}\"\nĐộ dài = {len(b)} bytes\nUTF-8 Hex = {b.hex()}"

        if item_id in ("node_k", "link_k_aes", "link_k_rsa"):
            if not state["session_key"]:
                return "Chưa sinh khóa phiên K."
            k_int = int.from_bytes(state["session_key"], "big")
            return f"K (Hex 16B) = {state['session_key'].hex()}\nK (Int)     = {k_int}\nKiểm tra K < n: {k_int < n_val}"

        if item_id in ("node_keygen", "link_pub_rsa", "link_priv_rsa"):
            mode_txt = "Tự sinh RSA-512" if state["key_mode"] == "auto" else f"Tùy chỉnh (p={state['custom_p']}, q={state['custom_q']})"
            eve_note = "\n[CẢNH BÁO] Đang dùng Private Key giả của Eve!" if (item_id == "link_priv_rsa" and state["use_wrong_key"]) else ""
            return f"Chế độ: {mode_txt}\ne = {e_val}\nn = {n_val}\nd = {d_val}{eve_note}"

        if item_id in ("node_aes_enc", "link_aes_net"):
            if not state["ciphertext"]:
                return "Chưa thực hiện mã hóa AES-128-GCM."
            return (
                f"Nonce (12B) : {state['nonce'].hex()}\n"
                f"C_data ({len(state['ciphertext'])}B): {state['ciphertext'].hex()}\n"
                f"Auth Tag    : {state['auth_tag'].hex()}"
            )

        if item_id in ("node_rsa_enc", "link_rsa_net", "link_net_rsa"):
            if not state["enc_session_key"]:
                return "Chưa thực hiện mã hóa RSA khóa K."
            return f"C_key (Hex) = 0x{state['enc_session_key']:x}\nC_key (Int) = {state['enc_session_key']}"

        if item_id == "node_net":
            if state["step_status"]["network"] == "waiting":
                return "Chưa đóng gói & truyền qua TCP."
            prefix = "[CẢNH BÁO MITM: C_data[0] ^= 0xFF]\n" if state["is_tampered"] else ""
            return (
                f"{prefix}{{\n"
                f'  "C_key": "0x{state["enc_session_key"]:x}",\n'
                f'  "IV": "{state["nonce"].hex()}",\n'
                f'  "C_data": "{state["ciphertext"].hex()}",\n'
                f'  "Tag": "{state["auth_tag"].hex()}"\n'
                f"}}"
            )

        if item_id in ("node_rsa_dec", "link_k_dec"):
            if not state["recovered_key"]:
                return "Chưa thực hiện giải mã RSA."
            match_str = "KHỚP K GỐC" if state["recovered_key"] == state["session_key"] else "SAI KHÁC K GỐC (Dùng sai khóa)"
            return f"K' (Hex 16B) = {state['recovered_key'].hex()}\nĐối chiếu    = {match_str}"

        if item_id in ("node_aes_dec", "link_net_aes", "node_m_out", "link_aes_mout"):
            if state["decrypt_error"]:
                return f"Trạng thái: THẤT BẠI (Hủy gói tin)\nChi tiết  : {state['decrypt_error']}"
            if state["decrypted_text"] is not None:
                return (
                    f"GHASH Tag : HỢP LỆ (Khớp 100%)\n"
                    f"M'        = \"{state['decrypted_text']}\"\n"
                    f"M' == M   : {state['decrypted_text'] == m_val}"
                )
            if state["ciphertext"]:
                return f"Đang chờ Bob kiểm thực & giải mã.\nIV  : {state['nonce'].hex()}\nTag : {state['auth_tag'].hex()}"
            return "Chưa có dữ liệu bản mã."

        return "—"

    def refresh_ui():
        svg_holder.set_content(build_svg())
        sel = state["selected_id"]
        meta = DIAGRAM_META.get(sel, DIAGRAM_META["node_m"])
        lbl_ins_title.set_content(format_math_html(meta["title"]))
        lbl_ins_kind.set_text(meta["kind"])
        lbl_ins_desc.set_content(format_math_html(meta["desc"]))
        lbl_ins_formula.set_content(format_math_html(meta["formula"]))
        lbl_ins_live.set_content(format_math_html(get_live_values_for(sel)))

        # Status badge
        st = state["step_status"]
        node_key = sel.replace("node_", "") if sel.startswith("node_") else None
        status_val = st.get(node_key, "ready") if node_key else "ready"
        badge_map = {
            "success": ("Hoàn tất", "emerald"),
            "active": ("Đang chạy", "amber"),
            "error": ("Lỗi / Tấn công", "rose"),
            "ready": ("Sẵn sàng", "indigo"),
            "waiting": ("Chờ thực thi", "slate"),
        }
        b_txt, b_col = badge_map.get(status_val, ("Sẵn sàng", "indigo"))
        badge_ins_status.set_text(b_txt)
        badge_ins_status.props(f"color={b_col}")

        # Toggle button styles for attack states
        btn_tamper.props(f"color={'rose' if state['is_tampered'] else 'slate'}")
        btn_wrong_key.props(f"color={'rose' if state['use_wrong_key'] else 'slate'}")

    def handle_diagram_select(e):
        item_id = e.args
        if item_id in DIAGRAM_META:
            state["selected_id"] = item_id
            refresh_ui()

    ui.on("diagram_select", handle_diagram_select)

    # -------------------------------------------------------------------------
    # CRYPTO ACTIONS (PRESERVED 100%)
    # -------------------------------------------------------------------------
    def reset_pipeline(keep_keys=True):
        if not keep_keys:
            state["bob_pub"], state["bob_priv"] = generate_rsa_keys(bits=512)
            state["key_mode"] = "auto"
        _, state["eve_priv"] = generate_rsa_keys(bits=512)
        for k in ("session_key", "nonce", "ciphertext", "auth_tag", "enc_session_key", "recovered_key", "decrypted_text", "decrypt_error"):
            state[k] = None
        state["is_tampered"] = False
        state["use_wrong_key"] = False
        state["step_status"] = {
            "keygen": "success",
            "m": "ready",
            "k": "waiting",
            "aes_enc": "waiting",
            "rsa_enc": "waiting",
            "network": "waiting",
            "rsa_dec": "waiting",
            "aes_dec": "waiting",
            "m_out": "waiting",
        }
        refresh_ui()

    async def action_generate_session_key():
        if state["is_busy"]:
            return
        set_busy(True, "Sinh khóa phiên K (128-bit)")
        state["selected_id"] = "node_k"
        state["step_status"]["k"] = "active"
        refresh_ui()
        state["session_key"] = os.urandom(16)
        await asyncio.sleep(0.18)
        log_math(f"[K-Gen] K (128-bit) = {state['session_key'].hex()}")
        state["step_status"]["k"] = "success"
        refresh_ui()
        set_busy(False)
        notify("Đã sinh khóa phiên K (128-bit)", "blue")

    async def action_aes_encrypt():
        if state["is_busy"]:
            return
        if not state["session_key"]:
            notify("Sinh khóa K trước", "amber")
            return
        pt = (txt_plaintext_input.value or "").strip()
        if not pt:
            notify("Nhập bản rõ M trước", "amber")
            return
        set_busy(True, "Mã hóa AES-128-GCM")
        state["selected_id"] = "node_aes_enc"
        state["step_status"]["aes_enc"] = "active"
        refresh_ui()
        await asyncio.sleep(0.18)
        state["ciphertext"], state["nonce"], state["auth_tag"] = aes_gcm_encrypt(state["session_key"], pt.encode("utf-8"))
        state["is_tampered"] = False
        log_math(
            f"[AES-GCM] |M|={len(pt.encode('utf-8'))}B | IV={state['nonce'].hex()} | Tag={state['auth_tag'].hex()}"
        )
        state["step_status"]["m"] = "success"
        state["step_status"]["aes_enc"] = "success"
        refresh_ui()
        set_busy(False)
        notify("AES-128-GCM: Mã hóa xong", "blue")

    async def action_rsa_encrypt_key():
        if state["is_busy"]:
            return
        if not state["session_key"] or not state["bob_pub"]:
            notify("Cần khóa K và Public Key Bob", "amber")
            return
        e, n = state["bob_pub"]
        key_int = int.from_bytes(state["session_key"], "big")
        if key_int >= n:
            notify("Lỗi: K >= n (n quá nhỏ cho AES-128, hãy dùng RSA >= 144 bit)", "red")
            return
        set_busy(True, "Mã hóa RSA khóa K")
        state["selected_id"] = "node_rsa_enc"
        state["step_status"]["rsa_enc"] = "active"
        refresh_ui()
        await asyncio.sleep(0.18)
        state["enc_session_key"] = rsa_encrypt(state["bob_pub"], key_int)
        log_math(f"[RSA Enc] C_key = K^{e} mod n -> 0x{state['enc_session_key']:x}")
        state["step_status"]["rsa_enc"] = "success"
        refresh_ui()
        set_busy(False)
        notify("RSA: Đã mã hóa khóa K", "indigo")

    async def action_send_packet():
        if state["is_busy"]:
            return
        if not state["enc_session_key"] or not state["ciphertext"]:
            notify("Hoàn tất AES-GCM và RSA Enc trước", "amber")
            return
        set_busy(True, "Truyền gói TCP")
        state["selected_id"] = "node_net"
        state["step_status"]["network"] = "active"
        refresh_ui()
        await asyncio.sleep(0.2)
        log_math("[TCP :5000] Đã đóng gói JSON 4 trường + 4B Header và truyền tới Bob.")
        state["step_status"]["network"] = "error" if state["is_tampered"] else "success"
        refresh_ui()
        set_busy(False)
        notify("Đã truyền gói tin qua TCP", "purple")

    async def action_simulate_tamper():
        if state["is_busy"]:
            return
        if not state["ciphertext"] or not state["enc_session_key"]:
            notify("Chạy AES-GCM và RSA Enc trước", "amber")
            return
        if state["is_tampered"]:
            notify("Gói tin đã bị sửa bit trước đó", "amber")
            return
        tampered = bytearray(state["ciphertext"])
        tampered[0] ^= 0xFF
        state["ciphertext"] = bytes(tampered)
        state["is_tampered"] = True
        state["selected_id"] = "node_net"
        state["step_status"]["network"] = "error"
        log_math("[MITM] Bit-Flip C_data[0] ^= 0xFF -> Bản mã bị biến đổi trên kênh truyền!")
        refresh_ui()
        notify("MITM: Đã sửa 1 byte C_data", "red")

    def action_toggle_wrong_key():
        if state["is_busy"]:
            return
        state["use_wrong_key"] = not state["use_wrong_key"]
        state["selected_id"] = "link_priv_rsa"
        log_math(
            "[Eve] Bật mô phỏng dùng sai Private Key để giải mã C_key."
            if state["use_wrong_key"]
            else "[Bob] Khôi phục dùng đúng Private Key của Bob."
        )
        refresh_ui()
        notify(
            "Đã bật chế độ sai khóa (Eve)" if state["use_wrong_key"] else "Đã tắt chế độ sai khóa",
            "rose" if state["use_wrong_key"] else "teal",
        )

    async def action_rsa_decrypt_key():
        if state["is_busy"]:
            return
        if not state["enc_session_key"]:
            notify("Chưa có C_key", "amber")
            return
        set_busy(True, "Giải mã RSA")
        state["selected_id"] = "node_rsa_dec"
        state["step_status"]["rsa_dec"] = "active"
        refresh_ui()
        await asyncio.sleep(0.18)
        priv_key = state["eve_priv"] if state["use_wrong_key"] else state["bob_priv"]
        try:
            rec_int = rsa_decrypt(priv_key, state["enc_session_key"])
            state["recovered_key"] = rec_int.to_bytes(16, "big")
            is_ok = (state["recovered_key"] == state["session_key"])
            state["step_status"]["rsa_dec"] = "success" if is_ok else "error"
            log_math(f"[RSA Dec] K' = {state['recovered_key'].hex()} ({'Khớp K' if is_ok else 'KHÔNG KHỚP K'})")
            notify("RSA Dec: Đã khôi phục K'" if is_ok else "RSA Dec: K' sai do dùng sai khóa!", "teal" if is_ok else "red")
        except (ValueError, OverflowError) as err:
            state["recovered_key"] = None
            state["decrypt_error"] = str(err)
            state["step_status"]["rsa_dec"] = "error"
            log_math(f"[RSA Dec Lỗi] {err}")
            notify(f"Lỗi giải mã RSA: {err}", "red")
        refresh_ui()
        set_busy(False)

    async def action_aes_decrypt_data():
        if state["is_busy"]:
            return
        if not state["recovered_key"]:
            notify("Giải mã RSA để lấy K' trước", "amber")
            return
        set_busy(True, "Xác thực GHASH & Giải mã AES")
        state["selected_id"] = "node_aes_dec"
        state["step_status"]["aes_dec"] = "active"
        refresh_ui()
        await asyncio.sleep(0.18)
        try:
            pt_bytes = aes_gcm_decrypt(
                session_key=state["recovered_key"],
                nonce_bytes=state["nonce"],
                ciphertext_bytes=state["ciphertext"],
                auth_tag_bytes=state["auth_tag"],
            )
            state["decrypted_text"] = pt_bytes.decode("utf-8")
            state["decrypt_error"] = None
            state["step_status"]["aes_dec"] = "success"
            state["step_status"]["m_out"] = "success"
            state["selected_id"] = "node_m_out"
            log_math(f"[GHASH OK] Tag trùng khớp! M' = \"{state['decrypted_text']}\"")
            notify("Xác thực GHASH & giải mã thành công!", "emerald")
        except Exception as err:
            state["decrypted_text"] = None
            state["decrypt_error"] = str(err)
            state["step_status"]["aes_dec"] = "error"
            state["step_status"]["m_out"] = "error"
            log_math(f"[GHASH LỖI] {err} -> Hủy gói tin!")
            notify("Kiểm tra Auth Tag thất bại!", "red")
        refresh_ui()
        set_busy(False)

    async def action_run_all():
        if state["is_busy"]:
            return
        # Reset data but keep current keys and wrong_key flag if user toggled it
        keep_wrong = state["use_wrong_key"]
        reset_pipeline(keep_keys=True)
        state["use_wrong_key"] = keep_wrong
        await action_generate_session_key()
        await action_aes_encrypt()
        await action_rsa_encrypt_key()
        await action_send_packet()
        await action_rsa_decrypt_key()
        await action_aes_decrypt_data()

    # -------------------------------------------------------------------------
    # DIALOG CẤU HÌNH KHÓA RSA (AUTO 512-BIT HOẶC NHẬP P, Q THỦ CÔNG)
    # -------------------------------------------------------------------------
    with ui.dialog() as dlg_keys, ui.card().classes("w-full max-w-md p-4"):
        ui.label("Cấu hình cặp khóa RSA (Bob)").classes("text-sm font-bold text-slate-800")
        ui.label("Mặc định RSA-512 (p, q 256-bit, e=65537, Miller-Rabin k=20).").classes("text-xs text-slate-500 mb-2")
        inp_p = ui.input("Số nguyên tố p (tùy chọn)").props("outlined dense").classes("w-full text-xs font-mono")
        inp_q = ui.input("Số nguyên tố q (tùy chọn)").props("outlined dense").classes("w-full text-xs font-mono mt-1")
        inp_e = ui.input("Số mũ công khai e", value="65537").props("outlined dense").classes("w-full text-xs font-mono mt-1")

        def apply_auto_keys():
            state["bob_pub"], state["bob_priv"] = generate_rsa_keys(bits=512)
            state["key_mode"] = "auto"
            reset_pipeline(keep_keys=True)
            log_math("[Keygen] Đã sinh mới cặp khóa RSA-512 (e=65537, Miller-Rabin k=20).")
            dlg_keys.close()
            notify("Đã sinh cặp khóa RSA-512 mới", "teal")

        def apply_custom_keys():
            try:
                p_val = int(inp_p.value.strip())
                q_val = int(inp_q.value.strip())
                e_val = int(inp_e.value.strip())
                pub, priv = generate_rsa_keys(p=p_val, q=q_val, e=e_val)
                state["bob_pub"], state["bob_priv"] = pub, priv
                state["key_mode"] = "custom"
                state["custom_p"], state["custom_q"] = p_val, q_val
                reset_pipeline(keep_keys=True)
                log_math(f"[Keygen] Đã nạp khóa tùy chỉnh p={p_val}, q={q_val}, e={e_val}.")
                dlg_keys.close()
                notify("Đã áp dụng cặp khóa p, q tùy chỉnh", "teal")
            except Exception as err:
                notify(f"Lỗi tham số khóa: {err}", "red")

        with ui.row().classes("w-full justify-end gap-2 mt-3"):
            ui.button("Sinh tự động 512-bit", on_click=apply_auto_keys).classes("bg-teal-600 text-white text-xs")
            ui.button("Áp dụng p, q", on_click=apply_custom_keys).classes("bg-indigo-600 text-white text-xs")
            ui.button("Đóng", on_click=dlg_keys.close).props("flat").classes("text-xs text-slate-600")

    # -------------------------------------------------------------------------
    # THANH ĐIỀU KHIỂN GỌN GÀNG TRÊN CÙNG
    # -------------------------------------------------------------------------
    with ui.column().classes("w-full max-w-7xl mx-auto px-3 pt-3 gap-2.5"):
        with ui.card().classes("w-full p-2.5 bg-white rounded-xl shadow-xs border border-slate-200"):
            with ui.row().classes("w-full items-center gap-2 flex-wrap"):
                txt_plaintext_input = ui.input(
                    label="Bản rõ M",
                    value="Hello cô Hạnh",
                ).props("outlined dense").classes("flex-1 min-w-[200px] text-xs")
                ui.button("Mẫu 1", on_click=lambda: (txt_plaintext_input.set_value("Hello cô Hạnh"), refresh_ui())).props("flat dense").classes("text-[11px] text-indigo-600")
                ui.button("Mẫu 2", on_click=lambda: (txt_plaintext_input.set_value("Nhóm 7 PBL3"), refresh_ui())).props("flat dense").classes("text-[11px] text-indigo-600")

                ui.separator().props("vertical").classes("h-6 mx-1")

                ui.button("Khóa RSA", icon="key", on_click=dlg_keys.open).props("outline dense").classes("text-xs text-teal-700 px-2")
                ui.button("▶ Chạy tất cả", on_click=action_run_all).props("unelevated dense").classes("bg-indigo-600 text-white text-xs font-semibold px-3")
                ui.button("↺ Reset", on_click=lambda: reset_pipeline(keep_keys=True)).props("outline dense").classes("text-xs text-slate-700 px-2")

                ui.separator().props("vertical").classes("h-6 mx-1")

                btn_tamper = ui.button("Sửa 1B (MITM)", icon="warning", on_click=action_simulate_tamper).props("outline dense").classes("text-xs px-2")
                btn_wrong_key = ui.button("Sai khóa (Eve)", icon="no_encryption", on_click=action_toggle_wrong_key).props("outline dense").classes("text-xs px-2")

            # Step-by-step micro bar
            with ui.row().classes("w-full items-center gap-1.5 pt-2 mt-2 border-t border-slate-100 flex-wrap"):
                ui.label("Từng bước:").classes("text-[11px] font-bold text-slate-500 uppercase mr-1")
                ui.button("1. Sinh K", on_click=action_generate_session_key).props("dense unelevated").classes("text-[11px] bg-slate-800 text-white px-2")
                ui.button("2. AES-GCM", on_click=action_aes_encrypt).props("dense unelevated").classes("text-[11px] bg-blue-600 text-white px-2")
                ui.button("3. RSA Enc", on_click=action_rsa_encrypt_key).props("dense unelevated").classes("text-[11px] bg-indigo-600 text-white px-2")
                ui.button("4. Gửi TCP", on_click=action_send_packet).props("dense unelevated").classes("text-[11px] bg-purple-600 text-white px-2")
                ui.button("5. RSA Dec", on_click=action_rsa_decrypt_key).props("dense unelevated").classes("text-[11px] bg-teal-700 text-white px-2")
                ui.button("6. GHASH & AES Dec", on_click=action_aes_decrypt_data).props("dense unelevated").classes("text-[11px] bg-emerald-600 text-white px-2")

        # ---------------------------------------------------------------------
        # KHUNG CHÍNH: SƠ ĐỒ SVG (TRÁI) + INSPECTOR PANEL (PHẢI)
        # ---------------------------------------------------------------------
        with ui.row().classes("w-full items-stretch gap-3 flex-nowrap max-lg:flex-wrap"):
            # CỘT TRÁI: SƠ ĐỒ TƯƠNG TÁC
            with ui.card().classes("flex-[2.2] min-w-[320px] p-3 bg-white rounded-xl shadow-sm border border-slate-200 dot-grid-bg"):
                with ui.row().classes("w-full items-center justify-between pb-2 mb-1 border-b border-slate-200/70"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("schema", size="1.2rem").classes("text-indigo-600")
                        ui.label("Kiến trúc truyền tin PGP Hybrid (Click khối hoặc mũi tên để kiểm tra)").classes("text-xs font-bold text-slate-800")
                    with ui.row().classes("items-center gap-2 text-[10px] font-semibold text-slate-500"):
                        ui.label("● Xanh: Xong").classes("text-emerald-600")
                        ui.label("● Vàng: Đang chạy").classes("text-amber-600")
                        ui.label("● Đỏ: Lỗi/MITM").classes("text-rose-600")
                        ui.label("● Tím: Đang chọn").classes("text-indigo-600")

                svg_holder = ui.html(build_svg(), sanitize=False).classes("w-full")

            # CỘT PHẢI: INSPECTOR PANEL
            with ui.card().classes("flex-1 min-w-[290px] p-3.5 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col justify-between"):
                with ui.column().classes("w-full gap-2"):
                    with ui.row().classes("w-full items-center justify-between border-b border-slate-100 pb-2"):
                        with ui.column().classes("gap-0"):
                            lbl_ins_kind = ui.label("Khối dữ liệu").classes("text-[10px] font-bold uppercase tracking-wider text-indigo-600")
                            lbl_ins_title = ui.html("Bản rõ M", sanitize=False).classes("text-sm font-bold text-slate-900")
                        badge_ins_status = ui.badge("Sẵn sàng", color="indigo").classes("text-[10px]")

                    lbl_ins_desc = ui.html("", sanitize=False).classes("text-xs text-slate-600 leading-relaxed")

                    with ui.card().classes("w-full p-2 bg-slate-50 border border-slate-200 rounded-lg"):
                        ui.label("Cơ chế / Công thức").classes("text-[10px] font-bold uppercase text-slate-400")
                        lbl_ins_formula = ui.html("", sanitize=False).classes("text-[11px] font-mono font-semibold text-indigo-700 break-all")

                    with ui.card().classes("w-full p-2.5 bg-slate-900 text-slate-100 rounded-lg"):
                        ui.label("Dữ liệu thực tế (Live)").classes("text-[10px] font-bold uppercase text-emerald-400 mb-1")
                        lbl_ins_live = ui.html("", sanitize=False).classes("text-[11px] font-mono whitespace-pre-wrap break-all leading-relaxed")

                ui.label("Mẹo: Click trực tiếp lên bất kỳ mũi tên nào để xem dữ liệu truyền qua liên kết đó.").classes("text-[10px] text-slate-400 italic pt-2")

    # BẢNG CONSOLE RESIZABLE ĐÁY (GỌN NHẸ)
    with ui.card().classes(
        "fixed bottom-0 left-0 right-0 z-50 w-full max-w-7xl mx-auto px-3 pb-2 pt-1 bg-slate-900 text-white rounded-t-xl shadow-2xl border-t-2 border-indigo-500 transition-none"
    ).style("height: 155px; min-height: 110px; max-height: 580px;").props("id=resizable-terminal-panel"):
        with ui.element("div").classes("resize-bar").props("id=console-resize-handle title='Kéo để thay đổi chiều cao'"):
            ui.element("div").classes("resize-line")
        with ui.row().classes("items-center justify-between w-full pb-1 border-b border-slate-800"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("terminal", size="1rem").classes("text-emerald-400")
                ui.label("Nhật ký số học").classes("text-[11px] font-mono font-bold text-emerald-400 uppercase")
            lbl_exec_status = ui.label("Sẵn sàng. Click node/mũi tên để kiểm tra dữ liệu.").classes("text-[11px] font-mono text-slate-400")
        progress_bar = ui.linear_progress().props("indeterminate").classes("w-full my-0.5")
        progress_bar.set_visibility(False)
        with ui.scroll_area().classes("w-full pr-2").style("height: 90px;").props("id=math-log-scroll"):
            lbl_math_console = ui.label("\n".join(state["log_history"])).classes("text-[11px] font-mono text-slate-300 whitespace-pre-wrap leading-relaxed")

    refresh_ui()


# =========================================================================
# TRANG 2: CHI TIẾT TỪNG KHỐI THUẬT TOÁN (NỐI LIỀN DỮ LIỆU THẬT & KHÉP KÍN LUỒNG)
# =========================================================================
@ui.page("/algorithms")
def page_algorithms():
    setup_page_head()
    ui.query("body").style("padding-bottom: 3rem;")
    render_header("algorithms")

    alg_data = {
        "pub": None,
        "priv": None,
        "plaintext": None,
        "k_bytes": None,
        "iv": None,
        "c_data": None,
        "tag": None,
        "c_key": None,
        "recovered_k": None,
        "decrypted_msg": None,
        "error_msg": None,
        "active_stage": 1,
        "active_subnode": "rsa_pq",
        "stage_status": {1: "waiting", 2: "waiting", 3: "waiting", 4: "waiting", 5: "waiting"},
        "stage_details": {
            1: ("• n: 512 bits | p, q: 256 bits\n• e = 65537 | Miller-Rabin: k = 20", "Nhấn 'Chạy' để sinh cặp khóa RSA-512...", "Chưa có khóa..."),
            2: ("• Thông điệp M (UTF-8)\n• Khóa phiên K (128-bit): —", "Nhấn 'Chạy' để sinh K và mã hóa AES-GCM...", "Chưa có kết quả..."),
            3: ("• K (16B): (chưa có)\n• Public Key (e, n): (chưa có)", "Chờ nhận K từ Khối 2...", "Chưa có kết quả..."),
            4: ("• C_key: (chưa có)\n• Private Key (d, n): (chưa có)", "Chờ nhận C_key từ Khối 3...", "Chưa có kết quả..."),
            5: ("• K': (chưa có)\n• IV, C_data, Tag: (lấy từ Khối 2)", "Chờ nhận K' từ Khối 4...", "Chờ thực thi..."),
        },
    }

    STAGE_META = {
        1: {"num": "1", "title": "Sinh khóa RSA-512", "sub": "Bob • p, q, n, e, d", "color": "teal", "col_titles": ("THAM SỐ", "XỬ LÝ SỐ HỌC", "OUTPUT (e, n, d)")},
        2: {"num": "2", "title": "Mã hóa AES-128-GCM", "sub": "Alice • K, IV, C_data, Tag", "color": "blue", "col_titles": ("INPUT (M, K)", "XỬ LÝ CTR & GHASH", "OUTPUT (IV, C_data, Tag)")},
        3: {"num": "3", "title": "Mã hóa RSA (K → C_key)", "sub": "Alice • K^e mod n", "color": "indigo", "col_titles": ("INPUT (K, e, n)", "XỬ LÝ SỐ HỌC", "OUTPUT (C_key)")},
        4: {"num": "4", "title": "Giải mã RSA (C_key → K')", "sub": "Bob • (C_key)^d mod n", "color": "cyan", "col_titles": ("INPUT (C_key, d, n)", "XỬ LÝ (ĐỊNH LÝ EULER)", "OUTPUT (K')")},
        5: {"num": "5", "title": "Giải mã & GHASH (M')", "sub": "Bob • Verify Tag & CTR", "color": "emerald", "col_titles": ("INPUT (K', IV, C_data, Tag)", "KIỂM THỰC GHASH & CTR", "OUTPUT (M')")},
    }

    SUBNODE_INFO = {
        # RSA sub-nodes
        "rsa_pq": ("p, q (256-bit)", "Sinh hai số nguyên tố ngẫu nhiên 256-bit bằng kiểm tra xác suất Miller-Rabin (k=20)."),
        "rsa_n_phi": ("n, φ(n)", "Tính modulus n = p·q (512-bit) làm không gian số học và hàm Euler φ(n) = (p-1)(q-1)."),
        "rsa_ed": ("e = 65537, d", "Chọn số mũ công khai e = 65537 và tìm khóa bí mật d = e⁻¹ mod φ(n) bằng Euclid mở rộng."),
        "rsa_enc": ("C_key = K^e mod n", "Mã hóa khóa phiên K (128-bit < n) bằng lũy thừa module nhanh Square-and-Multiply."),
        "rsa_dec": ("K' = C_key^d mod n", "Dùng khóa bí mật d và định lý Euler để khôi phục chính xác khóa phiên K' ≡ K (mod n)."),
        # AES-128 SPN & GCM sub-nodes
        "AddRoundKey": ("AddRoundKey", "XOR trực tiếp ma trận State 4×4 với Round Key 128-bit sinh từ lịch khóa (Key Schedule)."),
        "SubBytes": ("SubBytes (S-Box)", "Thay thế phi tuyến từng byte qua bảng S-Box dựa trên nghịch đảo trong trường GF(2⁸)."),
        "ShiftRows": ("ShiftRows", "Dịch vòng trái các hàng 1, 2, 3 của ma trận State lần lượt 1, 2, 3 byte để khuếch tán ngang."),
        "MixColumns": ("MixColumns", "Nhân từng cột State với ma trận cố định trên GF(2⁸) tạo khuếch tán mạnh giữa các byte."),
        "J_0": ("J_0 (Initial Counter)", "Ghép Nonce/IV 96-bit với 31 bit 0 và 1 bit 1 (IV || 0³¹1) làm bộ đếm gốc tính Auth Tag."),
        "CB_i": ("CB_i (Counter Block)", "Tăng bộ đếm 32-bit cuối khối lên 1 cho mỗi khối bản rõ 128-bit (CB_i = inc₃₂(CB_{i-1}))."),
        "CTR": ("CTR XOR", "Mã hóa/giải mã luồng bằng cách XOR bản rõ P_i với khối khóa AES_K(CB_i) mà không cần padding."),
        "GHASH": ("GHASH GF(2¹²⁸)", "Nhân dồn Horner bản mã C_data và độ dài trên trường Galois GF(2¹²⁸) với khóa H = AES_K(0¹²⁸)."),
        "Tag": ("Auth Tag (16B)", "XOR kết quả GHASH cuối cùng X_m với AES_K(J_0) để tạo thẻ xác thực toàn vẹn 128-bit."),
    }

    def _short_hex(b: bytes | None, limit: int = 24) -> str:
        if not b:
            return "—"
        h = b.hex()
        return h if len(h) <= limit else f"{h[:limit]}… ({len(b)}B)"

    def _short_int(val: int | None, limit: int = 22) -> str:
        if val is None:
            return "—"
        s = str(val)
        return s if len(s) <= limit else f"{s[:limit]}… ({val.bit_length()}b)"

    def get_subnode_live_value(nid: str) -> str:
        if nid == "rsa_pq":
            return "p, q: 256-bit primes (đã sinh)" if alg_data["pub"] else "Chưa sinh p, q"
        if nid == "rsa_n_phi":
            return f"n = {_short_int(alg_data['pub'][1])}" if alg_data["pub"] else "n = (chưa có)"
        if nid == "rsa_ed":
            if alg_data["pub"] and alg_data["priv"]:
                return f"e = {alg_data['pub'][0]} | d = {_short_int(alg_data['priv'][0])}"
            return "e = 65537 | d = (chưa có)"
        if nid == "rsa_enc":
            return f"C_key = 0x{alg_data['c_key']:x}"[:42] + ("…" if alg_data["c_key"] and len(f"0x{alg_data['c_key']:x}") > 40 else "") if alg_data["c_key"] else "C_key = (chưa có)"
        if nid == "rsa_dec":
            return f"K' = {_short_hex(alg_data['recovered_k'], 32)}" if alg_data["recovered_k"] else "K' = (chưa có)"
        if nid in ("AddRoundKey", "SubBytes", "ShiftRows", "MixColumns"):
            return f"K = {_short_hex(alg_data['k_bytes'], 32)}"
        if nid in ("J_0", "CB_i"):
            return f"IV = {_short_hex(alg_data['iv'], 24)}"
        if nid == "CTR":
            if alg_data["active_stage"] == 5 and alg_data["decrypted_msg"] is not None:
                return f"M' = \"{alg_data['decrypted_msg']}\" | C_data = {_short_hex(alg_data['c_data'], 20)}"
            return f"C_data = {_short_hex(alg_data['c_data'], 24)}"
        if nid in ("GHASH", "Tag"):
            return f"Tag = {_short_hex(alg_data['tag'], 32)}"
        return "—"

    def build_rsa_sub_svg() -> str:
        stage = alg_data["active_stage"]
        sel = alg_data["active_subnode"]
        nodes = [
            ("rsa_pq", 14, "p, q (256-bit)", "Miller-Rabin k=20", stage == 1),
            ("rsa_n_phi", 184, "n, φ(n)", "n=p·q | (p-1)(q-1)", stage == 1),
            ("rsa_ed", 354, "e = 65537, d", "Euclid mở rộng", stage == 1),
            ("rsa_enc", 524, "C_key = K^e mod n", "Mã hóa khóa K", stage == 3),
            ("rsa_dec", 694, "K' = C_key^d mod n", "Khôi phục khóa K'", stage == 4),
        ]
        arrows = [(164, 184), (334, 354), (504, 524), (674, 694)]
        parts = [
            '<svg viewBox="0 0 860 116" class="w-full h-auto select-none">',
            '<defs><marker id="alg-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            '<path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b"/></marker></defs>',
        ]
        for x1, x2 in arrows:
            parts.append(f'<line x1="{x1}" y1="58" x2="{x2 - 2}" y2="58" stroke="#94a3b8" stroke-width="2" marker-end="url(#alg-arr)"/>')
        for nid, x, title, sub, is_stage_hl in nodes:
            is_sel = (nid == sel)
            fill = "#eef2ff" if is_sel else ("#f0fdfa" if is_stage_hl else "#ffffff")
            stroke = "#4f46e5" if is_sel else ("#0d9488" if is_stage_hl else "#cbd5e1")
            sw = "2.5" if is_sel else ("2" if is_stage_hl else "1.2")
            t_col = "#312e81" if is_sel else "#0f172a"
            parts.append(
                f'<g class="svg-node" onclick="emitEvent(\'alg_node_select\', \'{nid}\')">'
                f'<rect x="{x}" y="22" width="150" height="72" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
                f'<text x="{x + 75}" y="50" text-anchor="middle" font-size="12" font-weight="700" fill="{t_col}">{format_math_svg(title)}</text>'
                f'<text x="{x + 75}" y="70" text-anchor="middle" font-size="10" fill="#475569">{format_math_svg(sub)}</text>'
                f'</g>'
            )
        parts.append("</svg>")
        return "".join(parts)

    def build_aes_sub_svg() -> str:
        sel = alg_data["active_subnode"]
        spn_nodes = [
            ("AddRoundKey", 14, "AddRoundKey", "XOR RoundKey"),
            ("SubBytes", 184, "SubBytes", "S-Box 8-bit"),
            ("ShiftRows", 354, "ShiftRows", "Dịch vòng hàng"),
            ("MixColumns", 524, "MixColumns", "Ma trận GF(2⁸)"),
            ("AddRoundKey", 694, "AddRoundKey (R10)", "XOR Key cuối"),
        ]
        gcm_nodes = [
            ("J_0", 14, "J_0", "IV || 0³¹1"),
            ("CB_i", 184, "CB_i", "Counter tăng dần"),
            ("CTR", 354, "CTR XOR", "P_i ⊕ AES_K(CB_i)"),
            ("GHASH", 524, "GHASH GF(2¹²⁸)", "Nhân Horner"),
            ("Tag", 694, "Auth Tag (16B)", "X_m ⊕ AES_K(J_0)"),
        ]
        parts = [
            '<svg viewBox="0 0 860 194" class="w-full h-auto select-none">',
            '<defs><marker id="alg-arr2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            '<path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b"/></marker></defs>',
            '<text x="14" y="14" font-size="10" font-weight="700" fill="#1d4ed8">AES-128 SPN (10 Vòng)</text>',
            '<text x="14" y="106" font-size="10" font-weight="700" fill="#047857">GCM Mode (CTR + Xác thực GHASH)</text>',
        ]
        for row_y, row_nodes, hl_stroke, hl_fill in [
            (22, spn_nodes, "#2563eb", "#eff6ff"),
            (114, gcm_nodes, "#059669", "#ecfdf5"),
        ]:
            for x1, x2 in [(164, 184), (334, 354), (504, 524), (674, 694)]:
                parts.append(f'<line x1="{x1}" y1="{row_y + 32}" x2="{x2 - 2}" y2="{row_y + 32}" stroke="#94a3b8" stroke-width="2" marker-end="url(#alg-arr2)"/>')
            for nid, x, title, sub in row_nodes:
                is_sel = (nid == sel)
                fill = hl_fill if is_sel else "#ffffff"
                stroke = hl_stroke if is_sel else "#cbd5e1"
                sw = "2.5" if is_sel else "1.2"
                parts.append(
                    f'<g class="svg-node" onclick="emitEvent(\'alg_node_select\', \'{nid}\')">'
                    f'<rect x="{x}" y="{row_y}" width="150" height="64" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
                    f'<text x="{x + 75}" y="{row_y + 27}" text-anchor="middle" font-size="12" font-weight="700" fill="#0f172a">{format_math_svg(title)}</text>'
                    f'<text x="{x + 75}" y="{row_y + 46}" text-anchor="middle" font-size="10" fill="#475569">{format_math_svg(sub)}</text>'
                    f'</g>'
                )
        parts.append("</svg>")
        return "".join(parts)

    def refresh_ui():
        # Update 5 pipeline stage cards
        for sid in range(1, 6):
            st = alg_data["stage_status"][sid]
            is_active = (alg_data["active_stage"] == sid)
            color = STAGE_META[sid]["color"]
            ring = f"border-2 border-{color}-600 ring-2 ring-{color}-100 bg-{color}-50/40" if is_active else "border border-slate-200 bg-white hover:border-slate-300"
            stage_cards[sid].classes(replace=f"p-2.5 rounded-xl cursor-pointer transition-all shadow-sm {ring}")

            badge = stage_badges[sid]
            if st == "done":
                badge.set_text("✓ Xong")
                badge.props("color=emerald")
            elif st == "error":
                badge.set_text("✗ Lỗi")
                badge.props("color=rose")
            else:
                badge.set_text("Chờ")
                badge.props("color=slate")

        # Update detail header & 3 columns
        sid = alg_data["active_stage"]
        meta = STAGE_META[sid]
        in_txt, proc_txt, out_txt = alg_data["stage_details"][sid]
        c1, c2, c3 = meta["col_titles"]

        lbl_detail_title.set_content(format_math_html(f"Khối {meta['num']}: {meta['title']}"))
        lbl_detail_sub.set_content(format_math_html(meta["sub"]))
        lbl_col1_title.set_content(format_math_html(c1))
        lbl_col2_title.set_content(format_math_html(c2))
        lbl_col3_title.set_content(format_math_html(c3))
        txt_col1.set_content(format_math_html(in_txt))
        txt_col2.set_content(format_math_html(proc_txt))
        txt_col3.set_content(format_math_html(out_txt))

        # Update interactive SVG sub-diagram
        is_rsa = sid in (1, 3, 4)
        if is_rsa and alg_data["active_subnode"] not in ("rsa_pq", "rsa_n_phi", "rsa_ed", "rsa_enc", "rsa_dec"):
            alg_data["active_subnode"] = {1: "rsa_pq", 3: "rsa_enc", 4: "rsa_dec"}[sid]
        elif not is_rsa and alg_data["active_subnode"] in ("rsa_pq", "rsa_n_phi", "rsa_ed", "rsa_enc", "rsa_dec"):
            alg_data["active_subnode"] = "SubBytes" if sid == 2 else "GHASH"

        lbl_sub_title.set_text("Sơ đồ số học RSA-512 (click khối để xem)" if is_rsa else "Sơ đồ nội bộ AES-128 SPN & GCM (click khối để xem)")
        svg_sub_holder.set_content(build_rsa_sub_svg() if is_rsa else build_aes_sub_svg())

        sub_id = alg_data["active_subnode"]
        s_title, s_desc = SUBNODE_INFO.get(sub_id, ("—", ""))
        lbl_subnode_name.set_content(format_math_html(s_title))
        lbl_subnode_desc.set_content(format_math_html(s_desc))
        lbl_subnode_live.set_content(format_math_html(get_subnode_live_value(sub_id)))

        # Live summary strip for AES-GCM stages
        if is_rsa:
            live_aes_strip.set_visibility(False)
        else:
            live_aes_strip.set_visibility(True)
            lbl_live_k.set_text(_short_hex(alg_data["k_bytes"], 32))
            lbl_live_iv.set_text(_short_hex(alg_data["iv"], 24))
            lbl_live_c.set_text(_short_hex(alg_data["c_data"], 24))
            lbl_live_tag.set_text(_short_hex(alg_data["tag"], 32))
            lbl_live_m_out.set_text(f"\"{alg_data['decrypted_msg']}\"" if alg_data["decrypted_msg"] is not None else "—")

    def select_stage(sid: int):
        alg_data["active_stage"] = sid
        if sid in (1, 3, 4):
            alg_data["active_subnode"] = {1: "rsa_pq", 3: "rsa_enc", 4: "rsa_dec"}[sid]
        else:
            alg_data["active_subnode"] = "SubBytes" if sid == 2 else "GHASH"
        refresh_ui()

    def handle_alg_node_select(e):
        nid = e.args
        if nid in SUBNODE_INFO:
            alg_data["active_subnode"] = nid
            refresh_ui()

    ui.on("alg_node_select", handle_alg_node_select)

    def execute_rsa_keygen(silent=False):
        pub, priv = generate_rsa_keys(bits=512)
        alg_data["pub"] = pub
        alg_data["priv"] = priv
        e_val, n_val = pub
        d_val, _ = priv

        alg_data["stage_details"][1] = (
            "• n: 512 bits | p, q: 256 bits\n• e = 65537 | Miller-Rabin: k = 20",
            f"1. Sinh p, q (256-bit) qua Miller-Rabin (k=20)\n"
            f"2. Tính Modulus: n = p * q (512-bit)\n"
            f"3. Hàm Euler: phi(n) = (p - 1)(q - 1)\n"
            f"4. Chọn Fermat e = {e_val} (gcd(e, phi(n)) = 1)\n"
            f"5. Euclid mở rộng tìm d: e*d ≡ 1 mod phi(n)",
            f"• Public Key (e, n):\n  e = {e_val}\n  n = {n_val}\n\n"
            f"• Private Key (d, n):\n  d = {d_val}",
        )
        # Update downstream input previews
        k_hex = alg_data["k_bytes"].hex() if alg_data["k_bytes"] else "(chưa có)"
        k_int = str(int.from_bytes(alg_data["k_bytes"], "big")) if alg_data["k_bytes"] else "(chưa có)"
        alg_data["stage_details"][3] = (
            f"• K (Hex): {k_hex}\n• K (Int): {k_int}\n• Pub (e, n): e={e_val}, n={n_val}",
            alg_data["stage_details"][3][1],
            alg_data["stage_details"][3][2],
        )
        ck_hex = f"0x{alg_data['c_key']:x}" if alg_data["c_key"] else "(chưa có)"
        alg_data["stage_details"][4] = (
            f"• C_key: {ck_hex}\n• Priv (d, n): d={d_val}, n={n_val}",
            alg_data["stage_details"][4][1],
            alg_data["stage_details"][4][2],
        )
        alg_data["stage_status"][1] = "done"
        if not silent:
            alg_data["active_stage"] = 1
            alg_data["active_subnode"] = "rsa_pq"
            notify("Đã sinh cặp khóa RSA-512", "teal")
        refresh_ui()

    def execute_aes_gcm(silent=False):
        msg = inp_aes_msg.value.strip()
        if not msg:
            notify("Vui lòng nhập thông điệp M", "amber")
            return False

        k_bytes = os.urandom(16)
        alg_data["plaintext"] = msg
        alg_data["k_bytes"] = k_bytes
        m_bytes = msg.encode("utf-8")

        c_data, iv, tag = aes_gcm_encrypt(k_bytes, m_bytes)
        alg_data["c_data"] = c_data
        alg_data["iv"] = iv
        alg_data["tag"] = tag

        alg_data["stage_details"][2] = (
            f"• Thông điệp M ({len(m_bytes)}B):\n  \"{msg}\"\n\n• Khóa phiên K (128-bit):\n  {k_bytes.hex()}",
            f"1. Sinh khóa phiên K 128-bit (16B) bằng CSPRNG\n"
            f"2. Sinh Nonce / IV 12 bytes (96-bit)\n"
            f"3. Mã hóa CTR Mode: C_i = P_i ⊕ AES_K(CB_i)\n"
            f"4. Nhân Horner trên GF(2^128) sinh Auth Tag (16B)",
            f"• Khóa phiên K (16B):\n  {k_bytes.hex()}\n\n"
            f"• Nonce / IV (12B):\n  {iv.hex()}\n\n"
            f"• C_data ({len(c_data)}B):\n  {c_data.hex()}\n\n"
            f"• Auth Tag (16B):\n  {tag.hex()}",
        )

        k_int = int.from_bytes(k_bytes, "big")
        pub_str = f"e={alg_data['pub'][0]}, n={alg_data['pub'][1]}" if alg_data["pub"] else "(chưa có)"
        alg_data["stage_details"][3] = (
            f"• K (Hex): {k_bytes.hex()}\n• K (Int): {k_int}\n• Pub (e, n): {pub_str}",
            alg_data["stage_details"][3][1],
            alg_data["stage_details"][3][2],
        )
        rec_k = alg_data["recovered_k"].hex() if alg_data["recovered_k"] else "(chưa có)"
        alg_data["stage_details"][5] = (
            f"• K': {rec_k}\n• IV: {iv.hex()}\n• C_data ({len(c_data)}B): {c_data.hex()}\n• Tag: {tag.hex()}",
            alg_data["stage_details"][5][1],
            alg_data["stage_details"][5][2],
        )
        alg_data["stage_status"][2] = "done"
        if not silent:
            alg_data["active_stage"] = 2
            alg_data["active_subnode"] = "SubBytes"
            notify("AES-GCM: Đã sinh K và mã hóa thông điệp", "blue")
        refresh_ui()
        return True

    def execute_rsa_enc(silent=False):
        if not alg_data["k_bytes"]:
            notify("Chạy Khối 2 để có K trước", "amber")
            return False
        if not alg_data["pub"]:
            notify("Chạy Khối 1 để có Public Key trước", "amber")
            return False

        e_val, n_val = alg_data["pub"]
        k_int = int.from_bytes(alg_data["k_bytes"], "big")
        if k_int >= n_val:
            notify("Lỗi: K >= n", "red")
            return False

        c_key = rsa_encrypt(alg_data["pub"], k_int)
        alg_data["c_key"] = c_key

        e_bin = bin(e_val)[2:]
        alg_data["stage_details"][3] = (
            f"• K (Hex): {alg_data['k_bytes'].hex()}\n• K (Int): {k_int}\n• Pub (e, n): e={e_val}, n={n_val}",
            f"1. Chuyển K (16B) thành số nguyên: K = {k_int}\n"
            f"2. Kiểm tra K < n ({k_int < n_val})\n"
            f"3. Nhị phân e = {e_val}: {e_bin}\n"
            f"4. Square-and-Multiply: C_key = K^e mod n",
            f"• C_key (Hex):\n  0x{c_key:x}\n\n"
            f"• C_key (Dec):\n  {c_key}",
        )
        d_str = f"d={alg_data['priv'][0]}, n={alg_data['priv'][1]}" if alg_data["priv"] else "(chưa có)"
        alg_data["stage_details"][4] = (
            f"• C_key: 0x{c_key:x}\n• Priv (d, n): {d_str}",
            alg_data["stage_details"][4][1],
            alg_data["stage_details"][4][2],
        )
        alg_data["stage_status"][3] = "done"
        if not silent:
            alg_data["active_stage"] = 3
            alg_data["active_subnode"] = "rsa_enc"
            notify("RSA: Đã mã hóa khóa K thành C_key", "indigo")
        refresh_ui()
        return True

    def execute_rsa_dec(silent=False):
        if not alg_data["c_key"] or not alg_data["priv"]:
            notify("Cần C_key và Private Key trước", "amber")
            return False

        d_val, n_val = alg_data["priv"]
        c_key = alg_data["c_key"]

        k_rec_int = rsa_decrypt(alg_data["priv"], c_key)
        k_rec_bytes = k_rec_int.to_bytes(16, "big")
        alg_data["recovered_k"] = k_rec_bytes

        is_matched = (k_rec_bytes == alg_data["k_bytes"])
        alg_data["stage_details"][4] = (
            f"• C_key: 0x{c_key:x}\n• Priv (d, n): d={d_val}, n={n_val}",
            f"1. Nạp C_key: 0x{c_key:x}\n"
            f"2. Nạp Private Key d: {d_val}\n"
            f"3. Định lý Euler: K' = (C_key)^d mod n ≡ K mod n\n"
            f"4. Chuyển K' về 16 bytes AES",
            f"• K' khôi phục (16B):\n  {k_rec_bytes.hex()}\n\n"
            f"• K gốc:\n  {alg_data['k_bytes'].hex()}\n\n"
            f"• Đối chiếu: {'✓ TRÙNG KHỚP' if is_matched else '✗ THẤT BẠI'}",
        )
        iv_hex = alg_data["iv"].hex() if alg_data["iv"] else "—"
        cd_hex = alg_data["c_data"].hex() if alg_data["c_data"] else "—"
        tg_hex = alg_data["tag"].hex() if alg_data["tag"] else "—"
        alg_data["stage_details"][5] = (
            f"• K': {k_rec_bytes.hex()}\n• IV: {iv_hex}\n• C_data: {cd_hex}\n• Tag: {tg_hex}",
            alg_data["stage_details"][5][1],
            alg_data["stage_details"][5][2],
        )
        alg_data["stage_status"][4] = "done" if is_matched else "error"
        if not silent:
            alg_data["active_stage"] = 4
            alg_data["active_subnode"] = "rsa_dec"
            notify("RSA Dec: Đã khôi phục khóa K'", "teal")
        refresh_ui()
        return True

    def execute_aes_dec(silent=False):
        if not alg_data["recovered_k"] or not alg_data["c_data"]:
            notify("Cần K' và dữ liệu từ Khối 2 trước", "amber")
            return False

        in_k5 = (
            f"• K': {alg_data['recovered_k'].hex()}\n"
            f"• IV: {alg_data['iv'].hex()}\n"
            f"• C_data ({len(alg_data['c_data'])}B): {alg_data['c_data'].hex()}\n"
            f"• Tag: {alg_data['tag'].hex()}"
        )
        try:
            pt_bytes = aes_gcm_decrypt(
                session_key=alg_data["recovered_k"],
                nonce_bytes=alg_data["iv"],
                ciphertext_bytes=alg_data["c_data"],
                auth_tag_bytes=alg_data["tag"],
            )
            msg_recovered = pt_bytes.decode("utf-8")
            alg_data["decrypted_msg"] = msg_recovered
            alg_data["error_msg"] = None

            alg_data["stage_details"][5] = (
                in_k5,
                f"1. Nạp K' từ Khối 4 và (IV, C_data, Tag) từ Khối 2\n"
                f"2. Xác thực GHASH trên GF(2^128): Tag khớp!\n"
                f"3. Giải mã CTR: P_i = C_i ⊕ AES_K'(CB_i)\n"
                f"4. Giải mã UTF-8 thành chuỗi M'",
                f"• Bản rõ khôi phục M':\n  \"{msg_recovered}\"\n\n"
                f"• Bản rõ gốc M:\n  \"{alg_data['plaintext']}\"\n\n"
                f"✓ KHÔI PHỤC CHÍNH XÁC (M' == M)",
            )
            alg_data["stage_status"][5] = "done"
            if not silent:
                alg_data["active_stage"] = 5
                alg_data["active_subnode"] = "GHASH"
                notify("Đã khôi phục trọn vẹn thông điệp gốc!", "emerald")
            refresh_ui()
            return True

        except Exception as e:
            alg_data["decrypted_msg"] = None
            alg_data["error_msg"] = str(e)
            alg_data["stage_details"][5] = (
                in_k5,
                f"Lỗi xác thực hoặc giải mã: {e}",
                f"✗ Thất bại: {e}",
            )
            alg_data["stage_status"][5] = "error"
            if not silent:
                alg_data["active_stage"] = 5
                alg_data["active_subnode"] = "GHASH"
                notify(f"Lỗi: {e}", "red")
            refresh_ui()
            return False

    async def run_all_blocks():
        btn_run_all.props("loading")
        execute_rsa_keygen(silent=True)
        await asyncio.sleep(0.15)
        if not execute_aes_gcm(silent=True):
            btn_run_all.props(remove="loading")
            return
        await asyncio.sleep(0.15)
        if not execute_rsa_enc(silent=True):
            btn_run_all.props(remove="loading")
            return
        await asyncio.sleep(0.15)
        if not execute_rsa_dec(silent=True):
            btn_run_all.props(remove="loading")
            return
        await asyncio.sleep(0.15)
        execute_aes_dec(silent=True)
        btn_run_all.props(remove="loading")
        alg_data["active_stage"] = 5
        alg_data["active_subnode"] = "GHASH"
        refresh_ui()
        notify("Đã hoàn tất toàn bộ 5 khối!", "emerald")

    def reset_blocks():
        for key in ("plaintext", "k_bytes", "iv", "c_data", "tag", "c_key", "recovered_k", "decrypted_msg", "error_msg"):
            alg_data[key] = None
        for sid in range(2, 6):
            alg_data["stage_status"][sid] = "waiting"
        alg_data["stage_details"][2] = ("• Thông điệp M (UTF-8)\n• Khóa phiên K (128-bit): —", "Nhấn 'Chạy' để sinh K và mã hóa AES-GCM...", "Chưa có kết quả...")
        alg_data["stage_details"][3] = ("• K (16B): (chưa có)\n• Public Key (e, n): (chưa có)", "Chờ nhận K từ Khối 2...", "Chưa có kết quả...")
        alg_data["stage_details"][4] = ("• C_key: (chưa có)\n• Private Key (d, n): (chưa có)", "Chờ nhận C_key từ Khối 3...", "Chưa có kết quả...")
        alg_data["stage_details"][5] = ("• K': (chưa có)\n• IV, C_data, Tag: (lấy từ Khối 2)", "Chờ nhận K' từ Khối 4...", "Chờ thực thi...")
        alg_data["active_stage"] = 1
        alg_data["active_subnode"] = "rsa_pq"
        execute_rsa_keygen(silent=True)
        notify("Đã làm mới dữ liệu các khối", "blue")

    STAGE_RUNNERS = {
        1: lambda: execute_rsa_keygen(),
        2: lambda: execute_aes_gcm(),
        3: lambda: execute_rsa_enc(),
        4: lambda: execute_rsa_dec(),
        5: lambda: execute_aes_dec(),
    }

    with ui.column().classes("w-full max-w-6xl mx-auto p-4 gap-3"):
        # 1. TOP CONTROL BAR
        with ui.card().classes("w-full p-3.5 bg-white rounded-xl shadow-sm border border-slate-200"):
            with ui.row().classes("items-center justify-between w-full flex-wrap gap-2 pb-2 border-b border-slate-100"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("tune", size="1.4rem").classes("text-indigo-600")
                    with ui.column().classes("gap-0"):
                        ui.label("Pipeline 5 Khối Thuật Toán & Sơ Đồ Nội Bộ").classes("text-base font-bold text-slate-800")
                        ui.label("Click từng khối trên pipeline để kiểm tra dữ liệu & sơ đồ toán học bên trong").classes("text-xs text-slate-500")
                with ui.row().classes("items-center gap-2"):
                    btn_run_all = ui.button("▶ Chạy tất cả", on_click=run_all_blocks).classes("bg-indigo-600 text-white text-xs font-semibold px-3 py-1.5 rounded-lg")
                    ui.button("↺ Làm mới", on_click=reset_blocks).classes("bg-slate-700 text-white text-xs px-3 py-1.5 rounded-lg")
                    ui.button("← Về sơ đồ chính", on_click=lambda: ui.navigate.to("/")).classes("bg-slate-800 text-white text-xs px-3 py-1.5 rounded-lg")

            with ui.row().classes("w-full items-center gap-2 pt-2 flex-wrap"):
                ui.label("Thông điệp M:").classes("text-xs font-semibold text-slate-600")
                inp_aes_msg = ui.input(value="Hello cô Hạnh").classes("flex-1 min-w-[240px] text-xs font-medium").props("outlined dense")
                ui.button("Mẫu: Hello cô Hạnh", on_click=lambda: inp_aes_msg.set_value("Hello cô Hạnh")).props("flat dense").classes("text-xs text-indigo-600")
                ui.button("Mẫu: Nhóm 7", on_click=lambda: inp_aes_msg.set_value("Xin chào Cô Hạnh, bọn em là nhóm 7")).props("flat dense").classes("text-xs text-indigo-600")

        # 2. 5-STAGE INTERACTIVE PIPELINE BAR
        stage_cards = {}
        stage_badges = {}
        with ui.grid(columns=5).classes("w-full gap-2"):
            for sid in range(1, 6):
                meta = STAGE_META[sid]
                color = meta["color"]
                card = ui.card().classes("p-2.5 rounded-xl cursor-pointer transition-all shadow-sm border border-slate-200 bg-white")
                card.on("click", lambda _, s=sid: select_stage(s))
                stage_cards[sid] = card
                with card:
                    with ui.row().classes("items-center justify-between w-full"):
                        ui.label(meta["num"]).classes(f"w-5 h-5 rounded-full bg-{color}-600 text-white flex items-center justify-center text-[11px] font-bold")
                        stage_badges[sid] = ui.badge("Chờ", color="slate").classes("text-[10px]")
                    ui.html(format_math_html(meta["title"]), sanitize=False).classes("text-xs font-bold text-slate-800 mt-1.5 leading-tight")
                    ui.html(format_math_html(meta["sub"]), sanitize=False).classes("text-[10px] text-slate-500 truncate w-full")
                    btn = ui.button("▶ Chạy", on_click=STAGE_RUNNERS[sid]).props("flat dense").classes(f"text-[11px] font-semibold text-{color}-700 mt-1 px-1.5 py-0.5 rounded bg-{color}-50 hover:bg-{color}-100")
                    btn.on("click.stop", lambda: None)

        # 3. STAGE DETAIL + INTERACTIVE SVG SUB-DIAGRAM
        with ui.card().classes("w-full p-4 bg-white rounded-xl shadow-sm border border-slate-200 gap-3"):
            with ui.row().classes("items-center justify-between w-full pb-2 border-b border-slate-100 flex-wrap gap-2"):
                with ui.column().classes("gap-0"):
                    lbl_detail_title = ui.html("Khối 1: Sinh khóa RSA-512", sanitize=False).classes("text-sm font-bold text-slate-800")
                    lbl_detail_sub = ui.html("Bob • p, q, n, e, d", sanitize=False).classes("text-xs text-slate-500")
                ui.button("▶ Chạy khối đang xem", on_click=lambda: STAGE_RUNNERS[alg_data["active_stage"]]()).classes("bg-indigo-600 text-white text-xs font-semibold px-3 py-1 rounded-lg")

            # Interactive SVG Sub-Diagram + 1-sentence Inspector
            with ui.card().classes("w-full p-3 dot-grid-bg rounded-xl border border-slate-200 gap-2"):
                lbl_sub_title = ui.label("Sơ đồ số học RSA-512").classes("text-xs font-bold text-slate-700")
                svg_sub_holder = ui.html("", sanitize=False).classes("w-full")

                with ui.row().classes("w-full items-center justify-between bg-white/95 rounded-lg border border-slate-200 px-3 py-2 gap-3 flex-wrap"):
                    with ui.column().classes("gap-0.5 flex-1 min-w-[260px]"):
                        lbl_subnode_name = ui.html("—", sanitize=False).classes("text-xs font-bold text-indigo-700")
                        lbl_subnode_desc = ui.html("—", sanitize=False).classes("text-xs text-slate-600")
                    lbl_subnode_live = ui.html("—", sanitize=False).classes("text-[11px] font-mono text-slate-800 bg-slate-100 px-2.5 py-1 rounded border border-slate-200 break-all max-w-full")

                live_aes_strip = ui.row().classes("w-full gap-2 flex-wrap pt-1")
                with live_aes_strip:
                    for lbl_name, ref_holder in [
                        ("K:", "k"), ("IV:", "iv"), ("C_data:", "c"), ("Tag:", "tag"), ("M':", "m_out")
                    ]:
                        with ui.row().classes("items-center gap-1 bg-white px-2 py-1 rounded border border-slate-200"):
                            ui.html(format_math_html(lbl_name), sanitize=False).classes("text-[10px] font-bold text-slate-500")
                            lbl_val = ui.label("—").classes("text-[10px] font-mono text-slate-800 break-all")
                            if ref_holder == "k":
                                lbl_live_k = lbl_val
                            elif ref_holder == "iv":
                                lbl_live_iv = lbl_val
                            elif ref_holder == "c":
                                lbl_live_c = lbl_val
                            elif ref_holder == "tag":
                                lbl_live_tag = lbl_val
                            else:
                                lbl_live_m_out = lbl_val

            # Compact 3-Column Inspector (Input | Arithmetic/Crypto Process | Output)
            with ui.grid(columns=3).classes("w-full gap-3 items-stretch"):
                with ui.card().classes("p-3 bg-slate-50 rounded-lg border border-slate-200"):
                    lbl_col1_title = ui.html("INPUT", sanitize=False).classes("text-[11px] font-bold text-slate-600 uppercase border-b pb-1")
                    txt_col1 = ui.html("", sanitize=False).classes("text-xs font-mono text-slate-700 whitespace-pre-wrap break-all mt-2 max-h-48 overflow-y-auto")
                with ui.card().classes("p-3 bg-indigo-50/40 rounded-lg border border-indigo-200"):
                    lbl_col2_title = ui.html("XỬ LÝ", sanitize=False).classes("text-[11px] font-bold text-indigo-800 uppercase border-b border-indigo-200 pb-1")
                    txt_col2 = ui.html("", sanitize=False).classes("text-xs font-mono text-slate-700 whitespace-pre-wrap break-all mt-2 max-h-48 overflow-y-auto")
                with ui.card().classes("p-3 bg-emerald-50/40 rounded-lg border border-emerald-200"):
                    lbl_col3_title = ui.html("OUTPUT", sanitize=False).classes("text-[11px] font-bold text-emerald-800 uppercase border-b border-emerald-200 pb-1")
                    txt_col3 = ui.html("", sanitize=False).classes("text-xs font-mono text-slate-800 whitespace-pre-wrap break-all mt-2 max-h-48 overflow-y-auto")

    execute_rsa_keygen(silent=True)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="PGP Hybrid Simulator & Algorithms", port=8080, reload=False, show=False)
