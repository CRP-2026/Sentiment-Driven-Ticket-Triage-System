"""Stdlib PBKDF2-HMAC-SHA256 implementation of PasswordHasherPort."""

import hashlib
import hmac
import secrets


class Pbkdf2PasswordHasher:
    """Zero-native-dependency password hasher safe for any container/cloud target."""

    SCHEME = "pbkdf2_sha256"

    def __init__(self, iterations: int = 260_000, salt_bytes: int = 16) -> None:
        self._iterations = iterations
        self._salt_bytes = salt_bytes

    def hash_password(self, plain_password: str) -> str:
        salt = secrets.token_bytes(self._salt_bytes)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            self._iterations,
        )
        return f"{self.SCHEME}${self._iterations}${salt.hex()}${digest.hex()}"

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        try:
            scheme, iter_str, salt_hex, digest_hex = password_hash.split("$", 3)
            if scheme != self.SCHEME:
                return False
            iterations = int(iter_str)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
        except (ValueError, TypeError):
            return False

        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(candidate, expected)
