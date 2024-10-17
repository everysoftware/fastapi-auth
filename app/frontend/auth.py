from fastapi import APIRouter, Request, Response

from app.templating import templates

router = APIRouter()


@router.get("/login")
def login(request: Request) -> Response:
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/oauth-callback")
def callback(request: Request) -> Response:
    return templates.TemplateResponse("login.html", {"request": request})
