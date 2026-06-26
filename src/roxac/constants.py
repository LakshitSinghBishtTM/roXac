"""
Global constants.
Single source of truth for all configuration values and algorithm identifiers.
"""

APP_NAME = "roXac"
VERSION = "1.0.0"
APP_DIR = "~/.roxac"

# Cryptographic algorithm identifiers
KEM_ALGORITHM = "ML-KEM-768"
CIPHER = "AES-256-GCM"
KDF = "Argon2id"

# File names within APP_DIR
CONFIG_FILE = "config.json"
AUTH_FILE = "auth.hash"
KEM_PUBLIC_KEY_FILE = "kem_public.key"
KEM_PRIVATE_KEY_FILE = "kem_private.enc"
HISTORY_FILE = "history.enc"

# AES-256-GCM parameters
AES_KEY_SIZE = 32       # 256 bits
AES_NONCE_SIZE = 12     # 96 bits (NIST recommended for GCM)

# Argon2id parameters

ARGON2_TIME_COST = 10
ARGON2_MEMORY_COST = 12582912
ARGON2_PARALLELISM = 8
ARGON2_HASH_LEN = 32
ARGON2_SALT_LEN = 16  

# Calculator
DECIMAL_PRECISION = 100      # Significant digits for full-precision arithmetic
VALID_OPERATORS = frozenset({"+", "-", "*", "/"})