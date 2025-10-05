# 🧪 AI Campaign Orchestration Lab

**Portfolio demo** showing how AI can analyze, optimize, and adjust multi-channel campaigns (Email + SMS + Paid) with
fatigue analysis, predictive engagement scoring, A/B subject line ideation, and an executive brief.

> ⚠️ Uses **synthetic data** in `data/`. Swap in your Eloqua/HubSpot/Mailchimp exports to showcase with real data.

## ✨ Features
- KPI dashboard with **AI Optimization toggle** (simulated uplift)
- **Fatigue detection** (7-day touches) and **segments export**
- **Predictive engagement score** (0–100)
- **Subject line generator** (template-based, offline)
- **Executive weekly brief** downloadable as PDF (if `reportlab` present) or Markdown

## 🚀 Quickstart
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Project Structure
```
AI_Campaign_Orchestration_Lab/
├─ app.py
├─ utils/
│  └─ ai_modules.py
├─ data/
│  ├─ synthetic_contacts.csv
│  └─ synthetic_campaign_events.csv
├─ assets/
└─ requirements.txt
```
## 🧠 Explainability (for CMOs/Legal)
- AI toggle demonstrates ROI sensitivity (default +8% lift)—adjust in `utils/ai_modules.py`
- Fatigue rule: >4 touches in 7 days → segmented reduction
- Exportable segments for journey routing and compliance review

---

© 2025 Karen Rogers‑Robinson. MIT License.
