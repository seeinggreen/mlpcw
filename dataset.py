import json
import os
import matplotlib.pyplot as plt
import numpy as np
import random
    
class Dataset:
    
    def __init__(self,load_balanced=False,load_data=False,exclude_ids=True):
        """
        Initalises a Dataset object

        Parameters
        ----------
        load_balanced : bool, optional
            Loads the balanced dataset into self.balanced. The default is False.
        load_data : bool, optional
            Loads the full dataset into self.data_by_year and self.all_data. The default is False.
        exclude_ids : bool, optional
            Removes the document IDs from the full dataset. The default is True.

        Returns
        -------
        None.

        """
        if load_data:
            self.load_dataset(exclude_ids)
        if load_balanced:
            self.load_dataset(balanced=True)
            
    def print_stats(self,balanced=False):
        """
        Calculates and prints some basic stats about the dataset loaded in memory.
        
        Parameters
        ----------
        balanced : bool, optional
            Prints stats for the balanced dataset if True, the full dataset if False. The default is False.

        Returns
        -------
        None.

        """
        if balanced:
            dataset = self.balanced
        else:
            dataset = self.all_data
        
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
        
    def load_dataset(self,balanced=False,exclude_ids=True):
        """
        Loads either the full dataset from file and stores it in a
        dictionary (data_by_year) and a list (all_data) OR loads the balanced
        dataset from file.
        
        Parameters
        ----------
        balanced : bool, optional
            Loads the balanced dataset if True, otherwise the full dataset. The default is False.
        
        exclude_ids : bool, optional
            If True, all_data will exclude the TMDb/Wikipedia IDs. The default is True.

        Returns
        -------
        None.

        """
        if not balanced:
            self.data_by_year = {}
            self.all_data = []
            for file in os.listdir('dataset_jsons'):
                year = file[:4]
                with open(os.path.join('dataset_jsons',file)) as f:
                    self.data_by_year[year] = json.load(f)
                self.all_data.extend(self.data_by_year[year])
        else:
            with open('balanced_dataset.json') as f:
                self.balanced = json.load(f)
          
        #Optionally remove the IDs from each film entry
        if exclude_ids and not balanced:
            for film in self.all_data:
                film.pop('tmdb_id',None)
                film.pop('wiki_id',None)
    
    def build_and_store_datset(self,balanced=False):
        """
        Rebuilds the stored dataset and stores it to file.
        
        Parameters
        ----------
        balanced : bool, optional
            Stores the balanced dataset if True, otherwise the full dataset. The default is False.


        Returns
        -------
        None.

        """
        if balanced:
            self.get_balanced_dataset()
        else:
            self.build_dataset()
        self.store_dataset(balanced)
    
    def store_dataset(self,balanced=False):
        """
        Stores the full dataset held in memory to file.

        Parameters
        ----------
        balanced : bool, optional
            Stores the balanced dataset if True, otherwise the full dataset. The default is False.

        Returns
        -------
        None.

        """
        if balanced:
            with open('balanced_dataset.json','w') as file:
                json.dump(self.balanced,file)
        else:
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
        
        self.imdb_only_by_year = {}
        self.no_id_by_year = {}
        
        self.wiki_data = {}
        for file in os.listdir('wiki_jsons'):
            with open(os.path.join('wiki_jsons',file)) as f:
                data = json.load(f)
            for page in data:
                self.wiki_data[page] = data[page]
            year = file[:4]
            self.imdb_only_by_year[year] = [page for page in data if 'imdb_id' in data[page]]
            self.no_id_by_year[year] = [page for page in data if 'tmdb_id' not in data[page] and 'imdb_id' not in data[page]]
                    
        #Get the TMDb data
        self.tmdb_data = {}
        self.tmdb_data_by_year = {}
        for file in os.listdir('tmdb_jsons'):
            with open(os.path.join('tmdb_jsons',file)) as f:
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
        for f in self.all_data:
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
        plt.savefig('stacked_genre.pdf')
        
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
            
        for f in self.all_data:
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
                
        for f in self.all_data:
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
        
    
    def get_balanced_dataset(self):
        """
        Gets a subset from the full dataset where the fractional genre counts are balanced.

        Returns
        -------
        None.

        """
        tbg = self.total_by_genre()
        tbg = [(g,tbg[g]) for g in tbg]
        tbg.sort(key=lambda x : x[1])
        threshold = tbg[-7][1]
        full_genres = [t[0] for t in tbg[:-7]]
        genres = [t[0] for t in tbg[-7:]]
        
        subset = [f for f in self.all_data if genres[0] in f['genres'] and not any([g in full_genres for g in f['genres']])]
        fgc = self.count_genres(subset)
        
        full_genres = set(full_genres)
    
        for g in genres[1:]:
            next_subset = [f for f in self.all_data if g in f['genres'] and not any([g in full_genres for g in f['genres']])]
            without_top3 = [f for f in next_subset if not any([g in ['Drama','Comedy','Romance'] for g in f['genres']])]
            without_drama_com = [f for f in next_subset if not any([g in ['Drama','Comedy'] for g in f['genres']])]
            without_drama = [f for f in next_subset if not 'Drama' in f['genres']]
            with_drama = [f for f in next_subset if 'Drama' in f['genres']]
            random.shuffle(without_top3)
            random.shuffle(without_drama_com)
            random.shuffle(with_drama)
            random.shuffle(without_drama)
            next_subset = without_top3 + without_drama_com + without_drama + with_drama

            for f in next_subset:
                if any([g in full_genres for g in f['genres']]):
                    continue
                subset.append(f)
                for g in f['genres']:
                    fgc[g] += 1 / len(f['genres'])
                
                for g in genres:
                    if fgc[g] > threshold:
                        full_genres.add(g)
                if g in full_genres:
                    break
                
        self.balanced = subset
                
            
        
        
        
