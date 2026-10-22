from encoder import canonical_codes, ESC, RAW_BITS


def decode(bit_string, lengths):
    """Rebuild the original bytes from the bit string and the code lengths."""
    if not bit_string:
        return b""

    codes = canonical_codes(lengths)                  # symbol -> "0101"
    table = {code: sym for sym, code in codes.items()}  # "0101" -> symbol

    out = bytearray()
    current = ""
    i = 0
    n = len(bit_string)

    while i < n:
        current += bit_string[i]
        i += 1
        symbol = table.get(current)
        if symbol is None:
            continue
        current = ""

        if symbol == ESC:
            raw = bit_string[i:i + RAW_BITS]
            if len(raw) < RAW_BITS:
                raise ValueError("Corrupted data: escape code without raw byte")
            out.append(int(raw, 2))
            i += RAW_BITS
        else:
            out.append(symbol)

    if current:
        raise ValueError("Corrupted data: leftover bits do not form a code")

    return bytes(out)