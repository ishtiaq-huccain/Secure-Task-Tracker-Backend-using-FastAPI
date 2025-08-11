# 📝 FastAPI Task Manager

A simple **Task Management API** built with [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), and [JWT Authentication](https://jwt.io/).  
It supports **user registration**, **login**, **CRUD operations** for tasks, and **admin-only endpoints** for managing users and tasks.

---

## 🚀 Features
- User registration & JWT-based authentication
- Role-based access control (`user` / `admin`)
- Create, read, update, delete tasks (user-scoped)
- Admin endpoints to view and manage all users & tasks
- Search and filter tasks by status or keywords
- Pagination for listing tasks and users

---

## 📂 Project Structure  
├── app/  
│ ├── main.py # FastAPI entry point  
│ ├── models.py # SQLAlchemy ORM models  
│ ├── database.py # DB engine & session  
│ ├── auth.py # JWT token creation & verification  
│ ├── routes/ # API endpoint definitions  
│ ├── schemas.py # Pydantic schemas  
│ ├── settings.py # App configuration  
│ └── ...  
├── requirements.txt  
├── README.md  


---

## ⚙️ Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/task-manager.git
cd task-manager

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt

DATABASE_URL=sqlite:///./app.db
JWT_SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

just create tables directly
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

uvicorn app.main:app --reload

```

## Authentication
This API uses JWT (JSON Web Tokens) for authentication.

Login to receive an access token.

Include the token in the Authorization header for protected endpoints.  

## API Endpoints:  
Auth:  
| Method | Endpoint    | Description                   |
| ------ | ----------- | ----------------------------- |
| POST   | `/register` | Create new user               |
| POST   | `/login`    | Authenticate user & get token |  

User Task Endpoints:    

| Method | Endpoint      | Description                                               |
| ------ | ------------- | --------------------------------------------------------- |
| POST   | `/tasks`      | Create task                                               |
| GET    | `/tasks`      | List tasks (supports `skip`, `limit`, `status`, `search`) |
| GET    | `/tasks/{id}` | Get specific task                                         |
| PUT    | `/tasks/{id}` | Update task                                               |
| DELETE | `/tasks/{id}` | Delete task                                               |  

Admin Endpoints:   
| Method | Endpoint                 | Description      |
| ------ | ------------------------ | ---------------- |
| GET    | `/admin/tasks`           | List all tasks   |
| GET    | `/admin/users`           | List all users   |
| DELETE | `/admin/users/{id}`      | Delete a user    |
| PUT    | `/admin/users/{id}/role` | Change user role |

