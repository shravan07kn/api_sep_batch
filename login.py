
from flask import Flask, request, render_template_string, redirect, url_for
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Set MONGO_URI to your MongoDB Atlas connection string
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["shravan_login"]
users = db["users"]

# Prevent duplicate usernames
users.create_index("username", unique=True)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Shravan | Authentication</title>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: "Segoe UI", sans-serif;
}

body {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    color: white;
    background:
        radial-gradient(circle at top left, #292044, transparent 45%),
        radial-gradient(circle at bottom right, #12313b, transparent 45%),
        #080910;
}

.card {
    width: 100%;
    max-width: 410px;
    padding: 38px 32px;
    background: rgba(22, 23, 35, .96);
    border: 1px solid #303143;
    border-radius: 24px;
    box-shadow: 0 25px 70px #0009;
    animation: appear .5s ease;
}

@keyframes appear {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

.logo {
    width: 62px;
    height: 62px;
    margin: 0 auto 22px;
    display: grid;
    place-items: center;
    border-radius: 19px;
    background: linear-gradient(135deg, #a78bfa, #6366f1);
    font-size: 29px;
    font-weight: bold;
}

h1 {
    text-align: center;
    font-size: 28px;
    margin-bottom: 9px;
}

.subtitle {
    text-align: center;
    color: #999caf;
    font-size: 13px;
    margin-bottom: 27px;
}

.tabs {
    display: flex;
    padding: 5px;
    background: #10121d;
    border-radius: 12px;
    margin-bottom: 25px;
}

.tabs button {
    flex: 1;
    padding: 11px 5px;
    color: #999caf;
    background: transparent;
    border: none;
    border-radius: 9px;
    cursor: pointer;
    font-size: 13px;
}

.tabs button.active {
    background: #29223f;
    color: #c4b5fd;
}

label {
    display: block;
    font-size: 13px;
    margin: 16px 0 8px;
    color: #e1e2ed;
}

.input-box {
    position: relative;
}

input {
    width: 100%;
    padding: 14px;
    color: white;
    background: #10121d;
    border: 1px solid #343548;
    border-radius: 11px;
    outline: none;
    font-size: 14px;
}

input:focus {
    border-color: #8b5cf6;
    box-shadow: 0 0 0 3px #8b5cf622;
}

input::placeholder {
    color: #71758a;
}

.password {
    padding-right: 65px;
}

.toggle {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #a78bfa;
    cursor: pointer;
}

.submit {
    width: 100%;
    padding: 15px;
    margin-top: 24px;
    border: none;
    border-radius: 11px;
    background: linear-gradient(100deg, #8b5cf6, #6366f1);
    color: white;
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
    transition: .25s;
}

.submit:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px #6366f155;
}

.message {
    padding: 12px;
    margin-bottom: 18px;
    border-radius: 10px;
    font-size: 13px;
    text-align: center;
    line-height: 1.5;
}

.error {
    background: #dc262620;
    color: #fca5a5;
    border: 1px solid #dc262655;
}

.success {
    background: #16a34a20;
    color: #86efac;
    border: 1px solid #16a34a55;
}

.hidden {
    display: none;
}

.footer {
    text-align: center;
    color: #777b8d;
    font-size: 12px;
    margin-top: 25px;
}

.footer span {
    color: #a78bfa;
}

@media (max-width: 450px) {
    .card { padding: 30px 22px; }
}
</style>
</head>

<body>
<div class="card">

    <div class="logo">S</div>

    <h1 id="heading">Welcome Back</h1>
    <p class="subtitle" id="subtitle">
        Sign in to access your account
    </p>

    <div class="tabs">
        <button type="button" id="loginTab"
                class="{{ 'active' if mode == 'login' else '' }}"
                onclick="showForm('login')">
            Sign In
        </button>

        <button type="button" id="registerTab"
                class="{{ 'active' if mode == 'register' else '' }}"
                onclick="showForm('register')">
            Create Account
        </button>
    </div>

    {% if message %}
    <div class="message {{ status }}" role="status">
        {{ message }}
    </div>
    {% endif %}

    <form id="loginForm" method="POST" action="/login"
          class="{{ 'hidden' if mode == 'register' else '' }}">

        <label for="loginUsername">Username</label>
        <input id="loginUsername" name="username"
               placeholder="Enter your username"
               autocomplete="username" required>

        <label for="loginPassword">Password</label>
        <div class="input-box">
            <input id="loginPassword" name="password"
                   class="password" type="password"
                   placeholder="Enter your password"
                   autocomplete="current-password" required>
            <button type="button" class="toggle"
                    onclick="togglePassword('loginPassword', this)">
                Show
            </button>
        </div>

        <button class="submit" type="submit">Sign In →</button>
    </form>

    <form id="registerForm" method="POST" action="/register"
          class="{{ 'hidden' if mode == 'login' else '' }}">

        <label for="newUsername">Choose Username</label>
        <input id="newUsername" name="username"
               placeholder="Create a username"
               minlength="3" maxlength="30"
               autocomplete="username" required>

        <label for="newPassword">Create Password</label>
        <div class="input-box">
            <input id="newPassword" name="password"
                   class="password" type="password"
                   placeholder="At least 8 characters"
                   minlength="8" autocomplete="new-password"
                   required>
            <button type="button" class="toggle"
                    onclick="togglePassword('newPassword', this)">
                Show
            </button>
        </div>

        <button class="submit" type="submit">
            Create Account →
        </button>
    </form>

    <div class="footer">Secure Access · <span>Shravan</span></div>
</div>

<script>
function showForm(mode) {
    const login = mode === "login";

    document.getElementById("loginForm").classList.toggle("hidden", !login);
    document.getElementById("registerForm").classList.toggle("hidden", login);

    document.getElementById("loginTab").classList.toggle("active", login);
    document.getElementById("registerTab").classList.toggle("active", !login);

    document.getElementById("heading").textContent =
        login ? "Welcome Back" : "Create Account";

    document.getElementById("subtitle").textContent =
        login ? "Sign in to access your account" :
                "Join us by creating your account";
}

function togglePassword(id, button) {
    const field = document.getElementById(id);
    field.type = field.type === "password" ? "text" : "password";
    button.textContent = field.type === "password" ? "Show" : "Hide";
}

// Show the registration form if Flask requests it
{% if mode == 'register' %}
showForm("register");
{% endif %}
</script>
</body>
</html>
"""


def render_page(mode="login", message="", status=""):
    return render_template_string(
        HTML, mode=mode, message=message, status=status
    )


@app.route("/")
def home():
    registered = request.args.get("registered") == "1"

    return render_page(
        mode="login",
        message="Account created successfully! Please sign in."
        if registered else "",
        status="success" if registered else ""
    )


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")

    try:
        user = users.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            # Login validated. Add your protected page/dashboard here.
            return render_page(
                mode="login",
                message=f"Login successful! Welcome, {username}.",
                status="success"
            )

        return render_page(
            mode="login",
            message="Invalid username or password.",
            status="error"
        )

    except PyMongoError:
        return render_page(
            mode="login",
            message="Database connection failed. Please try again.",
            status="error"
        )


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")

    if not username or len(username) < 3 or len(username) > 30:
        return render_page(
            "register", "Username must be 3–30 characters.", "error"
        )

    if not all(c.isalnum() or c in "_-" for c in username):
        return render_page(
            "register",
            "Username can contain letters, numbers, _ and - only.",
            "error"
        )

    if len(password) < 8:
        return render_page(
            "register", "Password must be at least 8 characters.", "error"
        )

    try:
        users.insert_one({
            "username": username,
            "password": generate_password_hash(password)
        })

        # After registration, redirect to the sign-in page
        return redirect(url_for("home", registered="1"))

    except DuplicateKeyError:
        return render_page(
            "register",
            "Username already exists. Please choose another.",
            "error"
        )

    except PyMongoError:
        return render_page(
            "register",
            "Database connection failed. Please try again.",
            "error"
        )


if __name__ == "__main__":
    app.run(debug=True)
