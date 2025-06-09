import asyncio
import websockets
import json
import secrets
import string

PORT = 6789

clients = {}  # code: {ws, name, peer, in_chatroom}
chatroom = set()  # Set of client codes in the chatroom

def random_name():
    return "client_" + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))

def generate_code():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

async def relay_message(peer_ws, data_dict):
    try:
        await peer_ws.send(json.dumps(data_dict))
    except:
        pass

async def broadcast_chatroom(sender_code, msg_text):
    sender_name = clients[sender_code]['name']
    message = {"type": "CHATROOM", "payload": {"sender": sender_name, "text": msg_text}}
    for code_in_room in list(chatroom):
        if code_in_room != sender_code and code_in_room in clients:
            peer_ws = clients[code_in_room]['ws']
            await relay_message(peer_ws, message)

async def broadcast_chatroom_notice(leaving_code, notice_text):
    message = {"type": "INFO", "payload": {"message": notice_text}}
    for code_in_room in list(chatroom):
        if code_in_room != leaving_code and code_in_room in clients:
            peer_ws = clients[code_in_room]['ws']
            await relay_message(peer_ws, message)

async def handler(websocket):
    code = generate_code()
    name = random_name()
    clients[code] = {'ws': websocket, 'name': name, 'peer': None, 'in_chatroom': False}
    print(f"[+] Client connected: {name} (code: {code})")
    await websocket.send(json.dumps({"type": "CONNECTED", "payload": {"code": code, "name": name}}))

    try:
        async for message_str in websocket:
            try:
                message = json.loads(message_str)
            except json.JSONDecodeError:
                print(f"[!] Received non-JSON message from {clients[code]['name']}: {message_str}")
                await relay_message(websocket, {"type": "ERROR", "payload": {"message": "Invalid JSON format."}})
                continue

            msg_type = message.get('type')
            payload = message.get('payload', {})

            if msg_type == "JOIN":
                other_code = payload.get('code')

                # Remove self from chatroom (if in it)
                if clients[code]['in_chatroom']:
                    chatroom.discard(code)
                    clients[code]['in_chatroom'] = False
                    await websocket.send(json.dumps({"type": "INFO", "payload": {"message": "You left the chatroom for 1:1 chat."}}))

                # Remove target peer from chatroom (if in it)
                if other_code in clients and clients[other_code]['in_chatroom']:
                    chatroom.discard(other_code)
                    clients[other_code]['in_chatroom'] = False
                    peer_ws = clients[other_code]['ws']
                    await relay_message(peer_ws, {"type": "INFO", "payload": {"message": "You left the chatroom for 1:1 chat."}})

                # If already in 1:1, disconnect from old peer.
                old_peer = clients[code]['peer']
                if old_peer and old_peer in clients:
                    peer_ws = clients[old_peer]['ws']
                    await relay_message(peer_ws, {"type": "PEER_LEFT", "payload": {}})
                    clients[old_peer]['peer'] = None
                clients[code]['peer'] = None

                # Proceed to 1:1 pairing
                if other_code in clients and clients[other_code]['peer'] is None:
                    clients[other_code]['peer'] = code
                    clients[code]['peer'] = other_code
                    peer_ws = clients[other_code]['ws']
                    peer_name = clients[other_code]['name']
                    print(f"[=] {clients[code]['name']} (code: {code}) joined chat with {peer_name} (code: {other_code})")
                    await websocket.send(json.dumps({"type": "PAIR", "payload": {"code": other_code, "name": peer_name}}))
                    await relay_message(peer_ws, {"type": "PAIR", "payload": {"code": code, "name": clients[code]['name']}})
                else:
                    await websocket.send(json.dumps({"type": "ERROR", "payload": {"message": "Invalid or busy code"}}))

            elif msg_type == "MSG":
                msg_text = payload.get('text')
                if not msg_text: continue # Ignore empty messages

                if clients[code]['in_chatroom']:
                    await broadcast_chatroom(code, msg_text)
                else:
                    peer_code = clients[code]['peer']
                    if peer_code and peer_code in clients:
                        peer_ws = clients[peer_code]['ws']
                        await relay_message(peer_ws, {"type": "MSGFROM", "payload": {"sender": clients[code]['name'], "text": msg_text}})

            elif msg_type == "RENAME":
                new_name = payload.get('newName')
                if not new_name: continue

                old_name = clients[code]['name']
                clients[code]['name'] = new_name
                print(f"[~] Client {old_name} (code: {code}) renamed to {new_name}")
                peer_code = clients[code]['peer']
                if peer_code and peer_code in clients:
                    peer_ws = clients[peer_code]['ws']
                    await relay_message(peer_ws, {"type": "RENAMED", "payload": {"newName": new_name}})

            elif msg_type == "LEAVE":
                if clients[code]['in_chatroom']:
                    # Notify other chatroom members BEFORE removing from chatroom
                    notice_text = f"{clients[code]['name']} (code: {code}) has disconnected from the chatroom."
                    await broadcast_chatroom_notice(code, notice_text)
                    chatroom.discard(code)
                    clients[code]['in_chatroom'] = False
                    await websocket.send(json.dumps({"type": "INFO", "payload": {"message": "You left the chatroom."}}))
                peer_code = clients[code]['peer']
                if peer_code and peer_code in clients:
                    peer_ws = clients[peer_code]['ws']
                    print(f"[-] {clients[code]['name']} (code: {code}) left chat with {clients[peer_code]['name']} (code: {peer_code})")
                    await relay_message(peer_ws, {"type": "PEER_LEFT", "payload": {}})
                    clients[peer_code]['peer'] = None
                clients[code]['peer'] = None

            elif msg_type == "/chatroom": # Client commands can be simple types if payload isn't strictly needed
                # Leave 1:1 chat if in one
                old_peer = clients[code]['peer']
                if old_peer and old_peer in clients:
                    peer_ws = clients[old_peer]['ws']
                    await relay_message(peer_ws, {"type": "PEER_LEFT_CHATROOM", "payload": {}})
                    clients[old_peer]['peer'] = None
                clients[code]['peer'] = None
                # Add to chatroom
                chatroom.add(code)
                clients[code]['in_chatroom'] = True
                print(f"[@] {clients[code]['name']} (code: {code}) joined chatroom.")
                await websocket.send(json.dumps({"type": "INFO", "payload": {"message": "You are now in the chatroom. Type messages to chat with everyone here."}}))

            elif msg_type == "/list": # Client commands can be simple types
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
                await websocket.send(json.dumps({"type": "INFO", "payload": {"message": list_text}}))

            # --- WebRTC/Video Signaling relay ---
            # These messages now expect a 'payload' field containing the actual signal data
            elif msg_type in ["VIDEO_PLEASE_START", "VIDEO_OFFER", "VIDEO_ANSWER", "VIDEO_ICE", "VIDEO_HANGUP"]:
                peer_code = clients[code]['peer']
                if peer_code and peer_code in clients:
                    peer_ws = clients[peer_code]['ws']
                    # The whole 'message' (which is a dict now) is relayed.
                    # relay_message will handle json.dumps()
                    await relay_message(peer_ws, message)
                else:
                    await websocket.send(json.dumps({"type": "ERROR", "payload": {"message": "Not paired with anyone for video chat."}}))


    except Exception as e:
        print(f"[!] Exception for client {clients[code]['name']} (code: {code}): {e}")
    finally:
        # Notify 1:1 peer
        peer_code = clients[code]['peer']
        if peer_code and peer_code in clients:
            peer_ws = clients[peer_code]['ws']
            await relay_message(peer_ws, {"type": "PEER_LEFT", "payload": {}})
            clients[peer_code]['peer'] = None
        # Notify chatroom BEFORE removing from set!
        if clients[code]['in_chatroom']:
            notice_text = f"{clients[code]['name']} (code: {code}) has disconnected from the chatroom."
            await broadcast_chatroom_notice(code, notice_text) # This now sends JSON
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
