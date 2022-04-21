import socket, re, os, argparse
from tqdm import tqdm
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description="A simple HTTP client that supports GET, HEAD and PUT requests (Python 3.10 is needed to run this program!)")

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


def find_html_code(response: bytes) -> str:
    response = response.decode(FORMAT, errors="ignore")
    # get the postions of the <html> tags, (?i) makes it case insensitive
    positions = [x.span() for x in re.finditer("(?i)<\/?html", response)]
    start, end = positions[0][0], positions[1][1]+1
    return response[start:end]

def find_image_urls(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    links = [l["src"] for l in soup.find_all('img')]
    print(links)
    return links

def change_img_tags(html: str, image_urls: list) -> str:
    for url in image_urls:
        new_url = "images/" + url.split("/")[-1]
        html = html.replace(url, new_url)
    return html


def get_request_length_and_transfer_encoding(uri: str, s: socket) -> int:
    request = f"HEAD / HTTP/1.1\r\nHost:{args.uri}\r\nAccept:text/html\r\n\r\n"
    s.send(request.encode())
    response = b""
    while True:
        data = s.recv(2048)
        response += data
        if not data or data.decode(FORMAT).endswith(CRLF): break
    header_length = len(response)
    print(header_length)
    response = response.decode(FORMAT)
    # regex searches for the Content-Length response in the response and gets the corresponding value
    content_lengths = re.findall("Content-Length:\s+\d+\s+", response)
    transfer_encoding = re.findall("Transfer-Encoding:\s+\w+", response)
    if transfer_encoding:
        transfer_encoding = transfer_encoding[0].split()[1]
    # Check if there was a Content-Length response in the header, if not return 4096
    if len(content_lengths) != 0:
        return power_of_two(int(content_lengths[0].strip("\r\n\r\n").strip("Content-Length: "))), header_length, transfer_encoding
    else:
        return None, header_length, transfer_encoding

def power_of_two(target):
    if target > 1:
        for i in range(1, int(target)):
            if (2 ** i >= target):
                return 2 ** i
    else:
        return 1


def main():
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.uri, args.port))
    filename = args.uri[args.uri.find("/") + 1:]

    match args.command:
        case "GET":
            # Get the Content-Length and Transer-Encoding from the header
            request_length, header_length, transfer_encoding = get_request_length_and_transfer_encoding(args.uri, s)
            print(request_length)
            request = f"{args.command} / HTTP/1.1\r\nHost:{args.uri}\r\n\r\n"
            s.sendall(request.encode())
            if request_length and request_length < 10000 and not transfer_encoding:
                response = s.recv(request_length + header_length)
                print('response', response)
            elif transfer_encoding == "chunked" or not request_length or request_length >= 10000:
                print('here')
                response = b""
                while True:
                    data = s.recv(4096)
                    response += data
                    # Check when the end of the request is recieved
                    if (data.endswith(CRLF.encode(FORMAT))
                    or not data 
                    or re.search(b"(?i)<\/html>", data)):
                        break
            # Split of the headers from the html file and get all the image urls
            html = find_html_code(response)
            image_urls = find_image_urls(html)
            # If there are image links on the page, download them and change the path in the html code
            if image_urls:
                for url in tqdm(image_urls, "Extracting images"):
                    if not url.startswith('/'): url = '/' + url
                    request = f"{args.command} {url} HTTP/1.1\r\nHost:{args.uri}\r\n\r\n"
                    s.sendall(request.encode())
                    response = s.recv(15000)
                    headers =  response.split(b'\r\n\r\n')[0]
                    image = response[len(headers)+4:]
                    url = "images/" + url.split("/")[-1]
                    os.makedirs("images", exist_ok=True)
                    with open(url, "wb") as image_file:
                        image_file.write(image)

                html = change_img_tags(html, image_urls)

            s.close()
            with open ("index.html", "w") as html_file:
                html_file.write(html)

        case "POST":
            request = f"{args.command} / HTTP/1.1\r\nHost:{args.uri}\r\nAccept:text/html\r\n\r\n"
            pass

        case "HEAD":
            request = f"{args.command} / HTTP/1.1\r\nHost:{args.uri}\r\nAccept:text/html\r\n\r\n"
            s.send(request.encode())
            response = s.recv(4096)
            print(response.decode(FORMAT))



if __name__ == "__main__":
    main()
