"""
Socket programming in Python
  as an illustration of the basic mechanisms of a web server.

  Based largely on https://docs.python.org/3.4/howto/sockets.html
  This trivial implementation is not robust:  We have omitted decent
  error handling and many other things to keep the illustration as simple
  as possible. 

  FIXME:
  Currently this program always serves an ascii graphic of a cat.
  Change it to serve files if they end with .html and are in the current directory
"""

import socket    # Basic TCP/IP communication on the internet
import random    # To pick a port at random, giving us some chance to pick a port not in use
import _thread   # Response computation runs concurrently with main program 


def listen(portnum):
    """
    Create and listen to a server socket.
    Args:
       portnum: Integer in range 1024-65535; temporary use ports
           should be in range 49152-65535.
    Returns:
       A server socket, unless connection fails (e.g., because
       the port is already in use).
    """
    # Internet, streaming socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind to port and make accessible from anywhere that has our IP address
    serversocket.bind(('', portnum))
    serversocket.listen(1)    # A real server would have multiple listeners
    return serversocket

def serve(sock, func):
    """
    Respond to connections on sock.
    Args:
       sock:  A server socket, already listening on some port.
       func:  a function that takes a client socket and does something with it
    Returns: nothing
    Effects:
        For each connection, func is called on a client socket connected
        to the connected client, running concurrently in its own thread.
    """
    while True:
        print("Attempting to accept a connection on {}".format(sock))
        (clientsocket, address) = sock.accept()
        _thread.start_new_thread(func, (clientsocket,))

def badurl(request, sock):
	"""
	Send the error for bad files
	
	"""
	transmit("\nI don't handle this request: {}\n".format(request), sock)

e404 = ("<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
            "<title>Page not found</title>\n"
        "</head>\n"
        "<body style='text-align: center;''>\n"
            "<h1>Page not found</h1>\n"
            "<h2>Please try another page...</h2>\n"
        "</body>\n"
        "</html>\n"
        )

def respond(sock):
    """
    Respond (only) to GET

    """
    sent = 0
    request = sock.recv(1024)  # We accept only short requests
    request = str(request, encoding='utf-8', errors='strict')
    print("\nRequest was {}\n".format(request))

    parts = request.split()
    if len(parts) > 1 and parts[0] == "GET":
        transmit("HTTP/1.0 200 OK\n\n", sock)
        
        url = parts[1]
        # None of those "undesirables"
        if ("~" not in url) and (".." not in url) and ("//" not in url):
        	# Only html and css requests (I also allow js)
        	if url.endswith(".html") or url.endswith(".css") or url.endswith(".js"):
        		try:
        			file = open(url[1:], "rb")
        			# Apparently it freaks out a little with text stuffs
                    # Need to use the decode to utf-8 thing...
        			transmit(file.read().decode("utf-8"), sock)
        		except Exception as e:
                    # File not found, or something else... but 404 anyway
        			transmit(e404, sock)
        	else:
        		badurl(request, sock)
        else:
        	badurl(request, sock)
    else:
        badurl(request, sock)

    sock.close()

    return

def transmit(msg, sock):
    """It might take several sends to get the whole buffer out"""
    sent = 0
    while sent < len(msg):
        buff = bytes( msg[sent: ], encoding="utf-8")
        sent += sock.send( buff )
    

def main():
    port = random.randint(5000,8000)
    sock = listen(port)
    print("Listening on port {}".format(port))
    print("Socket is {}".format(sock))
    serve(sock, respond)

main()
    
