#!/usr/bin/env python3

import argparse
import sys

def pad_to_eight_digits(token_number):
    # Convert to 8-digit string with leading zeros if necessary
    return str(token_number).zfill(8)

def get_parity(n):
    # Calculate parity for a given number
    return ~(((n * 0x0101010101010101) & 0x8040201008040201) % 0x1FF) & 1

def convert_hitag(token_number):
    # This is an example transformation, you should replace this with the actual logic
    hitag = token_number + 1
    return hitag

def convert_paxton(token_number):
    # Ensure the token_number is padded to 8 digits
    token_number = str(token_number).zfill(8)
    
    result = 0

    for index, digit in enumerate(token_number):
        dec = int(digit)
        dec = (get_parity(dec) << 4) + dec
        result = (result << 5) + dec
        if index == 5:
            result <<= 2

    result = (result << 22) + 4128768 + 6
    result_hex = hex(result)[2:].zfill(16)

    return {
        'page4': result_hex[:8],
        'page5': result_hex[8:]
    }

def convert_em4(token_number):
    # Transformation for em4: Convert to hexadecimal and pad to 8 characters
    em4 = f"{token_number:X}".zfill(8)
    return em4

def convert_prox(token_number):
    # Transformation for prox: Convert to binary and pad to 28 bits
    prox = f"{token_number:b}".zfill(28)
    return prox

def convert_mifare(token_number):
    # Transformation for mifare
    mifare = f"{token_number:X}".zfill(8)
    return mifare

def convert_to_em41x(page4, page5):
    # Convert page4 and page5 values to a decimal and hexadecimal EM41x value
    hex_value = int(page4 + page5, 16)
    num = i = 0
    output = 0
    skip = 64
    mask = 0xF800000000000000

    while i < 8:
        num = hex_value & mask
        skip -= 5
        mask = mask >> 5
        digit = (num >> skip) & 15
        output = (output * 10) + digit
        if i == 5:
            skip -= 2
            mask = mask >> 2
        i += 1

    return {
        'em41x_dec': output,
        'em41x_hex': hex(output)[2:].zfill(8)
    }

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Token number conversion script.")
    parser.add_argument("-t", "--token_number", type=int, help="Paxton token number")
    parser.add_argument("-4", "--page4", type=str, help="Page 4 data")
    parser.add_argument("-5", "--page5", type=str, help="Page 5 data")

    # If no arguments are provided, show help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Parse command line arguments
    args = parser.parse_args()

    if args.token_number is not None:
        token_number = args.token_number
        
        # Ensure the token number is converted to an 8-digit string
        padded_token = pad_to_eight_digits(token_number)
        
        # Convert the padded token back to integer for transformations
        padded_token_number = int(padded_token)
        
        # Get the converted outputs using the padded token number
        hitag = convert_paxton(padded_token_number)
        em4 = convert_em4(padded_token_number)
        prox = convert_prox(padded_token_number)
        mifare = convert_mifare(padded_token_number)
        
        # Output the results
        print(f"")
        print(f"Hitag: {hitag['page4']}{hitag['page5']}")
        print(f"lf hitag wrbl --ht2 -k bdf5e846 -p 4 -d {hitag['page4']}")
        print(f"lf hitag wrbl --ht2 -k bdf5e846 -p 5 -d {hitag['page5']}")
        print(f"lf hitag wrbl --ht2 -k bdf5e846 -p 6 -d 00600F8E")
        print(f"lf hitag wrbl --ht2 -k bdf5e846 -p 7 -d C6000010\n")
        print(f"EM4: {em4}")
        print(f"lf em 410x clone --id {em4}\n")
        print(f"HID Prox: {prox}")
        print(f"lf hid clone -w 2804W --bin {prox}\n")
        print(f"Mifare: {mifare}")
        print(f"hf mf csetuid -u {mifare}")
    
    if args.page4 and args.page5:
        page4 = args.page4
        page5 = args.page5
        
        # Get the EM41x converted outputs
        em41x = convert_to_em41x(page4, page5)
        
        # Output the results
        print(f"")
        print(f"Paxton Token Number: {em41x['em41x_dec']}")
        print(f"EM41x UID: {em41x['em41x_hex']}")

if __name__ == "__main__":
    main()