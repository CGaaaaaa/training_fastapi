from typing import List

from fastapi import HTTPException, Path, Query, APIRouter
from src.models.movie_model import Movie, Movie_create, Movie_update

movie_router = APIRouter()

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

# ALL MOVIES
@movie_router.get("/", tags=['Movies'])
def get_movies() -> List[Movie]:
    return movies

# MOVIE BY CATEGORY
@movie_router.get("/category", tags=['Movies'])
def get_movie_by_category(category: str = Query(min_length=5, max_length=20)) -> List[Movie]:
    result = [movie for movie in movies if movie.category == category]
    if not result:
        raise HTTPException(status_code=404, detail="No movies found in that category")
    return result

# MOVIE BY ID
@movie_router.get("/{id}", tags=['Movies'])
def get_movie(id: int = Path(gt=0)) -> Movie:
    for movie in movies:
        if movie.id == id:
            return movie
    raise HTTPException(status_code=404, detail="Movie not found")

# CREATE
@movie_router.post("/", tags=['Movies'])
def create_movie(movie: Movie_create) -> List[Movie]:
    new_movie = Movie(**movie.model_dump())
    movies.append(new_movie)
    return movies

# UPDATE
@movie_router.put("/{id}", tags=['Movies'])
def update_movie(id:int, movie: Movie_update): 
    for item in movies:
        if item.id == id:
            item.title = movie.title
            item.overview = movie.overview
            item.year = movie.year
            item.rating = movie.rating
            item.category = movie.category
        return movies
    raise HTTPException(status_code=404, detail="Movie not found")

# DELETE
@movie_router.delete("/{id}", tags=['Movies'])
def delete_movie(id: int) -> List[Movie]:
    for movie in movies:
        if movie.id == id:
            movies.remove(movie) 
        return movies
    raise HTTPException(status_code=404, detail="Movie not found")