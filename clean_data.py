import re

def clean_data(input_file, output_file):
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    for line in lines:
        # Skip the experimental warning line
        if ":warning: Experimental :warning:" in line:
            continue
            
        # Remove all emoji patterns (text surrounded by colons)
        cleaned_line = re.sub(r':[^:]+:', '', line)
        
        # Only add non-empty lines
        if cleaned_line.strip():
            cleaned_lines.append(cleaned_line)
    
    # Write the cleaned data to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)

if __name__ == "__main__":
    input_file = "data.txt"
    output_file = "cleaned_data.txt"
    clean_data(input_file, output_file)
    print(f"Data has been cleaned and saved to {output_file}") 