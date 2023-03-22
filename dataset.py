import json
import os
import matplotlib.pyplot as plt
import numpy as np
import random
    
MAIN_DATA_DIR = 'data'
FULL_DATASET_DIR = os.path.join(MAIN_DATA_DIR,'dataset_jsons')
BALANCED_DATASET_FILE = os.path.join(MAIN_DATA_DIR,'balanced_dataset.json')
WIKI_DIR = os.path.join(MAIN_DATA_DIR,'wiki_jsons')
TMDB_DIR = os.path.join(MAIN_DATA_DIR,'tmdb_jsons')

class Dataset:
    
    def __init__(self,balanced=False,load_data=False,exclude_ids=True):
        """
        Initalises a Dataset object

        Parameters
        ----------
        balanced : bool, optional
            Whether to use the balanced dataset (rather than the full dataset). The default is False.
        load_data : bool, optional
            Loads the selected dataset into memory The default is False.
        exclude_ids : bool, optional
            Removes the document IDs from the full dataset. The default is True.

        Returns
        -------
        None.

        """
        self.balanced = balanced
        if load_data:
            self.load_dataset(exclude_ids)
            
    def get_data(self):
        """
        Returns the dataset loaded in memory.

        Returns
        -------
        list of dict
            A list of all films in the selected dataset.

        """
        if self.balanced:
            return self.balanced_data
        else:
            return self.all_data
            
    def print_stats(self):
        """
        Calculates and prints some basic stats about the dataset loaded in memory.
        
        Returns
        -------
        None.

        """
        dataset = self.get_data()
        
        total_entries = len(dataset)
        wiki_plot_word_lengths = [len(film['wiki_plot'].split(' ')) for film in dataset]
        tmdb_plots_word_lengths = [len(film['tmdb_plot'].split(' ')) for film in dataset]
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
        
    def load_dataset(self,exclude_ids=True):
        """
        Loads either the full dataset from file and stores it in a
        dictionary (data_by_year) and a list (all_data) OR loads the balanced
        dataset from file.
        
        Parameters
        ----------
        exclude_ids : bool, optional
            If True, all_data will exclude the TMDb/Wikipedia IDs. The default is True.

        Returns
        -------
        None.

        """
        if not self.balanced:
            self.data_by_year = {}
            self.all_data = []
            for file in os.listdir(FULL_DATASET_DIR):
                year = file[:4]
                with open(os.path.join(FULL_DATASET_DIR,file)) as f:
                    self.data_by_year[year] = json.load(f)
                self.all_data.extend(self.data_by_year[year])
        else:
            with open(BALANCED_DATASET_FILE) as f:
                self.balanced_data = json.load(f)
          
        #Optionally remove the IDs from each film entry
        if exclude_ids and not self.balanced:
            for film in self.all_data:
                film.pop('tmdb_id',None)
                film.pop('wiki_id',None)
    
    def build_and_store_datset(self):
        """
        Rebuilds the stored dataset and stores it to file.

        Returns
        -------
        None.

        """
        if self.balanced:
            self.get_balanced_dataset()
        else:
            self.build_dataset()
        self.store_dataset()
    
    def store_dataset(self):
        """
        Stores the full dataset held in memory to file.
        
        Returns
        -------
        None.

        """
        if self.balanced:
            with open(BALANCED_DATASET_FILE,'w') as file:
                json.dump(self.balanced_data,file)
        else:
            for year in self.data_by_year:
                with open(os.path.join(FULL_DATASET_DIR,f'{year}.json'),'w') as file:
                    json.dump(self.data_by_year[year],file)
    
    def build_dataset(self):
        """
        Builds the dataset from TMDb and Wikipedia data.

        Returns
        -------
        None.

        """
        #Get the Wikipedia data
        
        self.imdb_only_by_year = {}
        self.no_id_by_year = {}
        
        self.wiki_data = {}
        for file in os.listdir(WIKI_DIR):
            with open(os.path.join(WIKI_DIR,file)) as f:
                data = json.load(f)
            for page in data:
                self.wiki_data[page] = data[page]
            year = file[:4]
            self.imdb_only_by_year[year] = [page for page in data if 'imdb_id' in data[page]]
            self.no_id_by_year[year] = [page for page in data if 'tmdb_id' not in data[page] and 'imdb_id' not in data[page]]
                    
        #Get the TMDb data
        self.tmdb_data = {}
        self.tmdb_data_by_year = {}
        for file in os.listdir(TMDB_DIR):
            with open(os.path.join('TMDB_DIR',file)) as f:
                data = json.load(f)
            self.tmdb_data_by_year[year] = data
            year = file[:4]
            for film in data:
                data[film]['year'] = year #Preserve the TMDb release year for later access
                self.tmdb_data[film] = data[film]
        
        #Filter to just the Wikipedia pages that have valid TMDb IDs attached
        tm_wiki_films = [page_id for page_id in self.wiki_data if 'tmdb_id' in self.wiki_data[page_id]]
  
        self.data_by_year = {}
        self.missing_tmdb_pages = [] #Keep track of missing TMDb entries
        self.missing_genres_by_year = {}
        for wiki_id in tm_wiki_films:
            tmdb_id = str(self.wiki_data[wiki_id]['tmdb_id'])
            if tmdb_id not in self.tmdb_data:
                self.missing_tmdb_pages.append(tmdb_id)
                continue
            tmdb = self.tmdb_data[tmdb_id]
            title = tmdb['title']
            year = tmdb['year']
            genres = tmdb['genres']
            #Reject entries with no genres stored in TMDb
            if not genres:
                if year not in self.missing_genres_by_year:
                    self.missing_genres_by_year[year] = []
                self.missing_genres_by_year[year].append(tmdb_id)
            tmdb_plot = tmdb['plot']
            wiki_plot = self.wiki_data[wiki_id]['plot']
            if year not in self.data_by_year:
                self.data_by_year[year] = []
            self.data_by_year[year].append({'title':title,
                         'genres':genres,
                         'wiki_plot':wiki_plot,
                         'tmdb_plot':tmdb_plot,
                         'tmdb_id':tmdb_id,
                         'wiki_id':wiki_id})
            
    def attempt_matches(self):
        """
        Attempts to match film titles between Wikipedia and TMDb.

        Returns
        -------
        None.

        """
        self.matches_by_year = {}
        for year in self.no_id_by_year:
            self.matches_by_year[year] = []
            tmdb_films = {}
            for tmdb_id in self.tmdb_data_by_year[year]:
                title = self.tmdb_data_by_year[year][tmdb_id]['title']
                tmdb_films[title.lower()] = tmdb_id
            for wiki_id in self.no_id_by_year[year]:
                wiki_title = self.wiki_data[wiki_id]['title']
                wiki_title = wiki_title.split(" (")[0].lower()
                if wiki_title in tmdb_films:
                    self.matches_by_year[year].append((wiki_id,tmdb_films[wiki_title]))
    
    def all_genres(self):
        """
        Returns a list of all genres in the full dataset.

        Returns
        -------
        all_genres : list of str
            A list of all genres in the dataset.

        """
        all_genres = set()
        for f in self.get_data():
            for g in f['genres']:
                all_genres.add(g)
        all_genres = list(all_genres)
        all_genres.sort()
        
        return all_genres
    
    def stacked_genre_chart(self):
        """
        Generates a stacked area chart for the genres in the full dataset.

        Returns
        -------
        None.

        """
        all_genres = self.all_genres()
        
        years = []
        genres_per_year = [[] for g in all_genres]
        for year in self.data_by_year:
            years.append(int(year))
            genres = {}
            for g in all_genres:
                genres[g] = 0
            for f in self.data_by_year[year]:
                for g in f['genres']:
                    genres[g] += 1 / len(f['genres'])
            for i,g in enumerate(all_genres):
                genres_per_year[i].append(genres[g])
        
        cmap = plt.cm.tab20b
        cs = cmap(np.linspace(0,1,len(all_genres)))
        plt.stackplot(years,*genres_per_year,labels=all_genres,colors=cs)
        plt.legend(loc='upper left',ncol=2,fontsize='small')
        plt.xlabel('Year')
        plt.ylabel('Films')
        plt.savefig('figures/stacked_genre.pdf')
        
    def total_by_genre(self,genres=None,fractional=True):
        """
        Gets the total number of films in each genre.

        Parameters
        ----------
        genres : list of str, optional
            The genres to count for, uses all genres if not specified. The default is None.
        fractional : bool, optional
            Whether to treat the count for multi genre films as 1 or a fractional value. The default is True.

        Returns
        -------
        tbg : dict
            The count for each genre.

        """
        if genres is None:
            genres = self.all_genres()
        tbg = {}
        for g in genres:
            tbg[g] = 0
            
        for f in self.get_data():
            for g in f['genres']:
                if g not in genres:
                    continue
                if fractional:
                    tbg[g] += 1 / len(f['genres'])
                else:
                    tbg[g] += 1
                    
        if fractional:
            for g in genres:
                tbg[g] = int(tbg[g])
        return tbg
        
    def genre_by_genre_table(self):
        """
        Generates a table in LaTeX format for the intergenre overlaps.

        Returns
        -------
        str
            The LaTeX code for the table.

        """
        all_genres = self.all_genres()
        
        gbg = {}
        for g in all_genres:
            gbg[g] = {}
            for gg in all_genres:
                if gg == g:
                    continue
                gbg[g][gg] = 0
                
        for f in self.get_data():
            for g in f['genres']:
                other_genres = [genre for genre in f['genres'] if genre != g]
                for og in other_genres:
                    gbg[g][og] += 1
                    
        tbg = self.total_by_genre(fractional=False)
        for g in all_genres:
            for gg in all_genres:
                if g == gg:
                    continue
                gbg[g][gg] /= tbg[g]
                    
        out = "\t\\hline\n\t$\\downarrow$ which are also $\\rightarrow$& "
        for g in all_genres:
            out += f'\\small{{{g[:2]}}} & '
        out = out[:-2] + '\\\\\n\t\\hline\n\t\\hline'
        for g in all_genres:
            out += f'\t{g} & '
            for gg in all_genres:
                if g == gg:
                    out += '&'
                else:
                    out += f'\\cv{{{gbg[g][gg]*100:.1f}}}&'
            out = out[:-1] + '\\\\\n\t\\hline\n'
        return out[:-1]
                
    def count_genres(self,subset):
        """
        Counts the fractional genres in the given subset of films.

        Parameters
        ----------
        subset : list of dict
            The list of films to count.

        Returns
        -------
        fgc : dict
            The count of genres.

        """
        fgc = {}
        for g in self.all_genres():
            fgc[g] = 0
        for f in subset:
            for g in f['genres']:
                fgc[g] += 1 / len(f['genres'])
        return fgc
    
    def genre_count_bar_chart(self):
        """
        Saves a bar chart of the genres in the selected dataset.

        Returns
        -------
        None.

        """
        tbg = self.total_by_genre(fractional=False)
        ftbg = self.total_by_genre(fractional=True)
        tbg = [tbg[g] for g in tbg]
        ftbg = [ftbg[g] for g in ftbg]
        
        fig, ax = plt.subplots()
        x = np.arange(len(tbg))
        bar_width = 0.4
        
        cmap = plt.cm.tab20b
        cs = cmap(np.linspace(0,1,19))
        
        if self.balanced:
            cs = np.take(cs,[0,3,4,6,10,13,16],0)
        
        ax.bar(x-(bar_width / 2),tbg,width=bar_width,color=cs,edgecolor='black')
        ax.bar(x+(bar_width / 2),ftbg,width=bar_width,color=cs,edgecolor='black')
        
        if self.balanced:
            ax.xaxis.set_ticks(x,self.all_genres())
        else:
            ax.xaxis.set_ticks(x,self.all_genres(),rotation=45,ha='right',rotation_mode='anchor')
        
        plt.xlabel('Genre')
        plt.ylabel('Films')
        if self.balanced:
            plt.savefig('figures/balanced_genre_bar.pdf')
        else:
            plt.subplots_adjust(bottom=0.3)
            plt.savefig('figures/genre_bar.pdf')
    
    def get_balanced_dataset(self):
        """
        Gets a subset from the full dataset where the fractional genre counts are balanced.

        Returns
        -------
        None.

        """
        #Get the total films by genre
        tbg = self.total_by_genre()
        tbg = [(g,tbg[g]) for g in tbg]
        #Sort by number of films
        tbg.sort(key=lambda x : x[1])
        #Aim for the same number of films as the least frequent selected genre
        threshold = tbg[-7][1]
        #Mark excluded genres as 'full' so they aren't included
        full_genres = [t[0] for t in tbg[:-7]]
        #Select all other genres for inclusion
        genres = [t[0] for t in tbg[-7:]]
        
        #Select all films without exlcuded genres, tagged with the first selected genre
        subset = [f for f in self.all_data if genres[0] in f['genres'] and not any([g in full_genres for g in f['genres']])]
        fgc = self.count_genres(subset)
        
        #Use a set to avoid needing to check if a genre is already full
        full_genres = set(full_genres)
    
        #For the remaining genres...
        for g in genres[1:]:
            #Select the films without excluded genres that are tagged with the selected genre
            next_subset = [f for f in self.all_data if g in f['genres'] and not any([g in full_genres for g in f['genres']])]
            #Split into those without the top three genres, without the top 2,
            #without the top genre and others
            without_top3 = [f for f in next_subset if not any([g in ['Drama','Comedy','Romance'] for g in f['genres']])]
            without_drama_com = [f for f in next_subset if not any([g in ['Drama','Comedy'] for g in f['genres']])]
            without_drama = [f for f in next_subset if not 'Drama' in f['genres']]
            with_drama = [f for f in next_subset if 'Drama' in f['genres']]
            #Shuffle each sublist
            random.shuffle(without_top3)
            random.shuffle(without_drama_com)
            random.shuffle(with_drama)
            random.shuffle(without_drama)
            #Recombine, depriortising well-represented genres
            next_subset = without_top3 + without_drama_com + without_drama + with_drama

            #Add the subset to the main list
            for f in next_subset:
                #Check if the genre has a (now) full genre and skip it if it does
                if any([g in full_genres for g in f['genres']]):
                    continue
                #Otherwise, add it to the main list
                subset.append(f)
                #Udpdate the counts
                for g in f['genres']:
                    fgc[g] += 1 / len(f['genres'])
                
                #Check all genres to see if any have been filled
                for g in genres:
                    if fgc[g] > threshold:
                        full_genres.add(g)
                #Once this genre is full, skip all remaining films in the list
                if g in full_genres:
                    break
        #Save the overall list
        self.balanced_data = subset
                
            
        
        
        
