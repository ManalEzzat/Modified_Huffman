import importlib.util
from pathlib import Path

from encoder import encode


def load_binary_module():
    module_path = Path(__file__).with_name("binary-file.py")
    spec = importlib.util.spec_from_file_location("binary_file_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_min_prob():
    while True:
        text = input("Enter min_prob (0 to 1): ").strip()
        try:
            value = float(text)
        except ValueError:
            print("That is not a number. Try again.")
            continue
        if 0 <= value <= 1:
            return value
        print("The number must be between 0 and 1. Try again.")


def compress_file():
    in_path = input("Input file path: ").strip()
    out_path = input("Output compressed file path: ").strip()
    min_prob = read_min_prob()

    with open(in_path, "rb") as file:
        data = file.read()

    bitstring, lengths = encode(data, min_prob)
    binary_module = load_binary_module()
    binary_module.write_binary_file(bitstring, out_path)

    original_size = len(data)
    bit_count = len(bitstring)
    data_size = (bit_count + 7) // 8

    print("Original size:     ", original_size, "bytes")
    print("Encoded bits:      ", bit_count)
    print("Encoded data size: ", data_size, "bytes (without header)")
    print("Symbols in table:  ", len(lengths))
    print("Compressed file:   ", out_path)
    if data_size > 0:
        print("Compression ratio: {:.2f}".format(original_size / data_size))
    return bitstring, lengths


def decompress_file():
    file_path = input("Compressed file path: ").strip()
    binary_module = load_binary_module()
    return binary_module.read_binary_file(file_path)


if __name__ == "__main__":
    compress_file()