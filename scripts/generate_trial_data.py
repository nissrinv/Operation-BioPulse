"""Generates a small, messy, synthetic clinical trial dataset for data-quality practice.
Run: python generate_trial_data.py
Creates demographics.csv, vitals.csv, adverse_events.csv and answer_key.txt (do not open the key until you have finished).
All data is fictional."""
import csv
import random
from datetime import date, timedelta

random.seed(42)
N = 60
SITES = ["Waterford", "Dublin", "Cork"]
AE_TERMS = ["Headache", "Nausea", "Fatigue", "Dizziness", "Rash", "Cough"]
key = []

# --- demographics ---
demo = []
for i in range(1, N + 1):
    consent = date(2024, 1, 8) + timedelta(days=random.randint(0, 150))
    demo.append({
        "subject_id": f"S{i:03d}", "site": random.choice(SITES),
        "sex": random.choice(["M", "F"]), "age": random.randint(18, 80),
        "consent_date": consent.isoformat(),
        "randomisation_date": (consent + timedelta(days=random.randint(3, 14))).isoformat(),
        "arm": random.choice(["A", "B"]),
    })

# --- vitals (4 visits per subject) ---
vitals = []
for d in demo:
    rand = date.fromisoformat(d["randomisation_date"])
    for visit, offset in [("Baseline", 0), ("Week4", 28), ("Week8", 56), ("Week12", 84)]:
        vitals.append({
            "subject_id": d["subject_id"], "visit": visit,
            "visit_date": (rand + timedelta(days=offset + random.randint(-2, 2))).isoformat(),
            "systolic_bp": random.randint(105, 160), "diastolic_bp": random.randint(65, 95),
            "heart_rate": random.randint(55, 95), "weight_kg": round(random.uniform(55, 110), 1),
        })

# --- adverse events ---
aes = []
for d in demo:
    for _ in range(random.choice([0, 0, 1, 1, 2, 3])):
        start = date.fromisoformat(d["randomisation_date"]) + timedelta(days=random.randint(1, 80))
        sev = random.choice(["Mild", "Mild", "Moderate", "Severe"])
        aes.append({"subject_id": d["subject_id"], "ae_term": random.choice(AE_TERMS),
                    "start_date": start.isoformat(),
                    "end_date": (start + timedelta(days=random.randint(1, 14))).isoformat(),
                    "severity": sev, "serious": "N"})

# --- inject known problems ---
for d in random.sample(demo, 3):                       # 1. duplicate subjects
    demo.append(dict(d)); key.append(f"Duplicate demographics row: {d['subject_id']}")
for d, v in zip(random.sample(demo[:N], 4), ["Male", "female", "m", "F "]):   # 2. inconsistent sex coding
    d["sex"] = v; key.append(f"Inconsistent sex coding '{v}': {d['subject_id']}")
for d in random.sample(demo[:N], 5):                   # 3. missing age
    d["age"] = ""; key.append(f"Missing age: {d['subject_id']}")
for d, a in zip(random.sample(demo[:N], 2), [16, 17]): # 4. under-18 (eligibility)
    d["age"] = a; key.append(f"Age {a} (below inclusion age 18): {d['subject_id']}")
for v in random.sample(vitals, 6):                     # 5. impossible vitals
    field, bad = random.choice([("systolic_bp", 300), ("systolic_bp", 40), ("heart_rate", 5), ("heart_rate", 250)])
    v[field] = bad; key.append(f"{field}={bad}: {v['subject_id']} {v['visit']}")
for d in random.sample(demo[:N], 4):                   # 6. baseline before consent
    for v in vitals:
        if v["subject_id"] == d["subject_id"] and v["visit"] == "Baseline":
            v["visit_date"] = (date.fromisoformat(d["consent_date"]) - timedelta(days=5)).isoformat()
            key.append(f"Baseline visit before consent: {d['subject_id']}")
for a in random.sample(aes, 3):                        # 7. AE end before start
    a["end_date"] = (date.fromisoformat(a["start_date"]) - timedelta(days=3)).isoformat()
    key.append(f"AE end before start: {a['subject_id']} {a['ae_term']}")
for sid in ["S998", "S999"]:                           # 8. orphan subjects
    vitals.append({"subject_id": sid, "visit": "Baseline", "visit_date": "2024-05-01",
                   "systolic_bp": 120, "diastolic_bp": 80, "heart_rate": 70, "weight_kg": 80.0})
    key.append(f"Vitals for subject not in demographics: {sid}")
for v in random.sample(vitals[:N * 4], 8):             # 9. mixed date formats
    y, m, dd = v["visit_date"].split("-"); v["visit_date"] = f"{dd}/{m}/{y}"
    key.append(f"Date in DD/MM/YYYY: {v['subject_id']} {v['visit']}")
for a in random.sample(aes, 3):                        # 10. serious but mild
    a["serious"] = "Y"; a["severity"] = "Mild"
    key.append(f"Serious=Y but severity Mild: {a['subject_id']} {a['ae_term']}")
vitals.extend(dict(v) for v in random.sample(vitals[:N * 4], 3))   # 11. duplicate vitals rows
key.append("3 duplicated vitals rows (find them by subject_id + visit)")

def write(name, rows):
    with open(name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

random.shuffle(vitals)
write("demographics.csv", demo); write("vitals.csv", vitals); write("adverse_events.csv", aes)
open("answer_key.txt", "w").write("\n".join(key))
print(f"Created demographics.csv ({len(demo)} rows), vitals.csv ({len(vitals)} rows), adverse_events.csv ({len(aes)} rows)")
