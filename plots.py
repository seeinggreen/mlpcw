from dataset import Dataset as dt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from os import listdir
from os.path import isfile, join


def get_all_results(path):
    """
    

    Parameters
    ----------
    path : TYPE
        DESCRIPTION.

    Returns
    -------
    final_df : TYPE
        DESCRIPTION.

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
    

    Returns
    -------
    df : TYPE
        DESCRIPTION.

    """

    ds = dt(load_data=True)
    dict_data = ds.all_data 
    df = pd.DataFrame(dict_data)
    return df


def genre_stats(df):
    """
    

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.

    Returns
    -------
    genre_count : TYPE
        DESCRIPTION.

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
    

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    freeze_stat : TYPE
        DESCRIPTION.
    plot_source : TYPE
        DESCRIPTION.

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
    

    Parameters
    ----------
    genre_dict : TYPE
        DESCRIPTION.

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

    