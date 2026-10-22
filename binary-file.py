import os


def write_binary_file(bit_string, filename, lengths):
    """
    Header: 4 bytes bit-length | 2 bytes table size | per entry: 2 bytes symbol, 1 byte code length
    Then the packed bits.
    """
    if bit_string is None:
        raise ValueError("bit_string cannot be None")

    if not isinstance(bit_string, str):
        bit_string = str(bit_string)

    if set(bit_string) - {"0", "1"}:
        raise ValueError("bit_string must contain only 0 and 1")

    original_length = len(bit_string)
    padding = (8 - (original_length % 8)) % 8
    padded_bits = bit_string + ("0" * padding)

    byte_list = [int(padded_bits[i:i + 8], 2) for i in range(0, len(padded_bits), 8)]

    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(filename, "wb") as file:
        file.write(original_length.to_bytes(4, byteorder="big"))
        file.write(len(lengths).to_bytes(2, byteorder="big"))
        for symbol in sorted(lengths):
            if lengths[symbol] > 255:
                raise ValueError("Code length too large for header")
            file.write(symbol.to_bytes(2, byteorder="big"))
            file.write(lengths[symbol].to_bytes(1, byteorder="big"))
        file.write(bytes(byte_list))

    return original_length


def read_binary_file(filename):
    """Returns (bit_string, lengths)."""
    with open(filename, "rb") as file:
        data = file.read()

    if len(data) < 6:
        raise ValueError("File is too short to contain header")

    original_length = int.from_bytes(data[:4], byteorder="big")
    table_size = int.from_bytes(data[4:6], byteorder="big")

    pos = 6
    lengths = {}
    for _ in range(table_size):
        if pos + 3 > len(data):
            raise ValueError("Corrupted header")
        symbol = int.from_bytes(data[pos:pos + 2], byteorder="big")
        lengths[symbol] = data[pos + 2]
        pos += 3

    payload = data[pos:]

    if original_length == 0:
        return "", lengths

    bit_string = "".join(f"{byte:08b}" for byte in payload)
    return bit_string[:original_length], lengths