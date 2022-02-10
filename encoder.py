import base64
import sys


def xor(data, key):
    key = str(key)
    l = len(key)
    output_str = ""
    for i in range(len(data)):
        # current = data[i]
        # current_key = key[i % l]
        output_str += chr(ord(data[i]) ^ ord(key[i % l]))
    return output_str

def other_xor(data, key):
    key = str(key)
    l = len(key)
    output_str = ""
    for i in range(len(data)):
        # current = data[i]
        # current_key = key[i % l]
        output_str += chr(data[i] ^ ord(key[i % l]))
    return output_str

def printCiphertext(ciphertext):
    print('{ 0x' + ', 0x'.join(hex(ord(x))[2:] for x in ciphertext) + ' };')



data = open("rs/reverseShell.py", "rb").read()
print(type(data))
encoded = base64.b64encode(data)

KEY = "xamy"

ciphertext = xor(encoded.decode(), KEY)
# print(ciphertext)
printCiphertext(ciphertext[10])


ordd=[ord(x) for x in ciphertext]
with open("chipher", "w") as f:
    l=" ".join(str(x) for x in ordd)
    f.write(l)
