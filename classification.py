from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
import pyarrow as pa
from datasets import Dataset, load_metric
from dataset import Dataset as dt
from transformers import AutoModelForSequenceClassification
import argparse
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np


BATCH_SIZE = 16
LEARNING_RATE = 2e-5
EPOCHS = 3
NUM_LABELS = 19


def compute_metrics(eval_pred):
    metric1 = load_metric("precision")
    metric2 = load_metric("recall")
    metric3 = load_metric("f1")
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    precision = metric1.compute(predictions=predictions, references=labels)['precision']
    recall = metric2.compute(predictions=predictions, references=labels)['recall']
    f1 = metric3.compute(predictions=predictions, references=labels)['f1']
    return {"precision": precision, "recall": recall, "f1": f1}


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict movie genres using plots.")
    parser.add_argument("--model", help="Select encoder model (BERT, RoBERTam DeBERTa, GPT-2)", choices=["bert", "roberta", "deberta", "gpt2"], default="bert")
    parser.add_argument("--plot_type", help="Select the plot you wish to do classification on", choices=['wiki', 'tmdb'])
    
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

    if args.plot_type == 'wiki':
        plot_type = 'wiki_plot'
    
    elif args.plot_type == 'tmdb':
        plot_type = 'tmdb_plot'

    df = load_data()
    df = labeling(df)

    processed_data = []

    for i in range(len(df)):
        processed_data.append(process_data(df.iloc[i], plot_type))

    new_df = pd.DataFrame(processed_data)

    train_df, valid_df = train_test_split(
        new_df,
        test_size=0.2,
        random_state=1234
    )

    train_hg = Dataset(pa.Table.from_pandas(train_df))
    valid_hg = Dataset(pa.Table.from_pandas(valid_df))

    training_args = TrainingArguments(
        output_dir="./result", 
        evaluation_strategy="epoch",
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        num_train_epochs=EPOCHS,
        )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_hg,
        eval_dataset=valid_hg,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    trainer.train()

    trainer.evaluate()
