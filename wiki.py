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
MAIN_DATA_DIR = 'data'
WIKI_DIR = os.path.join(MAIN_DATA_DIR,'wiki_jsons')


class Wiki:
    
    def __init__(self):
        """
        Initalises a Wiki object set to English Wikipedia.

        Returns
        -------
        None.

        """
        self.wiki = wikipediaapi.Wikipedia('en')
        #Start an API session for manual API calls
        self.session = requests.Session()
        
    def fetch_and_store_plots(self,tmdb):
        """
        Fetches the plot from Wikipedia movie pages.

        Parameters
        ----------
        tmdb : Tmdb
            A Tmdb object for translating IMDb IDs to TMDb IDs.

        Returns
        -------
        None.

        """
        #The total number of Wikipedia pages to process
        total = sum([len(self.wiki_pages[year]['pages']) for year in self.wiki_pages])
        #A list of years that are already (partially) processed
        done = [f[:4] for f in os.listdir(WIKI_DIR)]
        #Keep track of pages that didn't complete sucessfully
        self.errors = {}

        with tqdm(total=total) as pbar:
            for i,year in enumerate(self.wiki_pages):
                #If the year has been processed, get the pages already on file
                raw_films = {}
                if str(year) in done:
                    with open(os.path.join(WIKI_DIR,f'{year}.json')) as f:
                        raw_films = json.load(f)
                print(f'Fetching year {i+1} of {len(self.wiki_pages)} ({year}) - {pbar.n}/{pbar.total}:')
                self.errors[year]=[]
                try:
                    pages = self.wiki_pages[year]['pages']
                    films = {}
                    titles = []
                    #For existing entries, keep them if there was no error
                    for film in raw_films:
                        if not 'error' in raw_films[film]:
                            films[film] = raw_films[film]
                            titles.append(films[film]['title'])
                    #If there were no errors, update the progress bar and move on
                    if str(year) in done and len(films) == len(raw_films):
                        pbar.update(len(pages))
                        continue
                    pbar.update(len(titles))
                    for page in pages:
                        #Titles are preloaded, so no API call is required if the page gets skipped
                        title = page.title
                        if title in titles:
                            continue
                        page_id = page.pageid
                        try:
                            plot = self.get_plot(page)
                            if plot:
                                films[page_id] = {'title':title,'plot':plot}
                                #Use the IMDb ID (if present) to fetch a TMDb ID
                                imdb_id = self.get_imdb_id(page_id)
                                if imdb_id:
                                    tmdb_id = tmdb.get_tmdb_id_from_imdb_id(imdb_id)
                                    if tmdb_id:
                                        films[page_id]['tmdb_id'] = tmdb_id
                                    else:
                                        films[page_id]['imdb_id'] = imdb_id
                        except(KeyboardInterrupt):
                            return
                        except(Exception) as err:
                            films[page_id] = {'title':title,'error':True}
                            self.errors[year].append(page_id)
                            print(f'Error with page #{page_id} ({title}) in {year} - {err}')
                        pbar.update(1)
                    if films: #Don't create empty JSON files
                        print(f'Storing pages for {year}')
                        with open(os.path.join(WIKI_DIR,f'{year}.json'),'w') as file:
                            json.dump(films,file)
                    else:
                        print(f'No films for {year}')
                except(Exception) as err:
                    print(f'Error with {year}: {err}')
        
    def get_imdb_id(self,page_id):
        """
        Scrapes the external links on a Wikipedia page to try and get an IMDb ID.

        Parameters
        ----------
        page_id : int or str
            The ID of the Wikipedia page.

        Returns
        -------
        str or None
            Returns the IMDb ID if present, otherwise returns None.

        """
        links = self.get_ext_links(page_id)
        #Regex matches main pages of films and captures the ID in group 1
        imdb_links = [re.match(IMDB_REGEX,link).group(1) for link in links if re.match(IMDB_REGEX,link)]
        if len(imdb_links) == 0:
            return None
        #Reject pages that have multiple IMDb films linked
        if len(imdb_links) > 1:
            return None
        else:
            return imdb_links[0]
        
    def get_ext_links(self,page_id):
        """
        Performs a manual API call to fetch the external links on a Wikipedia page.

        Parameters
        ----------
        page_id : int or str
            The ID of the Wikipedia page.

        Returns
        -------
        links : list of str
            The external links on the given Wikipedia page.

        """
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
        """
        Fetches the Wikipedia pages about films using categories for the given list of years.

        Parameters
        ----------
        years_to_fetch : iterable
            The years to check categories for.

        Returns
        -------
        None.

        """
        self.wiki_pages = {}
        years = [] #Will be filled with years with valid category pages
        
        print('Fetching main year pages...')
        for year in tqdm(years_to_fetch):
            pages,sub_cats = self.fetch_films_from_year(year)
            if pages: #Pages will be None if the category page doesn't exist
                years.append(year)
                self.wiki_pages[year] = {}
                #Store the pages on the main category page and the sub-categories separately
                self.wiki_pages[year]['pages'] = pages
                self.wiki_pages[year]['sub_cats'] = sub_cats
            
        #Get a list of years for which there are sub-categories
        years = [year for year in years if self.wiki_pages[year]['sub_cats']]
        level = 0
        
        while(years):
            #Recursively fetch sub-categories until there are no more years with further sub-cats
            print(f"Fetching {'sub '*(level+1)}category pages for {len(years)} years...")
            years = self.get_sub_cat_pages(years, level)
            level += 1
            
        for year in tqdm(years):
            #Keep a set of all IDs already listed for the given year
            ids = [page.pageid for page in self.wiki_pages[year]['pages']]
            self.wiki_pages[year]['id_set'] = set(ids)
            
            #Add the sub-category pages for each level of sub-category
            for l in range(level):
                self.add_sub_cat_pages(year, l)
    
    def add_sub_cat_pages(self,year,level):
        """
        Attempts to add a level of sub-category pages to the main list of pages for a given year.

        Parameters
        ----------
        year : int
            The year the pages relate to.
        level : int
            The level below the main year's page.

        Returns
        -------
        None.

        """
        #Each layer's pages to add will be in their own list
        ps = 'extra_'*(level+1) + 'pages'
        if year not in self.wiki_pages[year]:
            return #Return if there are no extra pages to add
        pages = self.wiki_pages[year][ps]
        
        #For each extra page, add it if the ID isn't already present
        for page in pages:
            page_id = page.pageid
            if page_id not in self.wiki_pages[year]['id_set']:
                self.wiki_pages[year]['pages'].append(page)
                #Update the set of page IDs to reflect the addition
                self.wiki_pages[year]['id_set'].add(page_id)
        
    def get_sub_cat_pages(self,years,level):
        """
        Fetches the pages listed in a given sub-category.

        Parameters
        ----------
        years : list of int
            The years to fetch sub-categories for.
        level : int
            The level below the main year's page.

        Returns
        -------
        next_level_years : list of int
            The years which have sub-categories at the next level of depth.

        """
        #Generate the appropriate dictionary keys
        sc = 'extra_'*level + 'sub_cats'
        ps = 'extra_'*(level+1) + 'pages'

        #For each year, fetch the pages listed in the sub-category and the
        #sub-sub-categories listed
        for year in tqdm(years):
            extra_pages = []
            extra_sub_cats = []
            for sub_cat in self.wiki_pages[year][sc]:
                pages,sub_cats = self.get_pages_from_category(sub_cat, year)
                extra_pages.extend(pages)
                extra_sub_cats.extend(sub_cats)
            self.wiki_pages[year][ps] = extra_pages
            self.wiki_pages[year]['extra_'+sc] = extra_sub_cats
        
        #List the years that have further sub-categories to fetch
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