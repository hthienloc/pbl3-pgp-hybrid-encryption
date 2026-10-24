"""
Thư viện các thuật toán nền tảng cho đồ án PGP Hybrid Encryption:
- euclid: Giải thuật Euclid mở rộng và nghịch đảo modulo
- rsa: Thuật toán tạo khóa, mã hóa và giải mã RSA số học
- aes_gcm: Mã hóa đối xứng xác thực AES-GCM
- hybrid_pgp: Tích hợp mã hóa lai RSA - AES
"""

from .euclid import extended_gcd, mod_inverse
from .rsa import generate_rsa_keys, rsa_encrypt, rsa_decrypt
from .aes_gcm import aes_gcm_encrypt, aes_gcm_decrypt
from .hybrid_pgp import alice_encrypt_package, bob_decrypt_package

__all__ = [
    "extended_gcd",
    "mod_inverse",
    "generate_rsa_keys",
    "rsa_encrypt",
    "rsa_decrypt",
    "aes_gcm_encrypt",
    "aes_gcm_decrypt",
    "alice_encrypt_package",
    "bob_decrypt_package",
]
