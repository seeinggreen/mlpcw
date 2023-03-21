from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer, TrainerCallback
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from results import write_confusion_matrix,write_results
from datasets import Dataset
from dataset import Dataset as dt
import argparse
from sklearn.metrics import f1_score, hamming_loss, classification_report, multilabel_confusion_matrix
import pandas as pd
import os

BATCH_SIZE = 16
LEARNING_RATE = 2e-5
EPOCHS = 3

class CustomCallBack(TrainerCallback):
    def on_epoch_end(self, args, state, control, logs=None, **kwargs):
        print(f"Epoch {state.epoch}: ")
        
def compute_metrics(eval_pred):
    """
    Defines metrics for the model to compute the scores.

    Parameters
    ----------
    eval_pred : tuple
        Contains the output of the SequenceClassification of the model, and the true values

    Returns
    -------
    dict
        F1 Macro, F1 Micro, and the Hamming Loss.

    """
    predictions, labels = eval_pred
    predictions = (predictions > 0).astype(int)
    # Multi-label metrics:
    # f1-macro --> overall f1 score for multi-label classification
    # f1-micro --> per-class f1 score
    f1_macro = f1_score(labels, predictions, average='macro')
    f1_micro = f1_score(labels, predictions, average='micro')
    hamming = hamming_loss(labels, predictions)
    confusion_matrix = multilabel_confusion_matrix(labels, predictions)

    print(classification_report(labels, predictions, zero_division=0))

    return {"f1_macro": f1_macro, "f1_micro": f1_micro, "hamming_loss": hamming, "confusion_matrix": confusion_matrix.tolist()}
 

class Classification:

    def load_data(self):
        """
        Loads the dataset into a dataframe.

        Returns
        -------
        None.

        """
        ds = dt(balanced=self.balanced,load_data=True)
        dict_data = ds.get_data()
        self.df = pd.DataFrame(dict_data)
    
    
    def labeling(self):
        """
        

        Returns
        -------
        None.

        """
        mlb = MultiLabelBinarizer()
        yt = mlb.fit_transform(self.df['genres'])
        for i in range(len(yt)):
            self.df['genres'][i] = yt[i]
    
    
    def process_data(self,row, plot, max_length):
        """
        Processes and tokenize the data to prepare it for the model.

        Parameters
        ----------
        row : dataframe
            A row of the dataframe passed to the function.
        plot : str
            The plot source to use for the data. The source is either from wikipedia or TMDB
        max_length : int
            The maximum length of the input sequence to pass to the encoder.

        Returns
        -------
        encodings : dictionary
            A dictionary containing the original text, labels and the input encodings returned by the tokenizer.

        """
        text = row[plot]
        text = str(text)
        text = ' '.join(text.split())
    
        encodings = self.tokenizer(text, padding="max_length", truncation=True, max_length=max_length)

        encodings['label'] = row['genres'].astype(float)
        encodings['text'] = text
    
        return encodings
    
    def create_model(self):
        """
        Creates the tokenizer and model.

        Returns
        -------
        None.

        """
        if self.model_type == 'bert':
            full_model_name = 'bert-base-uncased'
        elif self.model_type == 'roberta':
            full_model_name = 'roberta-base'
        elif self.model_type == 'xlnet':
            full_model_name = 'xlnet-base-cased'
        
        self.tokenizer = AutoTokenizer.from_pretrained(full_model_name)
        
        self.model = AutoModelForSequenceClassification.from_pretrained(
        full_model_name,
        num_labels = self.NUM_LABELS,
        problem_type = 'multi_label_classification'
        )
        
        if self.freeze:
            if self.model_type == 'bert':
                params = self.model.bert.parameters()
            elif self.model_type == 'roberta':
                params = self.model.roberta.parameters()
            elif self.model_type == 'xlnet':
                params = self.model.transformer.parameters()
            
            for param in params:
                param.requires_grad = False    

    def load_and_process_data(self):
        """
        Loads the given dataset, processes the data and splits into into train/test sets.

        Returns
        -------
        None.

        """
        self.load_data()
        self.labeling()
    
        processed_data = []
    
        for i in range(len(self.df)):
            processed_data.append(self.process_data(self.df.iloc[i], self.plot_type, self.max_length))
    
        new_df = pd.DataFrame(processed_data)
    
        self.train_df, self.valid_df = train_test_split(
            new_df,
            test_size=0.2,
            random_state=1234
        )  
    
    def train(self):
        """
        Runs the training.

        Returns
        -------
        None.

        """
        self.train_hg = Dataset.from_pandas(self.train_df)
        self.valid_hg = Dataset.from_pandas(self.valid_df)
    
        training_args = TrainingArguments(
            output_dir="./result", 
            evaluation_strategy="epoch",
            per_device_train_batch_size=BATCH_SIZE,
            per_device_eval_batch_size=BATCH_SIZE,
            learning_rate=LEARNING_RATE,
            num_train_epochs=EPOCHS,
            save_strategy="epoch",
            save_total_limit=2,
            metric_for_best_model="f1_macro",
            load_best_model_at_end=True,
            weight_decay=0.01,
            )
    
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_hg,
            eval_dataset=self.valid_hg,
            tokenizer=self.tokenizer,
            compute_metrics=compute_metrics,
            callbacks = [CustomCallBack]
        )
    
        self.trainer.train()
    
    def get_results(self):
        """
        Evaluates the model and writes the results to file.

        Returns
        -------
        None.

        """
        model_results = self.trainer.evaluate()
    
        write_results(model_results, self.file_name, self.model_type, self.plot_type, self.freeze, self.max_length)
        write_confusion_matrix(self.file_name, model_results['eval_confusion_matrix'])
    
    def __init__(self,model_type,plot_type,file_name,balanced,freeze,max_length):
        """
        Initialises an encoder along with the classifier.

        Parameters
        ----------
        model_type : str
            Specificies the model to use. Either 'bert', 'roberta' or 'xlnet'.
        plot_type : str
            Specifies whether to use the Wiki plot or the TMDb plot. Either 'wiki' or 'tmdb'.
        file_name : str
            The file to store the results in.
        balanced : bool
            Whether to use the balanced dataset or the full dataset.
        freeze : bool
            Whether to freeze the encoder weights during training.
        max_length : int
            The maximum lenght of the input sequence.

        Returns
        -------
        None.

        """
        self.model_type = model_type
        self.file_name = file_name
        self.max_length = max_length
        self.balanced = balanced
        self.freeze = freeze
    
        if self.balanced:
            self.NUM_LABELS = 7
        else:
            self.NUM_LABELS = 19
        
        if plot_type == 'wiki':
            self.plot_type = 'wiki_plot'
        
        elif plot_type == 'tmdb':
            self.plot_type = 'tmdb_plot'
            
    def run(self):
        """
        Runs all steps of the classification.

        Returns
        -------
        None.

        """
        self.create_model()
        self.load_and_process_data()
        self.train()
        self.get_results()
            
if __name__ == "__main__":
    
    os.environ["CUDA_VISIBLE_DEVICES"]='0'
    
    parser = argparse.ArgumentParser(description="Predict movie genres using plots.")
    parser.add_argument("--model", help="Select encoder model (BERT, RoBERTa, xlnet)", choices=["bert", "roberta", "xlnet"], default="bert")
    parser.add_argument("--plot_type", help="Select the plot you wish to do classification on", choices=['wiki', 'tmdb'])
    parser.add_argument("--file_name", help="Choose an excel file name ending with .pkl")
    parser.add_argument("--balanced", action='store_true', help="Whether to use the balanced dataset.")
    parser.add_argument("--freeze", action="store_true", help="Whether to make to freeze the encoders")
    parser.add_argument("--max_length", help="Maximum sequence length (choose 400 for wiki and 60 for tmdb)")

  
    args = parser.parse_args()
    
    model = args.model
    plot_type = args.plot_type
    file_name = args.file_name
    balanced = args.balanced
    freeze = args.freeze
    max_length = int(args.max_length)
    
    classification = Classification(model,plot_type,file_name,balanced,freeze,max_length)
    classification.run()

