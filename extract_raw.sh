#!/usr/bin/bash

set -e

mkdir -p data

echo Extracting raw data from html chunks..
python parse/parse_words.py tmp/chunks
echo Extract Done.
