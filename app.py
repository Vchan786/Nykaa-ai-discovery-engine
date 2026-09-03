import streamlit as st
import pandas as pd
import re
from collections import Counter

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Nykaa Fashion AI Discovery Engine",
    page_icon="🔎",
    layout="wide"
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🔎 Nykaa Fashion")
st.subheader("AI-Powered Discovery Engine")

st.write(
    """
Analyze fashion-shopping feedback to identify:
**user intent, purchase blockers, uncertainty, behaviours,
workarounds, user segments and opportunity areas.**
"""
)

st.divider()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("About this engine")

st.sidebar.write(
    """
This prototype demonstrates how AI-assisted discovery can
move beyond sentiment analysis and identify recurring
problems that may influence Wishlist → Purchase conversion.
"""
)

st.sidebar.info(
    """
Prototype note:
This project uses illustrative/public-style feedback.
It does not use Nykaa Fashion internal customer data.
"""
)

# --------------------------------------------------
# SAMPLE DATA
# --------------------------------------------------

sample_feedback = """
I love this dress and saved it, but I am not sure about the size.
The reviews say it runs small so I will wait before buying.

I added this kurta to my wishlist because I liked the design.
I am waiting for a sale before I purchase it.

The product looks great but I don't know whether the colour
will look the same in real life.

I saved these shoes because I am comparing them with another
pair on Myntra.

I like the jeans but I am confused about which size to order.
I checked YouTube reviews before deciding.

I want this handbag but the price feels high. I will wait
for a discount.

I saved this dress for a wedding. I need to check whether
the material looks premium enough.

The reviews are mixed. Some people say the fit is perfect
and others say it is too tight.

I usually save products I like and come back later.
Sometimes I never buy them.

I want to purchase this top but I need to see how it looks
on someone with a similar body type.

I added this product to compare it with AJIO before buying.

I like the product but I am worried about returns if the size
doesn't fit.

I saved this item because I may need it next month.

The product is beautiful but I am waiting for payday.

I checked Instagram to see how influencers styled this dress.

I like the product but I need more customer photos before
I decide.

I saved this product just so I don't lose it.

I am not sure if the quality is worth the price.

The size chart is confusing and I don't know which size to pick.

I have three dresses saved and I cannot decide which one
is better for the occasion.

I am waiting to see if the price drops.

The reviews helped me decide that the product may not be
right for me.

I want this for a party but I am looking at other options too.

I saved it because it looked nice, but I don't actually
plan to buy it right now.

I need to know whether the fabric is transparent.

The product photos look good but I want to see customer
pictures before purchasing.
"""

# --------------------------------------------------
# INPUT
# --------------------------------------------------

st.header("1. Add User Feedback")

input_mode = st.radio(
    "Choose input",
    ["Use sample feedback", "Paste your own feedback"],
    horizontal=True
)

if input_mode == "Use sample feedback":
    feedback = st.text_area(
        "Feedback dataset",
        sample_feedback,
        height=300
    )
else:
    feedback = st.text_area(
        "Paste reviews / comments / conversations",
        height=300,
        placeholder="Paste multiple feedback items here..."
    )

# --------------------------------------------------
# CLASSIFICATION RULES
# --------------------------------------------------

themes = {
    "Fit & Size Confidence": [
        "size", "fit", "tight", "loose", "body type",
        "size chart", "sizing"
    ],

    "Price Uncertainty": [
        "price", "expensive", "discount", "sale",
        "payday", "price drop", "worth"
    ],

    "Trust & Product Quality": [
        "quality", "premium", "real life", "transparent",
        "fabric", "customer photos", "photos"
    ],

    "Reviews & Social Validation": [
        "reviews", "review", "youtube", "instagram",
        "influencer", "customer"
    ],

    "Alternative Comparison": [
        "compare", "comparison", "myntra", "ajio",
        "other options", "another"
    ],

    "Occasion & Styling": [
        "wedding", "party", "occasion", "styled",
        "styling", "dress"
    ],

    "Bookmarking Behaviour": [
        "don't lose", "come back later",
        "may need", "never buy", "save products"
    ],

    "Return / Exchange Risk": [
        "return", "returns", "exchange",
        "doesn't fit", "refund"
    ]
}

# --------------------------------------------------
# CLASSIFICATION FUNCTION
# --------------------------------------------------

def classify_feedback(text):

    text_lower = text.lower()

    matched_themes = []

    for theme, keywords in themes.items():

        for keyword in keywords:

            if keyword in text_lower:
                matched_themes.append(theme)
                break

    # Intent classification
    genuine_intent_words = [
        "buy", "purchase", "waiting for",
        "decide", "want", "will purchase"
    ]

    bookmark_words = [
        "don't lose", "come back later",
        "never buy", "may need"
    ]

    if any(word in text_lower for word in bookmark_words):
        intent = "Bookmark / Low Intent"

    elif any(word in text_lower for word in genuine_intent_words):
        intent = "Genuine Purchase Intent"

    else:
        intent = "Unclear Intent"

    # Behaviour
    if any(word in text_lower for word in [
        "wait", "waiting", "payday", "later"
    ]):
        behaviour = "Postponing Purchase"

    elif any(word in text_lower for word in [
        "compare", "looking at other"
    ]):
        behaviour = "Comparing Alternatives"

    elif any(word in text_lower for word in [
        "checked", "check", "youtube",
        "instagram", "reviews"
    ]):
        behaviour = "Seeking More Information"

    else:
        behaviour = "Exploring Product"

    # Segment
    if (
        "buy" in text_lower
        or "purchase" in text_lower
        or "decide" in text_lower
    ):
        segment = "High-Intent Shopper"

    elif "save" in text_lower:
        segment = "Exploring Shopper"

    else:
        segment = "Unclear"

    return {
        "themes": matched_themes,
        "intent": intent,
        "behaviour": behaviour,
        "segment": segment
    }


# --------------------------------------------------
# ANALYSE BUTTON
# --------------------------------------------------

if st.button(
    "🔍 Analyze Feedback",
    type="primary",
    use_container_width=True
):

    if not feedback.strip():

        st.error("Please provide feedback before analysing.")

    else:

        # Split feedback into individual items
        items = [
            item.strip()
            for item in re.split(r"\n+", feedback)
            if item.strip()
        ]

        results = []

        for item in items:

            classification = classify_feedback(item)

            results.append({
                "Feedback": item,
                "Intent": classification["intent"],
                "Behaviour": classification["behaviour"],
                "Segment": classification["segment"],
                "Themes": ", ".join(
                    classification["themes"]
                )
            })

        df = pd.DataFrame(results)

        # --------------------------------------------------
        # SUMMARY
        # --------------------------------------------------

        st.divider()

        st.header("2. Discovery Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Feedback Items",
                len(df)
            )

        with col2:
            high_intent = (
                df["Intent"]
                .eq("Genuine Purchase Intent")
                .sum()
            )

            st.metric(
                "Genuine Intent",
                high_intent
            )

        with col3:
            delayed = (
                df["Behaviour"]
                .eq("Postponing Purchase")
                .sum()
            )

            st.metric(
                "Purchase Delays",
                delayed
            )

        with col4:
            segments = df["Segment"].nunique()

            st.metric(
                "Segments",
                segments
            )

        # --------------------------------------------------
        # THEME FREQUENCY
        # --------------------------------------------------

        st.header("3. Opportunity Themes")

        theme_counter = Counter()

        for themes_found in df["Themes"]:

            for theme in themes_found.split(", "):

                if theme.strip():
                    theme_counter[theme] += 1

        theme_data = []

        for theme, count in theme_counter.most_common():

            percentage = (
                count / len(df) * 100
            )

            # Opportunity score
            score = round(
                (count * 2)
                + (
                    delayed * 1.5
                    if "Confidence" in theme
                    or "Price" in theme
                    or "Risk" in theme
                    else delayed
                ),
                1
            )

            theme_data.append({
                "Opportunity Area": theme,
                "Feedback Count": count,
                "Share %": round(percentage, 1),
                "Opportunity Score": score
            })

        theme_df = pd.DataFrame(theme_data)

        if not theme_df.empty:

            st.dataframe(
                theme_df,
                use_container_width=True,
                hide_index=True
            )

            # --------------------------------------------------
            # TOP OPPORTUNITY
            # --------------------------------------------------

            top_opportunity = theme_df.iloc[0][
                "Opportunity Area"
            ]

            st.success(
                f"""
### 🎯 Top Opportunity Area

**{top_opportunity}**

This theme appears frequently in the feedback and
may represent a meaningful opportunity to investigate
for Wishlist → Purchase conversion.
"""
            )

        # --------------------------------------------------
        # SEGMENTS
        # --------------------------------------------------

        st.header("4. User Segments")

        segment_counts = (
            df["Segment"]
            .value_counts()
            .reset_index()
        )

        segment_counts.columns = [
            "Segment",
            "Feedback Count"
        ]

        st.dataframe(
            segment_counts,
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------------------------
        # INTENT
        # --------------------------------------------------

        st.header("5. Wishlist Intent")

        intent_counts = (
            df["Intent"]
            .value_counts()
            .reset_index()
        )

        intent_counts.columns = [
            "Intent Type",
            "Feedback Count"
        ]

        st.dataframe(
            intent_counts,
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------------------------
        # BEHAVIOUR
        # --------------------------------------------------

        st.header("6. Purchase Behaviour")

        behaviour_counts = (
            df["Behaviour"]
            .value_counts()
            .reset_index()
        )

        behaviour_counts.columns = [
            "Behaviour",
            "Feedback Count"
        ]

        st.dataframe(
            behaviour_counts,
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------------------------
        # RESEARCH QUESTIONS
        # --------------------------------------------------

        st.header("7. Research Questions")

        questions = [
            "Why do high-intent users remain uncertain about fit and size?",
            "What information do users seek before purchasing a wishlisted item?",
            "How often do users compare wishlisted products with Myntra/AJIO?",
            "When does wishlist usage represent genuine intent versus bookmarking?",
            "How much does price uncertainty contribute to purchase postponement?",
            "How do customer reviews and social validation influence the final decision?",
            "What workarounds do users use to reduce purchase uncertainty?"
        ]

        for question in questions:
            st.write("🔹", question)

        # --------------------------------------------------
        # RAW ANALYSIS
        # --------------------------------------------------

        st.header("8. Feedback-Level Analysis")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # --------------------------------------------------
        # DOWNLOAD
        # --------------------------------------------------

        csv = df.to_csv(index=False)

        st.download_button(
            "⬇️ Download Analysis CSV",
            csv,
            "nykaa_discovery_analysis.csv",
            "text/csv"
        )

st.divider()

st.caption(
    "Nykaa Fashion Product Management Graduation Project | "
    "Discovery Engine Prototype | Illustrative/Public-style data"
)
