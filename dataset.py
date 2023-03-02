import json
import os
    
class Dataset:
    
    def __init__(self,load_data=False,exclude_ids=True):
        """
        Creates a Dataset object and (optionally) loads the data from file

        Parameters
        ----------
        load_data : bool, optional
            If True, the dataset is loaded from file. The default is False.
            
        exclude_ids : bool, optional
            If True, all_data will exclude the TMDb/Wikipedia IDs. The default is True.

        Returns
        -------
        None.

        """
        if load_data:
            self.load_dataset(exclude_ids)
            
    def print_stats(self):
        """
        Calculates and prints some basic stats about the dataset loaded in memory.

        Returns
        -------
        None.

        """
        total_entries = len(self.all_data)
        wiki_plot_word_lengths = [len(film['wiki_plot'].split(' ')) for film in self.all_data]
        tmdb_plots_word_lengths = [len(film['tmdb_plot'].split(' ')) for film in self.all_data]
        mean_wiki_plot_length = sum(wiki_plot_word_lengths) / total_entries
        mean_tmdb_plot_length = sum(tmdb_plots_word_lengths) / total_entries
        ratios = [wiki_plot_word_lengths[i] / tmdb_plots_word_lengths[i] for i in range(total_entries)]
        mean_ratio = sum(ratios) / total_entries
        shorter = len([ratio for ratio in ratios if ratio < 1])
        ratio2 = len([ratio for ratio in ratios if ratio >= 1 and ratio < 2])
        ratio3 = len([ratio for ratio in ratios if ratio >= 2 and ratio < 3])
        ratio5 = len([ratio for ratio in ratios if ratio >= 3 and ratio < 5])
        ratio7 = len([ratio for ratio in ratios if ratio >= 5 and ratio < 7])
        longer = len([ratio for ratio in ratios if ratio >= 7])
        
        print(f'Total entries in dataset: {total_entries}')
        print(f'Mean length of Wikipedia plots: {mean_wiki_plot_length:.1f} words')
        print(f'Mean length of TMDb plots: {mean_tmdb_plot_length:.1f} words')
        print(f'Mean ratio of Wikipedia:TMDb plot lengths: {mean_ratio:.2f}')
        print(f'Films with shorter Wikipedia plots: {shorter} ({shorter/total_entries*100:.2f}% of entries)')
        print(f'Ratios between 1-2: {ratio2} ({ratio2/total_entries*100:.2f}% of entries)')
        print(f'Ratios between 2-3: {ratio3} ({ratio3/total_entries*100:.2f}% of entries)')
        print(f'Ratios between 3-5: {ratio5} ({ratio5/total_entries*100:.2f}% of entries)')
        print(f'Ratios between 5-7: {ratio7} ({ratio7/total_entries*100:.2f}% of entries)')
        print(f'Ratios greater than 7: {longer} ({longer/total_entries*100:.2f}% of entries)')
        
    def load_dataset(self,exclude_ids):
        """
        Loads the data from file and stores it in a dictionary (data_by_year) and a list (all_data).
        
        Parameters
        ----------
        exclude_ids : bool, optional
            If True, all_data will exclude the TMDb/Wikipedia IDs. The default is True.

        Returns
        -------
        None.

        """
        self.data_by_year = {}
        self.all_data = []
        for file in os.listdir('dataset_jsons'):
            year = file[:4]
            with open(os.path.join('dataset_jsons',file)) as f:
                self.data_by_year[year] = json.load(f)
            self.all_data.extend(self.data_by_year[year])
          
        #Optionally remove the IDs from each film entry
        if exclude_ids:
            for film in self.all_data:
                film.pop('tmdb_id',None)
                film.pop('wiki_id',None)
    
    def build_and_store_datset(self):
        """
        Rebuilds the dataset and stores it to file.

        Returns
        -------
        None.

        """
        self.build_dataset()
        self.store_dataset()
    
    def store_dataset(self):
        """
        Stores the dataset held in memory to file.

        Returns
        -------
        None.

        """
        self.build_dataset()
        for year in self.data_by_year:
            with open(f'dataset_jsons/{year}.json','w') as file:
                json.dump(self.data_by_year[year],file)
    
    def build_dataset(self):
        """
        Builds the dataset from TMDb and Wikipedia data.

        Returns
        -------
        None.

        """
        #Get the Wikipedia data
        wiki_data = {}
        for file in os.listdir('wiki_jsons'):
            with open(os.path.join('wiki_jsons',file)) as f:
                year = json.load(f)
                for page in year:
                    wiki_data[page] = year[page]
        
        #Get the TMDb data
        tmdb_data = {}
        for file in os.listdir('tmdb_jsons'):
            with open(os.path.join('tmdb_jsons',file)) as f:
                year = json.load(f)
                for film in year:
                    year[film]['year'] = file[:4] #Preserve the TMDb release year for later access
                    tmdb_data[film] = year[film]
        
        #Filter to just the Wikipedia pages that have valid TMDb IDs attached
        tm_wiki_films = [page_id for page_id in wiki_data if 'tmdb_id' in wiki_data[page_id]]
        
        self.data_by_year = {}
        missing = [] #Keep track of missing TMDb entries
        for wiki_id in tm_wiki_films:
            tmdb_id = str(wiki_data[wiki_id]['tmdb_id'])
            if tmdb_id not in tmdb_data:
                missing.append(tmdb_id)
                continue
            tmdb = tmdb_data[tmdb_id]
            title = tmdb['title']
            year = tmdb['year']
            genres = tmdb['genres']
            #Reject entries with no genres stored in TMDb
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
        
