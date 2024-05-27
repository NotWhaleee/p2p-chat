import re
import threading
import socket

PORT = 8080

def message_listener() -> None:
    try:
        listener_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listener_socket.bind(('', PORT))
    except Exception as error:
        print(f'Failed to bind socket: {error}')
        return

    while True:
        try:
            data, address = listener_socket.recvfrom(1024)
            if data:
                print(f'Message from {address[0]}: {data.decode()}')
            else:
                listener_socket.close()
                break
        except Exception as error:
            print(f'Error receiving message: {error}')
            listener_socket.close()
            break

def send_direct_message(message: str, address: str) -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as direct_socket:
            direct_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            direct_socket.sendto(message.encode(), (address, PORT))
    except Exception as error:
        print(f'Failed to send message: {error}')

def send_broadcast_message(message: str) -> None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as broadcast_socket:
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcast_socket.sendto(message.encode(), ('255.255.255.255', PORT))
    except Exception as error:
        print(f'Failed to broadcast message: {error}')

def process_message_input(message: str) -> None:
    if message.startswith('to:'):
        match = re.match(r"^to:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", message)
        if match:
            ip_address = match.group(1)
            message_content = message[len(match.group(0)):].strip()
            send_direct_message(message_content, ip_address)
        else:
            print('Invalid format. Use "to:ipaddress message"')
    else:
        send_broadcast_message(message)

def start_client() -> None:
    try:
        threading.Thread(target=message_listener, daemon=True).start()
        while True:
            user_message = input()
            if user_message.lower() in {'quit', 'q'}:
                break
            process_message_input(user_message)
    except Exception as error:
        print(f'An error occurred: {error}')

if __name__ == "__main__":
    start_client()
