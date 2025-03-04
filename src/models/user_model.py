from pydantic import BaseModel, EmailStr

# Request models
class UserSignUp(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response model
class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"