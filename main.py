from fastapi import FastAPI, HTTPException, Body, Path, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Coroutine, Optional, List

from starlette.requests import Request
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

app = FastAPI()
app.title = "Mi aplicación con FastAPI"
app.version = "0.0.1"

class  JWTBearer(HTTPBearer):
    async def __call__(self, request: Request) :
        auth = await super().__call__(request)
        data= validate_token(auth.credentials)
        if data ['email'] != "admin@gmail.com":
            raise HTTPException(status_code=403, detail="Credenciales son invalidas")


class User(BaseModel):
    email:str
    password:str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(default="Mi peli", min_length=5, max_length=15)
    overview: str = Field(default="descripcion peli", min_length=5, max_length=50)
    year: int = Field(default=2023, le=2023)
    rating: float = Field(ge=1, le=10)
    category: str = Field(min_length=5, max_length=15)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Mi pelicula",
                "overview": "Descripcion de la pelicula",
                "year": 2022,
                "category": "Acción"
            }
        }

movies = [
    {
        'id': 1,
        'title': 'Avatar',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': '2009',
        'rating': 7.8,
        'category': 'Acción'
    },
    {
        'id': 2,
        'title': 'Avatar II',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': '2021',
        'rating': 8,
        'category': 'Acción'
    }
]

@app.get('/', tags=['home'])
def message():
    return HTMLResponse('<h1>hello world</h1>')

@app.post('/login', tags=['auth'])
def login(user:User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())
        return JSONResponse(content=token)

@app.get('/movies', tags=['movies'], response_model=List[Movie],status_code=200,dependencies=[Depends(JWTBearer())])
def get_all_movies() -> List[Movie]:
    return JSONResponse(status_code=200, content=movies)

@app.get('/movies/{movie_id}', tags=['movies'], status_code=200)
def get_movie(movie_id: int = Path(ge=1, le=2000)) -> List[Movie]:
    for item in movies:
        if item["id"] == movie_id:
            return JSONResponse(content=item)
    return JSONResponse({"message": "Movie not found"}, status_code=404)

@app.get('/movies/', tags=['movies'])
def get_movies_by_category(category: str = Query(min_length=5)):
    data = [item for item in movies if item['category'] == category]
    return JSONResponse(content=data)

@app.post('/movies', tags=['movies'], status_code=201)
def create_movie(movie: Movie) -> List[Movie]:
    new_id = max(item['id'] for item in movies) + 1 if movies else 1
    movie.id = new_id
    movies.append(movie.dict())
    return JSONResponse(content={"movies": movies}, status_code=201)

@app.put('/movies/{movie_id}', tags=['movies'])
def update_movie(movie_id: int, movie: Movie):
    for item in movies:
        if item["id"] == movie_id:
            item.update(movie.dict())
            return JSONResponse(content={"message": "Movie updated successfully"})
    return JSONResponse(content={"message": "Movie not found"})

@app.delete('/movies/{movie_id}', tags=['movies'])
def delete_movie(movie_id: int):
    movies[:] = [item for item in movies if item['id'] != movie_id]
    return JSONResponse(content={"message": "Movie deleted successfully"})
