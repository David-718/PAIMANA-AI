"""
Optional ML experiment for SIH26103.
Creates a simple RandomForest risk classifier using synthetic demo records.
The production version should be trained/evaluated on authorised historical data.
"""
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

BASE = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE / "data" / "projects.csv")

cost_overrun = (df.revised_cost_crore - df.original_cost_crore) / df.original_cost_crore * 100
schedule_gap = (df.elapsed_months / df.planned_duration_months * 100) - df.physical_progress_pct

df["risk_target"] = (
    (cost_overrun > 7) |
    (schedule_gap > 10) |
    (df.delayed_milestones >= 3) |
    (df.contractual_risk >= 65)
).astype(int)

features = [
    "original_cost_crore","planned_duration_months","elapsed_months",
    "physical_progress_pct","financial_progress_pct","delayed_milestones",
    "open_issues","contractual_risk"
]
X, y = df[features], df.risk_target

if len(df) >= 8 and y.nunique() > 1:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=.25, random_state=42, stratify=y
    )
    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X_train, y_train)
    print(classification_report(y_test, model.predict(X_test), zero_division=0))
else:
    print("Demo dataset is intentionally small; add authorised historical records before model evaluation.")
