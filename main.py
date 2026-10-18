from encoder import encode


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
    min_prob = read_min_prob()

    with open(in_path, "rb") as file:
        data = file.read()

    bitstring, lengths = encode(data, min_prob)

    original_size = len(data)
    bit_count = len(bitstring)
    data_size = (bit_count + 7) // 8   

    print("Original size:     ", original_size, "bytes")
    print("Encoded bits:      ", bit_count)
    print("Encoded data size: ", data_size, "bytes (without header)")
    print("Symbols in table:  ", len(lengths))
    if data_size > 0:
        print("Compression ratio: {:.2f}".format(original_size / data_size))
    return bitstring, lengths

if __name__ == "__main__":
    compress_file()