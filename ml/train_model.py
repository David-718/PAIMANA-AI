"""
Optional model-comparison experiment.
Run: python ml/train_model.py
This script is intentionally conservative: the supplied dataset is a demo snapshot,
so metrics are illustrative and must not be presented as production accuracy.
"""
from pathlib import Path
import pandas as pd
from sklearn.model_selection import cross_validate, KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_predict

BASE=Path(__file__).resolve().parent.parent
df=pd.read_csv(BASE/"data/projects.csv")
df["cost_escalation_pct"]=(df.revised_cost_crore-df.original_cost_crore)/df.original_cost_crore*100
df["expenditure_pct"]=df.expenditure_crore/df.original_cost_crore*100
df["risk_proxy"]=(
    df.cost_escalation_pct.clip(lower=0)*3
    +(100-df.physical_progress_pct).clip(lower=0)*0.35
    +df.expenditure_pct.clip(lower=0)*0.05
)
features=["original_cost_crore","revised_cost_crore","expenditure_crore","physical_progress_pct","cost_escalation_pct","expenditure_pct"]
X=df[features].fillna(0); y=df["risk_proxy"]
cv=KFold(n_splits=5,shuffle=True,random_state=42)
models={
    "LinearRegression":LinearRegression(),
    "RandomForest":RandomForestRegressor(n_estimators=250,random_state=42,max_depth=6)
}
print("Prototype model comparison (illustrative; not production validation)")
for name,m in models.items():
    pred=cross_val_predict(m,X,y,cv=cv)
    print(f"{name:18s} MAE={mean_absolute_error(y,pred):.2f}  R2={r2_score(y,pred):.3f}")
