---
title: "Diabetes Risk Classification"
kernel: python3
author: "Mathis Kristoffer Arends"
---

[TOC]

---

## 1. Business Understanding {#chapter1}

### 1.1 Projektkontext {#chap1_1}

Das Ziel dieses Projekts ist die Entwicklung eines Klassifikationsmodells zur Vorhersage des Diabetesrisikos basierend auf diagnostischen Messwerten.

### 1.2 Zielsetzung {#chap1_2}

- Binäre Klassifikation: **Diabetes ja/nein**
- Optimierung auf hohen Recall (Kranke nicht übersehen)
- Interpretierbarkeit des Modells für medizinisches Fachpersonal

---

## 2. Data Understanding {#chapter2}

### 2.1 Daten laden {#chap2_1}

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("diabetes.csv")
print(f"Shape: {df.shape}")
df.head()
```

### 2.2 Überblick {#chap2_2}

```python
df.describe()
```

```python
df.info()
```

### 2.3 Verteilung der Zielvariable {#chap2_3}

```python
fig, ax = plt.subplots(figsize=(6, 4))
df["Outcome"].value_counts().plot(kind="bar", color=["#2E86AB", "#E74C3C"], ax=ax)
ax.set_title("Verteilung der Zielvariable")
ax.set_xticklabels(["Kein Diabetes", "Diabetes"], rotation=0)
plt.tight_layout()
plt.show()
```

---

## 3. Data Preparation {#chapter3}

### 3.1 Fehlende Werte {#chap3_1}

Einige Features verwenden `0` als Platzhalter für fehlende Werte (z.B. Glucose, BloodPressure, BMI).

```python
zero_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
for col in zero_cols:
    df[col] = df[col].replace(0, np.nan)

print("Fehlende Werte pro Spalte:")
print(df.isnull().sum())
```

### 3.2 Imputation & Skalierung {#chap3_2}

```python
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

imputer = SimpleImputer(strategy="median")
df[zero_cols] = imputer.fit_transform(df[zero_cols])

scaler = StandardScaler()
X = scaler.fit_transform(df.drop("Outcome", axis=1))
y = df["Outcome"].values
```

---

## 4. Modeling {#chapter4}

### 4.1 Train/Test Split {#chap4_1}

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")
```

### 4.2 Random Forest {#chap4_2}

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, fbeta_score

model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
print(f"F₂-Score: {fbeta_score(y_test, y_pred, beta=2):.3f}")
```

---

## 5. Evaluation {#chapter5}

### 5.1 Confusion Matrix {#chap5_1}

```python
from sklearn.metrics import ConfusionMatrixDisplay

fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay.from_predictions(y_test, y_pred, ax=ax, cmap="Blues")
ax.set_title("Confusion Matrix")
plt.tight_layout()
plt.show()
```

### 5.2 Feature Importance {#chap5_2}

```python
importances = pd.Series(model.feature_importances_, index=df.drop("Outcome", axis=1).columns)
importances = importances.sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(8, 4))
importances.plot(kind="barh", color="#2E86AB", ax=ax)
ax.set_title("Feature Importance (Random Forest)")
plt.tight_layout()
plt.show()
```
