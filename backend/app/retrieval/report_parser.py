import io
import re
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

# Standard Clinical Reference Ranges for Common Lab Biomarkers
BIOMARKER_PATTERNS = [
    {
        "name": "Fasting Blood Glucose",
        "keywords": [r"fasting\s*(?:blood\s*)?glucose", r"fbs", r"fasting\s*sugar"],
        "unit": "mg/dL",
        "normal_min": 70,
        "normal_max": 99,
        "pre_diabetes_max": 125
    },
    {
        "name": "HbA1c (Glycated Hemoglobin)",
        "keywords": [r"hba1c", r"glycated\s*hemoglobin", r"a1c"],
        "unit": "%",
        "normal_min": 4.0,
        "normal_max": 5.6,
        "pre_diabetes_max": 6.4
    },
    {
        "name": "Systolic Blood Pressure",
        "keywords": [r"systolic(?:\s*bp)?", r"bp\s*systolic"],
        "unit": "mmHg",
        "normal_min": 90,
        "normal_max": 120
    },
    {
        "name": "Diastolic Blood Pressure",
        "keywords": [r"diastolic(?:\s*bp)?", r"bp\s*diastolic"],
        "unit": "mmHg",
        "normal_min": 60,
        "normal_max": 80
    },
    {
        "name": "Total Cholesterol",
        "keywords": [r"total\s*cholesterol", r"serum\s*cholesterol"],
        "unit": "mg/dL",
        "normal_min": 125,
        "normal_max": 200
    },
    {
        "name": "LDL Cholesterol",
        "keywords": [r"ldl(?:\s*cholesterol)?", r"bad\s*cholesterol"],
        "unit": "mg/dL",
        "normal_min": 0,
        "normal_max": 100
    },
    {
        "name": "HDL Cholesterol",
        "keywords": [r"hdl(?:\s*cholesterol)?", r"good\s*cholesterol"],
        "unit": "mg/dL",
        "normal_min": 40,
        "normal_max": 90
    },
    {
        "name": "Triglycerides",
        "keywords": [r"triglycerides?", r"tg"],
        "unit": "mg/dL",
        "normal_min": 0,
        "normal_max": 150
    },
    {
        "name": "Serum Creatinine",
        "keywords": [r"creatinine", r"serum\s*creatinine"],
        "unit": "mg/dL",
        "normal_min": 0.6,
        "normal_max": 1.3
    },
    {
        "name": "Hemoglobin",
        "keywords": [r"hemoglobin", r"\bhb\b"],
        "unit": "g/dL",
        "normal_min": 12.0,
        "normal_max": 17.0
    },
    {
        "name": "TSH (Thyroid Stimulating Hormone)",
        "keywords": [r"tsh", r"thyroid\s*stimulating\s*hormone"],
        "unit": "mIU/L",
        "normal_min": 0.4,
        "normal_max": 4.5
    }
]

def extract_text_from_file(filename: str, content_bytes: bytes) -> str:
    """
    Extracts plain text from PDF or text-based medical reports.
    """
    lower_name = filename.lower()
    
    # 1. PDF Documents
    if lower_name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            pdf = PdfReader(io.BytesIO(content_bytes))
            text_pages = [page.extract_text() or "" for page in pdf.pages]
            full_text = "\n".join(text_pages).strip()
            if full_text:
                return full_text
        except Exception as e:
            logger.warning(f"Error parsing PDF with pypdf: {e}")

    # 2. Text / CSV / Markdown files
    try:
        return content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return content_bytes.decode("latin-1")
        except Exception:
            return ""

def parse_lab_biomarkers(report_text: str) -> List[Dict[str, Any]]:
    """
    Scans report text to identify clinical biomarkers, their extracted numeric values,
    and compares them to medical reference ranges.
    """
    identified = []
    lines = report_text.lower().splitlines()

    for marker in BIOMARKER_PATTERNS:
        pattern_str = r"(?:" + "|".join(marker["keywords"]) + r")[:\s\-—]+([0-9]+(?:\.[0-9]+)?)"
        for line in lines:
            match = re.search(pattern_str, line)
            if match:
                try:
                    val = float(match.group(1))
                    status = "Normal"
                    if val > marker["normal_max"]:
                        status = "Elevated"
                    elif val < marker["normal_min"]:
                        status = "Low"
                    
                    identified.append({
                        "name": marker["name"],
                        "value": str(val),
                        "unit": marker["unit"],
                        "normal_range": f"{marker['normal_min']} - {marker['normal_max']} {marker['unit']}",
                        "status": status
                    })
                    break  # Found for this marker
                except Exception:
                    continue

    return identified
