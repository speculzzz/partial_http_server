import os
import sys
import socketserver
import threading
import mimetypes
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import unquote, urlparse
from socket import timeout, error as socket_error
from typing import Optional


HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_INTERNAL_ERROR = 500
HTTP_GATEWAY_TIMEOUT = 504

HTTP_ALLOWED_METHODS = ['GET', 'HEAD']
HTTP_LINE_ENDING = "\r\n"

RECV_BUFFER_SIZE = 1024


@dataclass
class ResponseParams:
    code: int
    content_type: str
    content: bytes
    extra_headers: Optional[list[str]] = None
    header_only: bool = False


class PartialHTTPRequestHandler(socketserver.BaseRequestHandler):

    def _get_http_date(self) -> str:
        return datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

    def _get_http_code_string(self, code: int) -> str:
        http_code_string = {
            HTTP_OK: "OK",
            HTTP_BAD_REQUEST: "Bad Request",
            HTTP_FORBIDDEN: "Forbidden",
            HTTP_NOT_FOUND: "Not Found",
            HTTP_METHOD_NOT_ALLOWED: "Method Not Allowed",
            HTTP_INTERNAL_ERROR: "Internal Server Error",
            HTTP_GATEWAY_TIMEOUT: "Gateway Time Out",
        }
        return http_code_string[code] if code in http_code_string else "Unknown"

    def _build_headers(self, response_params: ResponseParams) -> bytes:
        message = self._get_http_code_string(response_params.code)
        headers = [
            f"HTTP/1.1 {response_params.code} {message}",
            f"Date: {self._get_http_date()}",
            "Server: SimpleHTTP/1.0",
            f"Content-Length: {len(response_params.content)}",
            f"Content-Type: {response_params.content_type}",
            "Connection: close"
        ]

        if response_params.extra_headers:
            headers.extend(response_params.extra_headers)

        headers.append(HTTP_LINE_ENDING)

        return HTTP_LINE_ENDING.join(headers).encode('utf-8')

    def _send_response(self, response_params: ResponseParams) -> None:
        response = self._build_headers(response_params)

        if not response_params.header_only:
            response += response_params.content

        self.request.sendall(response)

    def _send_error(self, code: int) -> None:
        message = self._get_http_code_string(code)
        error_page = f"""<html>
<head><title>{code} {message}</title></head>
<body><h1>{code} {message}</h1></body>
</html>"""

        print(f"Error {code} has occurred: {message}")

        response = ResponseParams(
            code=code,
            content_type="text/html",
            content=error_page.encode('utf-8')
        )
        self._send_response(response)

    def _try_send_error(self, code: int) -> None:
        try:
            self._send_error(code)
        except (ConnectionResetError, socket_error, timeout) as e:
            print(f"Failed to send error: {e}", file=sys.stderr)
        except Exception as e: # pylint: disable=W0718
            print(f"Critical error while sending error: {e}", file=sys.stderr)
            sys.exit(1)

    def _get_safe_path(self, requested_path: str) -> str:
        is_dir = requested_path.endswith('/')

        # Layer 1: Basic traversal sequence removal
        sanitized_path = requested_path.replace('../', '').replace('..\\', '')

        # Layer 2: Advanced pattern detection
        if any(suspicious in sanitized_path for suspicious in ('../', '..\\', '~', '//')):
            raise PermissionError("Invalid path sequence detected")

        # Layer 3: Secure path construction
        abs_path = os.path.abspath(os.path.join(
            os.path.normpath(self.server.document_root),
            sanitized_path.lstrip('/\\')
        ))

        if is_dir:
            abs_path = os.path.join(abs_path, '')  # Returning '/' at the end of the path

        # Layer 4: Final containment validation
        if not os.path.commonpath([abs_path, self.server.document_root]) == self.server.document_root:
            raise PermissionError("Path traversal attempt blocked")

        return abs_path

    def _needs_charset(self, filepath: str) -> bool:
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                return content.decode('ascii', errors='strict') != content.decode('utf-8')
        except UnicodeError:
            return True  # Found non-ASCII symbols

    def handle(self) -> None:
        try:
            print(f"Current thread: {threading.current_thread().name}")

            request_data = self.request.recv(RECV_BUFFER_SIZE).decode('utf-8')
            if not request_data:
                return

            # HTTP-request parsing
            lines = request_data.split(HTTP_LINE_ENDING)
            request_line = lines[0].split()

            if len(request_line) < 2:
                self._send_error(HTTP_BAD_REQUEST)
                return

            # Only GET and HEAD request are possible
            method = request_line[0]
            print(f"Got {method} request:\n{lines}")
            if method not in HTTP_ALLOWED_METHODS:
                self._send_error(HTTP_METHOD_NOT_ALLOWED)
                return

            parsed_url = urlparse(request_line[1])
            path = unquote(parsed_url.path)

            self.process_request(method, path)

        except UnicodeDecodeError as e:
            print(f"Encoding error: {e}", file=sys.stderr)
            self._try_send_error(HTTP_BAD_REQUEST)

        except ConnectionResetError as e:
            print(f"Network error: {e}", file=sys.stderr)
            self._try_send_error(HTTP_INTERNAL_ERROR)

        except timeout as e:
            print(f"Timeout expired: {e}", file=sys.stderr)
            self._try_send_error(HTTP_GATEWAY_TIMEOUT)

        except OSError as e:
            print(f"OS error: {e}", file=sys.stderr)
            self._try_send_error(HTTP_NOT_FOUND if e.errno == 2 else HTTP_FORBIDDEN)

        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
            self._try_send_error(HTTP_INTERNAL_ERROR)
            raise

    def process_request(self, method: str, path: str) -> None:
        safe_path = self._get_safe_path(path)

        if not os.path.exists(safe_path):
            self._send_error(HTTP_NOT_FOUND)
            return

        if os.path.isdir(safe_path) or safe_path.endswith("/"):
            safe_path = os.path.join(safe_path, 'index.html')
            if not os.path.exists(safe_path):
                self._send_error(HTTP_NOT_FOUND)
                return

        with open(safe_path, 'rb') as f:
            content = f.read()

        content_type = self.guess_content_type(safe_path)
        header_only = method == 'HEAD'
        response = ResponseParams(
            code=HTTP_OK,
            content_type=content_type,
            content=content,
            header_only=header_only
        )
        self._send_response(response)
        print("Response has been sent successfully")

    def guess_content_type(self, path: str) -> str:
        mime_type, _ = mimetypes.guess_type(path)

        if not mime_type:
            mime_type = "application/octet-stream"

        if mime_type.startswith("text/") and self._needs_charset(path):
            mime_type = f"{mime_type}; charset=utf-8"

        return mime_type
