#!/usr/bin/env python3

import json
import gzip
import base64
import pprint

def decompress_json(compressed_base64):
    # Decode the base64 string to get the compressed bytes
    compressed_bytes = base64.b64decode(compressed_base64)

    # Decompress the bytes using gzip
    json_str = gzip.decompress(compressed_bytes).decode('utf-8')

    # Convert the JSON string back to a JSON object
    data = json.loads(json_str)

    return data

if __name__ == '__main__':
    # Example compressed base64 string
    input = input("Enter the compressed base64 string: ")
    pprint.pprint(decompress_json(input))

