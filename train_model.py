<<<<<<< HEAD
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
data = pd.read_csv("placement.csv")

# Convert Internship (Yes/No -> 1/0)
encoder = LabelEncoder()
data["internship"] = encoder.fit_transform(data["internship"])

# Features
X = data[[
    "cgpa",
    "tenth",
    "twelfth",
    "aptitude",
    "programming",
    "communication",
    "projects",
    "internship",
    "backlogs",
    "certifications"
]]

# Target
y = data["placed"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Accuracy
accuracy = model.score(X_test, y_test)
print("Accuracy:", accuracy)

# Save model
joblib.dump(model, "model.pkl")

=======
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
data = pd.read_csv("placement.csv")

# Convert Internship (Yes/No -> 1/0)
encoder = LabelEncoder()
data["internship"] = encoder.fit_transform(data["internship"])

# Features
X = data[[
    "cgpa",
    "tenth",
    "twelfth",
    "aptitude",
    "programming",
    "communication",
    "projects",
    "internship",
    "backlogs",
    "certifications"
]]

# Target
y = data["placed"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Accuracy
accuracy = model.score(X_test, y_test)
print("Accuracy:", accuracy)

# Save model
joblib.dump(model, "model.pkl")

>>>>>>> 87c3a9673fbff13ae707d7f5b6a3ae3c9f7e76c5
print("Model Saved Successfully")