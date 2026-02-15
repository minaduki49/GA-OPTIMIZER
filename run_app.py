import webbrowser
import uvicorn
import threading
import socket
import time

def wait_and_open():
    while True:
        try:
            with socket.create_connection(("127.0.0.1", 8000), timeout=0.5):
                break
        except OSError:
            time.sleep(0.2)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Thread(target=wait_and_open, daemon=True).start()
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        workers=1,
        reload=False
    )
