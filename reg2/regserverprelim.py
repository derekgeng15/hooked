#!/usr/bin/env python3
import os
import sys
import socket
import argparse

def handle_client(sock):
    try:
        # open both while socket is alive
        in_flo = sock.makefile(mode='r', encoding='utf-8', newline='\n')
        out_flo = sock.makefile(mode='w', encoding='utf-8', newline='\n')

        line = in_flo.readline()
        if line == "":
            # client closed connection before sending
            return

        line = line.rstrip()
        out_flo.write(line + "\n") 
        out_flo.flush()

    except Exception as ex:
        print(f"regserverprelim.py: {ex}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        prog="regserver.py",
        description="Server for the registrar application"
    )
    parser.add_argument("port", type=int, help="the port at which the server should listen")
    args = parser.parse_args()

    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if os.name != 'nt':
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_sock.bind(("", args.port))
        server_sock.listen()

    except OSError as ex:
        print(f"regserverprelim.py: {ex}", file=sys.stderr)
        sys.exit(1)

    while True:
        try:
            sock, _client_addr = server_sock.accept()
            with sock:
                handle_client(sock)
        except Exception as ex:
            # never let server die
            print(f"regserverprelim.py: {ex}", file=sys.stderr)

if __name__ == "__main__":
    main()
