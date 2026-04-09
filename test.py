import threading
import time

windows = []

def run_exec(code):
    local_vars = {}
    exec(code, globals(), local_vars)

code = """import time

w = {"Hello": "world!"}
windows.append(w)   # expose immediately

# keep doing work without blocking rendering
for i in range(10):
    w["Hello"] = f"Step {i}"
    time.sleep(0.5)
"""

threading.Thread(target=run_exec, args=(code,), daemon=True).start()

while True:
    for w in windows:
        print("Drawing:", w["Hello"])
    time.sleep(0.1)
