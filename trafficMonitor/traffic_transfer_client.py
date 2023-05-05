import json
import socket
import time

import config


class Client:
    tcp_port = None
    s = None  # socket

    def __init__(self, tcp_port):
        self.tcp_port = tcp_port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((config.get_ip(), tcp_port))
        print(self.s.recv(config.BUFFER_SIZE).decode())
        send_data = {'opt_type': 0}
        send_json = json.dumps(send_data)
        self.s.send(send_json.encode())


    def data_transfer(self, url: str, privacy_data: dict):
        send_data = {'opt_type': 1, 'url': url, 'data': privacy_data}
        print('Send Data')
        send_json = json.dumps(send_data).encode()
        if len(send_json) % config.BUFFER_SIZE == 0:
            send_json = send_json + b' '
        self.s.sendall(send_json)
        time.sleep(0.2)

    def close(self):
        send_data = {'opt_type': 2}
        send_json = json.dumps(send_data).encode()
        self.s.send(send_json)
        self.s.close()
