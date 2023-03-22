import pandas as pd
import os

def write_confusion_matrix(file_name, conf_matrix):
    """
    Gets filename and confusion matrix returned by the model to create a table of TP, FP, TN, and FN 
    for each class and write them in a pickle file.

    Parameters
    ----------
    file_name : str
        File name specified by the user
    conf_matrix : numpy.ndarray
        A three dimensional array that includes the TP, NP, FP, FN for each class.

    Returns
    -------
    None

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

def write_results(scores, file_name, model_name, plot_type, freeze, max_length):
    """
    Creates a table of F1 scores, Hamming Loss along with the model, the plot source it was trained on, 
    whether it was trained, and the maximum token length in a table. It then stores the results in a pickle 
    file.

    Parameters
    ----------
    scores : dict
        Consists of F1 Macro/Micro and Hamming Loss.
    file_name : str
        File name specified by the user.
    model_name : str
        The model used for encoding.
    plot_type : str
        The plot source used to carry out the training process.
    freeze : bool
        Whether the model was fine-tuned.
    max_length : int
        The maximum length of the input tokens.

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