import os
from typing import Annotated
from fastapi import Cookie, FastAPI, Header, Request, Response, status, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from app.routers.movie_router import movie_router
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.utils import exceptions

app = FastAPI() # app = FastAPI(dependencies=[Depends(common_params)]) # Añadir dependencias a nivel global de la app
app.title="App de prueba"
app.version="0.0.1"
app.include_router(movie_router) # Incluímos el router de movies
#app.add_middleware(HttpErrorHandler) # AÑADIR MIDDLEWARE EN FICHERO EXTERNO 

### OAUTH ###

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # Path operation existente
SECRET= "aabf6af607242cdc09259c29491c4314b005237f7bcff4be6928bab93a889062" # Generado con: openssl rand -hex 32
ALGORITHM= "HS256" # Algoritmo usado en el token
ACCESS_TOKEN_DURATION = 1 # DURACIÓN DEL TOKEN EN MINUTOS
crypt = CryptContext(schemes=["bcrypt"]) # Contexto para verificar la contraseña hasheada

fake_users_db = {
    "pedro":{
        "id":1,
        "username":"pedro",
        "email":"pedro@gmail.com",
        "password":"$2y$10$S9G.J4AlwNjDhjUq91Zkpug1sf6IC.I/BuUwpwg4Y9mPCE9r.KCDa", # pass=pata
        "disabled": False
        }, 
    "user2":{
        "id":2,
        "username":"user2",
        "email":"user2@gmail.com",
        "password":"$2y$10$aZpIEV2qgXQFSdg1YoR4Iebg7nJP1E78nFouI6XKP5siUj1tiHFSS", # pass=user2
        "disabled": True
        }  
}

# Usado para buscar el id de usuario que devuelve el JWT
def get_user_by_id(user_id):
    for user_data in fake_users_db.values():
        if user_data["id"] == user_id:
            return user_data
    return None

def encode_token(access_token:dict) -> str:
    token = jwt.encode(access_token, SECRET, algorithm=ALGORITHM)
    return token

def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        decode_token = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except JWTError:
        raise exceptions.INVALID_TOKEN_EXCEPTION

    user = get_user_by_id(decode_token["id"])
    if not user:
        raise exceptions.INVALID_TOKEN_EXCEPTION
    elif user["disabled"] == True:
        raise exceptions.DISABLED_USER_EXCEPTION
    return user

@app.post("/login", tags=['token'])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = fake_users_db.get(form_data.username)

    if not user or not crypt.verify(form_data.password, user["password"]): # Verifica si contraseña en plano y encriptada coinciden
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Username or password")
    elif user["disabled"] == True:
        raise exceptions.DISABLED_USER_EXCEPTION

    ACCESS_TOKEN_EXPIRATION = timedelta(minutes=ACCESS_TOKEN_DURATION)
    EXPIRATION_TOKEN = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRATION # Fecha actual + expiración del token

    access_token = encode_token({"id": user["id"],"exp":EXPIRATION_TOKEN})

    return {"access_token": access_token}

@app.get("/users/profile", tags=['token'])
async def profile(my_user: Annotated[dict, Depends(decode_token)]):
    return my_user

@app.get("/users/mail", tags=['token'])
async def my_email(my_user: Annotated[dict, Depends(decode_token)]):
    return my_user["email"]

### AÑADIR HEADERS ###

def get_headers(
        access_token: Annotated[str , Header()],
        user_role: Annotated[str | None, Header()] = None # Header no obligatorio
):
    if access_token != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")

    return {"access_token": access_token, "user_role": user_role}


@app.get("/Dashboard", tags=['Headers'])
async def dashboard(request: Request,
              response: Response,
              headers: Annotated[dict, Depends(get_headers)] # Pasamos headers como dependencias de función
):
    print(request.headers) # Imprime los headers de entrada
    response.headers["user_status"] = "enabled" # Añade headers de respuesta

    return {"access_token": headers["access_token"], "user_role": headers["user_role"]}

### MIDDLEWARE QUE CAPTURA EL TRÁFICO HTTP ANTES DE ENTRAR EN EL ENDPOINT ###

@app.middleware('http')
async def http_error_handler(request: Request, call_next) -> Response | JSONResponse:
    try:
        print("Middleware is running")
        return await call_next(request)
    except Exception as e:
        content = f"exc: {str(e)}"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(content, status_code=status_code)

@app.get("/", tags=['Home'])
async def home():
    return HTMLResponse('<h1>Hello World</h1>')

### COOKIES ###

@app.get("/cookies", tags=['Cookies'])
async def cookies():
    response = JSONResponse(content={"msg": "Welcome"})
    response.set_cookie(key="username", value="Pedro", expires=10)

    return response

@app.get("/get_cookies", tags=['Cookies'])
async def cookget_cookies(username: str = Cookie()):
    return username

### DEPENDENCIAS ###

def common_params(start_date: str, end_date: str): # DEPENDENCIAS DE FUNCIÓN
    return {"start_date": start_date, "end_date": end_date}

class Common_dep(): # DEPENDENCIA DE CLASE
    def __init__(self, start_date: str, end_date:str) -> None:
        self.start_date = start_date
        self.end_date = end_date

@app.get('/users', tags=['Dependencias'])   # DEPENDENCIA DE FUNCIÓN
async def get_users(commons: dict = Depends(common_params)):
    return f"Users created between {commons['start_date']} and {commons['end_date']}"

@app.get('/owners', tags=['Dependencias'])  # DEPENDENCIA DE CLASE
async def get_owners(commons:Common_dep = Depends()):
    return f"Owners created between {commons.start_date} and {commons.end_date}"

@app.get('/customer', tags=['Dependencias'])
async def get_customer(start_date: str, end_date: str):
    return f"Customers created between {start_date} and {end_date}"

### IMAGEN ESTÁTICA ###

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
static_dir_images = os.path.join(static_dir, "images")
app.mount("/static", StaticFiles(directory=static_dir), name="static") # http://localhost:8000/static/images/madrid.jpg Expone un recurso en su path

@app.get('/image', tags=['Imagen']) # Static files endpoint
async def get_images():
    image_path = os.path.join(static_dir_images,"madrid.jpg")
    
    return FileResponse(image_path, media_type="image/jpeg")