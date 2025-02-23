import hashlib
import random

# a large prime number p and a generator g
P = 2**127 - 1
G = 5


def hash_and_encrypt(value, private_key):
    hashed = int(hashlib.sha256(value.encode()).hexdigest(), 16) % P
    return pow(G, hashed * private_key, P)
