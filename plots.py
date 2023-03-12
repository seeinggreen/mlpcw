from dataset import Dataset as dt
import pandas as pd
import plotly.express as px


def load_data():

    ds = dt(load_data=True)
    dict_data = ds.all_data 
    df = pd.DataFrame(dict_data)
    return df


def genre_stats(df):

    genre_count = {}
    for list in df['genres']:

        for genre in list:
            if genre in genre_count.keys():
                genre_count[genre] += 1
                continue
            else:
                genre_count[genre] = 1

    return genre_count


def token_histogram(df):
    


def plot_genre_frequency(genre_dict):
    
    df_data = {'genre': [], 'frequency': []}
    for genre in genre_dict:
        df_data['genre'].append(genre)
        df_data['frequency'].append(genre_dict[genre])

    df = pd.DataFrame(df_data)
    fig = px.bar(df, y='frequency', x='genre', text_auto='.2s',
            title="Frequency per genre in the dataset")
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.show()


if __name__ == "__main__":

    df = load_data()
    all_genres = genre_stats(df)
    plot_genre_frequency(all_genres)

    