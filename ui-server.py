import http.server
import socketserver
import os

os.chdir("docs")

PORT = 8000


def main() -> None:
    handler = http.server.SimpleHTTPRequestHandler
    server = socketserver.TCPServer(("", PORT), handler, bind_and_activate=False)
    server.allow_reuse_address = True
    server.server_bind()
    server.server_activate()

    print("Serving local Twinbase UI at http://127.0.0.1:" + str(PORT))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("User interrupt")
    finally:
        print("Stopping server")
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
