import importlib.util
import os
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from encoder import (
    ESC,
    RAW_BITS,
    canonical_codes,
    code_lengths,
    encode,
    split_symbols,
)


def load_binary_module():
    module_path = Path(__file__).with_name("binary-file.py")
    spec = importlib.util.spec_from_file_location("binary_file_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestEncoder(unittest.TestCase):

    def test_empty_input(self):
        self.assertEqual(encode(b"", 0.1), ("", {}))

    def test_single_repeated_byte(self):
        bitstring, lengths = encode(b"aaaa", 0.1)
        self.assertEqual(lengths, {ord("a"): 1})
        self.assertEqual(bitstring, "0000")
        self.assertEqual(len(bitstring), 4)

    def test_min_prob_zero_has_no_esc(self):
        data = b"abracadabra"
        _, lengths = encode(data, 0.0)
        self.assertNotIn(ESC, lengths)
        self.assertEqual(set(lengths.keys()), set(data))

    def test_min_prob_one_everything_is_esc(self):
        data = b"abcabc"
        bitstring, lengths = encode(data, 1.0)
        self.assertEqual(lengths, {ESC: 1})
        self.assertEqual(len(bitstring), len(data) * (1 + RAW_BITS))

    def test_normal_text_with_rare_symbol(self):
        data = b"A" * 20 + b"B" * 10 + b"C" * 5 + b"D"
        bitstring, lengths = encode(data, 0.03)

        self.assertIn(ESC, lengths)          
        self.assertNotIn(ord("D"), lengths) 
        self.assertIn(ord("A"), lengths)
        self.assertIn(ord("B"), lengths)
        self.assertIn(ord("C"), lengths)

    def test_invalid_min_prob_raises(self):
        for bad in (-0.1, 1.5):
            with self.assertRaises(ValueError):
                encode(b"hello", bad)

    def test_no_code_is_a_prefix_of_another(self):
        data = bytes([0] * 10 + [1] * 5 + [2] * 3 + [3] * 2 + [4])
        _, lengths = encode(data, 0.02)
        codes = list(canonical_codes(lengths).values())
        codes.sort()
        for i in range(len(codes) - 1):
            self.assertFalse(
                codes[i + 1].startswith(codes[i]),
                "{} is a prefix of {}".format(codes[i], codes[i + 1]),
            )

    def test_canonical_codes_match_encode(self):
        data = b"mississippi"
        bitstring, lengths = encode(data, 0.0)
        codes = canonical_codes(lengths)

        rebuilt = "".join(codes[byte] for byte in data)
        self.assertEqual(bitstring, rebuilt)

    def test_bitstring_length(self):
        data = b"A" * 20 + b"B" * 10 + b"C" * 5 + b"XYZ"
        min_prob = 0.05
        bitstring, lengths = encode(data, min_prob)

        weights = split_symbols(Counter(data), min_prob)
        expected = sum(weights[s] * lengths[s] for s in weights)
        expected += RAW_BITS * weights.get(ESC, 0)
        self.assertEqual(len(bitstring), expected)

    def test_single_symbol_length_is_one(self):
        self.assertEqual(code_lengths({42: 100}), {42: 1})

    def test_probability_equal_to_min_prob_is_kept(self):
        data = b"aaaabbbccd"
        _, lengths = encode(data, 0.2)
        self.assertIn(ord("c"), lengths)
        self.assertNotIn(ord("d"), lengths)  
        self.assertIn(ESC, lengths)

    def test_known_example_bit_count(self):
        bitstring, _ = encode(b"aaaabbbccd", 0.2)
        self.assertEqual(len(bitstring), 27)

    def test_prefix_free_with_esc(self):
        data = bytes([0] * 20 + [1] * 10 + [2] * 5 + [3, 4, 5])
        _, lengths = encode(data, 0.05)
        self.assertIn(ESC, lengths)
        codes = sorted(canonical_codes(lengths).values())
        for i in range(len(codes) - 1):
            self.assertFalse(codes[i + 1].startswith(codes[i]))

    def test_binary_file_round_trip(self):
        binary_module = load_binary_module()
        bit_string = "101101001011"

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()

        try:
            binary_module.write_binary_file(bit_string, temp_file.name)
            self.assertEqual(binary_module.read_binary_file(temp_file.name), bit_string)
        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)


if __name__ == "__main__":
    unittest.main()