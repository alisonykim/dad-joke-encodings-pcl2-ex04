#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# task_2.py

# University of Zurich
# Department of Computational Linguistics

# Author 1: Alison Y. Kim
# Author 2: Naomi Bleiker


class FileHandler:
    """Handles files of different encodings (ISO 8859-1 or ASCII) and converts input file to the beloved UTF-8."""
    def __init__(self, input_file):
        self.filename = input_file
        self.encoding = self.detect_encoding()
    
    def detect_encoding(self):
        """Returns encoding of input. Only supports ASCII and ISO-8859-1 for now."""
        with open(self.filename, mode='rb') as file:
            lines = file.read() # This accounts for the whole file, BUT it would not be efficient for larger files
            try:
                if lines.decode('ascii'): # If lines are able to be decoded in ASCII
                    encoding = 'ascii'
            except UnicodeDecodeError: # If lines contain at least 1 non-ASCII character
                encoding = 'iso-8859-1'
        return encoding
    
    def convert_to_utf8(self, outfile='encoding_utf-8.txt') -> None:
        with open(outfile, 'a', encoding='utf-8') as output: # 'a' = append to end of file, 'w' overwrites due to for loop
            output.write(f'{self.filename}\n')
            with open(self.filename, 'r', encoding=self.encoding) as input:
                for line in input:
                    output.write(f'{line}')
                output.write(f'\n')
            input.close()
        output.close()


if __name__ == '__main__':
    # Test detect_encoding(self)
    file1 = FileHandler('encoding_1.txt')
    file2 = FileHandler('encoding_2.txt')
    file3 = FileHandler('encoding_3_de.txt')
    print(file1.encoding) # Should be ASCII
    print(file2.encoding) # Should be ISO
    print(file3.encoding) # Should be ISO

    # Create UTF-8-encoded version of files
    infiles = ['encoding_1.txt', 'encoding_2.txt'] # Can iterate through directory and grab *.txt if we want to extend script to accept other files
    for infile in infiles:
        file_object = FileHandler(infile) # Instantiate FileHandler-object
        file_object.convert_to_utf8()