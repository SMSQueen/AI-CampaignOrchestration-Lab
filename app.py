
import streamlit as st
import pandas as pd
from pathlib import Path
from utils.ai_modules import compute_fatigue, engagement_score, suggest_subject_lines, simulate_ai_uplift

st.set_page_config(page_title="AI Campaign Orchestration Lab", layout="wide")
st.title("🧪 AI Campaign Orchestration Lab")
st.caption("Portfolio Demo • Synthetic Data • Toggle AI to see simulated lift")

@st.cache_data
def load_data(data_dir: Path):
    contacts = pd.read_csv(data_dir / "synthetic_contacts.csv", parse_dates=["created_at"])
    events = pd.read_csv(data_dir / "synthetic_campaign_events.csv", parse_dates=["event_dt"])
    return contacts, events

data_dir = Path("data")
contacts, events = load_data(data_dir)

st.sidebar.header("Controls")
ai_on = st.sidebar.toggle("AI Optimization", value=True)
persona_filter = st.sidebar.multiselect("Persona", sorted(contacts["persona"].unique().tolist()))
channel_filter = st.sidebar.multiselect("Channel", sorted(events["channel"].unique().tolist()))
date_min, date_max = events["event_dt"].min(), events["event_dt"].max()
date_range = st.sidebar.date_input("Date range", (date_min, date_max), min_value=date_min, max_value=date_max)

filtered = events.copy()
if persona_filter:
    filtered = filtered[filtered["persona"].isin(persona_filter)]
if channel_filter:
    filtered = filtered[filtered["channel"].isin(channel_filter)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["event_dt"] >= start) & (filtered["event_dt"] <= end)]

def compute_kpis(ev: pd.DataFrame):
    if ev.empty: 
        return {k: None for k in ["sends","open_rate","ctr","ctor","unsub_rate"]}
    sends = len(ev)
    open_rate = ev["opened"].mean()
    ctr = ev["clicked"].mean()
    ctor = ev.loc[ev["opened"]==1, "clicked"].mean() if ev["opened"].sum() > 0 else 0.0
    unsub_rate = ev["unsubscribed"].mean()
    return {"sends": sends, "open_rate": round(open_rate,4), "ctr": round(ctr,4), "ctor": round(ctor,4), "unsub_rate": round(unsub_rate,4)}

kpis = compute_kpis(filtered)
kpis_ai = simulate_ai_uplift(kpis, uplift=0.08) if ai_on else kpis

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Sends", f"{kpis['sends'] if kpis['sends'] else 0:,}")
col2.metric("Open Rate", f"{(kpis_ai['open_rate'] or 0)*100:.1f}%")
col3.metric("CTR", f"{(kpis_ai['ctr'] or 0)*100:.1f}%")
col4.metric("CTOR", f"{(kpis_ai['ctor'] or 0)*100:.1f}%")
col5.metric("Unsub Rate", f"{(kpis['unsub_rate'] or 0)*100:.2f}%")

st.divider()

st.subheader("Fatigue & Engagement Scoring")
fatigue = compute_fatigue(filtered, window_days=7, threshold=4)
scores = engagement_score(filtered)
insights = fatigue.merge(scores, on="contact_id", how="outer").fillna({"touches":0, "fatigue_flag":False, "engagement_score":0})
st.dataframe(insights.sample(min(300, len(insights))))

with st.expander("Download segments (CSV)"):
    st.download_button("Download Fatigued Segment", insights[insights["fatigue_flag"]==True].to_csv(index=False), "fatigued_segment.csv", "text/csv")
    st.download_button("Download High-Engagement (score ≥ 60)", insights[insights["engagement_score"]>=60].to_csv(index=False), "high_engagement_segment.csv", "text/csv")

st.subheader("Subject Line Lab")
persona_for_subjects = st.selectbox("Select persona", sorted(contacts["persona"].unique().tolist()))
seed = st.slider("Random seed", 0, 999, 42)
suggestions = suggest_subject_lines(persona_for_subjects, n=6, seed=seed)
st.write("Use these as candidates for your next A/B test. When AI is ON, the system will simulate ~8% lift on Open/CTR metrics.")
st.write(pd.DataFrame({"suggested_subject": suggestions}))

st.subheader("Executive Brief")
st.caption("Generates a 1-page summary with KPIs, risks, and next actions.")

def generate_brief_md(k):
    lines = []
    lines.append(f"# Weekly Executive Brief — {pd.to_datetime(events['event_dt'].max()).date()}\\n")
    lines.append("## KPI Snapshot\\n")
    lines.append(f"- Sends: {k['sends']:,}")
    lines.append(f"- Open Rate: {k['open_rate']*100:.1f}%")
    lines.append(f"- CTR: {k['ctr']*100:.1f}%")
    lines.append(f"- CTOR: {k['ctor']*100:.1f}%")
    lines.append(f"- Unsub Rate: {k['unsub_rate']*100:.2f}%\\n")
    lines.append("## Risks & Alerts\\n- Fatigued contacts detected above threshold.\\n- Monitor unsub trends in SMS-heavy segments.\\n")
    lines.append("## AI Next Best Actions\\n- Reduce frequency for fatigued personas.\\n- Promote subject line winners to 100% of traffic.\\n- Shift budget to channels with higher predicted engagement.\\n")
    return "\\n".join(lines)

brief_md = generate_brief_md(kpis_ai if ai_on else kpis)
st.code(brief_md, language="markdown")

try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import LETTER
    import io
    def brief_pdf_bytes(md_text: str) -> bytes:
        styles = getSampleStyleSheet()
        story = []
        for line in md_text.split("\\n"):
            if line.startswith("# "):
                story.append(Paragraph(f"<b>{line[2:]}</b>", styles["Title"])) 
            elif line.startswith("## "):
                story.append(Spacer(1, 8))
                story.append(Paragraph(f"<b>{line[3:]}</b>", styles["Heading2"])) 
            elif line.strip().startswith("-"):
                story.append(Paragraph(line, styles["Normal"])) 
            else:
                if line.strip():
                    story.append(Paragraph(line, styles["Normal"])) 
            story.append(Spacer(1, 6))
        buff = io.BytesIO()
        doc = SimpleDocTemplate(buff, pagesize=LETTER)
        doc.build(story)
        return buff.getvalue()
    pdf_bytes = brief_pdf_bytes(brief_md)
    st.download_button("Download Executive Brief (PDF)", data=pdf_bytes, file_name="executive_brief.pdf", mime="application/pdf")
except Exception:
    st.info("ReportLab not available; download Markdown instead.")
    st.download_button("Download Executive Brief (Markdown)", data=brief_md, file_name="executive_brief.md", mime="text/markdown")
