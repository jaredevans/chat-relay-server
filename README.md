# chat-relay-server
Chat relay server and chat client for 1:1 chat and open chatroom

Caution: Only for proof-of-concept and reference only. Do not use for production due to insecure code.

CLI client:

<img src="https://i.imgur.com/wHc0Sym.png" width=700 height=500>

Webapp client:

<img src="https://i.imgur.com/Aey37AF.png" width=700 height=400>


```
Async Chat Relay Server with CLI and Webapp Clients
A lightweight, self-hosted WebSocket-based chat relay server with:

1:1 chat via unique codes
Group chatroom mode
Live renaming and presence
WebRTC video chat between peers

Two client types: Web (browser) & CLI (Python)

Easy deployment with nginx reverse proxy & SSL

Features
1:1 Peer Chat:
Share your code with someone to chat privately.

Chatroom:
Join a group chat where all members see all messages.

WebRTC Video Calls:
Start real-time video calls with your 1:1 peer (browser client).

Rename Yourself:
Change your display name at any time, and it updates for your peer/chatroom.

CLI & Web Client:
Use in the terminal or via a modern web browser.

Simple Commands:
/join CODE, /chatroom, /list, /name NEWNAME, /quit

How It Works
The server acts as a relay for chat and WebRTC signals—no media relaying; video/audio flows directly between clients (peer-to-peer).

Clients connect via WebSockets:
Each client gets a random code and default name.
Connect to a friend by exchanging codes.

Supports text chat, renaming, group chat, and video chat (web only).

Quick Start
1. Clone the Repo
git clone https://github.com/yourusername/chat-relay-server.git
cd chat-relay-server

2. Run the Relay Server
Requirements:
Python 3.7+
websockets library (pip install websockets)

python relay_server.py
(Default: listens on 127.0.0.1:6789, use HTTPS web reverse proxy, such as nginx.)

3. Deploy Web Client
Copy index.html to your web server (e.g., /var/www/chat/index.html)

Edit the WebSocket URL in the HTML:
ws = new WebSocket("wss://yourdomain.com/ws/");

Access in your browser:
https://chat.yourdomain.com/

4. Use the CLI Client
Requirements:
Python 3.7+
websockets library (pip install websockets)

Edit the WebSocket URL (WS_URL) at the top of the client file to your server.
python cli_client.py

5. Secure with Nginx & SSL/TLS
Example nginx.conf:

server {
    listen 443 ssl http2;
    server_name chat.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/chat.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/chat.yourdomain.com/privkey.pem;
    ssl_session_cache shared:SSL:10m;

    location /ws/ {
        proxy_pass http://127.0.0.1:6789;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }

    root /var/www/chat;
    index index.html;
}

Usage (Web & CLI Clients)

Common Commands:
/join CODE — connect 1:1 using a peer’s code
/chatroom — join the group chatroom
/list — show who is in the chatroom
/name NEWNAME — change your display name
/quit — exit

Web Client:
Click “Start Video Chat” for a live call (works after you are paired 1:1).
Click “Hang Up” to end the call.

CLI Client:
Type commands or messages directly.

Security/Privacy
End-to-end media: WebRTC video/audio goes directly peer-to-peer.
No message history is stored; all chat is ephemeral in memory.
Each chat is private unless in chatroom mode.
Use SSL for safe, encrypted transport.

FAQ
Q: Can I use this behind NAT?
A: Yes! WebRTC will attempt peer-to-peer via public STUN servers (configurable in the web client).

Q: What browsers are supported?
A: Chrome, Firefox, Edge, Safari (recent versions).

Q: Is the server scalable?
A: Intended for small to medium group usage (family, classrooms, clubs, etc).```
