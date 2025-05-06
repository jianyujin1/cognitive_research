# A Multimodal Cognitive Agent for Personalized Early Dementia Assessment Using Online and Offline Cognitive Tasks 
### 온오프라인 초기 치매 조기 진단 및 개선을 위한 개인 맞춤형 멀티모달 인지 평가 에이전트 🧠 
## Cognitive Assessment System Overview (Digital health application | Tailored Twoard Seniors for Conitive Sccreening and Improvement 

This README explains cognitive assessment system draft, covering both **online adaptive assessments** and **offline OCR-based uploads**. It includes real-time scoring, adaptive logic, performance trend analysis, and Gradio UIs.

---

## 🔧 Components

### 1. Online Adaptive Game Logic for Aassesment 
- **Animal Recall & Sentence Repetition**: Uses `SentenceTransformer` for semantic similarity.
- **Adaptive Difficulty**: Adjusts difficulty based on prior session performance (e.g., recall length).
- **Memory Tests**: Number and word recall games with scoring based on exact or partial matches.
- **Progress Comparison**: Compares current and previous sessions and shows per-task trends.
- **LLM Feedback**: Uses `Falcon-1B` (or similar model) to generate motivational summaries.

### 2. Offline (Printout) Upload with OCR
- **Upload Scanned Sheets**: Gradio UI for uploading a completed puzzle printout.
- **Text Extraction**: `pytesseract` OCR extracts game name, score, and user ID.
- **Field Parsing**: Regex-based pattern matching to extract structured fields.
- **Score Logging**: Appends to `cognitive_log.csv` and provides feedback trends.
- **Fallbacks**: If fields are not filled manually, OCR text is parsed as a backup.

### 3. Online Games with Gradio UI
- **Sudoku Step Game**: User fills in a missing number, gets feedback + explanation.
- **Sentence Recall**: Repeat sentence based on last performance.
- **Step-by-step UI**: Built with `gr.Blocks`, two-step quiz flow.



---

## 💾 Log File

All session results are saved to:
```
cognitive_log.csv
```
with these fields:
- `user_id`, `timestamp`, `question_type`, `question`, `expected`, `answer`, `score`

---

## 📈 Adaptive Engine Logic

1. **Memory Difficulty**:
   - `> 0.85`: Harder (7-digit or abstract words)
   - `< 0.60`: Easier (4-digit or common words)
2. **Sentence Repetition**:
   - Easy: `"The dog ran fast."`
   - Medium: `"The cat sat on the mat."`
   - Hard: `"Despite the complexity..."`

---

## 🧠 Feedback Generation

If previous and current scores exist:
- Trend detected → Generates LLM summary (e.g., "⬆️ Improved by +0.20")
- If error occurs or no model: fallback feedback message

---

## 📦 Key Packages Used

- `sentence-transformers`, `transformers`, `pytesseract`
- `gradio`, `pandas`, `torch`, `nltk`, `matplotlib`

---

## 📤 Deployment Instructions

1. Install dependencies:
```bash
pip install gradio sentence-transformers pytesseract matplotlib pandas torch transformers nltk
```
2. Run:
```bash
python your_ui_script.py
```

---

## 📍 Future Improvements

- Multi-language support
- Session trend graphs (matplotlib)


---

© 2025 | Multimodal Cognitive Health Agent – AI & Dementia Research Initiative
