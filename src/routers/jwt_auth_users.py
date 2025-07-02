from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt

ALGORITHM = "HS256 "

app = FastAPI()

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDB(User):
    password: str

users_db = {
    "runlevel": {
        "username": "runlevel",
        "full_name": "Pedro González",
        "email": "ped.ro@gmail.com",
        "disabled": False,
        "password": "123456"
    },
    "cris": {
        "username": "cris",
        "full_name": "Cris Carrillo",
        "email": "cris.car@gmail.com",
        "disabled": True,
        "password": "654321"
    }
}

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="El usuario no existe")

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = search_user_db(form.username)

    if not form.password == user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña no es correcta")
    
    return {"access_token":user.username, "token_type":"bearer"}