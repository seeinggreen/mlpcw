from tmdbv3api import TMDb
from tmdbv3api import Movie
from tmdbv3api import Find
import json
from collections import Counter
import time
from worker_pool import WorkerPool
from datetime import datetime
import os
from tqdm import tqdm

API_KEY_FILE ='api_key.txt' #Where the TMDb API key is stored
MOVIE_IDS_FILE = 'data/movie_ids_02_24_2023.json' #Where the TMDb movie IDs are stored

BATCH_SIZE = 1000 #Size of batch for each worker thread to fetch
WORKERS = 10 #Number of threads to use in the worker pool

class NoStoredFilmsError(Exception):
    pass

def thread_worker(work,result,finished):
    """
    The task to be completed by each thread when fetching film information.

    Parameters
    ----------
    work : collections.deque
        The queue of work to be carrried out by the pool of workers.
    result : collections.deque
        Variable to store task results; not used.
    finished : threading.Event
        Used to indicate whether the queue of work is complete.

    Returns
    -------
    None.

    """
    print("Thread started")
    #Create separate Tmdb object to avoid threading issues
    tmdb = Tmdb()
    #Loop until complete
    while True:
        task = None
        #Try and get a task from the queue
        try:
            task = work.pop()
        except IndexError:
            pass
        
        if task is None:
            #Check if the queue is complete otherwise sleep and check again
            if finished.is_set():
                break
            time.sleep(1)
            continue
        #Fetch a batch of films, using the task value as the batch number
        tmdb.fetch_and_store(task,BATCH_SIZE)

class Tmdb:
    
    def __init__(self,load_ids=False):
        """
        Initalises the Tmdb object with the API key and movie IDs.

        Returns
        -------
        None.

        """
        #Create a TMDb and Movie object
        self.tmdb = TMDb()
        self.movie = Movie()
        self.find = Find()
        
        #Read the API key from file and add it to the TMDb object
        with open(API_KEY_FILE) as f:
            api_key = f.read()
        self.tmdb.api_key = api_key
        
        #Read the movie IDs from file
        if load_ids:
            with open(MOVIE_IDS_FILE,encoding='utf8') as f:
                self.all_films = [json.loads(film) for film in f.readlines()]
            
    def get_tmdb_id_from_imdb_id(self,imdb_id):
        """
        Gets a TMDb ID from the given IMDb ID if it exists.

        Parameters
        ----------
        imdb_id : str
            The IMDb ID to check against.

        Returns
        -------
        str or None
            The TMDb if it has been found, otherwise None.

        """
        results = self.find.find_by_imdb_id(imdb_id)
        if results.movie_results:
            return results.movie_results[0].id
        else:
            return None
            
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
    
    def fetch_all_films(self,start=0,batches_to_do=None):
        """
        Uses a pool of workers to fetch the details of all films from TMDb

        Parameters
        ----------
        start : int, optional
            The batch number to start from. The default is 0.

        Returns
        -------
        None.

        """
        total_films = len(self.all_films)
        batches = total_films // BATCH_SIZE
        if batches_to_do is None:
            batches_to_do = range(batches)
        wp = WorkerPool(WORKERS,batches,thread_worker)
        wp.run(start=start,task_list=batches_to_do)
        #Run one final fetch to get the remaining films
        batch_size = total_films % BATCH_SIZE
        self.fetch_and_store(batches,batch_size)
            
    def check_stored_films(self,store=False):
        """
        Checks the data fetched from TMDb and stores the basic info in JSON files by year.

        Returns
        -------
        None.

        """
        #Get all the JSON files for the film batches
        json_files = os.listdir('tmdb_full_jsons')
        self.stored_films = {}
        for jf in tqdm(json_files):
            with open(os.path.join('tmdb_full_jsons',jf)) as f:
                films = json.load(f)
                for film in films:
                    released = film['status'] == 'Released'
                    #Ignore unreleased films or films without a valid release date
                    if released and film['release_date']:
                        title = film['title']
                        year = film['release_date'][:4]
                        genres = [g['name'] for g in film['genres']]
                        #Store the title and the JSON file with the full details
                        info = {'title':title, 'plot': film['overview'],'genres':genres,'file':jf}
                        #Add a new dictionary if needed
                        if year not in self.stored_films:
                            self.stored_films[year] = {}
                        #Store the films in dictionaries by year
                        self.stored_films[year][film['id']] = info
        if store:
            #Write the dictionaries to disk
            for year in self.stored_films:
                with open(f'tmdb_jsons/{year}.json','w') as f:
                    json.dump(self.stored_films[year],f)
    
    def fetch_and_store(self,i,batch_size):
        """
        Fetches a batch of films from TMDb and stores them in a JSON file.

        Parameters
        ----------
        i : int
            The batch number.
        batch_size : int
            The size of the batch.

        Returns
        -------
        None.

        """
        start = datetime.now()
        print(f'Fetching films {i*batch_size}-{(i+1)*batch_size-1}')
        films = self.fetch_n_films(batch_size,batch_size*i)
        with open(f'tmdb_full_jsons/{i}.json','w') as f:
            json.dump([film._json for film in films],f)
        end = datetime.now()
        print(f'Stored films {i*batch_size}-{(i+1)*batch_size-1} in {str(end-start)[2:-4]}')
    
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
        #print('Fetching film information from TMDb:')
        for film in films:
            try:
                search = self.movie.details(film['id']);
                self.film_selection.append(search);
            except Exception as err:
                print(f"Error fetching film #{film['id']}: {err}")
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