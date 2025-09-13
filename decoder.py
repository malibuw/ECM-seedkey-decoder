#!/usr/bin/env python3
import argparse
import struct

def gm_5byte_key(seed: int) -> int:
    """GM Global-A 5-byte programming seed/key calculator."""
    seed &= 0xFFFFFFFFFF
    hi = (seed >> 16) & 0xFFFFFFFF
    lo = seed & 0xFFFF
    key = ((hi << 11) | (hi >> 5)) & 0xFFFFFFFF
    key = (key + lo + 0xA7C5) & 0xFFFFFFFF
    key = ((key << 8) | (seed & 0xFF)) & 0xFFFFFFFFFF
    return key

def scan_bin_for_seeds(filepath: str):
    with open(filepath, "rb") as f:
        data = f.read()
    results = set()
    for i in range(len(data) - 4):
        chunk = data[i:i+5]
        if chunk[-1] != 0x06:
            continue
        seed = int.from_bytes(chunk, byteorder='big')
        key = gm_5byte_key(seed)
        results.add((seed, key))
    return sorted(results)

def main():
    parser = argparse.ArgumentParser(description="GM 5-byte seed→key decoder")
    parser.add_argument("--seed", help="Single 5-byte seed (e.g. 0xA3A3859E06)")
    parser.add_argument("--file", help="Binary file to scan for seeds")
    args = parser.parse_args()

    if args.seed:
        seed = int(args.seed, 16)
        key = gm_5byte_key(seed)
        print(f"{seed:010X} = {key:010X}")
    elif args.file:
        pairs = scan_bin_for_seeds(args.file)
        if not pairs:
            print("No 5-byte seeds ending in 0x06 found.")
        for seed, key in pairs:
            print(f"{seed:010X} = {key:010X}")
    else:
        print("Either --seed or --file must be provided.")

if __name__ == "__main__":
    main()
