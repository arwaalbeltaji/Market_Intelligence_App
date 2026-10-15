import streamlit as st
import pandas as pd
import plotly.express as px

from market_engine import (
    search_apps,
    analyze_competitors,
    create_excel_report,
)
from market_ai import generate_market_insights


st.set_page_config(
    page_title="Market Intelligence",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Market Intelligence & Competitor Analysis")
st.caption(
    "Discover competitors, analyze Google Play reviews, "
    "and identify market opportunities using AI."
)

# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "insights" not in st.session_state:
    st.session_state.insights = None


# Sidebar settings
with st.sidebar:
    st.header("⚙️ Analysis Settings")

    country = st.selectbox(
        "Google Play Country",
        ["us", "gb", "sa", "ae", "ps"],
    )

    language = st.selectbox(
        "Review Language",
        ["en", "ar"],
    )

    review_count = st.slider(
        "Reviews per App",
        min_value=150,
        max_value=300,
        value=200,
        step=50,
    )

    st.info("Select 2 to 4 apps for competitor analysis.")


# App discovery
st.header("🔎 Discover Competitors")

keyword = st.text_input(
    "Search Google Play",
    placeholder="e.g. food delivery, fitness tracker",
)

if st.button("Search Apps", type="primary"):
    if not keyword.strip():
        st.warning("Please enter a keyword or app name.")
    else:
        with st.spinner("Searching Google Play..."):
            try:
                st.session_state.search_results = search_apps(
                    keyword,
                    country=country,
                    language=language,
                )
                st.session_state.analysis = None
                st.session_state.insights = None
            except Exception as error:
                st.error(f"Search failed: {error}")


# App selection
selected_apps = []

if st.session_state.search_results:
    st.subheader("Select Competitors")

    for app in st.session_state.search_results:
        col1, col2, col3 = st.columns([1, 5, 2])

        with col1:
            if app.get("icon"):
                st.image(app["icon"], width=70)

        with col2:
            st.write(f"*{app['title']}*")
            st.caption(f"Developer: {app['developer']}")
            st.write(
                f"⭐ Rating: {app.get('score', 0) or 0:.1f}"
            )

        with col3:
            chosen = st.checkbox(
                "Select",
                key=f"select_{app['appId']}",
            )

            if chosen:
                selected_apps.append(app)

        st.divider()

    st.write(f"Selected apps: {len(selected_apps)} / 4")

    if st.button("🚀 Run Competitor Analysis"):
        if not 2 <= len(selected_apps) <= 4:
            st.warning("Please select 2 to 4 apps.")
        else:
            with st.spinner("Collecting and analyzing reviews..."):
                try:
                    st.session_state.analysis = analyze_competitors(
                        selected_apps,
                        review_count=review_count,
                        country=country,
                        language=language,
                    )
                    st.session_state.insights = None
                    st.success("Analysis completed successfully!")
                except Exception as error:
                    st.error(f"Analysis failed: {error}")


# Results dashboard
if st.session_state.analysis is not None:
    results = st.session_state.analysis

    summary = results["summary"]
    reviews = results["reviews"]

    st.header("📈 Competitor Analysis Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Competitors", len(summary))

    with col2:
        st.metric("Reviews Collected", len(reviews))

    with col3:
        negative_count = len(
            reviews[reviews["sentiment"] == "Negative"]
        )
        st.metric("Negative Reviews", negative_count)

    st.subheader("Competitor Ratings")

    fig_ratings = px.bar(
        summary,
        x="app_name",
        y="rating",
        color="app_name",
        title="Google Play Ratings Comparison",
    )
    st.plotly_chart(fig_ratings, use_container_width=True)

    st.subheader("Customer Sentiment")

    sentiment_counts = (
        reviews.groupby(["app_name", "sentiment"])
        .size()
        .reset_index(name="count")
    )

    fig_sentiment = px.bar(
        sentiment_counts,
        x="app_name",
        y="count",
        color="sentiment",
        barmode="group",
        title="Sentiment Comparison",
    )
    st.plotly_chart(fig_sentiment, use_container_width=True)

    st.subheader("Customer Reviews")
    st.dataframe(reviews, use_container_width=True)

    st.header("🤖 AI Market Gap Insights")

    if st.button("Generate AI Recommendations"):
        with st.spinner("Analyzing market gaps with Gemini..."):
            try:
                st.session_state.insights = (
                    generate_market_insights(reviews)
                )
            except Exception as error:
                st.error(f"AI analysis failed: {error}")

    if st.session_state.insights:
        st.markdown(st.session_state.insights)

    st.header("📥 Download Excel Report")

    excel_data = create_excel_report(
        summary,
        reviews,
    )

    st.download_button(
        label="Download Competitor Report",
        data=excel_data,
        file_name="competitor_analysis.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )