from fastapi import APIRouter
from ..models.user_model import UserSignUp, UserLogin, AuthResponse
from ..controllers.auth_controller import signup, login

router = APIRouter()

@router.post("/signup", response_model=AuthResponse)
async def signup_route(user: UserSignUp):
    return await signup(user)

@router.post("/login", response_model=AuthResponse)
async def login_route(user: UserLogin):
    return await login(user)