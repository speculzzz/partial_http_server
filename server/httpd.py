import argparse
import os
import sys
import socketserver
from concurrent.futures import ThreadPoolExecutor

from server.handler import PartialHTTPRequestHandler


class PartialHTTPServer(socketserver.ThreadingTCPServer):

    def __init__(self, server_address, request_handler, document_root, max_workers):
        self.allow_reuse_address = True
        self.allow_reuse_port = True

        super().__init__(server_address, request_handler)

        self.document_root = os.path.abspath(document_root)
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)

    def process_request(self, request, client_address):
        self.thread_pool.submit(self.process_request_thread, request, client_address)


def main():
    parser = argparse.ArgumentParser(description="Partial HTTP Server")
    parser.add_argument("-r", "--document-root", required=True, help="Document root directory")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Number of worker threads")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()

    if not os.path.isdir(args.document_root):
        print(f"Error: Document root '{args.document_root}' is not a directory", file=sys.stderr)
        sys.exit(1)

    server = PartialHTTPServer(
        ("", args.port),
        PartialHTTPRequestHandler,
        args.document_root,
        args.workers
    )

    print(f"Serving HTTP on port {args.port} with {args.workers} workers...")
    print(f"Document root is {args.document_root}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer is shutting down...", file=sys.stderr)
        server.shutdown()
