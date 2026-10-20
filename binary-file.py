import os


def write_binary_file(bit_string, filename):
    """ 
    Save a bit string as bytes, keeping the original bit length for decoding.
      """
    if bit_string is None:
        raise ValueError("bit_string cannot be None")

    if not isinstance(bit_string, str):
        bit_string = str(bit_string)

    if any(bit not in "01" for bit in bit_string):
        raise ValueError("bit_string must contain only 0 and 1")

    original_length = len(bit_string)
    padding = (8 - (original_length % 8)) % 8
    padded_bits = bit_string + ("0" * padding)

    byte_list = []
    for i in range(0, len(padded_bits), 8):
        chunk = padded_bits[i:i + 8]
        byte_list.append(int(chunk, 2))

    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(filename, "wb") as file:
        file.write(original_length.to_bytes(4, byteorder="big"))
        file.write(bytes(byte_list))

    return original_length


def read_binary_file(filename):
    """
    Read the bits back from a file and remove the padding bits."""
    with open(filename, "rb") as file:
        
        data = file.read()

    if len(data) < 4:
        raise ValueError("File is too short to contain bit-length metadata")

    original_length = int.from_bytes(data[:4], byteorder="big")
    payload = data[4:]

    if original_length == 0:
        return ""

    bit_string = "".join(f"{byte:08b}" for byte in payload)
    return bit_string[:original_length]
