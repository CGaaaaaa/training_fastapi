from typing import Annotated
from fastapi import Cookie, FastAPI, Header, Request, Response, status, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.routers.movie_router import movie_router
from jose import jwt

# DEPENDENCIA DE FUNCIÓN
def common_params(start_date: str, end_date: str):
    return {"start_date": start_date, "end_date": end_date}

# DEPENDENCIA DE CLASE
class Common_dep():
    def __init__(self, start_date: str, end_date:str) -> None:
        self.start_date = start_date
        self.end_date = end_date

app = FastAPI()#app = FastAPI(dependencies=[Depends(common_params)]) # Añadir dependencias a nivel global de la app
app.title="App de prueba"
app.version="0.0.1"

app.include_router(prefix='/movies', router=movie_router) # Incluímos el router de movies con el path ya incluído /movies

#app.add_middleware(HttpErrorHandler) # AÑADIR MIDDLEWARE EN FICHERO EXTERNO 

# OAUTH
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") #Path operation existente

users = {
    "pedro":{"username":"pedro", "email":"pedro@gmail.com", "password":"pata"},
    "user2":{"username":"user2", "email":"user2@gmail.com", "password":"user2"}
}

def encode_token(payload:dict) -> str:
    token = jwt.encode(payload, "my-secret", algorithm="HS256")
    return token

def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    data = jwt.decode(token, "my-secret", algorithms=["HS256"])
    user = users.get(data["username"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@app.post("/token", tags=['token'])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = users.get(form_data.username)

    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect Username or password")
    
    token = encode_token({"username":user["username"],"email":user["email"]})
    return {"access_token": token}

@app.get("/users/profile", tags=['token'])
async def profile(my_user: Annotated[dict, Depends(decode_token)]):
    return my_user

# AÑADIR HEADERS

def get_headers(
        access_token: Annotated[str , Header()],
        user_role: Annotated[str | None, Header()] = None # Header no obligatorio
):
    if access_token != "secret":
        raise HTTPException(status_code=401, detail="No autorizado")

    return {"access_token": access_token, "user_role": user_role}


@app.get("/Dashboard", tags=['Headers'])
async def dashboard(request: Request,
              response: Response,
              headers: Annotated[dict, Depends(get_headers)] # Pasamos headers como dependencias de función
):
    print(request.headers) # Imprime los headers de entrada
    response.headers["user_status"] = "enabled" # Añade headers de respuesta

    return {"access_token": headers["access_token"], "user_role": headers["user_role"]}
    


# MIDDLEWARE QUE CAPTURA EL TRÁFICO HTTP ANTES DE ENTRAR EN EL ENDPOINT
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

# COOKIES
@app.get("/cookies", tags=['Cookies'])
async def cookies():
    response = JSONResponse(content={"msg": "Welcome"})
    response.set_cookie(key="username", value="Pedro", expires=10)

    return response

@app.get("/get_cookies", tags=['Cookies'])
async def cookget_cookies(username: str = Cookie()):
    return username

#ENDPOINTS PARA PROBAR LA INYECCIÓN DE DEPENDENCIAS
@app.get('/users', tags=['Dependencias'])   # DEPENDENCIA DE FUNCIÓN
async def get_users(commons: dict = Depends(common_params)):
    return f"Users created between {commons['start_date']} and {commons['end_date']}"

@app.get('/owners', tags=['Dependencias'])  #DEPENDENCIA DE CLASE
async def get_owners(commons:Common_dep = Depends()):
    return f"Owners created between {commons.start_date} and {commons.end_date}"

@app.get('/customer', tags=['Dependencias'])
async def get_customer(start_date: str, end_date: str):
    return f"Customers created between {start_date} and {end_date}"