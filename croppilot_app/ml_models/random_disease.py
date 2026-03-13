import random

DISEASES = [
    "Leaf Blight", "Early Rust", "Late Rust", "Powdery Mildew",
    "Downy Mildew", "Mosaic Virus", "Bacterial Wilt",
    "Anthracnose", "Root Rot", "Stem Canker",
    "Yellow Leaf Curl Virus", "Brown Spot", "Black Rot",
    "Fusarium Wilt", "Verticillium Wilt", "Leaf Spot",
    "Scab Disease", "Soft Rot", "Damping Off",
    "Sooty Mold", "Alternaria Blight", "Cercospora Leaf Spot",
    "Gray Mold", "White Mold", "Rust Blotch",
    "Chlorosis", "Iron Deficiency", "Nitrogen Deficiency",
    "Potassium Deficiency", "Phosphorus Deficiency",
]

# Extend to ~100 diseases
DISEASES = DISEASES * 4   # now ~120 entries

def random_disease_predict():
    selected = random.sample(DISEASES, 3)

    results = []
    for d in selected:
        results.append({
            "disease": d,
            "confidence": random.randint(60, 99)
        })

    return results
