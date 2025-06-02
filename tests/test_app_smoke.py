import contextlib
import subprocess
import time

import requests


def wait_for_healthz(url, timeout=10):
    for _ in range(timeout):
        with contextlib.suppress(Exception):
            r = requests.get(url)
            if r.status_code == 200:
                return True
        time.sleep(1)
    return False


def test_health_and_ready():
    """
    Smoke test: start the app, check /healthz and /readyz endpoints.
    """
    # Start the app as a subprocess
    proc = subprocess.Popen(["python", "-m", "src.main"])
    try:
        base_url = "http://127.0.0.1:8080"
        assert wait_for_healthz(f"{base_url}/healthz"), "/healthz did not become ready"
        # /readyz may fail if RabbitMQ is not available, but should return 200 or 503
        r = requests.get(f"{base_url}/readyz")
        assert r.status_code in {200, 503}
    finally:
        proc.terminate()
        proc.wait(timeout=5)
