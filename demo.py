import random
from tmdb import Tmdb
from wiki import Wiki
import concurrent.futures

if __name__ == '__main__':

    tmdb = Tmdb()#Tmdb object for TMDb API calls
    wiki = Wiki()#Wiki object for Wikipedia API calls
        
    #Get some random films for demo purposes
    n = 100
    r = random.randint(0,len(tmdb.all_films) - n)
    films = tmdb.fetch_n_films(n, r)
        
    print()#blank line
    
    #Print some info about the first 10 films
    for film in films[:10]:
        print(film.title)
        print('\t Released: ' + film.release_date)
        print('\t Genre(s): ' + ', '.join(tmdb.get_genres(film)))
        
    print()#blank line
        
    #Print a plot summary from TMDb for the first film
    print(films[0].title + ':')
    print(films[0].overview)
    
    print()#blank line
    
    #Print the count of films by year
    year_count = tmdb.summarise_by_year(films)
    print('Summary by year:')
    for y,c in year_count.most_common():
        print(f'\t{y}: {c}')
        
    print()#blank line
    
    #Print the count of films by genre
    genre_count = tmdb.summarise_by_genre(films)
    print('Summary by genre:')
    for g,c in genre_count.most_common():
        print(f'\t{g}: {c}')
        
    print()#blank line
    
    #Get the 3 years with the most films for this selection
    top_3_years = [c[0] for c in year_count.most_common()[:3]]
    print('Top 3 years:')
    for year in top_3_years:
        print(f'\t{year}')
        
    print()#blank line
    
    #Get the Wikipedia pages for all the films in those years
    wiki_films_by_year = {}
    for year in top_3_years:
        print(f'Fetching Wikipedia pages for {year}...')
        wiki_films_by_year[year] = wiki.fetch_films_from_year(year)
        print(f'\t{len(wiki_films_by_year[year])} films found on Wikipedia for {year}')
        
    #Get the films for the top 3 years
    tmdb_films_by_year = {}
    for year in top_3_years:
        tmdb_films_by_year[year] = tmdb.get_films_by_year(films, year)

    print()#blank line
    
    #Check for matches between TMDb and Wikipedia
    matches_by_year = {}
    print('Matches by year:')
    for year in top_3_years:
        matches_by_year[year] = wiki.find_matches(tmdb_films_by_year[year], wiki_films_by_year[year])
        print(f'\t{year} - {len(matches_by_year[year])}/{len(tmdb_films_by_year[year])} films matched:')
        for wiki_film,tmdb_film in matches_by_year[year]:
            print(f'\t\t Wiki: {wiki_film.title}, TMDb: {tmdb_film.title}')
            
    print()#blank line
    
    #Check for plots in the matched Wikipedia pages
    plots_by_year = {}
    print('Plots by year:')
    for year in top_3_years:
        plots_by_year[year] = {}
        for wiki_film,tmdb_film in matches_by_year[year]:
            plot = wiki.get_plot(wiki_film)
            if plot is not None:
                plots_by_year[year][tmdb_film.title] = (plot,tmdb_film.overview)
        print(f'\t{year} - {len(plots_by_year[year])}/{len(matches_by_year[year])} pages with plots:')
        for film in plots_by_year[year]:
            wiki_plot_length = len(plots_by_year[year][film][0].split(' '))
            tmdb_plot_length = len(plots_by_year[year][film][1].split(' '))
            print(f'\t\t{film}')
            print(f'\t\t\tWiki Plot Length: {wiki_plot_length} words, TMDb Plot Length: {tmdb_plot_length} words')
        
    print()#blank line
    
    #Print final summary
    top_3 = sum([len(tmdb_films_by_year[films]) for films in tmdb_films_by_year])
    matches = sum([len(matches_by_year[films]) for films in matches_by_year])
    plots = sum([len(plots_by_year[films]) for films in plots_by_year])
    print(f'Of {n} films fetched from TMDb, {top_3} films were in the three most represented years...')
    print(f'Of those {top_3} films, {matches} of them had matching Wikipedia pages...')
    print(f'Of those {matches} pages, {plots} of them had valid plots...')
    print(f'So, for a random selection of {top_3} films, {plots} can be included in the dataset.')