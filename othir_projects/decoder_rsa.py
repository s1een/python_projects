import math
import random
import string
nalp = string.printable
alp = 'abcdefghijklmnopqrstuvwxyz 1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alp_ru = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя 1234567890АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
LANGUAGE = alp
def word_to_code(text,alp):
    k = []
    for i in text:
        k.append(alp.find(i))
    return k

def check_e(N):
    k = ([x for x in range(2, N) if not [n for n in range(2, x) if not x % n]])
    return random.choice(k)

def coding(number,public_key):
    tmp = pow(number,public_key[0])
    res = tmp % public_key[1]
    return res

def decoding(number,private_key):
    tmp = pow(number,private_key[0])
    res = tmp % private_key[1]
    return res

def word_coding(text, public_key):
    text = list(map(int,text))
    code_text = []
    coded = []
    for i in range(len(text)):
        code_text.append(coding(text[i],public_key))
    print(f"Your coded word: {code_text}")
    for k in code_text:
        if k > len(LANGUAGE):
            k = k % len(LANGUAGE)
            coded.append(LANGUAGE[k])
        else:
            coded.append(LANGUAGE[k])
    print(coded)
    return code_text

def word_decoding(text,private_key):
    decode_text = []
    for i in range(len(text)):
        decode_text.append(decoding(text[i],private_key))
    print(f"Your decoded word: {decode_text}")
    return decode_text

public_key = []
private_key = []
p,q = 7,13
#p,q = 31,37
n = q * p
el_func = (p - 1) * (q - 1)
e = check_e(n)
for i in range(1,n):
    d = ((i * el_func) + 1) / e
    if d.is_integer():
        break
d = int(d)
public_key.append(e) # 0
public_key.append(n) # 1
private_key.append(d) # 0
private_key.append(n) # 1
action = input("Select action:\n1 -> code ASCII text\n2 -> code num text\n:> ")
while action != 'exit':
    if action == '1':
        text = input("Enter your texe to code:> ")
        text = word_to_code(text,LANGUAGE)
        break
    elif action == '2':
        text = input("Enter code:> ").split()
        break
print(f"Public key: (n = {public_key[1]}, e = {public_key[0]})")
print(f"Private key: (n = {private_key[1]}, d = {private_key[0]})")
coded_text = word_coding(text,public_key)
decoded_text = word_decoding(coded_text,public_key)
text.clear()
for i in decoded_text:
    if i > len(LANGUAGE):
        k = i % len(LANGUAGE)
        text.append(LANGUAGE[k])
    text.append(LANGUAGE[i])
for i in text:
    print(i,end='')

