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
CRLF = "\r\n\r\n"

# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def find_html_code(response: bytes) -> str:
    response = response.decode(FORMAT, errors="ignore")
    html_code = re.search("<\/?html", response)
    print(html_code.span())
    return response.decode(FORMAT, errors="ignore").split(CRLF)[1]

def get_request_length(uri: str) -> int:
    request = f"GET / HTTP/1.1\r\nHost:{args.uri}\r\nAccept:text/html\r\n\r\n"
    s.send(request.encode())
    response = s.recv(2048).decode(FORMAT)
    # regex searches for the Content-Length response in the response and gets the corresponding value
    content_lengths = re.findall("Content-Length:\s+\d+\s+", response)
    # Check if there was a Content-Length response in the header, if not return 4096
    if len(content_lengths) != 0:
        return int(content_lengths[0].strip("\r\n\r\n").strip("Content-Length: "))
    else:
        return None

def main():
    s.connect((args.uri, args.port))
    filename = args.uri[args.uri.find("/") + 1:]

    match args.command:
        case "GET":
            # Get the Content-Length from the header
            #request_length = get_request_length(args.uri)
            request_length = None
            input()
            request = f"{args.command} / HTTP/1.1\r\nHost:{args.uri}\r\nAccept:text/html\r\n\r\n"
            s.sendall(request.encode())
            response = b""
            if request_length:
                response = s.recv(request_length)
                print(response, "\n\n")
            else:
                while True:
                    data = s.recv(4096)
                    response += data
                    # Check when the end of the request is recieved
                    if data.endswith(CRLF.encode(FORMAT)) or not data:
                        break
                    print(response)
            s.close()
            print(response)
            # Split of the headers from the html file
            html = find_html_code(response)
            with open ("index.html", "w") as file:
                file.write(html)


if __name__ == "__main__":
    main()
