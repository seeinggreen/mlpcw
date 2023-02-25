from tmdbv3api import TMDb
from tmdbv3api import Movie
import json
from tqdm import tqdm
from collections import Counter

API_KEY_FILE ='api_key.txt' #Where the TMDb API key is stored
MOVIE_IDS_FILE = 'movie_ids_02_24_2023.json' #Where the TMDb movie IDs are stored

class Tmdb:
    
    def __init__(self):
        """
        Initalises the Tmdb object with the API key and movie IDs.

        Returns
        -------
        None.

        """
        #Create a TMDb and Movie object
        self.tmdb = TMDb()
        self.movie = Movie()
        
        #Read the API key from file and add it to the TMDb object
        with open(API_KEY_FILE) as f:
            api_key = f.read()
        self.tmdb.api_key = api_key
        
        #Read the movie IDs from file
        with open(MOVIE_IDS_FILE,encoding='utf8') as f:
            self.all_films = [json.loads(film) for film in f.readlines()]
            
    def get_genres(self,film):
        """
        Extracts the genres as a list for a given film.

        Parameters
        ----------
        film : tmdbv3api.AsObj
            The film to extract the genres from.

        Returns
        -------
        list of str
            The genre(s) of the film according to TMDb.

        """
        return [g['name'] for g in film.genres]
    
    def fetch_n_films(self,n,start=0):
        """
        Fetches the given number of films from TMDb.

        Parameters
        ----------
        n : int
            The number of films to fetch.
        start : int
            The index to start fetching films from. Default is 0.

        Raises
        ------
        IndexError
            Raises an IndexError if the start index is too close to the end of the list of all films.

        Returns
        -------
        list of tmdbv3api.AsObj
            A list of information about n films from TMDb.

        """
        #Check if index/start value are valid
        if start + n > len(self.all_films):
            raise IndexError()
        #Slice the list of IDs
        films = self.all_films[start:start+n]
        #Fetch the info for each film ID
        self.film_selection = []
        print('Fetching film information from TMDb:')
        for film in tqdm(films):
            search = self.movie.details(film['id']);
            self.film_selection.append(search);
        return self.film_selection
    
    def summarise_by_year(self,films):
        """
        Returns a Counter of the films in the selction sorted by year.

        Parameters
        ----------
        films : list of tmdbv3api.AsObj
            The list of films to summarise.

        Returns
        -------
        collections.Counter
            A Counter object for the given films according to release year.

        """
        years = [film.release_date[:4] for film in films if film.release_date]
        return Counter(years)
    
    def summarise_by_genre(self,films):
        """
        Returns a Counter of the films in the selction sorted by genre.

        Parameters
        ----------
        films : list of tmdbv3api.AsObj
            The list of films to summarise.

        Returns
        -------
        collections.Counter
            A Counter object for the given films according to genres.

        """
        genres = [genre for film in films for genre in self.get_genres(film)]
        return Counter(genres)
    
    def get_films_by_year(self,films,year):
        """
        Returns all the films in the given selection released in the given year.

        Parameters
        ----------
        films : list of tmdbv3api.AsObj
            The films selection to check.
        year : int or str
            The year to check.

        Returns
        -------
        list of tmdbv3api.AsObj
            The films from the given selection released in the given year.

        """
        return [film for film in films if film.release_date[:4] == str(year)]