# Daily Routine (FastAPI + Jinja)

A simple daily routine tracker with:

- Navbar links: Routine, About, Contact, Help
- Index page
- Login page (demo auth)
- Home page after login
- Add / Delete / Progress update routines

## Run

```bash
pip install fastapi uvicorn jinja2 python-multipart
uvicorn main:app --reload
```

Open: `http://127.0.0.1:8000`

Demo login:

- username: `admin`
- password: `admin123`
