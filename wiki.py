import wikipediaapi
from tqdm import tqdm
import requests
import re
import json
import os

#The enum value for main Wikipedia pages
PAGE = wikipediaapi.Namespace.MAIN
CATEGORY = wikipediaapi.Namespace.CATEGORY
URL = 'https://en.wikipedia.org/w/api.php'
IMDB_REGEX = '^https?://www.imdb.com/title/(tt\d{7}\d*)/?$'


class Wiki:
    
    def __init__(self):
        """
        Initalises a Wiki object set to English Wikipedia.

        Returns
        -------
        None.

        """
        self.wiki = wikipediaapi.Wikipedia('en')
        self.session = requests.Session()
        
    def fetch_and_store_plots(self,tmdb):
        total = sum([len(self.wiki_pages[year]['pages']) for year in self.wiki_pages])
        done = [f[:4] for f in os.listdir('wiki_jsons')]
        self.errors = {}

        with tqdm(total=total) as pbar:
            for i,year in enumerate(self.wiki_pages):
                raw_films = {}
                if str(year) in done:
                    with open(f'wiki_jsons/{year}.json') as f:
                        raw_films = json.load(f)
                print(f'Fetching year {i+1} of {len(self.wiki_pages)} ({year}) - {pbar.n}/{pbar.total}:')
                self.errors=[]
                try:
                    pages = self.wiki_pages[year]['pages']
                    films = {}
                    titles = []
                    for film in raw_films:
                        if not 'error' in raw_films[film]:
                            films[film] = raw_films[film]
                            titles.append(films[film]['title'])
                    pbar.update(len(pages))
                    if len(films) == len(raw_films):
                        continue
                    for page in pages:
                        title = page.title
                        if title in titles:
                            continue
                        page_id = page.pageid
                        try:
                            plot = self.get_plot(page)
                            if plot:
                                films[page_id] = {'title':title,'plot':plot}
                                imdb_id = self.get_imdb_id(page_id)
                                if imdb_id:
                                    tmdb_id = tmdb.get_tmdb_id_from_imdb_id(imdb_id)
                                    if tmdb_id:
                                        films[page_id]['tmdb_id'] = tmdb_id
                                    else:
                                        films[page_id]['imdb_id'] = imdb_id
                        except(KeyboardInterrupt):
                            return
                        except:
                            films[page_id] = {'title':title,'error':True}
                            self.errors.append(page_id)
                            print(f'Error with page #{page_id} ({title}) in {year}')
                        pbar.update(1)
                    if films:
                        with open(f'wiki_jsons/{year}.json','w') as file:
                            json.dump(films,file)
                except(Exception) as err:
                    print(f'Error with {year}: {err}')
        
    def get_imdb_id(self,page_id):
        links = self.get_ext_links(page_id)
        imdb_links = [re.match(IMDB_REGEX,link).group(1) for link in links if re.match(IMDB_REGEX,link)]
        if len(imdb_links) == 0:
            return None
        if len(imdb_links) > 1:
            return None
        else:
            return imdb_links[0]
        
    def get_ext_links(self,page_id):
        params = {
            "action": "parse",
            "pageid": page_id,
            "prop": "externallinks",
            "format": "json"
        }
        result = self.session.get(url=URL,params=params)
        data = result.json()
        links = data['parse']['externallinks']
        return links
    
    def fetch_all_years(self,years_to_fetch):
        self.wiki_pages = {}
        
        years = []
        
        print('Fetching main year pages...')
        for year in tqdm(years_to_fetch):
            pages,sub_cats = self.fetch_films_from_year(year)
            if pages:
                years.append(year)
                self.wiki_pages[year] = {}
                self.wiki_pages[year]['pages'] = pages
                self.wiki_pages[year]['sub_cats'] = sub_cats
            
        years = [year for year in years if self.wiki_pages[year]['sub_cats']]
        level = 0
        
        while(years):
            print(f"Fetching {'sub '*(level+1)}category pages for {len(years)} years...")
            years = self.get_sub_cat_pages(years, level)
            level += 1
            
        for year in tqdm(years):
            ids = [page.pageid for page in self.wiki_pages[year]['pages']]
            self.wiki_pages[year]['id_set'] = set(ids)
            
            for l in range(level):
                self.add_sub_cat_pages(year, l)
    
    def add_sub_cat_pages(self,year,level):
        ps = 'extra_'*(level+1) + 'pages'
        if year not in self.wiki_pages[year]:
            return
        pages = self.wiki_pages[year][ps]
        
        for page in pages:
            page_id = page.pageid
            if page_id not in self.wiki_pages[year]['id_set']:
                self.wiki_pages[year]['pages'].append(page)
                self.wiki_pages[year]['id_set'].add(page_id)
        
    def get_sub_cat_pages(self,years,level):
        sc = 'extra_'*level + 'sub_cats'
        ps = 'extra_'*(level+1) + 'pages'

        for year in tqdm(years):
            extra_pages = []
            extra_sub_cats = []
            for sub_cat in self.wiki_pages[year][sc]:
                pages,sub_cats = self.get_pages_from_category(sub_cat, year)
                extra_pages.extend(pages)
                extra_sub_cats.extend(sub_cats)
            self.wiki_pages[year][ps] = extra_pages
            self.wiki_pages[year]['extra_'+sc] = extra_sub_cats
        
        next_level_years = [year for year in years if self.wiki_pages[year]['extra_'+sc]]
        return next_level_years

    def fetch_films_from_year(self,year):
        """
        Gets all the Wikipedia pages for films in a given year.

        Parameters
        ----------
        year : int or str
            The year to fetch films for.

        Returns
        -------
        pages : list of wikipediaapi.WikipediaPage
            The Wikipedia pages for the films from the given year.

        """
        #Get the category page for the given year's films
        cat_title = f'Category:{year}_films'
        cat_page = self.wiki.page(cat_title)
        if not cat_page.exists():
            return None,None
        #Extract the actual film pages from the category page
        pages,sub_cats = self.get_pages_from_category(cat_page,year)

        return pages,sub_cats

    def get_pages_from_category(self,category,year):
        """
        Extracts the actual film pages from a category page.

        Parameters
        ----------
        category : wikipediaapi.WikipediaPage
            A Wikipedia category page for a year of films.
        year : int or str
            The year the category relates to.

        Returns
        -------
        pages : list of wikipediaapi.WikipediaPage
            The Wikipedia pages for the films from the given year.

        """
        #Get the member pages of the category
        cat_mem = category.categorymembers
        #Restrict to just pages (e.g. not subcategories)
        pages = [cat_mem[p] for p in cat_mem if cat_mem[p].ns == PAGE]
        #Reject pages which are lists of films rather than actual film pages
        pages = [p for p in pages if not self.is_list_page(p,year)]
        
        sub_cats = [cat_mem[p] for p in cat_mem if cat_mem[p].ns == CATEGORY]
        
        return pages, sub_cats

    def is_list_page(self,page, year):
        """
        Checks if the given Wikipedia page is a list of films from a given year.

        Parameters
        ----------
        page : wikipediaapi.WikipediaPage
            A WikipediaPage to check.
        year : int or str
            The year the page relates to.

        Returns
        -------
        bool
            True if the page is a list of films, otherwise False.

        """
        #Checks for pages in the style 'List of <type> films of <year>'
        return page.title.startswith('List of ') and page.title.endswith(f'films of {year}')
    
    def find_matches(self,tmdb_films,wiki_films):
        """
        Tries to find a matched Wikipedia page for each TMDb film.

        Parameters
        ----------
        tmdb_films : list of tmdbv3api.AsObj
            A list of TMDb films to match against.
        wiki_films : list of wikipediaapi.WikipediaPage
            A list of Wikipedia film pages to match against.

        Returns
        -------
        matches : tuple of (wikipediaapi.WikipediaPage, tmdbv3api.AsObj)
            A matched pair of Wikipedia page and TMDb film.

        """
        matches = [];
        for film in tmdb_films:
            #Ignore case and Wikipedia disambiguation text
            fs = [(f,film) for f in wiki_films if f.title.lower().startswith(film.title.lower())]
            if len(fs) == 1:
                matches.append(fs[0])
        return matches
    
    def get_plot(self,page):
        """
        Attempts to get the text of the plot from the given Wikipedia film page.

        Parameters
        ----------
        page : wikipediaapi.WikipediaPage
            A Wikipedia film page.

        Returns
        -------
        str or None
            Returns the text of the plot if it exists or None if it doesn't.

        """
        sections = [section.title for section in page.sections]
        #Favour 'Plot' over 'Plot summary' if both are present
        if 'Plot' in sections:
            return page.section_by_title('Plot').text
        elif 'Plot Summary' in sections:
            return page.section_by_title('Plot Summary').text
        elif 'Plot summary' in sections:
            return page.section_by_title('Plot summary').text
        else:
            return None