import wikipediaapi

#The enum value for main Wikipedia pages
PAGE = wikipediaapi.Namespace.MAIN

class Wiki:
    
    def __init__(self):
        """
        Initalises a Wiki object set to English Wikipedia.

        Returns
        -------
        None.

        """
        self.wiki = wikipediaapi.Wikipedia('en')

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
        #Extract the actual film pages from the category page
        pages = self.get_pages_from_category(cat_page,year)
        return pages

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
        return pages

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