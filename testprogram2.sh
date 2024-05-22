
rm result_format_a.txt
for i in {01..18}; do
    input_file="test_files/test9b${i}.txt"
    echo '??????????????????????????????????????????????????' >> "result_format.txt"
    echo "Test $input_file" >> "result_format_b.txt"
    echo '' >> "result_format_b.txt"
    echo '' >> "result_format_b.txt"
    sudo python3 src/tool.py -v -y < $input_file >> "result_format_b.txt"
    echo ' sudo python3 src/tool.py -v -y < $input_file >> "result_format_b.txt"'
    echo '' >> "result_format_b.txt"
    echo '' >> "result_format_b.txt"
done
