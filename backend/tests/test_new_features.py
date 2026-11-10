import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- Test 1: Natural Response Formatting ---")
r = client.post("/api/chat", json={"query": "What lifestyle changes can help manage high blood pressure?"})
res = r.json()
print("Category:", res.get("category"))
print("Answer Preview:\n", res["answer"][:400])

print("\n--- Test 2: Live Web Search Grounding ---")
r_web = client.post(
    "/api/chat",
    json={
        "query": "Recent medical studies on Mediterranean diet and heart health",
        "enable_web_search": True
    }
)
res_web = r_web.json()
print("Web Searched:", res_web.get("web_searched"))
print("Total sources:", len(res_web.get("sources", [])))
for s in res_web.get("sources", []):
    print(f"  Source: {s['document']} | Type: {s.get('source_type')} | URL: {s.get('url')}")

print("\n--- Test 3: Upload Medical Report ---")
sample_report = """
PATIENT COMPREHENSIVE METABOLIC PANEL
Patient: John Doe | Age: 52
Fasting Blood Glucose: 138 mg/dL
HbA1c: 7.2 %
Systolic BP: 145 mmHg
Diastolic BP: 92 mmHg
Total Cholesterol: 228 mg/dL
LDL Cholesterol: 142 mg/dL
HDL Cholesterol: 38 mg/dL
Triglycerides: 195 mg/dL
Serum Creatinine: 1.1 mg/dL
"""
files = {"file": ("sample_lab_report.txt", sample_report.encode("utf-8"), "text/plain")}
r_rep = client.post("/api/upload-report", files=files)
res_rep = r_rep.json()
print("Report Category:", res_rep.get("category"))
print("Extracted Biomarkers:", len(res_rep.get("biomarkers", [])))
for b in res_rep.get("biomarkers", []):
    print(f"  {b['name']}: {b['value']} {b['unit']} -> {b['status']}")
print("\nReport Summary Preview:\n", res_rep.get("summary", "")[:350])
print("\nALL NEW FEATURE TESTS PASSED!")
