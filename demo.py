import json
import random
from tmdbv3api import TMDb
from tmdbv3api import Movie
    
#Create a TMDb and Movie object
tmdb = TMDb()
movie = Movie()

#Read the API key from file and add it to the TMDb object
with open('api_key.txt') as f:
    api_key = f.read();
tmdb.api_key = api_key;

#Read the movie IDs from file
with open('movie_ids_02_24_2023.json',encoding='utf8') as f:
    films = [json.loads(film) for film in f.readlines()]
    
#Get 10 random films for demo purposes
r = random.randint(0,len(films) - 10);
films = films[r:r+10]

#For each film, retrieve the full info
info = []
for film in films:
    print(f"Fetching information for {film['original_title']}")
    search = movie.details(film['id']);
    info.append(search);
    
print()#blank line
    
#Print some info
for film in info:
    print(film.title)
    print('\t Released: ' + film.release_date)
    genres = [g['name'] for g in film.genres];
    print('\t Genre(s): ' + ', '.join(genres))
    
print()#blank line
    
#Print a plot summary for one film
print(info[0].title + ':')
print(info[0].overview)