import asyncio
import websockets
import secrets
import string

PORT = 6789

clients = {}  # code: {ws, name, peer, in_chatroom}
chatroom = set()  # Set of client codes in the chatroom

def random_name():
    return "client_" + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))

def generate_code():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

async def relay_message(peer_ws, msg):
    try:
        await peer_ws.send(msg)
    except:
        pass

async def broadcast_chatroom(sender_code, msg):
    sender_name = clients[sender_code]['name']
    for code in list(chatroom):
        if code != sender_code and code in clients:
            peer_ws = clients[code]['ws']
            await relay_message(peer_ws, f"CHATROOM:{sender_name}:{msg}")

async def broadcast_chatroom_notice(leaving_code, notice_text):
    for code in list(chatroom):
        if code != leaving_code and code in clients:
            peer_ws = clients[code]['ws']
            await relay_message(peer_ws, f"INFO:{notice_text}")

async def handler(websocket):
    code = generate_code()
    name = random_name()
    clients[code] = {'ws': websocket, 'name': name, 'peer': None, 'in_chatroom': False}
    print(f"[+] Client connected: {name} (code: {code})")
    await websocket.send(f"CONNECTED:{code}:{name}")

    try:
        async for message in websocket:
            if message.startswith("JOIN:"):
                other_code = message[5:]

                # Remove self from chatroom (if in it)
                if clients[code]['in_chatroom']:
                    chatroom.discard(code)
                    clients[code]['in_chatroom'] = False
                    await websocket.send("INFO:You left the chatroom for 1:1 chat.")

                # Remove target peer from chatroom (if in it)
                if other_code in clients and clients[other_code]['in_chatroom']:
                    chatroom.discard(other_code)
                    clients[other_code]['in_chatroom'] = False
                    peer_ws = clients[other_code]['ws']
                    await relay_message(peer_ws, "INFO:You left the chatroom for 1:1 chat.")

                # If already in 1:1, disconnect from old peer.
                old_peer = clients[code]['peer']                                                                                        if old_peer and old_peer in clients:
                    peer_ws = clients[old_peer]['ws']
                    await relay_message(peer_ws, "PEER_LEFT")
                    clients[old_peer]['peer'] = None
                clients[code]['peer'] = None

                # Proceed to 1:1 pairing
                if other_code in clients and clients[other_code]['peer'] is None:
                    clients[other_code]['peer'] = code
                    clients[code]['peer'] = other_code
                    peer_ws = clients[other_code]['ws']
                    peer_name = clients[other_code]['name']
                    print(f"[=] {clients[code]['name']} (code: {code}) joined chat with {peer_name} (code: {other_code})")
                    await websocket.send(f"PAIR:{other_code}:{peer_name}")
                    await peer_ws.send(f"PAIR:{code}:{clients[code]['name']}")
                else:
                    await websocket.send("ERROR:Invalid or busy code")

            elif message.startswith("MSG:"):
                msg_text = message[4:]
                if clients[code]['in_chatroom']:
                    await broadcast_chatroom(code, msg_text)
                else:
                    peer_code = clients[code]['peer']
                    if peer_code and peer_code in clients:
                        peer_ws = clients[peer_code]['ws']
                        await relay_message(peer_ws, f"MSGFROM:{clients[code]['name']}:{msg_text}")

            elif message.startswith("RENAME:"):
                new_name = message[7:]
                old_name = clients[code]['name']
                clients[code]['name'] = new_name
                print(f"[~] Client {old_name} (code: {code}) renamed to {new_name}")
                peer_code = clients[code]['peer']
                if peer_code and peer_code in clients:
                    peer_ws = clients[peer_code]['ws']
                    await relay_message(peer_ws, f"RENAMED:{new_name}")
            elif message == "LEAVE":
                if clients[code]['in_chatroom']:
                    # Notify other chatroom members BEFORE removing from chatroom
                    notice_text = f"{clients[code]['name']} (code: {code}) has disconnected from the chatroom."
                    await broadcast_chatroom_notice(code, notice_text)
                    chatroom.discard(code)
                    clients[code]['in_chatroom'] = False
                    await websocket.send("INFO:You left the chatroom.")
                peer_code = clients[code]['peer']
                if peer_code and peer_code in clients:
                    peer_ws = clients[peer_code]['ws']
                    print(f"[-] {clients[code]['name']} (code: {code}) left chat with {clients[peer_code]['name']} (code: {peer_code})")
                    await relay_message(peer_ws, "PEER_LEFT")
                    clients[peer_code]['peer'] = None
                clients[code]['peer'] = None

            elif message == "/chatroom":
                # Leave 1:1 chat if in one
                old_peer = clients[code]['peer']
                if old_peer and old_peer in clients:
                    peer_ws = clients[old_peer]['ws']
                    await relay_message(peer_ws, "PEER_LEFT_CHATROOM")
                    clients[old_peer]['peer'] = None
                clients[code]['peer'] = None
                # Add to chatroom
                chatroom.add(code)
                clients[code]['in_chatroom'] = True
                print(f"[@] {clients[code]['name']} (code: {code}) joined chatroom.")
                await websocket.send("INFO:You are now in the chatroom. Type messages to chat with everyone here.")

            elif message == "/list":
                member_lines = []
                for member_code in chatroom:
                    member = clients.get(member_code)
                    if member:
                        member_line = f"{member['name']} (code: {member_code})"
                        if member_code == code:
                            member_line += " [you]"
                        member_lines.append(member_line)
                if member_lines:
                    list_text = "Members in chatroom:\n" + "\n".join(member_lines)
                else:
                    list_text = "No one is currently in the chatroom."
                await websocket.send(f"INFO:{list_text}")

            # --- WebRTC/Video Signaling relay, including hangup ---
            elif (
                message == "VIDEO_PLEASE_START"
                or message.startswith("VIDEO_OFFER:")
                or message.startswith("VIDEO_ANSWER:")
                or message.startswith("VIDEO_ICE:")
                or message == "VIDEO_HANGUP"
            ):
                peer_code = clients[code]['peer']
                if peer_code and peer_code in clients:
                    peer_ws = clients[peer_code]['ws']
                    await relay_message(peer_ws, message)

    except Exception as e:
        print(f"[!] Exception for client {clients[code]['name']} (code: {code}): {e}")
    finally:
        # Notify 1:1 peer
        peer_code = clients[code]['peer']
        if peer_code and peer_code in clients:
            peer_ws = clients[peer_code]['ws']
            await relay_message(peer_ws, "PEER_LEFT")
            clients[peer_code]['peer'] = None
        # Notify chatroom BEFORE removing from set!
        if clients[code]['in_chatroom']:
            notice_text = f"{clients[code]['name']} (code: {code}) has disconnected from the chatroom."
            await broadcast_chatroom_notice(code, notice_text)
            chatroom.discard(code)
        print(f"[*] Client disconnected: {clients[code]['name']} (code: {code})")
        if code in clients:
            del clients[code]

async def main():
    async with websockets.serve(handler, "127.0.0.1", PORT):
        print(f"Relay server running on ws://127.0.0.1:{PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
