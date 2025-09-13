# rebuild_stgterm.py
import sys

def clean_stgterm(input_path, output_path):
    with open(input_path, "rb") as f:
        data = f.read()

    # Filter out only bytes that look like actual binary ops, not ASCII text
    cleaned = bytearray()
    for b in data:
        if b < 0x80:  # keep binary-like opcodes/values
            cleaned.append(b)

    print(f"Extracted {len(cleaned)} bytes")
    with open(output_path, "wb") as out:
        out.write(cleaned)
    print(f"Wrote cleaned binary file: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 rebuild_stgterm.py input.dat output.bin")
        sys.exit(1)
    clean_stgterm(sys.argv[1], sys.argv[2])
