import heapq
from collections import Counter

ESC = 256
RAW_BITS = 8


def split_symbols(freq, min_prob):
    total = sum(freq.values())
    if total == 0:
        return {}

    weights = {}
    for symbol, count in freq.items():
        probability = count / total
        if probability < min_prob:
            weights[ESC] = weights.get(ESC, 0) + count
        else:
            weights[symbol] = count
    return weights


def code_lengths(weights):
    if not weights:
        return {}
    if len(weights) == 1:
        only_symbol = next(iter(weights))
        return {only_symbol: 1}
    heap = []
    tie = 0
    for symbol, weight in weights.items():
        heap.append((weight, tie, symbol))
        tie += 1
    heapq.heapify(heap)

    while len(heap) > 1:
        weight1, _, node1 = heapq.heappop(heap)
        weight2, _, node2 = heapq.heappop(heap)
        merged = (node1, node2) 
        heapq.heappush(heap, (weight1 + weight2, tie, merged))
        tie += 1
    lengths = {}
    root = heap[0][2]

    def walk(node, depth):
        if isinstance(node, int):  
            lengths[node] = depth
        else:
            walk(node[0], depth + 1)
            walk(node[1], depth + 1)

    walk(root, 0)
    for symbol in lengths:
        if lengths[symbol] == 0:
            lengths[symbol] = 1
    return lengths


def canonical_codes(lengths):
    codes = {}
    if not lengths:
        return codes

    code = 0
    prev_length = 0
    for i, symbol in enumerate(sorted(lengths, key=lambda s: (lengths[s], s))):
        length = lengths[symbol]
        if i > 0:
            code = (code + 1) << (length - prev_length)
        codes[symbol] = format(code, "0{}b".format(length))
        prev_length = length
    return codes


def encode(data, min_prob):
    if not 0 <= min_prob <= 1:
        raise ValueError("min_prob must be between 0 and 1")

    if not data:
        return "", {}

    freq = Counter(data)
    weights = split_symbols(freq, min_prob)
    lengths = code_lengths(weights)
    codes = canonical_codes(lengths)

    bits = []
    for byte in data:
        if byte in codes:
            bits.append(codes[byte])
        else:
            bits.append(codes[ESC] + format(byte, "0{}b".format(RAW_BITS)))

    return "".join(bits), lengths
