"""
Compare the shipped emotion classifier with more modern approaches.

    python api/text_emotion/compare.py

Every model is trained on the same training set and scored on the same held-out
test set that train.py uses:

  baseline    word counts + logistic regression (the model the API serves)
  embeddings  a frozen pretrained sentence encoder + logistic regression
  fine-tuned  DistilRoBERTa fine-tuned on the training set

Everything runs locally and needs the packages in requirements-eval.txt. The
fine-tuning step takes a few minutes on a laptop with a GPU or Apple silicon.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline

from train import CONFIDENCE_THRESHOLD, RANDOM_STATE, split_dataset

RESULTS_DIR = Path(__file__).resolve().parent / 'results'
EMOTIONS = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'shame', 'surprise']

EMBEDDING_MODEL = 'sentence-transformers/all-mpnet-base-v2'
FINE_TUNE_MODEL = 'distilroberta-base'
FINE_TUNE_EPOCHS = 3
FINE_TUNE_BATCH_SIZE = 32
FINE_TUNE_LEARNING_RATE = 3e-5



def device():
    import torch
    if torch.cuda.is_available():
        return 'cuda'
    return 'mps' if torch.backends.mps.is_available() else 'cpu'


def run_baseline(train_texts, train_emotions, test_texts):
    model = Pipeline([('cv', CountVectorizer()), ('lr', LogisticRegression(max_iter=2000))])
    model.fit(train_texts, train_emotions)
    return model.classes_, model.predict_proba(test_texts)


def run_embeddings(train_texts, train_emotions, test_texts):
    from sentence_transformers import SentenceTransformer
    encoder = SentenceTransformer(EMBEDDING_MODEL, device=device())
    encode = lambda texts: encoder.encode(texts, batch_size=128, normalize_embeddings=True)
    classifier = LogisticRegression(C=10, max_iter=3000)
    classifier.fit(encode(train_texts), train_emotions)
    return classifier.classes_, classifier.predict_proba(encode(test_texts))


def run_fine_tuned(train_texts, train_emotions, test_texts):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    torch.manual_seed(RANDOM_STATE)
    target = device()
    tokenizer = AutoTokenizer.from_pretrained(FINE_TUNE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        FINE_TUNE_MODEL, num_labels=len(EMOTIONS)
    ).to(target)
    labels = torch.tensor([EMOTIONS.index(emotion) for emotion in train_emotions])

    def tokenize(texts):
        return tokenizer(texts, padding=True, truncation=True, max_length=96, return_tensors='pt').to(target)

    # Linear warmup over the first 6% of steps, then linear decay to zero.
    steps_per_epoch = -(-len(train_texts) // FINE_TUNE_BATCH_SIZE)
    total_steps = FINE_TUNE_EPOCHS * steps_per_epoch
    warmup_steps = int(0.06 * total_steps)
    optimizer = torch.optim.AdamW(model.parameters(), lr=FINE_TUNE_LEARNING_RATE, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.LambdaLR(
        optimizer,
        lambda step: step / warmup_steps if step < warmup_steps
        else max(0.0, (total_steps - step) / (total_steps - warmup_steps)),
    )

    for epoch in range(FINE_TUNE_EPOCHS):
        model.train()
        order = np.random.RandomState(RANDOM_STATE + epoch).permutation(len(train_texts))
        for start in range(0, len(order), FINE_TUNE_BATCH_SIZE):
            batch = order[start:start + FINE_TUNE_BATCH_SIZE]
            loss = model(**tokenize([train_texts[i] for i in batch]), labels=labels[batch].to(target)).loss
            loss.backward()
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
        print(f'  fine-tuning: epoch {epoch + 1} of {FINE_TUNE_EPOCHS} done')

    model.eval()
    probabilities = []
    with torch.no_grad():
        for start in range(0, len(test_texts), FINE_TUNE_BATCH_SIZE):
            logits = model(**tokenize(test_texts[start:start + FINE_TUNE_BATCH_SIZE])).logits
            probabilities.append(torch.softmax(logits, dim=-1).cpu().numpy())
    return np.array(EMOTIONS), np.concatenate(probabilities)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--skip', nargs='*', default=[], choices=['embeddings', 'fine-tuned'])
    args = parser.parse_args()

    train_texts, test_texts, train_emotions, test_emotions = split_dataset()
    actual = np.array(test_emotions)

    local_models = {
        'Word counts + logistic regression (baseline)': run_baseline,
        f'Frozen embeddings ({EMBEDDING_MODEL.split("/")[-1]}) + logistic regression': run_embeddings,
        f'Fine-tuned {FINE_TUNE_MODEL}': run_fine_tuned,
    }
    skipped = {'embeddings': 'Frozen', 'fine-tuned': 'Fine-tuned'}
    rows = []
    for name, run in local_models.items():
        if any(name.startswith(skipped[key]) for key in args.skip):
            continue
        print(f'Running: {name}')
        classes, probabilities = run(train_texts, train_emotions, test_texts)
        predicted = classes[probabilities.argmax(axis=1)]
        confident = probabilities.max(axis=1) >= CONFIDENCE_THRESHOLD
        rows.append({
            'model': name,
            'accuracy': accuracy_score(actual, predicted),
            'macro_f1': f1_score(actual, predicted, average='macro'),
            'coverage': confident.mean(),
            'confident_accuracy': accuracy_score(actual[confident], predicted[confident]),
        })

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / 'comparison.json', 'w', encoding='utf-8') as file:
        json.dump({'test_size': len(actual), 'models': rows}, file, indent=2)

    print(f'\nHeld-out test set: {len(actual):,} texts.\n')
    print(f'| Model | Accuracy | Macro F1 | Accuracy at confidence >= {CONFIDENCE_THRESHOLD:.0%} (share of texts) |')
    print('|---|---|---|---|')
    for row in rows:
        print(
            f"| {row['model']} | {row['accuracy']:.1%} | {row['macro_f1']:.2f} | "
            f"{row['confident_accuracy']:.0%} ({row['coverage']:.0%}) |"
        )


if __name__ == '__main__':
    main()
