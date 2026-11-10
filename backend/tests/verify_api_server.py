import time
import httpx
import subprocess
import sys
import os

print("Starting FastAPI Uvicorn server in subprocess...")
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
venv_python = os.path.join(backend_dir, "venv", "Scripts", "python.exe")

proc = subprocess.Popen(
    [venv_python, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=backend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

try:
    print("Waiting 5 seconds for server startup...")
    time.sleep(5)

    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=25.0) as client:
        # 1. Health check
        print("\n1. Testing GET /api/health ...")
        r_health = client.get("/api/health")
        print(f"Status: {r_health.status_code}")
        print(f"Response: {r_health.json()}")
        assert r_health.status_code == 200

        # 2. Categories check
        print("\n2. Testing GET /api/categories ...")
        r_cat = client.get("/api/categories")
        print(f"Status: {r_cat.status_code}")
        print(f"Response: {r_cat.json()}")
        assert r_cat.status_code == 200

        # 3. Chat endpoint with sample question from prompt
        print("\n3. Testing POST /api/chat ...")
        chat_payload = {
            "query": "What lifestyle changes can help manage high blood pressure?",
            "history": []
        }
        r_chat = client.post("/api/chat", json=chat_payload)
        print(f"Status: {r_chat.status_code}")
        res = r_chat.json()
        print(f"Detected Category: {res.get('category')} (Confidence: {res.get('category_confidence')})")
        print(f"Retrieved Sources: {len(res.get('sources', []))} chunks")
        for s in res.get('sources', []):
            print(f"  - [{s['document']}] {s['section']} (score: {s['score']})")
        print(f"Answer snippet: {res.get('answer')[:250]}...")
        assert r_chat.status_code == 200
        assert res.get('category') == "Hypertension"
        assert len(res.get('sources', [])) > 0

        print("\n✓ FULL REST API SERVER VERIFICATION COMPLETED SUCCESSFULLY!")

finally:
    print("Terminating server process...")
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
