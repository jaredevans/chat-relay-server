# chat-relay-server
Chat relay server and chat client for 1:1 chat and open chatroom

Caution: Only for proof-of-concept and reference only. Do not use for production due to insecure code.

CLI client:

<img src="https://i.imgur.com/wHc0Sym.png" width=700 height=500>

Webapp client:

<img src="https://i.imgur.com/Wd8PxaE.png" width=700 height=600>

Video chat (between iPad [must run Safari] and Mac laptop [Google Chrome]):

<img src="https://i.imgur.com/OvH4tAP.jpeg" width=700 height=600>

```
Async Chat Relay Server with Text and Video Chat, with CLI and webapp clients

Overview:
This project is a lightweight chat relay server that supports both text chat and peer-to-peer video chat.
It’s designed to be self-hosted and easy to run, requiring minimal dependencies.
The server acts as a signaling relay for chat messages and for exchanging WebRTC information (for video),
but does not relay video or audio data—all media streams go directly between users’ browsers
using secure peer-to-peer connections.

The project includes:

A Python relay server for handling WebSocket chat and WebRTC signaling.

A cross-platform command-line client (Python).

A modern, easy-to-use web client with both text chat and video chat capability.

Also provided is an example configuration for using nginx as a secure HTTPS reverse proxy.

How It Works:
Each user who connects gets a unique code and a random display name.
Users can chat one-on-one by exchanging codes, or join a shared chatroom.
You can change your display name, join or leave the chatroom, and see who else is in the chatroom.

For video chat, users connect in a private one-on-one session. The server relays the WebRTC offer/answer/ICE candidates,
but the actual video stream is peer-to-peer.

Features:
Private, no account registration or central user database.
Text chat: one-on-one (via code) or group (via chatroom).
Video chat: one-on-one only, using WebRTC (works in all modern browsers).
Simple Python CLI client for desktop chat.
Web client for text + video chat.
User renaming and chatroom listing.
Secure deployment using HTTPS with nginx reverse proxy.

Getting Started:
1. Prerequisites
Python 3.7 or higher
The websockets Python library (pip install websockets)
nginx configuration for HTTPS reverse proxy

2. Running the Relay Server
Start the server with:
python3 relay_server.py

By default, it listens on 127.0.0.1:6789 - use nginx reverse proxy make it accessible to others.

3. Using the CLI Chat Client
Save the client script as chat_client.py.
Edit the WS_URL at the top of the script if necessary to match your deployment.

Run with:
python3 chat_client.py

The client will print your unique code and display name. Share your code with a friend or
enter someone else's code to connect.

Supported CLI Commands:
/join CODE — Start a private chat with another user (use their code).
/name NEWNAME — Change your display name.
/chatroom — Join the shared chatroom (group text).
/list — Show list of chatroom members.
/quit — Disconnect.

4. Using the Web Client
Save the HTML file and open it in a modern browser (Chrome, Firefox, Edge, Safari).
The web client connects via WebSocket to /ws/ and allows:

One-on-one text chat (by code)
Group chatroom text chat
One-on-one video calls (WebRTC)

Click “Start Video Chat” to request a 1:1 video call with your chat partner.
Click “Hang Up” to end the video call.

5. Deploying with nginx Reverse Proxy (for HTTPS)
Use the provided nginx config example (replace chat.www.com with your domain).
Set up SSL/TLS with your certificates for HTTPS.

Place the file index.html in the web root.

Security Notes:
The server is intended for small private use (friends, small groups, testing).
No message history is stored. All state is in memory only.
There is no user authentication; anyone who knows your server address can connect and get a code.
Caution: This was more of a learning experience for me. The code, while functional,
has not undergone a security review and is vulnerable to being exploited.
*** Do not continually expose to public Internet. ***
```
