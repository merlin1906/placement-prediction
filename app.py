from flask import Flask, render_template, request, redirect, session 
from flask_mysqldb import MySQL
import joblib
import numpy as np
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.secret_key = "placement_prediction_secret"

app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "placement_prediction"

mysql = MySQL(app)
model = joblib.load("model.pkl")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method=="POST":

        name=request.form["name"]
        email=request.form["email"]
        password=request.form["password"]
        department=request.form["department"]
        cgpa=request.form["cgpa"]
        tenth=request.form["tenth"]
        twelfth=request.form["twelfth"]
        aptitude=request.form["aptitude"]
        programming=request.form["programming"]
        communication=request.form["communication"]
        projects=request.form["projects"]
        internship=request.form["internship"]
        backlogs=request.form["backlogs"]
        certifications=request.form["certifications"]

        cur=mysql.connection.cursor()

        cur.execute("""
        INSERT INTO students
        (name,email,password,department,cgpa,tenth,twelfth,
        aptitude,programming,communication,
        projects,internship,backlogs,certifications)

        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)

        """,

        (name,email,password,department,cgpa,tenth,
        twelfth,aptitude,programming,
        communication,projects,
        internship,backlogs,certifications))

        mysql.connection.commit()

        cur.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM students WHERE email=%s AND password=%s",
            (email, password)
        )

        student = cur.fetchone()

        cur.close()

        if student:
           session["email"] = email
           return redirect("/dashboard")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "email" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM students WHERE email=%s",
        (session["email"],)
    )

    data = cur.fetchone()

    # Latest prediction
    cur.execute("""
    SELECT prediction
    FROM prediction_history
    WHERE student_email=%s
    ORDER BY created_at DESC
    LIMIT 1
    """, (session["email"],))

    pred = cur.fetchone()

    cur.close()

    student = {
        "name": data[1],
        "email": data[2],
        "department": data[4],
        "cgpa": data[5],
        "projects": data[11],
        "internship": data[12],
        "prediction": pred[0] if pred else "Pending"
    }

    return render_template("dashboard.html", student=student)
@app.route("/prediction")
def prediction():

    if "email" not in session:
        return redirect("/login")

    return render_template("prediction.html")
@app.route("/predict", methods=["POST"])
def predict():
    if "email" not in session:
         return redirect("/login")

    cgpa = float(request.form["cgpa"])
    tenth = float(request.form["tenth"])
    twelfth = float(request.form["twelfth"])
    aptitude = int(request.form["aptitude"])
    programming = int(request.form["programming"])
    communication = int(request.form["communication"])
    projects = int(request.form["projects"])

    internship = request.form["internship"]
    internship_value = 1 if internship == "Yes" else 0

    backlogs = int(request.form["backlogs"])
    certifications = int(request.form["certifications"])

    features = np.array([[
        cgpa,
        tenth,
        twelfth,
        aptitude,
        programming,
        communication,
        projects,
        internship_value,
        backlogs,
        certifications
    ]])

    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]
    chance = round(max(probability) * 100, 2)

    if prediction == 1:
        result = "Placed"
    else:
        result = "Not Placed"

    cur = mysql.connection.cursor()

    cur.execute("""
    INSERT INTO prediction_history
    (student_email, cgpa, tenth, twelfth, aptitude,
    programming, communication, projects,
    internship, backlogs, certifications,
    prediction, probability)

    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        session["email"],
        cgpa,
        tenth,
        twelfth,
        aptitude,
        programming,
        communication,
        projects,
        internship,
        backlogs,
        certifications,
        result,
        chance
    ))

    mysql.connection.commit()
    cur.close()

    return render_template(
        "result.html",
        result=result,
        chance=chance
    )
@app.route("/history")
def history():

    if "email" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT cgpa, prediction, probability, created_at
        FROM prediction_history
        WHERE student_email=%s
        ORDER BY created_at DESC
    """, (session["email"],))

    history = cur.fetchall()

    cur.close()

    return render_template("history.html", history=history)
@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "email" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    if request.method == "POST":

        name = request.form["name"]
        department = request.form["department"]
        cgpa = request.form["cgpa"]
        tenth = request.form["tenth"]
        twelfth = request.form["twelfth"]
        aptitude = request.form["aptitude"]
        programming = request.form["programming"]
        communication = request.form["communication"]
        projects = request.form["projects"]
        internship = request.form["internship"]
        backlogs = request.form["backlogs"]
        certifications = request.form["certifications"]

        photo = request.files.get("photo")

        if photo and photo.filename != "":

            filename = secure_filename(photo.filename)

            photo.save(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )
            
            print("Photo object:", photo)
            print("Filename:", filename)
            cur.execute("""
            UPDATE students
            SET
            name=%s,
            department=%s,
            cgpa=%s,
            tenth=%s,
            twelfth=%s,
            aptitude=%s,
            programming=%s,
            communication=%s,
            projects=%s,
            internship=%s,
            backlogs=%s,
            certifications=%s,
            photo=%s
            WHERE email=%s
            """,
            (
                name,
                department,
                cgpa,
                tenth,
                twelfth,
                aptitude,
                programming,
                communication,
                projects,
                internship,
                backlogs,
                certifications,
                filename,
                session["email"]
            ))

        else:

            cur.execute("""
            UPDATE students
            SET
            name=%s,
            department=%s,
            cgpa=%s,
            tenth=%s,
            twelfth=%s,
            aptitude=%s,
            programming=%s,
            communication=%s,
            projects=%s,
            internship=%s,
            backlogs=%s,
            certifications=%s
            WHERE email=%s
            """,
            (
                name,
                department,
                cgpa,
                tenth,
                twelfth,
                aptitude,
                programming,
                communication,
                projects,
                internship,
                backlogs,
                certifications,
                session["email"]
            ))

        mysql.connection.commit()
        print("Profile Updated Successfully")

    cur.execute(
        "SELECT * FROM students WHERE email=%s",
        (session["email"],)
    )

    data = cur.fetchone()

    cur.close()

    student = {
        "name": data[1],
        "email": data[2],
        "department": data[4],
        "cgpa": data[5],
        "tenth": data[6],
        "twelfth": data[7],
        "aptitude": data[8],
        "programming": data[9],
        "communication": data[10],
        "projects": data[11],
        "internship": data[12],
        "backlogs": data[13],
        "certifications": data[14],
        "photo": data[15]
    }

    return render_template("profile.html", student=student)
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/testdb")
def testdb():

    cur = mysql.connection.cursor()
    cur.execute("SELECT DATABASE()")
    data = cur.fetchone()
    cur.close()

    return f"Connected Successfully : {data}"

if __name__ == "__main__":
    app.run(debug=True)