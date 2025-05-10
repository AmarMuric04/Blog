# 📝 Flask Blog – Personal + Shared Blog System

A simple but powerful **blog platform** built with **Flask**, using **Jinja templates** and **Bootstrap** for clean, responsive design. Designed for **personal** use and optionally **shared authorship**, this blog includes secure login, post creation/editing, and SQLite persistence.

Deployed effortlessly on **Render** – just plug in and write.

---

## 🧰 Tech Stack

| Layer        | Tech                |
|--------------|---------------------|
| Backend      | Flask (Python)      |
| Templates    | Jinja2              |
| Frontend     | Bootstrap 5         |
| Auth         | Flask-Login         |
| Forms        | WTForms             |
| Passwords    | Werkzeug (secure hash) |
| Database     | SQLite (local)      |
| Deployment   | Render              |

---

## 🚀 Features

- 🧑‍💻 User registration & login with secure password hashing
- ✍️ Create, edit, delete posts (only by the author)
- 👥 Shared author capability (multiple users can post)
- 🧾 WTForms-based form handling with validation
- 🪪 Flask-Login session management
- 💡 Responsive and clean design with Bootstrap
- ⚡ Deployed on [Render](https://render.com)

---

## 🏁 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/amarmuric04/blog.git
cd flask-blog
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venvScriptsactivate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables (optional for dev)

On Linux/macOS:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
export EMAIL_USER=muricamar2004@gmail.com
export EMAIL_PASS=jexjlwyiovoruwxp
```

On Windows:

```bash
set FLASK_APP=app.py
set FLASK_ENV=development
set EMAIL_USER=muricamar2004@gmail.com
set EMAIL_PASS=jexjlwyiovoruwxp
```

### 5. Initialize the Database

```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

> This creates `blog.db` in the project root.

### 6. Run the App

```bash
flask run
```

Go to: **http://127.0.0.1:10000**

---

## 📁 Project Structure

``
/templates          → Jinja2 HTML templates
/static             → Bootstrap, custom CSS, JS
/app.py             → Main Flask app
/models.py          → Database models
/forms.py           → WTForms for login/register/posts
/routes.py          → View functions and routes
/requirements.txt   → Python dependencies
/blog.db            → SQLite database (auto-generated)
``

---

## 🌍 Deployment (Render)

1. Create a new Web Service on [Render](https://render.com)
2. Set your start command:
   ```
   gunicorn app:app
   ```
3. Add a `requirements.txt` and `render.yaml` if desired
4. Set environment variables on Render (e.g. FLASK_ENV)

---

## 🔐 Security Notes

- Passwords are hashed using Werkzeug's secure hashing tools
- User sessions are managed with Flask-Login
- WTForms includes CSRF protection by default
- SQLite is great for personal use; upgrade to Postgres if scaling

---

## 📄 License

MIT

---

Built with ❤️ using Flask, Bootstrap, and SQLite.
