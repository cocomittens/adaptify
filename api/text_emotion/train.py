"""
Train and evaluate the emotion classifier, then save it for the API to load.

    python api/text_emotion/train.py

The model is a bag-of-words logistic regression: each text becomes a vector of
word counts, and a multinomial logistic regression maps those counts to one of
eight emotions. It is small and fast enough to serve from a free-tier server and
gives a probability for every emotion, which the demo uses to stay neutral when
no emotion is likely enough.

20% of the dataset is held out, stratified by emotion, and never used for
training. All figures printed below are measured on that held-out part.
"""

import csv
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

HERE = Path(__file__).resolve().parent
DATA_PATH = HERE / 'data' / 'emotion_dataset.csv'
MODEL_PATH = HERE / 'models' / 'emotion_classifier_pipe_lr.pkl'

TEST_SIZE = 0.2
RANDOM_STATE = 42
# The demo treats predictions below this confidence as "not sure".
CONFIDENCE_THRESHOLD = 0.55


def load_dataset():
    with open(DATA_PATH, encoding='utf-8') as file:
        rows = list(csv.DictReader(file))
    return [row['Text'] for row in rows], [row['Emotion'] for row in rows]


def main():
    texts, emotions = load_dataset()
    train_texts, test_texts, train_emotions, test_emotions = train_test_split(
        texts, emotions, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=emotions
    )

    model = Pipeline([
        ('cv', CountVectorizer()),
        ('lr', LogisticRegression(max_iter=2000)),
    ])
    model.fit(train_texts, train_emotions)

    probabilities = model.predict_proba(test_texts)
    predicted = model.classes_[probabilities.argmax(axis=1)]
    confidence = probabilities.max(axis=1)
    actual = np.array(test_emotions)

    print(f'Trained on {len(train_texts):,} texts, tested on {len(test_texts):,} held-out texts.\n')
    print(classification_report(actual, predicted, digits=2))

    confident = confidence >= CONFIDENCE_THRESHOLD
    print(
        f'At confidence >= {CONFIDENCE_THRESHOLD:.0%}: '
        f'{confident.mean():.0%} of texts get a label, '
        f'with {accuracy_score(actual[confident], predicted[confident]):.0%} accuracy.'
    )

    joblib.dump(model, MODEL_PATH)
    print(f'\nSaved model to {MODEL_PATH}')


if __name__ == '__main__':
    main()
