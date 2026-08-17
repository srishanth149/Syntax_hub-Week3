import streamlit as st
import pandas as pd
import json

from scraper import (
    scrape_source,
    scrape_all_sources,
    filter_headlines
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Headline Scraper",
    page_icon="📰",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.header {
    padding: 25px;
    border-radius: 15px;
    background: linear-gradient(
        135deg,
        #1f2937,
        #374151
    );
    color: white;
    margin-bottom: 25px;
}

.header h1 {
    margin-bottom: 5px;
}

.header p {
    color: #d1d5db;
}

.card {
    padding: 20px;
    border-radius: 12px;
    background: white;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

.card h3 {
    margin-top: 0;
}

.card a {
    text-decoration: none;
    font-weight: bold;
}

.time {
    color: #6b7280;
    font-size: 14px;
}

.source {
    color: #2563eb;
    font-size: 14px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="header">

<h1>📰 Web Scraper for Headlines</h1>

<p>
Scrape, search and download the latest headlines
from the web.
</p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Scraper Settings")

source = st.sidebar.selectbox(
    "News Source",
    [
        "All Sources",
        "Hacker News",
        "The Guardian",
        "DW News",
        "Al Jazeera"
    ]
)

keyword = st.sidebar.text_input(
    "🔎 Search Keyword",
    placeholder="Example: AI"
)

scrape_button = st.sidebar.button(
    "🔄 Scrape Headlines",
    use_container_width=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "articles" not in st.session_state:
    st.session_state.articles = []


# =========================================================
# SCRAPE BUTTON
# =========================================================

if scrape_button:

    with st.spinner(
        "Fetching latest headlines..."
    ):

        try:

            if source == "All Sources":

                articles = scrape_all_sources()

            else:

                articles = scrape_source(source)

            articles = filter_headlines(
                articles,
                keyword
            )

            st.session_state.articles = articles

            if articles:

                st.success(
                    f"{len(articles)} headlines found!"
                )

            else:

                st.warning(
                    "No headlines found."
                )

        except Exception as e:

            st.error(
                f"Scraping failed: {e}"
            )


# =========================================================
# DATA
# =========================================================

articles = st.session_state.articles


# =========================================================
# STATISTICS
# =========================================================

if articles:

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📰 Headlines",
            len(articles)
        )

    with col2:
        st.metric(
            "🌐 Source",
            source
        )

    with col3:
        st.metric(
            "🔎 Filter",
            keyword if keyword else "All"
        )


    st.markdown("---")


    # =====================================================
    # HEADLINES
    # =====================================================

    st.subheader(
        "Latest Headlines"
    )

    for i, article in enumerate(
        articles,
        start=1
    ):

        st.markdown(
            f"""
            <div class="card">

            <h3>
            {i}. {article["title"]}
            </h3>

            <p class="source">
            🌐 {article["source"]}
            </p>

            <p class="time">
            🕒 {article["time"]}
            </p>

            <a href="{article["url"]}"
               target="_blank">
            🔗 Read Article →
            </a>

            </div>
            """,
            unsafe_allow_html=True
        )


    # =====================================================
    # DOWNLOAD SECTION
    # =====================================================

    st.markdown("---")

    st.subheader(
        "💾 Download Data"
    )

    col1, col2 = st.columns(2)


    # -----------------------------------------------------
    # CSV
    # -----------------------------------------------------

    with col1:

        df = pd.DataFrame(
            articles
        )

        csv_data = df.to_csv(
            index=False
        )

        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="headlines.csv",
            mime="text/csv",
            use_container_width=True
        )


    # -----------------------------------------------------
    # JSON
    # -----------------------------------------------------

    with col2:

        json_data = json.dumps(
            articles,
            indent=4,
            ensure_ascii=False
        )

        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name="headlines.json",
            mime="application/json",
            use_container_width=True
        )


# =========================================================
# INITIAL SCREEN
# =========================================================

else:

    st.info(
        "👈 Select a news source and click "
        "**Scrape Headlines** to begin."
    )

    st.markdown("""
    ### How it works

    1. Select a news source.
    2. Enter an optional keyword.
    3. Click **Scrape Headlines**.
    4. The application fetches the webpage.
    5. BeautifulSoup extracts the headlines.
    6. Results are displayed here.
    7. Download the results as CSV or JSON.
    """)