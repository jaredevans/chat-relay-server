# **chat-relay-server**

Chat relay server for text and video chat, using websockets and WebRTC. Includes both CLI and web chat clients for one-on-one and group chat.

### ⚠️ Caution:
This project is for proof-of-concept, learning, and reference purposes only.
It is not secure for production and should not be exposed directly to the public Internet.

CLI client:

<img src="https://i.imgur.com/wHc0Sym.png" width=700 height=500>

Webapp client:

<img src="https://i.imgur.com/Wd8PxaE.png" width=700 height=600>

Video chat (between iPad [must run Safari] and Mac laptop [Google Chrome]):

<img src="https://jarednevans.wordpress.com/wp-content/uploads/2025/06/laptop_ipad_videochat.png" width=700 height=600>

**Overview**

This project implements a lightweight, async chat relay server supporting both text chat and peer-to-peer video chat. All messages and WebRTC signaling are relayed by a Python server using websockets. Media streams for video are sent peer-to-peer via WebRTC (the server never sees video or audio).

**The repo includes:**

* A Python relay server (relay_server.py) handling all WebSocket chat and WebRTC signaling.
* A Python command-line client (chat_client.py).
* A web client (index.html) supporting both text and video chat.
* Example nginx configuration for secure HTTPS reverse proxying to the chat relay server.

**How It Works**

Each client connecting to the server gets a unique code and random display name.

Users can chat one-on-one (by exchanging codes) or join a public chatroom for group messaging.

Users can change their display name, join or leave the chatroom, and view current members.

Video chat is one-on-one only, using WebRTC for a direct peer connection. The server just relays the setup information.

No data (messages, logs, etc.) are stored—everything is kept in server memory only.

**Features**

* Private, anonymous chat: No registration, no database, no saved logs.
* Text chat: 1:1 (using codes) or group chatroom.
* Video chat: 1:1 WebRTC between browser clients (modern browsers supported; iPad users must use Safari).
* Simple CLI client for text chat (cross-platform).
* Modern web client for text and video.
* User renaming and chatroom listing commands.
* Designed for deployment behind an HTTPS nginx reverse proxy.

**Getting Started**

Prerequisites

* Python 3.7 or higher
* websockets Python library (pip install websockets)
* nginx for HTTPS reverse proxy

**Running the Relay Server**

Start the server:

```python3 relay_server.py```

By default, it listens on 127.0.0.1:6789.

Note: For security, you should NOT expose this port directly. Use nginx to proxy WebSocket connections securely.

**Using the CLI Chat Client**

Edit WS\_URL at the top of chat\_client.py to match your deployment.

Run:

```python3 chat_client.py```

On startup, you’ll see your unique code and display name.

**Supported CLI Commands**

> /join CODE — Start a private chat with another user.
> 
> /name NEWNAME — Change your display name.
> 
> /chatroom — Join the shared group chatroom.
> 
> /list — Show chatroom members.
> 
> /quit — Disconnect.

**Using the Web Client**

Edit the WebSocket address in index.html to match your deployment (search for wss://).

Open index.html in a browser or place it in your server running nginx.

Use the UI for 1:1 or group chat, and to start/hang up video calls.

**Deploying with nginx Reverse Proxy (for HTTPS)**

Example nginx config:

```
server {
    listen 443 ssl;
    server_name chat.www.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location /ws/ {
        proxy_pass http://127.0.0.1:6789;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }

    location / {
        root /var/www/html;  # where index.html lives
    }
}
```
Replace chat.www.com with your own domain.

Avoid exposing the Python server port directly to public Internet.

**Security Notes**

* No authentication. Anyone who knows your server address can connect and obtain a code.
* No stored history or logs. All chat state is in memory only and lost when the server restarts.
* No input validation or sanitization. Vulnerable to many classes of attacks if exposed publicly.
* No access controls. All connected users are peers.
* NOT suitable for public or production use.
* Only expose via HTTPS using a reverse proxy, and keep server access private/restricted.
* For serious deployments, you must implement authentication, secure code review, and monitoring.


**Final Note:**

This project is for learning and demonstration only. Please do not use it for sensitive communications or expose it to untrusted users. If you want a production chat solution, look for a mature, audited project with proper security controls.
