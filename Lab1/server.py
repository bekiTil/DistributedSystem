# -*- coding:utf-8 -*-

import socket
import threading
from datetime import datetime


ip_port = ('0.0.0.0', 9999)
ENC = 'utf-8'
BUF = 4096
BACKLOG = 50

# ---- Shared state (guarded by locks) ----
next_id = 1
id_lock = threading.Lock()

clients = {}           
clients_lock = threading.Lock()

history = {}          
history_lock = threading.Lock()




def assign_id():
    global next_id
    with id_lock:
        cid = next_id
        next_id += 1
        return cid


def write_line(sock, text):
    try:
        sock.sendall((text + "\n").encode(ENC))
    except OSError:
        pass


def record_history(src_id, dst_id, content):
    key = frozenset({src_id, dst_id})
    ts = datetime.now().isoformat(timespec="seconds") + "Z"
    line = f"{src_id} -> {dst_id} @ {ts}: {content}"
    with history_lock:
        history.setdefault(key, []).append(line)


def get_history(a, b):
    key = frozenset({a, b})
    with history_lock:
        return list(history.get(key, []))


def list_client_ids():
    with clients_lock:
        return sorted(clients.keys())


def get_client_socket(cid):
    with clients_lock:
        info = clients.get(cid)
        return info[0] if info else None


def unregister(cid):
    with clients_lock:
        clients.pop(cid, None)


def link_handler(conn, addr, cid):
    # Send assigned ID immediately
    write_line(conn, f"ASSIGNED {cid}")

    # Simple line-buffered receive loop
    buffer = ""
    try:
        while True:
            chunk = conn.recv(BUF)
            if not chunk:
                break
            buffer += chunk.decode(ENC, errors="replace") 
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                parts = line.split(maxsplit=2)
                cmd = parts[0].lower()

                if cmd == "list":
                    ids = list_client_ids()
                    write_line(conn, "CLIENTS " + " ".join(map(str, ids)))

                elif cmd == "forward":
                    # forward <ID> <message...>
                    if len(parts) < 3:
                        write_line(conn, "ERR usage: forward <ID> <message>")
                        continue
                    try:
                        dst_id = int(parts[1])
                    except ValueError:
                        write_line(conn, "ERR target ID must be an integer")
                        continue
                    msg = parts[2]
                    dst_sock = get_client_socket(dst_id)
                    if dst_sock is None:
                        write_line(conn, "ERR no such client")
                        continue

                    # Deliver and ack
                    write_line(dst_sock, f"{cid}: {msg}")
                    write_line(conn, "OK delivered")
                    record_history(cid, dst_id, msg)

                elif cmd == "history":
                    # history <ID>
                    if len(parts) < 2:
                        write_line(conn, "ERR usage: history <ID>")
                        continue
                    try:
                        other_id = int(parts[1])
                    except ValueError:
                        write_line(conn, "ERR target ID must be an integer")
                        continue
                    lines = get_history(cid, other_id)
                    if not lines:
                        write_line(conn, "NO_HISTORY")
                    else:
                        for h in lines:
                            write_line(conn, h)
                    write_line(conn, "END OF_HISTORY")

                elif cmd == "exit":
                    write_line(conn, "Goodbye")
                    conn.close()
                    unregister(cid)
                    return

                else:
                    write_line(conn, "ERR unknown command")

    except ConnectionResetError:
        pass
    finally:
        try:
            conn.close()
        except OSError:
            pass
        unregister(cid)
        print(f"Client {cid} disconnected: {addr}")


def main():
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
    sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sk.bind(ip_port)
    sk.listen(BACKLOG)
    print('start socket server，waiting client...')

    while True:
        conn, address = sk.accept()
        cid = assign_id()
        with clients_lock:
            clients[cid] = (conn, address)
        print('create a new thread for client [%s:%s] -> ID %d' % (address[0], address[1], cid))
        t = threading.Thread(target=link_handler, args=(conn, address, cid), daemon=True)
        t.start()


if __name__ == "__main__":
    main()
