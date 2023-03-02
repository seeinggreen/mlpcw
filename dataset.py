import json
import os
    
class Dataset:
    
    def __init__(self,load_data=False):
        if load_data:
            self.load_dataset()
    
    def load_dataset(self):
        self.data_by_year = {}
        for file in os.listdir('dataset_jsons'):
            year = file[:4]
            with open(os.path.join('dataset_jsons',file)) as f:
                self.data_by_year[year] = json.load(f)
    
    def build_and_store_datset(self):
        self.build_dataset()
        self.store_dataset()
    
    def store_dataset(self):
        self.build_dataset()
        for year in self.data_by_year:
            with open(f'dataset_jsons/{year}.json','w') as file:
                json.dump(self.data_by_year[year],file)
    
    def build_dataset(self):
        wiki_data = {}
        for file in os.listdir('wiki_jsons'):
            with open(os.path.join('wiki_jsons',file)) as f:
                year = json.load(f)
                for page in year:
                    wiki_data[page] = year[page]
            
        tmdb_data = {}
        for file in os.listdir('tmdb_jsons'):
            with open(os.path.join('tmdb_jsons',file)) as f:
                year = json.load(f)
                for film in year:
                    year[film]['year'] = file[:4]
                    tmdb_data[film] = year[film]
        
        tm_wiki_films = [page_id for page_id in wiki_data if 'tmdb_id' in wiki_data[page_id]]
        
        self.data_by_year = {}
        missing = []
        for wiki_id in tm_wiki_films:
            tmdb_id = str(wiki_data[wiki_id]['tmdb_id'])
            if tmdb_id not in tmdb_data:
                missing.append(tmdb_id)
                continue
            tmdb = tmdb_data[tmdb_id]
            title = tmdb['title']
            year = tmdb['year']
            genres = tmdb['genres']
            if not genres:
                continue
            tmdb_plot = tmdb['plot']
            wiki_plot = wiki_data[wiki_id]['plot']
            if year not in self.data_by_year:
                self.data_by_year[year] = []
            self.data_by_year[year].append({'title':title,
                         'genres':genres,
                         'wiki_plot':wiki_plot,
                         'tmdb_plot':tmdb_plot,
                         'tmdb_id':tmdb_id,
                         'wiki_id':wiki_id})
        
