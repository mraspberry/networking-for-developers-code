import logging
import socket
import ssl
import string


def main():
    host = "www.ramseysolutions.com"
    logging.basicConfig(
        level=logging.DEBUG, format="{asctime}|{levelname:8}|{message}", style="{"
    )
    logging.debug("Getting address info for domain %s", host)
    info = socket.getaddrinfo(
        host, 443, family=socket.AF_INET, proto=socket.IPPROTO_TCP
    )
    (
        sock_family,
        sock_type,
        sock_proto,
        sock_canonname,
        sock_addr,
    ) = info[0]
    logging.debug("Creating TLS context for TLS connection")
    ctx = ssl.create_default_context()
    logging.debug("Creating IPv4 TCP socket")
    sock = socket.socket(sock_family, sock_type, sock_proto)
    logging.debug("Connecting to %s", host)
    with sock:
        sock.settimeout(10)
        with ctx.wrap_socket(sock, server_hostname=host) as ssl_sock:
            ssl_sock.connect(sock_addr)
            sent = ssl_sock.send(f"GET / HTTP/1.1\r\nHost: {host}\r\n\r\n".encode())
            logging.debug("Sent %i bytes", sent)
            logging.debug("Receiving response from server")
            response = b""
            data_read = True
            while data_read:
                try:
                    received = ssl_sock.recv(1024)
                except socket.timeout:
                    received = b""
                if received:
                    response += received
                else:
                    data_read = False
    with open("rs-com.html", "w") as outfd:
        for line in response.decode().split("\r\n"):
            if (
                line.startswith(tuple(string.ascii_uppercase)) and ":" in line
            ) or line.startswith("HTTP"):
                print(line)
            else:
                outfd.write(line)
