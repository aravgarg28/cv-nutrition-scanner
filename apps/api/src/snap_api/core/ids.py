"""UUIDv7 generation (RFC 9562).

Time-ordered UUIDs give better index locality than uuid4 for our primary keys
(docs/architecture/DATA_MODEL.md). Implemented inline to avoid a dependency; the
stdlib does not provide uuid7 on Python 3.12.

Layout: bytes 0-5 = 48-bit Unix-ms timestamp, byte 6 high nibble = version 7,
byte 8 high bits = RFC 4122 variant (10xx), remaining bits random.
"""

from __future__ import annotations

import os
import time
import uuid


def uuid7() -> uuid.UUID:
    unix_ms = time.time_ns() // 1_000_000
    data = bytearray(os.urandom(16))

    ts = unix_ms & 0xFFFF_FFFF_FFFF
    data[0] = (ts >> 40) & 0xFF
    data[1] = (ts >> 32) & 0xFF
    data[2] = (ts >> 24) & 0xFF
    data[3] = (ts >> 16) & 0xFF
    data[4] = (ts >> 8) & 0xFF
    data[5] = ts & 0xFF

    data[6] = (data[6] & 0x0F) | 0x70  # version 7
    data[8] = (data[8] & 0x3F) | 0x80  # variant 10xx

    return uuid.UUID(bytes=bytes(data))
