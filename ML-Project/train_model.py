import pandas as pd
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

print("Starting Training...")

BASE = os.path.dirname(os.path.abspath(__file__))

# Dataset paths
sql_path = BASE+"/dataset/sqliv2.csv"
xss_path = BASE+"/dataset/XSS_dataset.csv"

# Load dataset (Kaggle format fix)
data1 = pd.read_csv(sql_path,encoding="latin1",on_bad_lines='skip')
data2 = pd.read_csv(xss_path,encoding="latin1",on_bad_lines='skip')

# Merge datasets
data = pd.concat([data1,data2],ignore_index=True)

# ⭐ Your dataset columns
if "Sentence" in data.columns:
    X = data["Sentence"]
else:
    print("❌ Sentence column not found")
    exit()

if "Label" in data.columns:
    y = data["Label"]
else:
    print("❌ Label column not found")
    exit()

# Remove empty rows
data = pd.DataFrame({"X":X,"y":y}).dropna()

X = data["X"]
y = data["y"]

# ML Training
vectorizer = TfidfVectorizer()

X_vec = vectorizer.fit_transform(X)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_vec,y)

# Save model
os.makedirs("model",exist_ok=True)

joblib.dump(model,"model/ml_model.pkl")
joblib.dump(vectorizer,"model/vectorizer.pkl")

print("✅ Training Completed Successfully")