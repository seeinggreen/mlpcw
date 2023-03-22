# mlpcw

A collection of film datasets with plots, plot summaries and mutli-label genres for use in machine learning. Also includes code to apply LLMs to the data and evaluate the results. All files are commented with Numpydoc for reference.

## 1 - TMDb Data Scrape (Full film data for 700K+ films)

A full data scrape of all TMDb film data as of Feburary 2023 is available in ```data/tmdb_full_jsons```. The data is unordered and grouped into arbirtary groups that are <50MB each. To use the full dataset, read each JSON (e.g. using ```json.load(file)```) sequentially. If you need to have all the data in one list, it is reccomended to first append each file to a list of lists and then flatten the list (using e.g  ```all_films = [film for sublist in json_data for film in sublist]```) as the dataset is very large. The dictionary keys correspond to the TMDb API - more information can be found here - https://developers.themoviedb.org/3/movies/get-movie-details.

## 2 - Wikipedia Data Scrape (Titles, Release Years and Plots for 85k films)

A full data scrape of all film pages on English Wikipedia as of Feburary 2023 is available in ```data/wiki_jsons```. The films are grouped by year of release (according to Wikipedia). Each JSON file contains information for a single release year. The Wikipedia page ID is the key of the dictionary and each entry is then a dictionairy with a 'title' entry (the Wikipedia page title, possibly with disambiguation text) and a 'plot' entry which is the plot in plaintext from Wiipedia. Around 85% of films will also have a 'tmdb_id' entry which is the TMDb ID of the film. Some will have an 'imdb_id' entry, which is where an IMDb ID is known, but no matching TMDb ID was found.

## 3 - Full Dataset and Balanced Dataset (Titles, Release Years, Plots, Plot Summaries and Genres for 73k/22k films)

To access the full dataset, import the Dataset class and create a new dataset object with ```load_data=True```. To load the balanced dataset, set ```balanced=True``` and use ```get_data()``` to select whichever dataset is loaded:
```
from dataset import Dataset

ds = Dataset(load_data=True)
full_dataset = ds.get_data()

#OR

ds = Dataset(balanced=True,load_data=True)
balanced_dataset = ds.get_data()
```
Both datasets use TMDb for the title, release year, genre(s) and plot summary. The long-form plot is taken from Wikipedia. The balanced dataset has equal numbers of each genre.

## 4 - Further TMDb API Use
If you need to rebuild or add to the datasets, you will need a TMDb API key - https://www.themoviedb.org/settings/api. Place the key in a file called ```api_key.txt``` in the main folder of the repo. You will also need the list of film IDs from a daily export - https://developers.themoviedb.org/3/getting-started/daily-file-exports. Either download the specified export (24/02/2023) or update ```tmdb.py``` with the filename of the export you have used.

## 5 - Required Packages (not needed to simply use the datasets)
- tmdbv3api (clone from https://github.com/AnthonyBloomer/tmdbv3api into the top level of the repo or run 'pip install tmdbv3api')
- wikipedia-api (run 'pip install wikipedia-api' or 'conda install -c conda-forge wikipedia-api')

## 6 - Training and Evaluating the models
To train the classification model, ```classification.py``` with the appropriate arguments (see the file, or run it with the ```--help``` flag)
