#!/usr/bin/env python3
# generator.py
# Genera muestras: repetitivo, pseudoaleatorio (patrones) y "realista" (concatenación de textos).

import os
import argparse
import random
import string

def gen_repetitive(path, size_bytes):
    chunk = b"A" * 1024  # altamente repetible
    with open(path, "wb") as f:
        written = 0
        while written < size_bytes:
            remain = min(len(chunk), size_bytes - written)
            f.write(chunk[:remain])
            written += remain

def gen_patterned(path, size_bytes):
    patterns = [b"0123456789\n", b"AAAAAAA\n", b"ABCD" * 64, b"\x00\xFF" * 64]
    with open(path, "wb") as f:
        written = 0
        while written < size_bytes:
            p = random.choice(patterns)
            to_write = p[:min(len(p), size_bytes - written)]
            f.write(to_write)
            written += len(to_write)

def gen_realistic(path, size_bytes):
    # Simula archivo "real" concatenando textos repetidos y bloques binarios
    lorem = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 10).encode()
    binchunk = os.urandom(1024)
    with open(path, "wb") as f:
        written = 0
        toggle = True
        while written < size_bytes:
            if toggle:
                w = lorem[:min(len(lorem), size_bytes - written)]
            else:
                w = binchunk[:min(len(binchunk), size_bytes - written)]
            f.write(w)
            written += len(w)
            toggle = not toggle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--size-mb", type=int, default=50)
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    size_bytes = args.size_mb * 1024 * 1024
    gen_repetitive(os.path.join(args.out_dir, "repetitive.bin"), size_bytes)
    gen_patterned(os.path.join(args.out_dir, "patterned.bin"), size_bytes)
    gen_realistic(os.path.join(args.out_dir, "realistic.bin"), size_bytes)
    print("Muestras generadas en", args.out_dir)

if __name__ == "__main__":
    main()
