#import "../styles.typ": report-table

= Cài đặt RSA bằng Python

Thuật toán RSA được tổ chức thành các mô-đun độc lập trong thư mục `algorithms/` nhằm phục vụ việc kiểm thử từng thành phần:

== Bảng đặc tả các hàm chính

#align(center)[
  #report-table(
    columns: (1.2fr, 2fr),
    headers: ("Tên hàm", "Mô tả chức năng & Giải thuật"),
    rows: (
      ([`extended_gcd(a, b)`], [Cài đặt giải thuật Euclid mở rộng: đệ quy tìm ước chung lớn nhất và các hệ số Bézout $x, y$ sao cho $a x + b y = gcd(a, b)$. Dùng để tính số mũ bí mật $d$.]),
      ([`is_prime(n, k)`], [Kiểm tra số nguyên tố xác suất bằng thuật toán Miller–Rabin với $k$ vòng thử (mặc định $k = 20$), dùng nguồn ngẫu nhiên an toàn `random.SystemRandom`. Là cơ sở để sinh $p, q$ động.]),
      ([`generate_prime(bits)`], [Sinh ngẫu nhiên một số nguyên tố có độ dài `bits` bit: bật bit cao nhất và bit thấp nhất để bảo đảm độ dài, sau đó lặp tới khi vượt qua `is_prime`.]),
      ([`generate_rsa_keys(p=None, q=None, e=65537, bits=256)`], [Giai đoạn sinh khóa: nếu truyền `p, q` thì dùng trực tiếp (ví dụ minh họa $p=61, q=53, e=17$); nếu không, tự sinh hai số nguyên tố $p, q$ động (mặc định 256-bit) thỏa $gcd(e, phi(n)) = 1$, rồi tính $n = p times q$, $phi = (p-1)(q-1)$, $d=$ `mod_inverse(e, phi)`, trả về cặp `((e, n), (d, n))`.]),
      ([`rsa_encrypt(pub_key, M)`], [Giai đoạn mã hóa: Áp dụng công thức $C = M^e mod n$ sử dụng hàm lũy thừa modulo tối ưu `pow(M, e, n)`.]),
      ([`rsa_decrypt(priv_key, C)`], [Giai đoạn giải mã: Áp dụng công thức $M = C^d mod n$ thông qua `pow(C, d, n)`.])
    )
  )
]

== Tham chiếu mã nguồn thuật toán RSA

Mã nguồn chi tiết được tổ chức tại thư mục `algorithms/`:
- Giải thuật Euclid mở rộng: `algorithms/euclid.py` (hàm `extended_gcd`, `mod_inverse`).
- Thuật toán RSA số học: `algorithms/rsa.py` (sinh khóa, kiểm tra Miller–Rabin, mã hóa và giải mã).

== Kết quả thực thi (`algorithms/rsa.py`)

Kết quả xuất ra khi chạy `python3 -m algorithms.rsa` (chế độ minh họa truyền thống với $p=61, q=53, e=17$):

```text
Public Key (e, n): (17, 3233)
Private Key (d, n): (2753, 3233)
Bản rõ: 125 -> Bản mã: 1516 -> Khôi phục: 125
Khôi phục thành công.
```

#import "../components.typ": info-box
#info-box(title: "Điểm cần nhớ")[
  - Cả hai hàm `rsa_encrypt` và `rsa_decrypt` đều thực thi thuật toán tính lũy thừa theo mô-đun (`pow(base, exp, mod)`), chỉ khác nhau ở số mũ: quá trình mã hóa sử dụng số mũ công khai $e$, trong khi quá trình giải mã sử dụng số mũ bí mật $d$.
  - Khi *không* truyền `p, q`, hàm `generate_rsa_keys` mặc định sinh khóa động 256-bit (`bits=256`, `e=65537`). Độ dài này bảo đảm modulus $n > 2^128$, đủ lớn để mã hóa trọn vẹn một Session Key AES-128 (16 bytes) mà không bị mất bit.
]
