# chat-relay-server
Chat relay server and chat client for 1:1 chat and open chatroom

Caution: Only for proof-of-concept and reference only. Do not use for production due to insecure code.

CLI client:

<img src="https://i.imgur.com/wHc0Sym.png" width=700 height=500>

Webapp client:

<img src="https://i.imgur.com/TuWmUjI.png" width=700 height=500>


```
Async Python Chat Relay

A simple asynchronous chat relay server and command-line client written in Python using websockets and asyncio.
Supports both private 1:1 chat (using unique codes) and public chatrooms with multiple participants.

Features
WebSocket-based: Real-time communication with low latency.
Unique chat codes: Easily connect privately to friends or colleagues.
Simple chatroom: Join a shared group chat anytime.
Rename yourself: Change your display name on the fly.

Project Structure

chat-relay/
├── relay_server.py   # WebSocket relay server
├── chat_client.py    # Command-line chat client
├── index.html        # Webapp chat client

Getting Started

1. Install requirements
pip install websockets

2. Run the Relay Server
On your server or local machine:

python relay_server.py

The server will listen on ws://127.0.0.1:6789 by default.

3. Configure your webserver:
See accompanying nginx conifguration to proxy the websocket traffic.

3. Run the Client for CLI and Web
On any computer with python installed:

python chat_client.py

Edit WS_URL at the top of chat_client.py if connecting to a remote server.

Copy index.html to the web root directory for the chat webapp on your web server.

How It Works
When you connect, you receive a unique code (e.g., H3X8E2JK) and a default name.
Share your code with someone else so they can connect to you for a private 1:1 chat.

You can also join a public chatroom to talk with everyone else in the room.

Client Commands
You can enter these commands at any time in the chat client:

Command	Description
/join CODE	Connect to another user for private 1:1 chat. Replace CODE with their code.
/name NEWNAME	Change your display name to NEWNAME.
/chatroom	Leave private chat (if any) and join the group chatroom.
/list	Show a list of current chatroom members.
/quit	Cleanly leave chat (from chatroom or 1:1) and exit the client.
(any message)	Send message to current chat (1:1 or chatroom).

Example Usage
Private 1:1 Chat
User A starts a client, gets a code (e.g., ABCD1234), shares it with User B.
User B starts a client, runs /join ABCD1234.
Both users are connected privately. Type messages as you wish.

Chatroom
Type /chatroom to join the public chatroom.
Anyone else in the chatroom will see your messages.

Type /list to see who else is there.

Renaming
Type /name MyCoolName to change how you appear to others.

Graceful Disconnects
/quit safely exits the chat and notifies others (chat partner or chatroom).
If you close the client with Ctrl-C, the server will also notify others of your departure.

Notes
The server is a relay only. It does not store messages or logs.

All chat is ephemeral (disappears if server restarts or users disconnect).

Server output is printed to the terminal for monitoring.

Security & Privacy
No authentication: anyone with access to the server can join.
Codes are randomly generated to reduce accidental collisions, but not cryptographically secure.
Do not use for sensitive data.
```
