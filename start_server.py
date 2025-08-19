import os
import nest_asyncio
from pyngrok import ngrok
import threading
import subprocess
import time
from dotenv import load_dotenv

load_dotenv()

# AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
# if AUTH_TOKEN:
#     ngrok.set_auth_token(AUTH_TOKEN)

# nest_asyncio.apply()

# def run_gunicorn():
#     # Using subprocess.Popen instead of run, so it's non-blocking
#     process = subprocess.Popen([
#         "gunicorn",
#         "app:app",
#         "--bind", "0.0.0.0:5000",
#         "--timeout", "120"
#     ])
#     # Wait for the process to complete (it won't until killed)
#     process.communicate()
#
# # Start Gunicorn in a thread (not daemon, so it keeps running)
# gunicorn_thread = threading.Thread(target=run_gunicorn)
# gunicorn_thread.start()
#
# # Wait a few seconds to let Gunicorn start
# time.sleep(5)

# # Open ngrok tunnel on port 5000
# public_url = ngrok.connect(5000)
# print("🔗 Public URL:", public_url)
#
# # Keep the main thread alive so both Gunicorn and ngrok keep running
# try:
#     while True:
#         time.sleep(10)
# except KeyboardInterrupt:
#     print("Shutting down.")
#     ngrok.kill()

def run_gunicorn():
    # Run gunicorn for your Flask app
    subprocess.run([
        "gunicorn",
        "app:app",
        "--bind", "0.0.0.0:5000",
        "--timeout", "120"
    ])

threading.Thread(target=run_gunicorn, daemon=True).start()
