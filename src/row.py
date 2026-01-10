import struct
from typing import ClassVar


class Row:
    """
    [Phase 1 Refactored] Teacher's Reference Implementation

    Changes:
    1. Endianness: Changed to Little-endian (<) for native performance on modern CPUs.
    2. Validation: Added explicit length checks to prevent silent data loss.
    3. Error Handling: Removed try-except blocks. Errors are propagated to the caller (Fail Fast).
    """

    # Constants
    ID_SIZE: ClassVar[int] = 4
    USERNAME_SIZE: ClassVar[int] = 10
    EMAIL_SIZE: ClassVar[int] = 30

    # Format: Little-endian (<), int, 10s, 30s
    STRUCT_FORMAT: ClassVar[str] = f"<i{USERNAME_SIZE}s{EMAIL_SIZE}s"
    _struct: ClassVar[struct.Struct] = struct.Struct(STRUCT_FORMAT)

    __slots__ = ("user_id", "username", "email")

    def __init__(self, user_id: int, username: str, email: str):
        self.user_id: int = user_id
        self.username: str = username
        self.email: str = email

    def serialize(self) -> bytes:
        # 1. Encode strings
        username_bytes = self.username.encode("utf-8")
        email_bytes = self.email.encode("utf-8")

        # 2. Validation (Critical Step!)
        # struct.pack silently truncates strings. We MUST catch this.
        if not isinstance(self.user_id, int):
            raise ValueError("id must be integer")

        if len(username_bytes) > self.USERNAME_SIZE:
            raise ValueError(
                f"Username too long: {len(username_bytes)} bytes (Max {self.USERNAME_SIZE})"
            )

        if len(email_bytes) > self.EMAIL_SIZE:
            raise ValueError(
                f"Email too long: {len(email_bytes)} bytes (Max {self.EMAIL_SIZE})"
            )

        # 3. Pack
        # No try-except: If packing fails, we WANT the DB to crash or handle it explicitly.
        return self._struct.pack(self.user_id, username_bytes, email_bytes)

    @classmethod
    def deserialize(cls, data: bytes) -> "Row":
        # 1. Unpack
        # unpack raises struct.error if data length is wrong. Let it bubble up.
        unpacked = cls._struct.unpack(data)
        # 2. Decode and Clean
        # rstrip(b'\x00') removes the null padding added by struct
        username = unpacked[1].rstrip(b"\x00").decode("utf-8")
        email = unpacked[2].rstrip(b"\x00").decode("utf-8")

        return cls(user_id=unpacked[0], username=username, email=email)

    @property
    def size(self):
        return self._struct.size

    def __repr__(self):
        return (
            f"Row(id={self.user_id}, username='{self.username}', email='{self.email}')"
        )


if __name__ == "__main__":
    r = Row(1, "sdf", "sdfsdf")
    print(r)
