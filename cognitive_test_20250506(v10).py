
# =======================================
# 🧠 Cognitive Test with Online & Offline Entry
# =======================================

# --- Step 1: Install & Import Required Libraries ---
import random, time, datetime, csv, os, re
import pandas as pd
import pytz
from PIL import Image
import pytesseract
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import torch

# --- Step 2: Initialize Model & Timezone ---
encoder = SentenceTransformer('all-MiniLM-L6-v2')  # Load sentence encoder
kst = pytz.timezone("Asia/Seoul")  # Korea Standard Time
today_weekday = datetime.datetime.now(kst).strftime('%A')  # Today weekday

# --- Step 3: Define Animal Checker Using WordNet ---
from nltk.corpus import wordnet as wn
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')

def is_animal(word):
    word = word.strip().lower()
    synsets = wn.synsets(word, pos=wn.NOUN)
    for syn in synsets[:2]:
        for path in syn.hypernym_paths():
            for h in path:
                if 'animal.n.01' in h.name():
                    return True
    return False

def score_animals(user_input):
    words = [w.strip().lower() for w in user_input.split(",")]
    matched_animals = [w for w in words if is_animal(w)]
    return round(min(len(matched_animals), 3) / 3, 2)

# --- Step 4: Define Memory and Recall Games ---
def number_recall_game():
    digit_length = random.choice([4, 5, 6])
    number = ''.join([str(random.randint(0, 9)) for _ in range(digit_length)])
    print(f"REMEMBER THIS NUMBER: {number}")
    time.sleep(5)
    print("
" * 50)
    user_input = input("Now type the number you saw: ")
    correct_digits = sum([1 for a, b in zip(number, user_input) if a == b])
    score = round(correct_digits / digit_length, 2)
    return score, number, user_input

def word_list_recall_game():
    word_list = ["apple", "table", "car", "banana", "house"]
    print("Memorize these words:
" + ", ".join(word_list))
    time.sleep(5)
    print("
" * 50)
    user_input = input("Recall the words (comma-separated): ").lower()
    user_words = [w.strip() for w in user_input.split(",")]
    correct = sum([1 for word in word_list if word in user_words])
    score = round(correct / len(word_list), 2)
    return score, ", ".join(word_list), ", ".join(user_words)

# --- Step 5: Run Online Test (Text + Memory) ---
questions = [
    "1. What day of the week is it?",
    "2. Can you name three animals?",
    "3. Please repeat this sentence: The cat sat on the mat."
]
expected_answers = [today_weekday, "", "The cat sat on the mat"]

score_details = []

print("🧠 Starting Cognitive Test")
for i, q in enumerate(questions):
    print(q)
    user_input = input("Your answer: ")
    if i == 1:
        score = score_animals(user_input)
    else:
        user_vec = encoder.encode(user_input, convert_to_tensor=True)
        expected_vec = encoder.encode(expected_answers[i], convert_to_tensor=True)
        score = float(util.pytorch_cos_sim(user_vec, expected_vec)[0])
    score_details.append({
        "type": "text", "question": q,
        "expected": expected_answers[i] or "Any 3 animals",
        "user_answer": user_input,
        "score": round(score, 2)
    })

# --- Step 6: Append Number and Word Recall ---
recall_score, shown_number, recalled_number = number_recall_game()
score_details.append({
    "type": "memory", "question": "Number Recall",
    "expected": shown_number, "user_answer": recalled_number,
    "score": round(recall_score, 2)
})

recall_score, original_words, recalled_words = word_list_recall_game()
score_details.append({
    "type": "recall", "question": "Word Recall",
    "expected": original_words, "user_answer": recalled_words,
    "score": round(recall_score, 2)
})

# --- Step 7: Save to Log ---
nickname = input("Nickname: ").strip().lower()
phone_last4 = input("Last 4 digits of phone: ").strip()
email = input("Email (optional): ").strip()
user_id = f"{nickname}_{phone_last4}_{email or 'noemail'}"
timestamp = datetime.datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
log_file = "cognitive_log.csv"
write_header = not os.path.exists(log_file)

with open(log_file, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    if write_header:
        writer.writerow(['user_id', 'timestamp', 'question_type', 'question', 'expected', 'answer', 'score'])
    for entry in score_details:
        writer.writerow([
            user_id, timestamp,
            entry['type'], entry['question'],
            entry['expected'], entry['user_answer'], entry['score']
        ])

# --- Step 8: Show Summary ---
print(f"✅ Session saved to {log_file}")
df = pd.read_csv(log_file)
user_df = df[df['user_id'] == user_id]
summary = user_df.groupby('timestamp')['score'].mean().reset_index()
for i, row in summary.iterrows():
    print(f"Session {i+1} - {row['timestamp']}: Avg Score = {round(row['score'], 2)}")

# --- Step 9: Trend Feedback using LLM ---
last_two = summary.tail(2)
if len(last_two) >= 2:
    prev_score = round(last_two.iloc[0]['score'], 2)
    curr_score = round(last_two.iloc[1]['score'], 2)
    trend = "improved" if curr_score > prev_score else "declined" if curr_score < prev_score else "stayed consistent"
    prompt = f"""
    The user {user_id} completed a cognitive test.
    Previous score: {prev_score}
    Current score: {curr_score}
    Trend: {trend}
    Write a short motivational message and next task suggestion.
    """
    try:
        summarizer = pipeline("text-generation", model="tiiuae/falcon-rw-1b", max_length=100)
        response = summarizer(prompt)[0]['generated_text']
        print("
🤖 Feedback:
" + response.strip())
    except:
        print(f"
🤖 Feedback: Score {trend} from {prev_score} to {curr_score}. Keep it up!")

# --- Step 10: OCR Support for Offline Uploads ---
def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"OCR Error: {str(e)}"

def extract_fields_from_text(text):
    fields = {
        "nickname": None, "digits": None, "game_name": None,
        "score": None, "date": None, "agent": None
    }
    patterns = {
        "nickname": r"Nickname:\s*(\w+)",
        "digits": r"Last 4 digits.*?:\s*(\d{4})",
        "game_name": r"Game name:\s*(.+)",
        "score": r"Score:\s*(\d+)",
        "date": r"Date:\s*(\d+)",
        "agent": r"Agent:\s*(\w+)"
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[key] = match.group(1).strip()
    return fields

def process_uploaded_image(image_path, user_id=None, digits=None, game_name=None, score=None):
    timestamp = datetime.datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
    ocr_text = extract_text_from_image(image_path)
    fields = extract_fields_from_text(ocr_text)
    nickname = user_id or fields['nickname']
    digits = digits or fields['digits']
    game_name = game_name or fields['game_name']
    score = score or fields['score']
    if nickname and digits and game_name and score:
        full_id = f"{nickname.lower()}_{digits}"
        result = {
            "user_id": full_id,
            "timestamp": timestamp,
            "question_type": game_name,
            "question": "offline_upload",
            "expected": "N/A",
            "answer": f"OCR by {fields.get('agent', 'unknown')}",
            "score": float(score)
        }
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                result['user_id'], result['timestamp'],
                result['question_type'], result['question'],
                result['expected'], result['answer'], result['score']
            ])
        print(f"✅ Saved offline score: {game_name} | Score: {score} | Agent: {fields.get('agent')} | Date: {fields.get('date')}")
    else:
        print("⚠️ Could not extract all required fields from OCR.")

# To test offline:
# process_uploaded_image("example_image.png")
