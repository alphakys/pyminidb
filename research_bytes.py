
b = b"hello"
print(f"Original: {id(b)}")

# Assignment
b1 = b
print(f"Assignment (b1 = b): {id(b1)} (Same: {id(b) == id(b1)})")

# Full Slice
b_slice = b[:]
print(f"Full Slice (b[:]): {id(b_slice)} (Same: {id(b) == id(b_slice)})")

# Partial Slice
b_part = b[1:4]
print(f"Partial Slice (b[1:4]): {id(b_part)} (Same: {id(b) == id(b_part)})")

# bytes() constructor with bytes
b_const = bytes(b)
print(f"bytes(b): {id(b_const)} (Same: {id(b) == id(b_const)})")

# bytes() constructor with bytearray
ba = bytearray(b)
b_from_ba = bytes(ba)
print(f"bytes(bytearray): {id(b_from_ba)} (Same: {id(b) == id(b_from_ba)})")

# Concatenation
b_concat = b + b""
print(f"Concatenation (b + b''): {id(b_concat)} (Same: {id(b) == id(b_concat)})")

# Methods
b_upper = b.upper()
print(f"Method (b.upper()): {id(b_upper)} (Same: {id(b) == id(b_upper)})")


# Multiplication
b_mult = b * 1
print(f"Multiplication (b * 1): {id(b_mult)} (Same: {id(b) == id(b_mult)})")
b_mult2 = b * 2
print(f"Multiplication (b * 2): {id(b_mult2)} (Same: {id(b) == id(b_mult2)})")

# copy module
import copy
b_copy = copy.copy(b)
print(f"copy.copy(b): {id(b_copy)} (Same: {id(b) == id(b_copy)})")
b_deepcopy = copy.deepcopy(b)
print(f"copy.deepcopy(b): {id(b_deepcopy)} (Same: {id(b) == id(b_deepcopy)})")

# string encoding
s = "hello"
b_enc = s.encode()
b_enc2 = s.encode()
print(f"s.encode() vs s.encode(): {id(b_enc) == id(b_enc2)} (False means new object each time)")

# bytes.fromhex
b_hex = bytes.fromhex("68656c6c6f")
print(f"bytes.fromhex: {id(b_hex)} (Same: {id(b) == id(b_hex)})")
