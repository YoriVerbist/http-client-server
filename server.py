import socket
import threading
import datetime

FORMAT = "utf-8"
IMAGE_FILES = ("jpg", "gif", "png")

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        # If an exception occurs during the execution of try clause
        # the rest of the clause is skipped
        # If the exception type matches the word after except
        # the except clause is executed
        try:
            # Receives the request message from the client
            message =  conn.recv(1024).decode(FORMAT)
            print(message)
            # Extract the path of the requested object from the message
            # The path is the second part of HTTP header, identified by [1]
            operation = message.split()[0]
            match operation:
                case "GET":
                    filename = message.split()[1]
                    if filename == "/": filename = "/index.html"
            
                    print(filename)
                    try:
                        if filename[-3:] in IMAGE_FILES:
                            f = open(filename[1:], 'rb')
                        else:
                            # Don't select the leading /
                            f = open(filename[1:])
                    except:
                        # Send HTTP response message for file not found
                        conn.send("HTTP/1.1 404 File Not Found!\r\n\r\n".encode(FORMAT))
                        conn.send("<html><head></head><body><h1>404 File Not Found!</h1></body></html>\r\n".encode(FORMAT))
                        # Close the client connection socket
                        break

                    outputdata = f.read()
                    print(outputdata)
                    # Send the HTTP response header line to the connection socket
                    conn.send(f"HTTP/1.1 200 OK\r\nContent-Length: {len(outputdata)}\r\nContent-Type: text/html\r\ndate: {datetime.datetime.now()}\r\n\r\n".encode(FORMAT))
     
                    # Send all the requested data
                    for i in range(0, len(outputdata)):  
                        # When the file is a image it's already in bytes, only encode when it's not an image
                        if filename[-3:] in IMAGE_FILES:
                            conn.send(outputdata[i])
                        else:
                            conn.send(outputdata[i].encode(FORMAT))
                    conn.send("\r\n\r\n".encode(FORMAT))
                    break
            
        except IOError:
            # Send HTTP response message for file not found
            conn.send("HTTP/1.1 500 Internal Server Error\r\n\r\n".encode(FORMAT))
            conn.send("<html><head></head><body><h1>500 Internal Server Error</h1></body></html>\r\n".encode(FORMAT))
            # Close the client connection socket
            break

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
    s.close()


if __name__ == "__main__":
    main()
