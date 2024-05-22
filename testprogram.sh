#!/bin/bash

rm result_format_a.txt

for i in {01..19}; do
    ini_file="test_files/test9a${i}.ini"
    echo '??????????????????????????????????????????????????' >> "result_format_a.txt"
    echo "Test $ini_file" >> "result_format_a.txt"
    echo '' >> "result_format_a.txt"
    echo '' >> "result_format_a.txt"
    sudo python3 src/tool.py -v -y -i "$ini_file" >> "result_format_a.txt"
    echo ' sudo python3 src/tool.py -v -y -i "$ini_file" >> "result_format_a.txt"'
    echo '' >> "result_format_a.txt"
    echo '' >> "result_format_a.txt"
done
