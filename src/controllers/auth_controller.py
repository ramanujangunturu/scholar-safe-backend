from fastapi import HTTPException, status
from ..models.user_model import UserSignUp, UserLogin
from ..services.auth_service import create_access_token, verify_password, get_password_hash
from ..services.database_service import get_user_by_email, create_user

async def signup(user: UserSignUp):
    existing_user = await get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    user_data = {"email": user.email, "username": user.username, "password": hashed_password}
    await create_user(user_data)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

async def login(user: UserLogin):
    db_user = await get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

async def loginEmail(user: UserLogin):
    db_user = await get_user_by_email(user.email)
    print(db_user)
    print("helo")
    if not db_user :
        raise HTTPException(status_code=400, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}