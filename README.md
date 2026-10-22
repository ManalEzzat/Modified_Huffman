# Modified Huffman Compression

## 📌 Overview
A Python implementation of the Modified Huffman Coding algorithm for lossless data compression. 
The project compresses files into binary format and decompresses them to recover the original data.

## How it works

- The user enters a **minimum probability** (`min_prob`, between 0 and 1).
- Any byte whose probability is **below** `min_prob` is grouped into one special **ESC** symbol.
- The remaining bytes and ESC get canonical Huffman codes.
- An escaped byte is written as: `ESC code + 8 raw bits`.
- The 0/1 stream is packed into real bits and saved to a binary file.

## Files

| File | Purpose |
|---|---|
| `main.py` | Menu: compress (c) or decompress (d) |
| `encoder.py` | Builds the code table and encodes the data |
| `decoder.py` | Decodes the bit string back to the original bytes |
| `binary-file.py` | Writes/reads the compressed binary file |

## Compressed file format

```
4 bytes  : number of valid bits
2 bytes  : number of table entries
per entry: 2 bytes symbol (256 = ESC) + 1 byte code length
rest     : the packed bits (padded with zeros to full bytes)
```

The header is the only overhead; the data itself is stored as bits.

## Usage

```
python main.py
```

1. Choose `c` to compress: enter the input file, the output file and `min_prob`.
2. Choose `d` to decompress: enter the compressed file and the output file.

## Verify

