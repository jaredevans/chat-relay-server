import asyncio
import websockets
import sys

WS_URL = "wss://chat.www.com/ws/"

async def main():
    peer_name = None
    my_name = None
    my_code = None
    in_chatroom = False
    quitting = False  # Track if user requested /quit

    try:
        async with websockets.connect(WS_URL) as ws:
            connected = await ws.recv()
            if connected.startswith("CONNECTED:"):
                parts = connected.split(":")
                my_code, my_name = parts[1], parts[2]
                print(f"Your unique chat code is: {my_code}")
                print(f"Your current name is: {my_name}")
                print("Give your code to your friend, or enter their code to chat.")
                print("Type /join CODE to connect, /name NEWNAME to rename, /chatroom to join the chatroom, /list to see chatroom members, /quit to exit.")
            else:
                print("Failed to connect.")
                return

            def show_info():
                print(f"Your chat code is: {my_code}, your name is: {my_name}")

            async def send_input():
                nonlocal in_chatroom, quitting, my_name
                while True:
                    user_input = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                    user_input = user_input.strip()
                    if user_input.startswith("/join "):
                        join_code = user_input.split(" ", 1)[1]
                        await ws.send(f"JOIN:{join_code}")
                        in_chatroom = False
                    elif user_input.startswith("/name "):
                        new_name = user_input.split(" ", 1)[1]
                        await ws.send(f"RENAME:{new_name}")
                        my_name = new_name
                        show_info()
                        print(f"[You are now known as: {my_name}]")
                    elif user_input == "/chatroom":
                        await ws.send("/chatroom")
                        in_chatroom = True
                    elif user_input == "/list":
                        await ws.send("/list")
                    elif user_input == "/quit":
                        await ws.send("LEAVE")
                        quitting = True
                        print("Leaving... (waiting for confirmation from server)")
                        await ws.close()
                        break  # Stop sending input, but let receive() handle closure
                    else:
                        await ws.send(f"MSG:{user_input}")
                        print(f"You: {user_input}")  # Echo your own message

            async def receive():
                nonlocal peer_name, in_chatroom, quitting
                while True:
                    try:
                        msg = await ws.recv()
                    except websockets.ConnectionClosed:
                        print("Connection closed.")
                        break
                    if msg.startswith("PAIR:"):
                        _, code, name = msg.split(":", 2)
                        peer_name = name
                        in_chatroom = False
                        print(f"\n[Connected! You are chatting with {peer_name} (code {code})]\n")
                    elif msg.startswith("MSGFROM:"):
                        _, sender, text = msg.split(":", 2)
                        peer_name = sender  # Keep peer_name in sync
                        print(f"{sender}: {text}")
                    elif msg.startswith("RENAMED:"):
                        new_name = msg.split(":", 1)[1]
                        peer_name = new_name
                        print(f"\n[Your chat partner is now known as: {new_name}]\n")
                    elif msg == "PEER_LEFT":
                        print("\n[Your chat partner disconnected. Type /join CODE to connect to another.]\n")
                        peer_name = None
                        in_chatroom = False
                    elif msg == "PEER_LEFT_CHATROOM":
                        print("\n[Your chat partner has left for the chatroom.]\n")
                        peer_name = None
                        in_chatroom = False
                    elif msg.startswith("CHATROOM:"):
                        _, sender, text = msg.split(":", 2)
                        print(f"[{sender} @ chatroom]: {text}")
                    elif msg.startswith("INFO:"):
                        print(f"[Info] {msg[5:]}")
                        # Wait for leave confirmation before closing
                        if quitting and (
                            msg[5:].startswith("You left the chatroom.") or
                            msg[5:].startswith("You left") or
                            msg[5:].startswith("You are now in the chatroom.")  # safety if order changes
                        ):
                            await ws.close()
                            break
                    elif msg.startswith("ERROR:"):
                        print(f"[ERROR] {msg[6:]}")
                    else:
                        print(f"[Server] {msg}")

            await asyncio.gather(send_input(), receive())

    except (websockets.exceptions.InvalidStatus, OSError, ConnectionRefusedError, websockets.exceptions.WebSocketException):
        print("Server isn't available. Please check your internet connection or try again later.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting.")

