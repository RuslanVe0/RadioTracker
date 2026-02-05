import ffmpeg
import copy
from httplib._socket import socket
import utils.utils



class httplib(object):
    
    def __init__(self, host: str, path: str, port: int) -> None:
        self.host: str = host
        self.path = path
        self.socket = socket.create_socket(host, port)
        self.payload: str = ""
    
    def __repr__(self):
        return f"<httplib host={self.host} path={self.path}>"
    
    def create_request_get(self):
        http_header: str = f"GET /{self.path} HTTP/1.1\r\x0AHost: {self.host}\r\x0AUser-Agent: Python/RadioTracker\r\x0AConnection: close\r\x0AAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\x0A\r\x0A"
        self.socket.send(http_header.encode("utf-8", errors = "ignore"))
        for _ in range(0, 2, 1):
            self.payload += self.socket.recv(8192).decode("utf-8", errors = "ignore")
        return self
    
    def work(self):
        self.payload = self.payload.split("\r\x0A\r\x0A")[1]
        return self

    
    def create_request_file(self, constructor):
        http_header: str = f"GET /{self.path} HTTP/1.1\r\x0AHost: {self.host}\r\x0AUser-Agent: Python/RadioTracker\r\x0AConnection: close\r\x0AAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\x0A\r\x0A"
        self.socket.send(http_header.encode("utf-8", errors = "ignore"))
        data: bytes = self.socket.recv(4096)
        received: bytes = data.split(b"\r\x0A\r\x0A")[1]
        for _ in range(0, 1000, 1):
            try:
                data = self.socket.recv(4096)
            except OSError or Exception as exception:
                print("[-] Downloading failed. Could not download data.")
                return False
            received += data
        return received
    
    def create_request_stream(self, constructor, writing_pipe, path: str):
        http_header: str = f"GET /{self.path} HTTP/1.1\r\x0AHost: {self.host}\r\x0AUser-Agent: Python/RadioTracker\r\x0AConnection: close\r\x0AAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\x0A\r\x0A"
        self.socket.send(http_header.encode("utf-8", errors = "ignore"))
        data: bytes = self.socket.recv(4096).split(b"\r\x0A\r\x0A")[1]
        old_constructor = copy.deepcopy(constructor)
        print("[+] Downloading full audio...")
        total_downloaded: int = 0
        counter: int = 0
        while constructor.current_artist == old_constructor.current_artist and constructor.current_song == old_constructor.current_song:
            try:
                data = self.socket.recv(4096)
            except OSError or Exception as exception:
                print("[-] Downloading failed. Could not download data.")
                return
            if not data:
                writing_pipe.close()
            if not counter % 1200:
                print(f"[+] Total {total_downloaded}-bytes downloaded ({old_constructor.current_artist} - {old_constructor.current_song}).")
            writing_pipe.write(data)
            total_downloaded += len(data)
            counter += 5