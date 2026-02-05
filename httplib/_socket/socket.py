from socket import socket, AF_INET, SOCK_STREAM
import ssl


def create_socket(host: str, port: int):
    _new_sock: socket = socket(AF_INET, SOCK_STREAM)
    _new_sock.connect((host.strip(), port))
    if port == 443:
        context = ssl.create_default_context()
        _new_sock = context.wrap_socket(_new_sock, server_hostname = host)
    return _new_sock