from dataset import Dataset as dt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from os import listdir
from os.path import isfile, join


def get_all_results(path):
    """
    Loads experiments' results from pickled files located in the directory located at `path`.

    Parameters
    ----------
    path : String
        Path to the directory containing result files.

    Returns
    -------
    final_df : pandas.Dataframe
        Dataframe containing all results.

    """
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    df_list = []
    for file in onlyfiles:
        df = pd.read_pickle(path + file)
        df_list.append(df)
    final_df = pd.concat(df_list)

    return final_df

def load_data():
    """
    Load the movie plots and genre dataset in a pandas Dataframe using our custom Dataset class.

    Returns
    -------
    df : pandas.Dataframe
        The full dataset.

    """

    ds = dt(load_data=True)
    dict_data = ds.all_data 
    df = pd.DataFrame(dict_data)
    return df


def genre_stats(df):
    """
    Count number of occurences for each genre and returns it in a dictionnary.

    Parameters
    ----------
    df : pd.Dataframe
        The full movie plots and genre dataset.

    Returns
    -------
    genre_count : Dict
        A dictionnary of (k, v) pairs where k are each genre and v the number of occurences in the dataset.

    """

    genre_count = {}
    for list in df['genres']:

        for genre in list:
            if genre in genre_count.keys():
                genre_count[genre] += 1
                continue
            else:
                genre_count[genre] = 1

    return genre_count
    

def plot_scores(df, freeze_stat, plot_source):
    """
    Create bar plots of models' results for a given plot source and a given type of training (pre-trained or fine-tuned).

    Parameters
    ----------
    df : pandas.Dataframe
        The results dataset for all our experiments.
    freeze_stat : Boolean
        True for plotting results of the models with frozen weights.
        False for plotting results of the fine-tuned models.
    plot_source : String
        'wiki_plot' for models evaluated on the Wikipedia plots.
        'tmdb_plot' for models evaluated on the TMDb plots.

    Returns
    -------
    None.

    """

    df = df.loc[(df['Freeze?'] == freeze_stat) & (df['Plot Source'] == plot_source)]
    df['F1 Micro'] = round(df['F1 Micro']*100, 2)
    df['F1 Macro'] = round(df['F1 Macro']*100, 2)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Model Name'],
        y= df['F1 Micro'],
        width=0.2,
        name='F1 Micro',
        marker_color='#0a2342'
    ))
    fig.add_trace(go.Bar(
        x=df['Model Name'],
        y=df['F1 Macro'],
        width=0.2,
        name='F1 Macro',
        marker_color='#2ca58d'
    ))

    fig.update_layout(barmode='group', 
                      xaxis_tickangle=-45, 
                      font=dict(size=18), 
                      width=700, height=550)
    
    fig.update_yaxes(tickfont_family="Arial Black")
    fig.update_xaxes(tickfont_family="Arial Black")
    fig.show()

def plot_genre_frequency(genre_dict):
    """
    Create a bar plot of the frequency of each genre in the dataset.

    Parameters
    ----------
    genre_dict : Dict
        Dictionnary of (k, v) pairs where k are genres and v are occurences of each genre in the dataset.

    Returns
    -------
    None.

    """
    
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

   df = get_all_results('result_pkls/')

#    plot_scores(df, True, plot_source='wiki_plot')

    
