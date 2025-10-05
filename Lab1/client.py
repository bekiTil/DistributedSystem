# -*- coding:utf-8 -*-
import socket, threading, sys

ip_port = ('127.0.0.1', 9999)
ENC = 'utf-8'
BUF = 4096

def reader(sock):
    try:
        while True:
            data = sock.recv(BUF)
            if not data:
                print("[connection closed]")
                break
            for line in data.decode(ENC, errors="replace").splitlines():
                print(line)
    except OSError:
        pass
    finally:
      
        try:
            sock.close()
        except OSError:
            pass

def main():
    s = socket.socket()
    s.connect(ip_port)

   
    t = threading.Thread(target=reader, args=(s,), daemon=False)
    t.start()

    print("Commands: list | forward <ID> <message> | history <ID> | exit")
    try:
        for line in sys.stdin:
            msg = line.rstrip("\n")
            if not msg:
                continue
            s.sendall((msg + "\n").encode(ENC))

            if msg.lower() == "exit":
                break
    finally:
     
        pass

if __name__ == "__main__":
    main()
