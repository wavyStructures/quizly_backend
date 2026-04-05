# 🧠 Quizly Backend

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)  
![Django](https://img.shields.io/badge/Django-5-green?logo=django&logoColor=white)  
![DRF](https://img.shields.io/badge/DRF-REST%20Framework-red?logo=django&logoColor=white)  
![SQLite](https://img.shields.io/badge/SQLite-3-blue?logo=sqlite&logoColor=white)  

---

A **Django REST Framework** backend for **Quizly**, a quiz management application.  
It provides user authentication and a fully functional API to create, manage, and retrieve quizzes.

The project is designed as a clean, scalable REST API with proper testing and authentication.

---

## 🌐 Frontend Integration

This backend is designed to work with an external frontend (e.g. running on `http://127.0.0.1:5500`).

Important settings:
- CORS is enabled for the frontend origin
- Cookies are used for authentication (JWT in HTTP-only cookies)
- Requests must include credentials (`credentials: "include"`)

Make sure your `.env` and settings are configured accordingly.



## 🚀 Features

- 🔑 **Authentication**
  - User registration
  - Login with JWT (stored in cookies)

- 🧑‍💻 **User System**
  - Custom user model
  - Login using username

- 📝 **Quiz Management**
  - Create quizzes
  - Retrieve quiz details
  - List quizzes (user-specific)
  - Permissions (users only see their own quizzes)

- 🔒 **Security**
  - Cookie-based JWT authentication
  - CSRF protection

- 🧪 **Testing**
  - Pytest-based test suite
  - Covers authentication and quiz endpoints

---

## 🛠️ Tech Stack

- **Backend**: Django 5 + Django REST Framework  
- **Database**: SQLite (development)  
- **Authentication**: JWT (SimpleJWT, cookie-based)  
- **Testing**: Pytest + DRF test utilities  

---

## 📦 Installation & Setup

### 🔹 Prerequisites

- Python 3.12+  
- pip / virtualenv  

---

### 🔹 Clone the Repository

git clone https://github.com/your-username/quizly_backend.git
cd quizly_backend


## Environment Variables

This project requires a Google API key to generate quizzes.

### 1. Create `.env` file

In the root directory of the project, create a file named `.env`.

You can copy the provided template:

cp .env.template .env


## 📦 Setup & Usage Guide

### 🔹 Create Virtual Environment

python -m venv env
source env/bin/activate   # macOS/Linux
env\Scripts\activate      # Windows



### 🔹 Install Dependencies

pip install -r requirements.txt


### 🔹 Apply Migrations

python manage.py migrate


## 🔹 Run the Server

    python manage.py runserver

Server will be available at:

📡 http://127.0.0.1:8000

---

## 📡 API Endpoints (Examples)

### 🔑 Authentication

- POST /api/register/ → Register new user  
- POST /api/login/ → Login (sets auth cookies)  
- POST /api/logout/ → Logout  
- POST /api/refresh/ → Refresh token  

### 📝 Quiz Management

- POST /api/quizzes/ → Create a new quiz (from YouTube URL)  
- GET /api/quizzes/ → List user’s quizzes  
- GET /api/quizzes/{id}/ → Retrieve quiz details  
- PATCH /api/quizzes/{id}/ → Update quiz (partial update)  
- DELETE /api/quizzes/{id}/ → Delete quiz  

---

## 🧪 Running Tests

    pytest

---

## ⚙️ Project Structure (Simplified)

    quizly_backend/
    │
    ├── quizly_app/        # Quiz logic
    ├── user_auth_app/     # Authentication system
    ├── core/              # Settings & configuration
    ├── tests/             # Pytest test suite
    └── manage.py

---

## 📖 Notes

- Uses SQLite → no external database required  
- db.sqlite3 is not tracked in Git  
- Migrations are included and required  
- Authentication uses cookies (JWT) instead of headers  

---

## 📜 License

MIT License – free to use and adapt.