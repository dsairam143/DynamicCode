# main.py

from fastapi import FastAPI
import  pandas as pd
from sqlalchemy import create_engine
import urllib

password = urllib.parse.quote_plus("@regular@123")

app = FastAPI()
DATABASE_URL = "mysql+mysqlconnector://regular:"+password+"@localhost:3306/just_movie_info"
engine = create_engine(DATABASE_URL)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/api/movies")
async def root():
    df = pd.read_sql('SELECT * FROM just_movie_info.movies order by id desc;', engine)
    data = df.to_dict(orient='records')
    return data

@app.get("/api/movie")
async def root(movie_id:int, ):
    df = pd.read_sql('SELECT * FROM just_movie_info.movies where id='+str(movie_id)+';', engine)
    data = df.to_dict(orient='records')
    return data

@app.post("/api/movie/save")
async def save_movie(movie: dict):
    if movie:
        movie.pop('id')
        df = pd.DataFrame([movie])
        df.to_sql('movies', engine, if_exists='append', index=False)
        return {'Status': 'Data save successfully'}
    return {'Status': 'Not Saved', 'data':movie}