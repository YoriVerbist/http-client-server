import socket, re, os, argparse
from tqdm import tqdm
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
            else:
                while True:
                    data = s.recv(4096)
                    response += data
                    # Check when the end of the request is recieved
                    if (data.endswith(CRLF.encode(FORMAT))
                    or not data 
                    or re.search(b"(?i)<\/html>", data)):
                        break
            print(response)
            # Split of the headers from the html file and get all the image urls
            html = find_html_code(response)
            image_urls = find_image_urls(html)
            # If there are image links on the page, download them and change the path in the html code
            if image_urls:
                for url in tqdm(image_urls, "Extracting images"):
                    if not url.startswith('/'): url = '/' + url
                    request = f"{args.command} {url} HTTP/1.1\r\nHost:{args.uri}\r\n\r\n"
                    s.sendall(request.encode())
                    response = s.recv(1000)
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


if __name__ == "__main__":
    main()
