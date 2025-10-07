# Lab 1 — TCP Chat (Server + Client)

TCP chat you can run **locally** or on **GCP VMs**.

**Features**

* Unique ID per client (sent on connect)
* Commands: `list`, `forward <ID> <message>`, `history <ID>`, `exit`
* Forward format: `sourceID: message_content`
* Multi-client concurrency (threads) + per-pair chat history

---

## Files

```
server.py   # Multi-client threaded TCP server (binds 0.0.0.0:9999)
client.py   # Interactive client with async reader (--host/--port)
```


---

## Quick Start — Local (same machine)

**Terminal 1 (server):**

```bash
python3 server.py
# prints: "Server listening on 0.0.0.0:9999 ..."
```

**Terminal 2 (client 1):**

```bash
python3 client.py --host 127.0.0.1 --port 9999
```

**Terminal 3 (client 2):**

```bash
python3 client.py --host 127.0.0.1 --port 9999
```

---

## Quick Start — VMs (same VPC/subnet)

**On server VM:**

```bash
python3 server.py    # binds 0.0.0.0:9999
```

Find internal IP (e.g., `10.128.x.y`) via `hostname -I` or the cloud console.

**On each client VM:**

```bash
python3 client.py --host 10.128.x.y --port 9999
```

> If it times out: ensure a VPC firewall rule allows **TCP 9999** from client subnet(s).
> Default GCP networks usually allow internal traffic.

---

## Commands (type in client)

```
list
forward <ID> <message>
history <ID>
exit
```

**Expected responses**

* `list` → `CLIENTS 1 2 ...`
* `forward 2 hi` → on target: `1: hi`; on sender: `OK delivered`
* `history 2` → lines, then `END OF_HISTORY`
* `exit` → `Goodbye` then `[connection closed]`

---

## Sample Session

Client A:

```
list
# CLIENTS 1 2
forward 2 hello there
# OK delivered
history 2
# 1 -> 2 @ 2025-10-05T12:00:00Z: hello there
# END OF_HISTORY
exit
# Goodbye
# [connection closed]
```

Client B sees:

```
ASSIGNED 2
1: hello there
```

---

## Notes

* Server listens on **0.0.0.0** so local **and** remote clients can connect.
* Use **internal IPs** (`10.*`) for VMs in the same VPC.
* Client flags: `--host <ip/hostname> --port <num>`.

---
