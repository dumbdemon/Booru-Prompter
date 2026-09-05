import os
import base64
from typing import Any
from pathlib import Path
from .logger import get_logger
from .paths_manager import paths

logger = get_logger("crytography")

try:
    import blake3 as _blake3

    _BLAKE3_AVAILABLE = True
except ImportError:  # pragma: no cover
    _BLAKE3_AVAILABLE = False

KEY_FILENAME = ".sexrect.key"

_NONCE_LEN = 16
_MAC_LEN = 32
_KEY_LEN = 32


def _get_or_create_key() -> bytes:
    if not _BLAKE3_AVAILABLE:
        raise RuntimeError(
            "blake3 is required for encrypted settings. It is bundled with ComfyUI."
        )

    key_path: Path = paths.get_user_path(KEY_FILENAME)
    if key_path.is_file():
        raw = key_path.read_bytes().strip()
        # Expect 64 hex chars encoding 32 bytes.  Old Fernet keys are 44 chars;
        # if we encounter one (or anything else invalid) we replace it.
        if len(raw) == 64:
            try:
                key = bytes.fromhex(raw.decode("ascii"))
                if len(key) == _KEY_LEN:
                    return key
            except ValueError:
                pass
        logger.info("Replacing old or invalid settings key with new blake3 key.")

    key = os.urandom(_KEY_LEN)
    key_path.write_bytes(key.hex().encode("ascii") + b"\n")
    try:
        os.chmod(key_path, 0o600)
    except OSError:
        # Best effort: chmod may not be available on all platforms.
        pass
    logger.info("Created local settings encryption key.")
    return key


def _constant_time_compare(a: bytes, b: bytes) -> bool:
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    return result == 0


def _encrypt_bytes(key: bytes, plaintext: bytes) -> bytes:
    """Return nonce + mac + ciphertext using blake3 stream cipher + MAC."""
    nonce = os.urandom(_NONCE_LEN)
    # 0x00 prefix: keystream domain; 0x01 prefix: MAC domain.
    keystream = _blake3.blake3(b"\x00" + nonce, key=key).digest(length=len(plaintext))
    ciphertext = bytes(p ^ k for p, k in zip(plaintext, keystream))
    mac = _blake3.blake3(b"\x01" + nonce + ciphertext, key=key).digest(length=_MAC_LEN)
    return nonce + mac + ciphertext


def _decrypt_bytes(key: bytes, data: bytes) -> bytes:
    """Decrypt data from _encrypt_bytes. Raises ValueError on auth failure."""
    if len(data) < _NONCE_LEN + _MAC_LEN:
        raise ValueError("Encrypted data too short.")
    nonce = data[:_NONCE_LEN]
    mac = data[_NONCE_LEN : _NONCE_LEN + _MAC_LEN]
    ciphertext = data[_NONCE_LEN + _MAC_LEN :]
    expected_mac = _blake3.blake3(b"\x01" + nonce + ciphertext, key=key).digest(
        length=_MAC_LEN
    )
    if not _constant_time_compare(mac, expected_mac):
        raise ValueError("MAC verification failed.")
    keystream = _blake3.blake3(b"\x00" + nonce, key=key).digest(length=len(ciphertext))
    return bytes(c ^ k for c, k in zip(ciphertext, keystream))


def encrypt(key: str, value: Any) -> Any:
    if value is None:
        return ""

    if key != "booru_api_token":
        return value

    plain_txt = str(value)

    if not plain_txt:
        return ""

    raw = _encrypt_bytes(_get_or_create_key(), plain_txt.encode("utf-8"))
    token = base64.urlsafe_b64encode(raw).decode("ascii")
    return token


def decrypt(key: str, value: Any) -> Any:
    if value is None:
        return ""

    if key != "booru_api_token":
        return value

    try:
        raw = base64.urlsafe_b64decode(value.encode("ascii"))
        return _decrypt_bytes(_get_or_create_key(), raw).decode("utf-8")
    except (ValueError, RuntimeError) as e:
        logger.warning("Unable to decrypt setting '%s': %s. Using empty value.", key, e)
        return ""
