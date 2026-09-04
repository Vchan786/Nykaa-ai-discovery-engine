import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Nykaa Fashion AI Discovery Engine", page_icon="🧠", layout="wide")

st.title("🧠 Nykaa Fashion — AI Discovery Engine")
st.caption("Upload primary survey/interview feedback and discover themes, intent, behaviour and opportunities.")

THEMES = {
    "Price / Discount": ["price","discount","offer","sale","coupon","budget","expensive","cost","cheaper","deal"],
    "Fit / Size Confidence": ["size","fit","fitting","measurement","model","body type","length"],
    "Quality / Product Confidence": ["quality","material","fabric","durable","genuine","authentic","trust","finish","colour","color"],
    "Reviews / Social Proof": ["review","reviews","rating","ratings","comment","feedback","recommend"],
    "Competitor Comparison": ["myntra","amazon","flipkart","ajio","meesho","other app","other site","compare","comparison","competitor","elsewhere","better option"],
    "Return / Exchange Risk": ["return","returns","exchange","refund","replacement"],
    "Stock / Availability": ["stock","out of stock","sold out","available","availability","size unavailable"],
    "Delivery / Timing": ["delivery","deliver","shipping","arrive","arrival","late","urgent"],
    "Reminder / Forgetting": ["forgot","forget","reminder","remember","notification","notify"],
    "Occasion / Need": ["occasion","wedding","party","function","event","need","needed","urgent","use"]
}

INTENT = {
    "Genuine Purchase Intent": ["buy","purchase","planning to buy","waiting for discount","waiting for sale","waiting for offer","budget","need it"],
    "Bookmark-Low Intent": ["just liked","browsing","mood board","exploring","not planning","no intention"]
}

BEHAVIOUR = {
    "Postponing Purchase": ["wait","waiting","later","postpone","delay","delayed","salary","discount","sale","offer","budget"],
    "Comparing Alternatives": ["compare","comparison","other app","other site","myntra","amazon","ajio","flipkart","meesho","elsewhere","better option"],
    "Seeking More Information": ["review","reviews","rating","size","fit","quality","return","exchange","material","information","check"],
    "Exploring Product": ["browsing","exploring","just liked","mood board","liked it","save","wishlist"]
}

SEGMENT = {
    "High-Intent Shopper": ["buy","purchase","waiting for discount","waiting for sale","planning to buy","need it","budget"],
    "Confidence-Seeking Shopper": ["review","reviews","rating","size","fit","quality","return","exchange","material","trust"],
    "Deal-Seeking Shopper": ["price","discount","sale","offer","coupon","budget","expensive","deal"],
    "Exploring Shopper": ["browsing","exploring","just liked","mood board"]
}

IMPACT = {
    "Price / Discount":5, "Fit / Size Confidence":5, "Quality / Product Confidence":5,
    "Reviews / Social Proof":4, "Competitor Comparison":5, "Return / Exchange Risk":4,
    "Stock / Availability":4, "Delivery / Timing":3, "Reminder / Forgetting":3, "Occasion / Need":3
}

def norm(x):
    return re.sub(r"\s+", " ", str(x).lower()).strip()

def matches(text, words):
    t = norm(text)
    return [w for w in words if w.lower() in t]

def classify(text, rules):
    scores = {k: len(matches(text,v)) for k,v in rules.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Unclear"

def themes_found(text):
    found = [k for k,v in THEMES.items() if matches(text,v)]
    return found or ["Other / Unclassified"]

def primary_theme(text):
    scores = {k:len(matches(text,v)) for k,v in THEMES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Other / Unclassified"

def load_file(f):
    if f.name.lower().endswith(".csv"):
        return pd.read_csv(f)
    return pd.read_excel(f)

def prepare(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Preferred format: source_type, respondent_id, feedback
    if "feedback" in df.columns:
        if "source_type" not in df.columns:
            df["source_type"] = "Unknown"
        if "respondent_id" not in df.columns:
            df["respondent_id"] = [f"R{i+1}" for i in range(len(df))]
        out = df[["source_type","respondent_id","feedback"]].copy()
        out["feedback"] = out["feedback"].fillna("").astype(str).str.strip()
        return out[out["feedback"].str.len() > 0].reset_index(drop=True)

    # Fallback for raw survey/interview files: combine text columns
    text_cols = df.select_dtypes(include=["object","string"]).columns.tolist()
    if not text_cols:
        raise ValueError("No text columns found.")

    source_col = next((c for c in df.columns if str(c).lower() in ["source","source_type","research_source"]), None)
    id_col = next((c for c in df.columns if str(c).lower() in ["id","respondent_id","respondent","name"]), None)

    rows = []
    for i,row in df.iterrows():
        parts = []
        for c in text_cols:
            if c in [source_col,id_col]:
                continue
            if pd.notna(row[c]) and str(row[c]).strip():
                parts.append(f"{c}: {row[c]}")
        if parts:
            rows.append({
                "source_type": row[source_col] if source_col else "Uploaded Research",
                "respondent_id": row[id_col] if id_col else f"R{i+1}",
                "feedback": " | ".join(parts)
            })
    return pd.DataFrame(rows)

uploaded = st.file_uploader("Upload primary research data", type=["csv","xlsx"])
st.info("Recommended file: Nykaa_AI_Discovery_Engine_Combined_Input.csv")

if uploaded is None:
    st.stop()

try:
    df = prepare(load_file(uploaded))
except Exception as e:
    st.error(f"Could not process file: {e}")
    st.stop()

rows = []
for _,r in df.iterrows():
    text = r["feedback"]
    rows.append({
        "source_type": r["source_type"],
        "respondent_id": r["respondent_id"],
        "feedback": text,
        "primary_theme": primary_theme(text),
        "themes_found": ", ".join(themes_found(text)),
        "intent": classify(text, INTENT),
        "behaviour": classify(text, BEHAVIOUR),
        "segment": classify(text, SEGMENT)
    })

result = pd.DataFrame(rows)

st.success(f"Successfully loaded {len(result)} research records.")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total Records", len(result))
c2.metric("Survey", int(result["source_type"].astype(str).str.lower().str.contains("survey").sum()))
c3.metric("Interviews", int(result["source_type"].astype(str).str.lower().str.contains("interview").sum()))
c4.metric("Other", len(result)-int(result["source_type"].astype(str).str.lower().str.contains("survey").sum())-int(result["source_type"].astype(str).str.lower().str.contains("interview").sum()))

st.divider()

st.header("1. Discovery Themes")
themes = result["primary_theme"].value_counts().rename_axis("Theme").reset_index(name="Records")
themes["Share %"] = (themes["Records"]/len(result)*100).round(1)
themes["Impact"] = themes["Theme"].map(IMPACT).fillna(2)
themes["Opportunity Score"] = themes["Records"] * themes["Impact"]
themes["Priority"] = themes["Opportunity Score"].apply(lambda x: "Very High" if x >= 25 else ("High" if x >= 10 else "Medium"))
st.dataframe(themes[["Theme","Records","Share %","Opportunity Score","Priority"]], use_container_width=True, hide_index=True)

st.header("2. Purchase Intent")
intent = result["intent"].value_counts().rename_axis("Intent").reset_index(name="Records")
intent["Share %"] = (intent["Records"]/len(result)*100).round(1)
st.dataframe(intent, use_container_width=True, hide_index=True)

st.header("3. Purchase Behaviour")
beh = result["behaviour"].value_counts().rename_axis("Behaviour").reset_index(name="Records")
beh["Share %"] = (beh["Records"]/len(result)*100).round(1)
st.dataframe(beh, use_container_width=True, hide_index=True)

st.header("4. User Segments")
seg = result["segment"].value_counts().rename_axis("Segment").reset_index(name="Records")
seg["Share %"] = (seg["Records"]/len(result)*100).round(1)
st.dataframe(seg, use_container_width=True, hide_index=True)

st.header("5. Evidence")
theme_choice = st.selectbox("Select a theme", themes["Theme"].tolist())
evidence = result[result["primary_theme"] == theme_choice][["source_type","respondent_id","feedback","intent","behaviour"]]
st.dataframe(evidence, use_container_width=True, hide_index=True)

st.header("6. Priority Opportunity Areas")
for _,r in themes.sort_values("Opportunity Score",ascending=False).head(5).iterrows():
    st.markdown(f"**{r['Priority']} — {r['Theme']}**: {int(r['Records'])} record(s), {r['Share %']}% of records. Opportunity score: **{int(r['Opportunity Score'])}**.")

st.header("7. Research Questions")
questions = [
    "Why do high-intent wishlist shoppers postpone purchase after saving an item?",
    "How strongly does waiting for a discount affect wishlist-to-purchase conversion?",
    "What information is missing when users hesitate because of fit, size or quality?",
    "How often does competitor comparison cause wishlist purchase leakage?",
    "Which signals would give shoppers enough confidence to purchase now?",
    "Does a generic reminder create action, or is a contextual trigger required?"
]
for q in questions:
    st.markdown(f"- {q}")

st.header("8. Record-Level Analysis")
st.dataframe(result, use_container_width=True, hide_index=True)

st.download_button(
    "⬇️ Download Analyzed CSV",
    result.to_csv(index=False).encode("utf-8"),
    "Nykaa_AI_Discovery_Analysis.csv",
    "text/csv"
)

st.caption("Prototype note: labels use transparent keyword/rule-based heuristics. Validate conclusions against the original survey/interview evidence.")
