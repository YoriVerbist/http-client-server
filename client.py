import socket
import argparse
import re
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
FORMAT = "utf-8"

# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def find_html_code(response):
    return response.decode().split("\r\n\r\n")[1]

def get_request_length(uri:str) -> int:
    request = f"HEAD / HTTP/1.1\r\nHost:{args.uri}\r\nAccept:text/html\r\n\r\n"
    s.sendall(request.encode())
    response = s.recv(1024).decode(FORMAT)
    # regex searches for the Content-Length variable in the response and gets the corresponding value
    return int(re.findall("Content-Length:\s+\d+\s+", response)[0].strip("\r\n\r\n").strip("Content-Length: "))

def main():
    s.connect((args.uri, args.port))
    filename = args.uri[args.uri.find("/") + 1:]
    print(filename)

    match args.command:
        case "GET":
            request_length = get_request_length(args.uri)
            print(type(request_length))
            input()
            request = f"{args.command} / HTTP/1.1\r\nHost:{args.uri}\r\nAccept:text/html\r\n\r\n"
            s.sendall(request.encode())

            response = b""
            while True:
                data = s.recv(4096)
                print(data)
                if len(data) <= 0: 
                    break
                response += data
                print(response)
            print(data.decode("utf-8"))
            # Split of the headers from the html file
            html = find_html_code(response)
            with open ("index.html", "w") as file:
                file.write(html)


if __name__ == "__main__":
    main()
