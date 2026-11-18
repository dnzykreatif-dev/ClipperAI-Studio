"""
Helper script untuk membuka browser default hanya ketika server FastAPI Uvicorn
sudah 100% siap merespon HTTP 200 OK.
Mencegah munculnya layar error 'This site can't be reached / ERR_CONNECTION_REFUSED'.
"""
import sys
import time
import urllib.request
import webbrowser

TARGET_URL = "http://127.0.0.1:8000"
MAX_WAIT_SECONDS = 45
START_TIME = time.time()

while time.time() - START_TIME < MAX_WAIT_SECONDS:
    try:
        # Cek apakah endpoint root sudah mengembalikan status 200 OK
        with urllib.request.urlopen(f"{TARGET_URL}/", timeout=1.0) as resp:
            if resp.status == 200:
                time.sleep(0.2)  # Jeda mikro agar rendering socket bersih
                webbrowser.open(TARGET_URL)
                sys.exit(0)
    except Exception:
        time.sleep(0.5)

# Fallback jika waktu tunggu habis (misal server lambat tapi tetap dibuka)
try:
    webbrowser.open(TARGET_URL)
except Exception:
    pass
