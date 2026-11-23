# Adaptify
Adaptive user interface based on human emotion. 

Adaptify is designed to adjust its visual elements in response to the emotional cues detected from user-provided text. By analyzing input data, it dynamically modifies the interface to reflect a range of emotional states, offering both insights and a personalized user experience. 

Use the Dashboard and Demo links in the header to switch between the two.

## Demo
Try it out [here.](https://adaptify-frontend.vercel.app/dashboard)

The demo runs on free hosting, so the first load can take up to a minute while the server wakes up. Its data is sample data that resets whenever the server restarts.

## Features
* **Live emotion detection** - The demo analyzes text as you type and shows the probability of each of eight emotions: anger, disgust, fear, joy, neutral, sadness, shame and surprise.
* **Adaptive interface** - The page takes on the color of the detected emotion, and an example support panel changes its wording and actions to suit it. An angry message, for example, brings "Talk to a person now" and a refund option to the front.
* **"Not sure" state** - When the model's confidence is below 55%, the interface stays neutral instead of guessing.
* **Dashboard** - Entries per day by emotion, a ranked breakdown with average confidence per emotion, and average confidence over time.
* **API** - A single endpoint that classifies text and lists recorded entries. It stores data in SQLite by default, or in Supabase when configured.

## Frontend
Frontend repo found [here.](https://github.com/cocomittens/adaptify-frontend)

## Running locally
Requires Python 3.9–3.11 (the pinned numpy/scikit-learn versions don't support newer Pythons).

```bash
git clone https://github.com/cocomittens/adaptify
cd adaptify
python3.9 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # optional; sets DEBUG=True
python manage.py migrate
python manage.py seed_demo      # optional; sample history for the dashboard
python manage.py runserver
```

The API is now at `http://localhost:8000/api/text/`:

```bash
# Detect the emotion in a piece of text
curl -X POST http://localhost:8000/api/text/ \
  -H 'Content-Type: application/json' \
  -d '{"text": "I am so happy today"}'

# Analyze without recording an entry
curl -X POST http://localhost:8000/api/text/ \
  -H 'Content-Type: application/json' \
  -d '{"text": "I am so happy today", "save": false}'

# List all recorded emotions
curl http://localhost:8000/api/text/
```

The response contains the top `emotion`, its `confidence`, and the `probabilities` of all eight emotions.

No configuration is needed: by default everything is stored in a local SQLite file.
To use Postgres instead, set `DATABASE_URL` in `.env`; to use Supabase, fill in the Supabase values (see `.env.example`).

## Model
The classifier is a bag-of-words logistic regression built with scikit-learn: each text becomes a vector of word counts, and a multinomial logistic regression maps those counts to one of eight emotions. It was chosen because it is small, fast enough for a free-tier server, and gives a probability for every emotion.

It is trained on 34,792 labeled texts (`api/text_emotion/data/emotion_dataset.csv`). 20% of them are held out for testing, stratified by emotion. On that held-out set:

| | |
|---|---|
| Accuracy across all eight emotions | 65% |
| Macro F1 | 0.62 |
| Accuracy when confidence is at least 55% (67% of texts) | 77% |

The model is strongest on fear and joy (F1 0.72) and weakest on disgust (F1 0.32), which has few training examples. It was trained mostly on emotional text, so plain factual sentences are often given a low-confidence emotion. That is why the demo only adapts when confidence is at least 55%.

To retrain the model and print the full evaluation:

```bash
python api/text_emotion/train.py
```

### Comparison with other models
`api/text_emotion/compare.py` trains two more modern models on the same training set and scores all three on the same held-out test set (6,959 texts):

| Model | Accuracy | Macro F1 | Accuracy when confidence is at least 55% (share of texts) |
|---|---|---|---|
| Word counts + logistic regression (served by the API) | 65.0% | 0.62 | 77% (67%) |
| Frozen sentence embeddings (`all-mpnet-base-v2`) + logistic regression | 66.4% | 0.60 | 78% (67%) |
| Fine-tuned DistilRoBERTa | 73.6% | 0.72 | 80% (86%) |

* A pretrained language model used as-is adds about one point over word counts. General-purpose sentence embeddings do not separate these eight emotions much better than the words themselves.
* Fine-tuning a small transformer on the dataset adds almost nine points, and it is confident on far more texts (86% against 67%) at slightly higher accuracy. It trains in about five minutes on a laptop.
* The API still serves the word-count model because it is a 2 MB file with no deep-learning dependencies, which fits free hosting. Serving the fine-tuned model is the next step.

To reproduce the table (this downloads the pretrained models and needs the extra packages):

```bash
pip install -r requirements-eval.txt
python api/text_emotion/compare.py
```

## Screenshots
### Dashboard
<img alt="Screenshot - Dashboard" src="docs/screenshots/dashboard.png">
The dashboard displays historical trends and various metrics of users' emotions.

### Demo
### Neutral
<img alt="Screenshot - Neutral" src="docs/screenshots/demo-neutral.png">
The demo before any emotion is detected: a neutral page and the default support panel.

### Angry
<img alt="Screenshot - Angry" src="docs/screenshots/demo-angry.png">
After an angry message: the page takes the emotion's color and the support panel puts a person and a refund first.

## Planned Features
* Sign in and per-user data - The demo currently records everything under one demo user.
* Persistent storage for the hosted demo.
* Serve the fine-tuned model - It is clearly more accurate, but needs more memory than the free hosting provides.
* More adaptive components - The support panel is one example; the goal is a reusable set of components driven by emotion.
* Dashboard filters - Date ranges and per-user views.
