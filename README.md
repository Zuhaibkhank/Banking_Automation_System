# 🏦 Banking Automation System

A full-stack banking web application built using Flask and MongoDB that allows users to securely create accounts, log in, and perform basic banking operations such as deposits and withdrawals.

---

## 🌐 Live Demo

[![Live Demo](https://img.shields.io/badge/Live%20Website-Click%20Here-green?style=for-the-badge)](https://banking-automation-system.onrender.com/)
---

## 🚀 Features

* 🔐 User Registration & Login System
* 🔒 Secure Password Hashing using Werkzeug
* 💰 Deposit Money
* 💸 Withdraw Money
* 📊 Real-time Balance Update
* 🧠 Session Management (Login/Logout)
* ☁️ MongoDB Atlas Cloud Database
* 🌍 Deployed on Render

---

## 🛠️ Tech Stack

**Frontend**

* HTML5
* CSS3

**Backend**

* Python (Flask)

**Database**

* MongoDB Atlas

**Deployment**

* Render

---

## 📂 Project Structure

```
Banking_Automation_System/
│
├── static/
│   └── style.css
│
├── templates/
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
│
├── app.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup (Local)

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/Banking_Automation_System.git
cd Banking_Automation_System
```

### 2️⃣ Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup environment variables

Create a `.env` file or set manually:

```env
MONGO_URI=your_mongodb_connection_string
SECRET_KEY=your_secret_key
```

### 5️⃣ Run the app

```bash
python app.py
```

👉 Open in browser: http://127.0.0.1:5000/

---

## ☁️ Deployment

This project is deployed using **Render** with MongoDB Atlas.

### Steps:

* Push code to GitHub
* Connect repository to Render
* Add environment variables (MONGO_URI, SECRET_KEY)
* Deploy using:

```bash
gunicorn app:app
```

---

## 🔐 Security Features

* Passwords are hashed using `werkzeug.security`
* Session-based authentication
* Input validation for user data
* Duplicate account prevention

---

## 📸 Screenshots

(Add your project screenshots here for better presentation)

---

## 📈 Future Improvements

* 📜 Transaction History
* 📧 Email Notifications
* 🧾 Account Statements (PDF)
* 🛡️ Two-Factor Authentication
* 👨‍💼 Admin Dashboard

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork this repository and submit a pull request.

---

## 📄 License

This project is open-source and available under the MIT License.

---

## 👨‍💻 Author

**Zuhaib Khan**
🔗 GitHub: https://github.com/Zuhaibkhank

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
