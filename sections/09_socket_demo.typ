#import "../styles.typ": report-table
#import "../components.typ": info-box
#import "../figures.typ": fig-socket-sequence

= Mô phỏng truyền thông PGP Hybrid qua Socket TCP

Các chương trước đã kiểm chứng mô hình mã hóa lai trong phạm vi một tiến trình duy nhất (`src/hybrid_demo.py`). Để tiến gần hơn tới bài toán thực tế của môn học Mạng máy tính, nhóm bổ sung một bản demo truyền thông qua giao thức *TCP Socket*, trong đó Alice và Bob có thể chạy trên hai máy tính khác nhau trong cùng mạng LAN.

== Kiến trúc chương trình

Mã nguồn được tách thành 3 tệp độc lập trong thư mục `PGP_RSA_AES_Socket_3_files/`:

#align(center)[
  #report-table(
    columns: (1.1fr, 2fr),
    headers: ("Tệp nguồn", "Vai trò"),
    rows: (
      ([`server_bob.py`], [Máy B — TCP Server: sinh cặp khóa RSA bằng `algorithms/rsa.py`, lắng nghe tại `0.0.0.0:5000`, nhận gói tin và giải mã.]),
      ([`client_alice.py`], [Máy A — TCP Client: lấy Public Key của Bob, gọi `encrypt_message`, gửi gói tin qua TCP và hiển thị phản hồi.]),
      ([`pgp_crypto.py`], [Cầu nối dữ liệu: chuyển đổi giữa cấu trúc JSON/Base64 trên đường truyền và các hàm thuần Python trong `algorithms/hybrid_pgp.py`.]),
    )
  )
]

Cả hai phía đều import trực tiếp gói `algorithms` của nhóm, nhờ đó toàn bộ thuật toán Euclid mở rộng, RSA và AES-GCM chỉ tồn tại ở một nơi duy nhất, tránh sai lệch giữa bản demo cục bộ và bản chạy qua mạng.

== Đóng gói và truyền nhận gói tin

TCP là giao thức luồng byte (byte stream), không bảo toàn ranh giới thông điệp. Vì vậy chương trình áp dụng cơ chế *length-prefixed framing*: mỗi gói tin được gửi kèm 4 byte độ dài ở đầu, theo thứ tự Big-Endian.

```python
def send_json(connection, payload_dict):
    data = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")
    connection.sendall(struct.pack("!I", len(data)) + data)

def receive_json(connection):
    packet_length = struct.unpack("!I", recv_exact(connection, 4))[0]
    if not 0 < packet_length <= MAX_PACKET:
        raise ValueError("Kích thước gói tin không hợp lệ.")
    packet = recv_exact(connection, packet_length)
    return json.loads(packet.decode("utf-8"))
```

Hàm `recv_exact` lặp `recv()` cho tới khi đọc đủ số byte yêu cầu, khắc phục hiện tượng một lần `recv()` chỉ trả về một phần dữ liệu. Các trường nhị phân (`nonce`, `ciphertext`, `auth_tag`) được mã hóa Base64, còn `enc_session_key` được biểu diễn dạng chuỗi hex vì là số nguyên lớn. Gói tin bị giới hạn tối đa 1 MB và mỗi kết nối có timeout 15 giây.

== Bắt tay và xác thực Public Key

Trước khi gửi dữ liệu, Alice cần Public Key $(e_B, n)$ của Bob. Chương trình hỗ trợ hai đường lấy khóa:

1. *Đọc từ tệp cục bộ* `bob_public.json` nếu đã được sao chép từ máy Bob.
2. *Tải tự động qua mạng*: Alice gửi yêu cầu `{"action": "GET_PUBLIC_KEY"}`, Bob phản hồi `{"e": ..., "n": ...}`, Alice lưu lại thành tệp cho các lần sau.

Sau khi có khóa, cả hai máy in ra *mã băm SHA-256* của Public Key:

```python
def fingerprint(public_key):
    e, n = public_key
    return hashlib.sha256(f"RSA:{e}:{n}".encode("ascii")).hexdigest()
```

Người dùng đối chiếu trực tiếp hai chuỗi hex trên màn hình hai máy. Nếu trùng khớp, khóa nhận được đúng là của Bob; nếu khác, kênh đã bị can thiệp và phải dừng phiên. Đây là bước kiểm tra ngoài kênh (out-of-band) nhằm hạn chế tấn công xen giữa ở giai đoạn trao đổi khóa.

== Quy trình hoạt động

#align(center)[
  #fig-socket-sequence
]

== Kịch bản kiểm thử trên mạng

Giao diện dòng lệnh của Alice cung cấp 3 chế độ tương ứng với 3 tình huống kiểm thử:

#align(center)[
  #report-table(
    columns: (auto, 1.4fr, 1.8fr),
    headers: ("Chế độ", "Thao tác", "Kỳ vọng"),
    rows: (
      ([`1`], [Gửi gói tin hợp lệ, không chỉnh sửa.], [Bob giải mã đúng bản rõ và trả về `status: OK`.]),
      ([`2`], [Đảo bit byte đầu tiên của `ciphertext` trước khi gửi.], [AES-GCM báo `MAC check failed`; Bob hủy gói tin và trả về `status: ERROR`.]),
      ([`3`], [XOR `enc_session_key` với `0x1` để làm sai khóa phiên.], [RSA cho ra Session Key sai; AES-GCM từ chối xác thực, Bob trả về `status: ERROR`.]),
    )
  )
]

== Hướng dẫn chạy

Khởi động máy Bob trước; màn hình sẽ in địa chỉ IP LAN cần nhập ở máy Alice:

```bash
cd PGP_RSA_AES_Socket_3_files
python3 server_bob.py
```

Trên máy Alice, truyền IP của Bob làm tham số (dùng `127.0.0.1` nếu chạy cùng máy):

```bash
cd PGP_RSA_AES_Socket_3_files
python3 client_alice.py 192.168.1.11
```

Nếu chạy trên cùng một máy, cần mở hai cửa sổ terminal riêng biệt.

== Kết quả thực nghiệm

Nhật ký phía Alice khi gửi gói tin hợp lệ (chế độ `1`):

```text
[ALICE] SHA-256 Public Key Fingerprint của Bob:
        2acda677ab4ca7b3948733f742a6630ae7feec0fe8659ad5e3e01add128ac796
[ALICE] [1] Đã sinh Session Key K (16B)  : 4ca6cc7cc3807b853e8951d8b61ec716
[ALICE] [2] enc_session_key (RSA)        : 0x1881420e6080945c46b52904d59d421efb601dceb7...
[ALICE] [3] nonce (AES-GCM 12B)          : YJMcoCbdoqQAZgFL
[ALICE] [4] auth_tag (GHASH 16B)         : rAO87+vJhSC+3TlTKLbAcQ==
[ALICE] [5] ciphertext (AES)             : 7IA1Msw+8ysC64slujE3txcHOUnns/i4V0L9YuUnQRdv...
[ALICE] >>> Đã truyền 309 bytes qua TCP tới 127.0.0.1:5000.
[ALICE] <<< Phản hồi từ máy Bob: [OK] Bob da giai ma va xac thuc thanh cong!
```

Nhật ký tương ứng phía Bob:

```text
[BOB] Đã sinh mới cặp khóa RSA 511-bit từ algorithms.rsa.
[BOB] Đang lắng nghe TCP tại 0.0.0.0:5000 ... (Nhấn Ctrl+C để dừng)

[BOB] >>> Kết nối mới từ 127.0.0.1:43994
[BOB] Đã nhận gói tin PGP gồm 4 thành phần:
      + enc_session_key (RSA) : 0x1881420e6080945c46b52904d59d421efb601dceb7...
      + nonce (AES-GCM 12B)   : YJMcoCbdoqQAZgFL
      + auth_tag (GHASH 16B)  : rAO87+vJhSC+3TlTKLbAcQ==
      + ciphertext (AES)      : 7IA1Msw+8ysC64slujE3txcHOUnns/i4V0L9YuUnQRdv...
[BOB] Đã giải mã RSA & xác thực toàn vẹn AES-GCM thành công!
[BOB] >>> BẢN RÕ NHẬN ĐƯỢC: "Thong diep kiem thu PGP Hybrid qua TCP!"
```

Khi chọn chế độ `2` hoặc `3`, phía Bob phát hiện bất thường và hủy gói tin:

```text
[BOB] [!] CẢNH BÁO AN TOÀN MẬT MÃ:
      Phát hiện gói tin bị can thiệp hoặc sai khóa! Chi tiết: MAC check failed
      -> Bản tin đã bị hủy bỏ theo cơ chế toàn vẹn AES-GCM.
```

Phía Alice nhận phản hồi `[ERROR] Tu choi goi tin: MAC check failed`, xác nhận gói tin đã bị chặn đúng như thiết kế.

#info-box(title: "Giới hạn của bản mô phỏng")[
  - Kênh TCP trong demo *không được bọc TLS*. Do đó bước tải Public Key tự động vẫn có thể bị tấn công xen giữa; việc đối chiếu fingerprint thủ công chỉ là biện pháp giảm thiểu ở mức minh họa.
  - Khóa RSA 256-bit (mặc định `bits=256`) chỉ đủ chứa Session Key 128-bit và phục vụ mục tiêu học tập. RFC 8017 yêu cầu khóa tối thiểu 2048-bit cùng đệm RSA-OAEP cho triển khai thực tế.
  - Giao thức chưa có cơ chế chống phát lại (replay), chưa xác thực danh tính bằng chứng chỉ số và chưa hỗ trợ nhiều phiên đồng thời.
]
