from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer, TrainerCallback
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from results import *
from datasets import Dataset
from dataset import Dataset as dt
from transformers import AutoModelForSequenceClassification
import argparse
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score, hamming_loss, classification_report
import numpy as np


import os

BATCH_SIZE = 16
LEARNING_RATE = 2e-5
EPOCHS = 3
NUM_LABELS = 19


class CustomCallBack(TrainerCallback):
    def on_epoch_end(self, args, state, control, logs=None, **kwargs):
        print(f"Epoch {state.epoch}: ")


def load_data():
    ds = dt(load_data=True)
    dict_data = ds.all_data 
    df = pd.DataFrame(dict_data)
    return df


def labeling(df):

    mlb = MultiLabelBinarizer()
    yt = mlb.fit_transform(df['genres'])
    for i in range(len(yt)):
        df['genres'][i] = yt[i]

    return df


def process_data(row, plot):

    text = row[plot]
    text = str(text)
    text = ' '.join(text.split())

    encodings = tokenizer(text, padding="max_length", truncation=True, max_length=256)



    encodings['label'] = row['genres'].astype(float)
    encodings['text'] = text

    return encodings


def compute_metrics(eval_pred):

    predictions, labels = eval_pred
    predictions = (predictions > 0).astype(int)
    # Multi-label metrics:
    # f1-macro --> overall f1 score for multi-label classification
    # f1-micro --> per-class f1 score
    f1_macro = f1_score(labels, predictions, average='macro')
    f1_micro = f1_score(labels, predictions, average='micro')
    hamming = hamming_loss(labels, predictions)

    print(classification_report(labels, predictions, zero_division=0))

    return {"f1_macro": f1_macro, "f1_micro": f1_micro, "hamming_loss": hamming}


if __name__ == "__main__":
    
    os.environ["CUDA_VISIBLE_DEVICES"]='0'
    
    parser = argparse.ArgumentParser(description="Predict movie genres using plots.")
    parser.add_argument("--model", help="Select encoder model (BERT, RoBERTa, xlnet)", choices=["bert", "roberta", "xlnet"], default="bert")
    parser.add_argument("--plot_type", help="Select the plot you wish to do classification on", choices=['wiki', 'tmdb'])
    parser.add_argument("--file_name", help="Choose an excel file name ending with .pkl")
    
    args = parser.parse_args()

    if args.model == 'bert':
        tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        model = AutoModelForSequenceClassification.from_pretrained(
        'bert-base-uncased',
        num_labels = NUM_LABELS,
        problem_type = "multi_label_classification"
        )
    elif args.model == 'roberta':
        tokenizer = AutoTokenizer.from_pretrained('roberta-base')
        model = AutoModelForSequenceClassification.from_pretrained(
        'roberta-base',
        num_labels=NUM_LABELS,
        problem_type = "multi_label_classification"
        )
    elif args.model == 'xlnet':
        tokenizer = AutoTokenizer.from_pretrained('xlnet-base-cased')
        model = AutoModelForSequenceClassification.from_pretrained(
        'xlnet-base-cased',
        num_labels=NUM_LABELS,
        problem_type = "multi_label_classification"
        )

    if args.plot_type == 'wiki':
        plot_type = 'wiki_plot'
    
    elif args.plot_type == 'tmdb':
        plot_type = 'tmdb_plot'

    df = load_data()
    df = labeling(df)

    processed_data = []

    for i in range:
        processed_data.append(process_data(df.iloc[i], plot_type))

    new_df = pd.DataFrame(processed_data)

    train_df, valid_df = train_test_split(
        new_df,
        test_size=0.2,
        random_state=1234
    )

    # train_hg = Dataset(pa.Table.from_pandas(train_df))
    # valid_hg = Dataset(pa.Table.from_pandas(valid_df))
    
    train_hg = Dataset.from_pandas(train_df)
    valid_hg = Dataset.from_pandas(valid_df)

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

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_hg,
        eval_dataset=valid_hg,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        callbacks = [CustomCallBack]
    )

    trainer.train()

    model_results = trainer.evaluate()

    write_results(model_results, args.file_name, args.model, args.plot_type)
