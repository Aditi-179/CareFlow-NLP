from typing import Dict, Any, List

CATEGORIES = [
    "Diabetes",
    "Hypertension",
    "Cardiovascular Health",
    "Nutrition",
    "Symptoms",
    "Medication Information",
    "General Healthcare"
]

# Curated domain keyword taxonomy with weighted terms
CATEGORY_TAXONOMY: Dict[str, Dict[str, float]] = {
    "Diabetes": {
        "diabetes": 3.0, "diabetic": 3.0, "glucose": 2.5, "insulin": 3.0, 
        "hba1c": 3.0, "glycemic": 2.5, "t1dm": 3.0, "t2dm": 3.0, "type 1": 2.5, 
        "type 2": 2.5, "hyperglycemia": 3.0, "hypoglycemia": 3.0, "ketoacidosis": 3.0, 
        "metformin": 2.5, "blood sugar": 2.5, "glucometer": 2.5, "smbg": 2.5,
        "polyuria": 2.0, "polydipsia": 2.0, "polyphagia": 2.0
    },
    "Hypertension": {
        "hypertension": 3.0, "hypertensive": 3.0, "blood pressure": 3.0, "bp": 2.0, 
        "systolic": 2.5, "diastolic": 2.5, "dash": 2.5, "sodium": 2.0, 
        "salt": 1.5, "vasoconstriction": 2.0, "arterial": 2.0, "high bp": 3.0,
        "amlodipine": 2.5, "lisinopril": 2.5, "losartan": 2.5, "diuretic": 2.0
    },
    "Cardiovascular Health": {
        "cardiovascular": 3.0, "cardio": 2.0, "heart": 2.5, "coronary": 2.5, 
        "infarction": 3.0, "myocardial": 3.0, "atherosclerosis": 3.0, "plaque": 2.0, 
        "cholesterol": 2.5, "ldl": 2.5, "hdl": 2.5, "triglycerides": 2.5, 
        "angina": 3.0, "arrhythmia": 3.0, "chest pain": 2.5, "stroke": 2.5, 
        "artery": 2.0, "statin": 2.5, "cardiac": 2.5, "ascvd": 3.0
    },
    "Nutrition": {
        "nutrition": 3.0, "diet": 2.5, "dietary": 2.5, "food": 1.5, "carbohydrate": 2.5, 
        "carbs": 2.0, "protein": 2.5, "fat": 1.5, "fats": 2.0, "fiber": 2.5, 
        "vitamins": 2.0, "vitamin": 2.0, "mineral": 2.0, "potassium": 2.0, 
        "magnesium": 2.0, "omega-3": 2.5, "caloric": 2.0, "calories": 2.0, 
        "mediterranean diet": 3.0, "eating": 1.5, "meal": 1.5, "glycemic index": 2.5
    },
    "Symptoms": {
        "symptom": 3.0, "symptoms": 3.0, "sign": 1.5, "signs": 1.5, "pain": 2.0, 
        "dizziness": 2.5, "fatigue": 2.5, "nausea": 2.5, "shortness of breath": 3.0, 
        "dyspnea": 3.0, "headache": 2.5, "fever": 2.5, "swelling": 2.0, 
        "numbness": 2.5, "tingling": 2.5, "blurred vision": 2.5, "sweats": 2.0, 
        "vomiting": 2.0, "warning signs": 2.5, "red flag": 2.5
    },
    "Medication Information": {
        "medication": 3.0, "medications": 3.0, "medicine": 2.5, "drug": 2.5, 
        "drugs": 2.5, "dose": 2.5, "dosage": 2.5, "prescription": 2.5, 
        "side effect": 3.0, "side effects": 3.0, "statin": 2.5, "metformin": 2.5, 
        "lisinopril": 2.5, "amlodipine": 2.5, "insulin injection": 2.5, 
        "pharmacotherapy": 3.0, "pill": 2.0, "tablets": 2.0, "contraindication": 3.0
    },
    "General Healthcare": {
        "health": 1.5, "healthcare": 2.0, "wellness": 2.0, "preventative": 2.5, 
        "prevention": 2.5, "lifestyle": 2.0, "exercise": 2.0, "sleep": 2.0, 
        "hydration": 2.0, "water": 1.5, "checkup": 2.5, "screening": 2.5, 
        "doctor": 1.5, "hospital": 1.5, "general": 1.5, "routine": 2.0, 
        "guideline": 2.0, "guidelines": 2.0
    }
}


class HealthcareQueryClassifier:
    """
    Lightweight, deterministic healthcare query classifier.
    Scans processed tokens and multi-word n-grams against curated clinical taxonomies,
    evaluating category match scores and returning confidence scores.
    """

    def __init__(self):
        self.taxonomy = CATEGORY_TAXONOMY

    def classify(self, query: str, informative_tokens: List[str] = None) -> Dict[str, Any]:
        query_lower = query.lower()
        scores: Dict[str, float] = {cat: 0.0 for cat in CATEGORIES}
        matched_terms: Dict[str, List[str]] = {cat: [] for cat in CATEGORIES}

        # Check multi-word phrase matching directly on query string
        for category, terms in self.taxonomy.items():
            for term, weight in terms.items():
                if " " in term:
                    if term in query_lower:
                        scores[category] += weight * 1.5
                        matched_terms[category].append(term)

        # Check token matches
        tokens_to_check = informative_tokens or query_lower.split()
        for token in tokens_to_check:
            for category, terms in self.taxonomy.items():
                if token in terms and " " not in token:
                    scores[category] += terms[token]
                    matched_terms[category].append(token)

        # Determine winner
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]

        # If zero or very low score, default to General Healthcare
        if best_score < 1.0:
            best_category = "General Healthcare"
            confidence = 0.50
        else:
            total_score = sum(scores.values())
            confidence = round(min(1.0, best_score / total_score if total_score > 0 else 0.5), 2)

        return {
            "category": best_category,
            "confidence": confidence,
            "matched_keywords": list(set(matched_terms[best_category])),
            "all_scores": {k: round(v, 2) for k, v in scores.items() if v > 0}
        }


classifier = HealthcareQueryClassifier()

def classify_query(query: str, informative_tokens: List[str] = None) -> Dict[str, Any]:
    return classifier.classify(query, informative_tokens)

