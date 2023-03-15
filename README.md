# mlpcw

Files are commented with Numpydoc for reference.

To access the full dataset, import the Dataset class and create a new dataset object with ```load_data=True```. To load the balanced dataset, set ```load_balanced=True``` and access either ```all_data``` or ```balanced``` respecitively:
```
from dataset import Dataset

ds = Dataset(load_data=True)
films = ds.all_data

#OR

ds = Dataset(load_balanced=True)
films = ds.balanced
```
## Files Required But Not Included
The following files should all be placed in the top level of the project (they will be ignored by git):
- api_key.txt (the TMDb API key)
- movie_ids_02_24_2023.json (the movie ids file - extracted from http://files.tmdb.org/p/exports/movie_ids_02_24_2023.json.gz)
- tmdbv3api (Python package for API access, cloned from https://github.com/AnthonyBloomer/tmdbv3api OR install as below)

## Required Packages
- tmdbv3api (clone as above or run 'pip install tmdbv3api')
- wikipedia-api (run 'pip install wikipedia-api' or 'conda install -c conda-forge wikipedia-api')

## Training and Evaluating the model
To train the classification model, run the following command:
python classification.py --model [bert, roberta] --plot_type [wiki, tmdb]
