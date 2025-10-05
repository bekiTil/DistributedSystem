# Lab 1 — TCP Chat (Server + Client)

This repo contains a minimal, rubric-aligned TCP chat system you can run locally or on GCP. It implements:
- Unique IDs per client (sent on connect)
- Commands: `list`, `forward <ID> <message>`, `history <ID>`, `exit`
- Forwarded message format: `sourceID: message_content`
- Multi-client concurrency (threads) and per-pair chat history

## Quick start (local)
Terminal 1:

```bash
python3 server.py
````


Terminal 2:

```bash
python3 client.py
```

Terminal 3:

```bash
python3 client.py
```

## Commands

```
list
forward <ID> <message>
history <ID>
exit
```

```
```
