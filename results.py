import pandas as pd
import os

def write_results(scores, file_name, model_name, plot_type):

    file_path = './' + file_name

    if not os.path.isfile(file_path):
        score_dict = {'Model Name': [], 'Plot Source': [], 'F1 Macro': [], 
                      'F1 Micro': [], 'Hamming Loss': []}
        
        score_dict['Model Name'].append(model_name)
        score_dict['Plot Source'].append(plot_type)
        score_dict['F1 Macro'].append(scores['eval_f1_macro'])
        score_dict['F1 Micro'].append(scores['eval_f1_micro'])
        score_dict['Hamming Loss'].append(scores['eval_hamming_loss'])

        df = pd.DataFrame(score_dict)
        df.to_pickle(file_name)

    else:

        df = pd.read_pickle(file_path)
        data = {'Model Name': model_name, 'Plot Source': plot_type, 'F1 Macro': scores['eval_f1_macro'], 
                'F1 Micro': scores['eval_f1_micro'], 'Hamming Loss': scores['eval_hamming_loss']}
        df.append(data, ignore_index=True)

        os.remove(file_path)
        df.to_pickle(file_name)
    
    return('Results are saved in {}'.format(file_name))