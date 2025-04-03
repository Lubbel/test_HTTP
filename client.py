import sys
import toml
import json
import base64
import socket
class Request:
    def __init__(self, listVar):
        self.userName = listVar[0]
        self.password = listVar[1]
        self.sender = listVar[2]
        self.recipient = listVar[3]
        self.message = listVar[4]
        self.host = listVar[5]
        self.port = listVar[6]

    def to_bytes (self):
        dataSend = json.dumps({
            "sender":self.sender,
            "recipient":self.recipient,
            "message":self.message
        })
        authorization = (f"{self.userName}:{self.password}").encode()
        code64 = base64.b64encode(authorization).decode()
        post = (
            f"POST /send_sms HTTP/1.1\r\n"
            f"HOST: {self.host}:{self.port}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(dataSend)}\r\n"
            f"Authorization: Basic {code64}\r\n"
            f"\r\n"
            f"{dataSend}"
        )
        return post.encode()
class Response:
    def __init__(self):
        self.response = ""
    def from_bytes(self, binary_data):
        self.response = binary_data.decode()
        data = binary_data.decode().split('\r\n\r\n', 1)
        code = data[0].split()[1]
        body = data[1]

        return [code, body]

if __name__ == "__main__":
    tomlConf = toml.load(open("config.toml","r"))
    userName = tomlConf['userName']
    password = tomlConf['password']
    host = tomlConf['host']
    port = int(tomlConf['port'])

    sender = sys.argv[1]
    recipient = sys.argv[2]
    message = sys.argv[3]

    listVar = [userName, password, sender, recipient,message, host, port]

    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.connect((host, port))

    request = Request(listVar).to_bytes()
    mySocket.sendall(request)

    response = mySocket.recv(1024)
    respon = Response().from_bytes(response)
    print(f"Ответ от сервера: \n Код ответа:{respon[0]}\n{respon[1]}")

    mySocket.close()