from typing import List

from fastapi import HTTPException, Path, Query, APIRouter, status
from app.models.movie_model import Movie, Movie_create, Movie_update

movie_router = APIRouter(prefix='/movies', tags=['Movies'])

movies: List[Movie] = [
    Movie(
        id= 1,
        title= "Lo que le viento se llevó",
        overview= "Lorem ipsum cuantum matic",
        year= 1999,
        rating= 7.8,
        category= "romantic"
    ),
    Movie(
        id= 2,
        title= "Lo que el agua se llevó",
        overview= "Lorem ipsum cuantum matic",
        year= 1996,
        rating= 7.1,
        category= "comedy"
    )
]
### CRUD ###

### CREATE ###
@movie_router.post("/", status_code=status.HTTP_201_CREATED, response_model= List[Movie])
async def create_movie(movie: Movie_create) -> List[Movie]:
    new_movie = Movie(**movie.model_dump())
    movies.append(new_movie)

    return movies

### UPDATE ###
@movie_router.put("/{id}", response_model=Movie)
async def update_movie(id:int, movie: Movie_update) -> Movie:
    for item in movies:
        if item.id == id:
            item.title = movie.title
            item.overview = movie.overview
            item.year = movie.year
            item.rating = movie.rating
            item.category = movie.category
            return item
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

### DELETE ###
@movie_router.delete("/{id}", response_model= List[Movie])
async def delete_movie(id: int) -> List[Movie]:
    for movie in movies:
        if movie.id == id:
            movies.remove(movie)
            return movies
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

### SEARCH ###

### ALL MOVIES ###
@movie_router.get("/", response_model= List[Movie])
async def get_movies() -> List[Movie]:

    return movies

### MOVIE BY CATEGORY ###
@movie_router.get("/category", response_model= List[Movie])
async def get_movie_by_category(category: str = Query(min_length=5, max_length=20)) -> List[Movie]:
    result = [movie for movie in movies if movie.category == category]
    if not result:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No movies found in that category")
    
    return result

### MOVIE BY ID ###
@movie_router.get("/{id}", response_model=Movie)
async def get_movie(id: int = Path(gt=0)) -> Movie:
    for movie in movies:
        if movie.id == id:

            return movie
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")