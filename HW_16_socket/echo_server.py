import socket
from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"
PORT = 5000

def get_status_line(status_param):
    if not status_param:
        return "200 OK"
    try:
        code = int(status_param)
        status_obj = HTTPStatus(code)
        return f"{code} {status_obj.phrase}"
    except (ValueError, KeyError):
        return "200 OK"

def parse_request_line_and_headers(data: bytes):
    text = data.decode("utf-8", errors="ignore")
    lines = text.splitlines()
    if not lines:
        return None, None, {}, ""

    request_line = lines[0]
    parts = request_line.split(" ", 2)
    if len(parts) < 2:
        return None, None, {}, ""

    method = parts[0]
    path_with_query = parts[1]

    parsed = urlparse(path_with_query)
    path = parsed.path
    query_string = parsed.query

    headers = {}
    i = 1
    while i < len(lines):
        line = lines[i].strip()
        if line == "":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
        i += 1

    return method, path, headers, query_string

def build_response(method, addr, status_line, client_headers):
    # 1. Тело: именно сюда кладём эхо-строки
    body_lines = []
    body_lines.append(f"Request Method: {method}")
    body_lines.append(f"Request Source: {addr}")
    body_lines.append(f"Response Status: {status_line}")

    for name, value in client_headers.items():
        body_lines.append(f"{name}: {value}")

    body = "\r\n".join(body_lines)
    body_bytes = body.encode("utf-8")

    # 2. Только валидные HTTP-заголовки (до разделителя \r\n\r\n)
    headers_lines = [
        f"HTTP/1.1 {status_line}",
        "Content-Type: text/plain; charset=utf-8",
        f"Content-Length: {len(body_bytes)}",
        "Connection: close",
    ]

    header_block = "\r\n".join(headers_lines)

    # 3. Полный ответ: заголовки + \r\n\r\n + тело
    response = (header_block + "\r\n\r\n").encode("utf-8") + body_bytes
    return response

def handle_client(conn, addr):
    data = conn.recv(4096)
    if not data:
        conn.close()
        return

    method, path, headers, query_string = parse_request_line_and_headers(data)
    if method is None:
        resp = build_response("UNKNOWN", addr, "200 OK", {})
        conn.sendall(resp)
        conn.close()
        return

    query_params = parse_qs(query_string)
    status_param = query_params.get("status", [None])[0]

    status_line = get_status_line(status_param)
    response = build_response(method, addr, status_line, headers)
    conn.sendall(response)
    conn.close()

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_sock.bind((HOST, PORT))
        except OSError:
            print(f"Ошибка: порт {PORT} занят!")
            return
        server_sock.listen()
        print(f"Echo server listening on {HOST}:{PORT}")
        while True:
            conn, addr = server_sock.accept()
            handle_client(conn, addr)

if __name__ == "__main__":
    run_server()
