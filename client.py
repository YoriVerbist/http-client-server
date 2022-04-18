import socket
import argparse
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description="A simple HTTP client that supports GET, HEAD and PUT requests")

parser.add_argument(
    "--command",
    choices=["HEAD", "GET", "PUT"],
    type=str,
    help="Type of HTTP command, possibilities: HEAD, GET, PUT",
    required=True,
)
parser.add_argument(
    "--uri", type=str, help="The URI you want to connect with", required=True
)
parser.add_argument(
    "--port", type=int, help="The port you want to connect with", default=80
)

args = parser.parse_args()

# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)

def find_html_code(response):
    return response.decode().split("\r\n\r\n")[1]

def main():
    s.connect((args.uri, args.port))
    match args.command:
        case "GET":
            request = f"{args.command} / HTTP/1.1\r\nHost:{args.uri}\r\nConnection: close\r\n\r\n"
            s.sendall(request.encode())
            response = b""
            try:
                while True:
                    response += s.recv(4096);
            except:
                print("Session timed out!")
            print(response.decode())
            #print(response.decode().split('\r\n\r\n')[1].split('\n')[1])
            # Split of the headers from the html file
            html = find_html_code(response)
            with open ("index.html", "w") as file:
                file.write(html)


if __name__ == "__main__":
    main()
