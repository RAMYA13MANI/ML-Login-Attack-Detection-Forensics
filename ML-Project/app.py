from flask import Flask,render_template,request
import joblib
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Database (Port 3307)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Root@321",
    database="vapt_ml",
    port=3307
)

cursor = conn.cursor()

# Load ML Model
model = joblib.load("model/ml_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")

# Login page
@app.route('/')
def home():
    return render_template("login.html")

# Detection function
def detect_attack(text):

    text = text.lower()

    # Rule based detection (VERY IMPORTANT ⭐)
    sql_keywords = ["select","union","insert","delete","drop","--","' or","1=1"]
    xss_keywords = ["<script","alert(","onerror","onclick","javascript"]

    for kw in sql_keywords:
        if kw in text:
            return "SQL Injection",100

    for kw in xss_keywords:
        if kw in text:
            return "XSS Attack",100

    # ML Prediction
    vec = vectorizer.transform([text])

    pred = model.predict(vec)[0]
    confidence = max(model.predict_proba(vec)[0])*100

    attack_map = {
        0:"Normal",
        1:"SQL Injection",
        2:"XSS Attack"
    }

    attack = attack_map.get(int(pred),"Unknown")

    return attack,confidence# Login process
@app.route('/login',methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    # Your real credential
    real_user = "ramya1"
    real_pass = "ramya123"

    payload = username + password

    attack,confidence = detect_attack(payload)

    print(f"[{datetime.now()}] {payload} --> {attack} ({confidence:.2f}%)")

    # Store mysql log
    ip = request.remote_addr

    cursor.execute("""
    INSERT INTO logs(username,password,ip,attack,confidence)
    VALUES(%s,SHA2(%s,256),%s,%s,%s)
    """,(username,password,ip,attack,confidence))

    conn.commit()

    # Authentication check
    if username==real_user and password==real_pass:

        return """
        <h2>Login Success ✅</h2>
        <a href="/">Back</a>
        """

    else:

        return f"""
        <h2>Login Failed ❌</h2>
        Attack Type : {attack}<br>
        Confidence : {confidence:.2f}%
        """

if __name__=="__main__":
    app.run(debug=True)