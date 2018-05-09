import socket
from .settings import HOST, PORT
    

def stop_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.send("stop")
    received = sock.recv(1024)
    sock.close()
    print("Sent: %s" % "stop")
    print("Received: %s" % received)


if __name__ == "__main__":
    stop_server()
