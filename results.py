import pandas as pd
import os

def write_confusion_matrix(file_name, conf_matrix):
    """
    

    Parameters
    ----------
    file_name : TYPE
        DESCRIPTION.
    conf_matrix : TYPE
        DESCRIPTION.

    Returns
    -------
    dict : TYPE
        DESCRIPTION.

    """
    
    file_path = './confusion_pkls/' + file_name

    l = [{
            'class': i,
            'TN': label[0][0],
            'FN': label[0][1],
            'TP': label[1][0],
            'FP': label[1][1]}
            for i,label in enumerate(conf_matrix)]
        
    if not os.path.isfile(file_path):
        df = pd.DataFrame(l)
        df.to_pickle(file_path)
    else:
        df = pd.read_pickle(file_path)
        data = l
        
        df.append(data, ignore_index=True)

        os.remove(file_path)
        df.to_pickle(file_path)
    return dict

def write_results(scores, file_name, model_name, plot_type, freeze, max_length):
    """
    

    Parameters
    ----------
    scores : TYPE
        DESCRIPTION.
    file_name : TYPE
        DESCRIPTION.
    model_name : TYPE
        DESCRIPTION.
    plot_type : TYPE
        DESCRIPTION.
    freeze : TYPE
        DESCRIPTION.
    max_length : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """

    file_path = './result_pkls/' + file_name

    if not os.path.isfile(file_path):
        score_dict = {'Model Name': [], 'Plot Source': [], 'F1 Macro': [], 
                      'F1 Micro': [], 'Hamming Loss': [], 'Freeze?': [], 'Max Length': []}
        
        score_dict['Model Name'].append(model_name)
        score_dict['Plot Source'].append(plot_type)
        score_dict['Freeze?'].append(freeze)
        score_dict['Max Length'].append(max_length)
        score_dict['F1 Macro'].append(scores['eval_f1_macro'])
        score_dict['F1 Micro'].append(scores['eval_f1_micro'])
        score_dict['Hamming Loss'].append(scores['eval_hamming_loss'])

        df = pd.DataFrame(score_dict)
        df.to_pickle(file_path)

    else:

        df = pd.read_pickle(file_path)
        data = {'Model Name': model_name, 'Plot Source': plot_type, 'F1 Macro': scores['eval_f1_macro'], 
                'F1 Micro': scores['eval_f1_micro'], 'Hamming Loss': scores['eval_hamming_loss'], 'Freeze?': freeze,
                'Max Length': max_length}
        
        df.append(data, ignore_index=True)

        os.remove(file_path)
        df.to_pickle(file_path)
    
    return('Results are saved in {}'.format(file_path))