import io
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from google_play_scraper import search, reviews, Sort


DATABASE_PATH = Path("competitor_intelligence.db")

REVIEW_COLUMNS = [
    "app_id",
    "app_name",
    "review_id",
    "review_text",
    "rating",
    "sentiment",
    "review_date",
    "thumbs_up",
]

SUMMARY_COLUMNS = [
    "app_id",
    "app_name",
    "developer",
    "rating",
    "reviews_collected",
    "positive",
    "neutral",
    "negative",
]


# 1. Search Google Play applications

def search_apps(keyword, country="us", language="en"):
    keyword = keyword.strip()

    if not keyword:
        return []

    results = search(
        keyword,
        lang=language,
        country=country,
        n_hits=15,
    )

    unique_apps = []
    seen_ids = set()

    for app in results:
        app_id = app.get("appId")

        if not app_id or app_id in seen_ids:
            continue

        seen_ids.add(app_id)

        unique_apps.append({
            "appId": app_id,
            "title": app.get("title", "Unknown"),
            "developer": app.get("developer", "Unknown"),
            "score": app.get("score") or 0,
            "icon": app.get("icon"),
        })

    return unique_apps


# 2. Clean customer feedback

def clean_review_text(text):
    if not isinstance(text, str):
        return ""

    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# 3. Rating-based sentiment segmentation

def classify_sentiment(rating):
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return "Neutral"

    if rating >= 4:
        return "Positive"

    if rating == 3:
        return "Neutral"

    return "Negative"


# 4. Collect reviews for one application

def collect_app_reviews(
    app,
    review_count=200,
    country="us",
    language="en",
):
    collected = []
    continuation_token = None
    seen_review_ids = set()

    while len(collected) < review_count:
        remaining = review_count - len(collected)
        batch_size = min(100, remaining)

        batch, continuation_token = reviews(
            app["appId"],
            lang=language,
            country=country,
            sort=Sort.NEWEST,
            count=batch_size,
            continuation_token=continuation_token,
        )

        if not batch:
            break

        for review in batch:
            review_id = review.get("reviewId")

            if not review_id or review_id in seen_review_ids:
                continue

            seen_review_ids.add(review_id)

            review_text = clean_review_text(
                review.get("content", "")
            )

            if not review_text:
                continue

            review_date = review.get("at")

            if isinstance(review_date, datetime):
                review_date = review_date.isoformat()
            else:
                review_date = None

            rating = review.get("score", 0)

            collected.append({
                "app_id": app["appId"],
                "app_name": app["title"],
                "review_id": review_id,
                "review_text": review_text,
                "rating": rating,
                "sentiment": classify_sentiment(rating),
                "review_date": review_date,
                "thumbs_up": review.get("thumbsUpCount", 0),
            })

            if len(collected) >= review_count:
                break

        if continuation_token is None:
            break

    return collected


# 5. Create relational SQLite database

def initialize_database():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS apps (
                app_id TEXT PRIMARY KEY,
                app_name TEXT NOT NULL,
                developer TEXT,
                rating REAL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id TEXT PRIMARY KEY,
                app_id TEXT NOT NULL,
                review_text TEXT,
                rating INTEGER,
                sentiment TEXT,
                review_date TEXT,
                thumbs_up INTEGER,
                FOREIGN KEY (app_id)
                    REFERENCES apps(app_id)
            )
        """)

        connection.commit()


# 6. Save results into SQLite

def save_to_database(summary, reviews_df):
    initialize_database()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        for _, app in summary.iterrows():
            connection.execute("""
                INSERT INTO apps (
                    app_id, app_name, developer, rating
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(app_id) DO UPDATE SET
                    app_name = excluded.app_name,
                    developer = excluded.developer,
                    rating = excluded.rating
            """, (
                app["app_id"],
                app["app_name"],
                app["developer"],
                float(app["rating"]),
            ))

        for _, review in reviews_df.iterrows():
            connection.execute("""
                INSERT INTO reviews (
                    review_id, app_id, review_text,
                    rating, sentiment, review_date,
                    thumbs_up
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(review_id) DO UPDATE SET
                    review_text = excluded.review_text,
                    rating = excluded.rating,
                    sentiment = excluded.sentiment,
                    review_date = excluded.review_date,
                    thumbs_up = excluded.thumbs_up
            """, (
                review["review_id"],
                review["app_id"],
                review["review_text"],
                int(review["rating"]),
                review["sentiment"],
                review["review_date"],
                int(review["thumbs_up"]),
            ))

        connection.commit()


# 7. Analyze selected competitors

def analyze_competitors(
    selected_apps,
    review_count=200,
    country="us",
    language="en",
):
    if not 2 <= len(selected_apps) <= 4:
        raise ValueError(
            "Please select between 2 and 4 applications."
        )

    if not 150 <= review_count <= 300:
        raise ValueError(
            "Review count must be between 150 and 300."
        )

    all_reviews = []
    summary_rows = []

    for app in selected_apps:
        app_reviews = collect_app_reviews(
            app,
            review_count=review_count,
            country=country,
            language=language,
        )

        all_reviews.extend(app_reviews)

        positive = sum(
            r["sentiment"] == "Positive"
            for r in app_reviews
        )

        neutral = sum(
            r["sentiment"] == "Neutral"
            for r in app_reviews
        )

        negative = sum(
            r["sentiment"] == "Negative"
            for r in app_reviews
        )

        summary_rows.append({
            "app_id": app["appId"],
            "app_name": app["title"],
            "developer": app["developer"],
            "rating": app["score"],
            "reviews_collected": len(app_reviews),
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
        })

    summary_df = pd.DataFrame(
        summary_rows,
        columns=SUMMARY_COLUMNS,
    )

    reviews_df = pd.DataFrame(
        all_reviews,
        columns=REVIEW_COLUMNS,
    )

    save_to_database(summary_df, reviews_df)

    return {
        "summary": summary_df,
        "reviews": reviews_df,
    }


# 8. Generate multi-sheet Excel report

def create_excel_report(summary, reviews_df):
    output = io.BytesIO()

    sentiment_summary = (
        reviews_df.groupby(
            ["app_name", "sentiment"]
        )
        .size()
        .reset_index(name="count")
        if not reviews_df.empty
        else pd.DataFrame(
            columns=["app_name", "sentiment", "count"]
        )
    )

    negative_reviews = reviews_df[
        reviews_df["sentiment"] == "Negative"
    ]

    with pd.ExcelWriter(
        output,
        engine="openpyxl",
    ) as writer:
        summary.to_excel(
            writer,
            sheet_name="Competitor Summary",
            index=False,
        )

        reviews_df.to_excel(
            writer,
            sheet_name="All Reviews",
            index=False,
        )

        sentiment_summary.to_excel(
            writer,
            sheet_name="Sentiment Analysis",
            index=False,
        )

        negative_reviews.to_excel(
            writer,
            sheet_name="Negative Feedback",
            index=False,
        )

        for worksheet in writer.book.worksheets:
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions

            for column in worksheet.columns:
                column_letter = column[0].column_letter

                max_length = max(
                    len(str(cell.value or ""))
                    for cell in column
                )

                worksheet.column_dimensions[
                    column_letter
                ].width = min(max_length + 3, 55)

    output.seek(0)
    return output.getvalue()