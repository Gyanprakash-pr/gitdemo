from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI(title="Daily Routine")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@dataclass
class Routine:
    id: int
    title: str
    description: str
    progress: int


routines: List[Routine] = []
next_id = 1

# Demo in-memory user store (plain text for demo only)
users: Dict[str, str] = {"admin": "admin123"}


def current_user(request: Request) -> Optional[str]:
    return request.cookies.get("user")


def auth_required(request: Request) -> Optional[RedirectResponse]:
    if not current_user(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return None


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": current_user(request),
            "routines": routines,
        },
    )


@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse(
        "about.html",
        {"request": request, "user": current_user(request)},
    )


@app.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse(
        "contact.html",
        {"request": request, "user": current_user(request)},
    )


@app.get("/help")
def help_page(request: Request):
    return templates.TemplateResponse(
        "help.html",
        {"request": request, "user": current_user(request)},
    )


@app.get("/login")
def login_page(request: Request, error: str = ""):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": error,
            "user": current_user(request),
        },
    )


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if users.get(username) != password:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password.",
                "user": None,
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    response = RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("user", username, httponly=True)
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("user")
    return response


@app.get("/home")
def home(request: Request):
    redirect = auth_required(request)
    if redirect:
        return redirect

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": current_user(request),
            "routines": routines,
        },
    )


@app.post("/routines/add")
def add_routine(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    progress: int = Form(0),
):
    redirect = auth_required(request)
    if redirect:
        return redirect

    global next_id
    safe_progress = max(0, min(progress, 100))
    routines.append(
        Routine(id=next_id, title=title.strip(), description=description.strip(), progress=safe_progress)
    )
    next_id += 1
    return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/routines/{routine_id}/delete")
def delete_routine(request: Request, routine_id: int):
    redirect = auth_required(request)
    if redirect:
        return redirect

    global routines
    routines = [routine for routine in routines if routine.id != routine_id]
    return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/routines/{routine_id}/progress")
def update_progress(request: Request, routine_id: int, progress: int = Form(...)):
    redirect = auth_required(request)
    if redirect:
        return redirect

    safe_progress = max(0, min(progress, 100))
    for routine in routines:
        if routine.id == routine_id:
            routine.progress = safe_progress
            break

    return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)
