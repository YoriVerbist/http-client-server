import socket, threading, datetime, time, os

FORMAT = "utf-8"
IMAGE_FILES = ("jpg", "gif", "png")
NOT_FOUND = "<html><head></head><body><h1>404 File Not Found!</h1></body></html>\r\n"
INTERNAT_ERROR = "<html><head></head><body><h1>500 Internal Server Error</h1></body></html>\r\n"
BAD_REQ = "<html><head></head><body><h1>400 Bad Request!</h1></body></html>\r\n"



def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        # When something fails return a 500 Internal Server Error
        try:
            # Receives the request message from the client
            message =  conn.recv(1024).decode(FORMAT)
            if message.find("Host") == -1:
                conn.send(f"HTTP/1.1 400 Bad Request!\r\nContent-Length: {len({BAD_REQ})}\r\nContent-Type: text/html\r\n\r\n".encode(FORMAT))
                conn.send(BAD_REQ.encode(FORMAT))
                break

            # Extract the path of the requested object from the message
            # The path is the second part of HTTP header, identified by [1]
            operation = message.split()[0]
            match operation:
                case "GET":
                    filename = message.split()[1]
                    if filename == "/": filename = "/index.html"
                    try:
                        # If the file is an image then read it as a byte
                        if filename.endswith(IMAGE_FILES):
                            f = open(filename[1:], 'rb')
                        else:
                            f = open(filename[1:])
                    except:
                        # Send HTTP response message for file not found
                        conn.send("HTTP/1.1 404 File Not Found!\r\nContent-Length: {len(NOT_FOUND)}\r\nContent-Type: text/html\r\n\r\n".encode(FORMAT))
                        conn.send(NOT_FOUND.encode(FORMAT))
                        break
                    outputdata = f.read()
                    # Send the HTTP response header line to the connection socket
                    conn.send(f"HTTP/1.1 200 OK\r\nContent-Length: {len(outputdata)}\r\nContent-Type: text/html\r\ndate: {datetime.datetime.now()}\r\n\r\n".encode(FORMAT))
     
                    # Send all the requested data
                    if filename.endswith(IMAGE_FILES):
                        conn.sendall(outputdata)
                    else:
                        conn.send(outputdata.encode(FORMAT))
                    conn.send("\r\n\r\n".encode(FORMAT))
                    break


                case "POST":
                    user_message = message.split("\r\n\r\n")[-1]
                    filename = message.split()[1]
                    if filename == "/": filename = "user_message.txt"
                    with open(filename, 'a') as file:
                        file.write(user_message)
                        conn.send(f"HTTP/1.1 200 OK\r\nContent-Length: {len(user_message)}\r\nContent-Type: text/html\r\ndate: {datetime.datetime.now()}\r\n\r\n".encode(FORMAT))
                    break

                case "PUT":
                    user_message = message.split("\r\n\r\n")[-1]
                    filename = message.split()[1]
                    if filename == "/": filename = "user_message.txt"
                    with open(filename, 'w') as file:
                        file.write(user_message)
                    conn.send(f"HTTP/1.1 200 OK\r\nContent-Length: {len(user_message)}\r\nContent-Type: text/html\r\ndate: {datetime.datetime.now()}\r\n\r\n".encode(FORMAT))
                    break

                case "HEAD":
                    filename = message.split()[1]
                    if filename == "/": filename = "/index.html"
                    try:
                        with open(filename[1:], 'r') as file:
                            content_length = len(file.read())
                            conn.send(f"HTTP/1.1 200 OK\r\nContent-Length: {content_length}\r\nContent-Type: text/html\r\ndate: {datetime.datetime.now()}\r\n\r\n".encode(FORMAT))
                            print('here')
                        break
                    except:
                        # Send HTTP response message for file not found
                        conn.send(f"HTTP/1.1 404 File Not Found!\r\nContent-Length: {len({NOT_FOUND})}\r\nContent-Type: text/html\r\n\r\n".encode(FORMAT))
                        conn.send(NOT_FOUND.encode(FORMAT))
                        break

            
        except IOError:
            conn.send("HTTP/1.1 500 Internal Server Error\r\nContent-Length: {len(INTERNAT_ERROR)}\r\nContent-Type: text/html\r\n\r\n".encode(FORMAT))
            conn.send(INTERNAT_ERROR.encode(FORMAT))
            break

    # Close the connection
    conn.close()


def start():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 1234))
    s.listen(10)
    print(f"[LISTENING] Server is listening on {socket.gethostname()}")
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


def main():
    print("[STARTING] server is starting...")
    start()


if __name__ == "__main__":
    main()
