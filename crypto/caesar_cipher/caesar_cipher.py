import sys

def rotate_char(c, offset):
    code = ord(c) + offset
    
    # Resolve cases where ASCII code exceeds front or end index of alpha characters
    if c.islower():
        if code < ord('a'):
            code = ord('z') - (ord('a') - code) + 1
        elif code > ord('z'):
            code = ord('a') + (code - ord('z')) - 1
    elif c.isupper(): 
        if code < ord('A'):
            code = ord('Z') - (ord('A') - code) + 1
        elif code > ord('Z'):
            code = ord('A') + (code - ord('Z')) - 1

    return chr(code);

def caesar_cipher(s, offset):
    char_list = [c for c in s]

    # Only rotate alpha characters
    for i in range(len(char_list)):
        if char_list[i].isalpha():
            char_list[i] = rotate_char(char_list[i], offset)

    return "".join(char_list)

if __name__ == "__main__":
    raw_message = input("Enter message to encode: ")
    
    try:
        offset = int(input("Enter an offset: ")) % 26
    except ValueError:
        print("ValueError: Offset must be an integer")
        sys.exit() 

    print("Caesar Cipher Encoded Message: " +  caesar_cipher(raw_message, offset))
