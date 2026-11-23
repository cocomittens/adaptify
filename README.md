# Adaptify
Adaptive user interface based on human emotion. 

Adaptify is designed to adjust its visual elements in response to the emotional cues detected from user-provided text. By analyzing input data, it dynamically modifies the interface to reflect a range of emotional states, offering both insights and a personalized user experience. 

Click on the "view demo" or "view dashboard" button in the upper right hand corner to switch between modes.

## Demo
Try it out [here.](https://adaptify-frontend.vercel.app/dashboard)

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

# List all recorded emotions
curl http://localhost:8000/api/text/
```

No configuration is needed: by default everything is stored in a local SQLite file.
To use Supabase instead, fill in the Supabase values in `.env` (see `.env.example`).

## Screenshots
### Dashboard
<img width="1439" alt="Screenshot - Dashboard" src="https://github.com/user-attachments/assets/d15038d0-ffb4-4aad-8007-d4c585b47346">
The dashboard displays historical trends and various metrics of users' emotions.

### Demo
### Neutral
<img width="1437" alt="Screenshot - Neutral" src="https://github.com/user-attachments/assets/1de309eb-6151-47be-b48a-73027b6e0b27">
Interface showcasing a neutral state without any specific emotional input.

### Angry
<img width="1435" alt="Screenshot - Angry" src="https://github.com/user-attachments/assets/c1ab9e53-05e8-427a-a809-49d932c4c8f9">
Interface reflecting detected angry sentiment from the text.

## Planned Features
* Sign in page and auth
* Dashboard customization - Options to personalize the display.
* UI component library based on emotional data - Reusable components driven by emotion metrics.
* Enhanced dashboard functionality - Features such as user sorting, customizable graphs, and improved responsiveness.
* Additional demo UI features - Further refinements to react to real-time emotional data.
