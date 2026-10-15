# Market Intelligence & Competitor Analysis

## Project Overview

Market Intelligence & Competitor Analysis is a Python-based web application designed to help product teams research competing mobile applications on the Google Play Store.

The application collects real customer reviews, analyzes user sentiment, compares competitors, and uses Google Gemini AI to identify customer pain points and potential market opportunities.

The goal is to support data-driven decisions before developing and launching a new mobile application.

## Key Features

### 1. Dynamic App Discovery
- Search Google Play by application name or keyword.
- Display matching applications.
- View app names, developers, ratings, and icons.

### 2. Competitor Selection
- Select 2 to 4 competing applications.
- Choose a target of 150 to 300 reviews per application.
- Collect recent customer feedback.

### 3. Data Processing and Sentiment Analysis
- Clean and normalize review text.
- Extract review dates and star ratings.
- Classify reviews using rating-based sentiment:
  - Positive: 4–5 stars
  - Neutral: 3 stars
  - Negative: 1–2 stars

### 4. SQLite Database
- Store application information and customer reviews.
- Use relational tables with primary and foreign keys.
- Support structured data storage and querying.

### 5. Interactive Dashboard
- Built using Streamlit.
- Display competitor ratings.
- Compare customer sentiment.
- Explore collected customer reviews.
- Visualize results using Plotly.

### 6. AI-Powered Market Gap Analysis
- Integrate Google Gemini AI.
- Analyze 1-star and 2-star customer reviews.
- Identify recurring complaints.
- Highlight customer feature requests.
- Generate strategic recommendations for new applications.

### 7. Excel Reporting
Generate a downloadable Excel report containing:
- Competitor Summary
- All Reviews
- Sentiment Analysis
- Negative Feedback

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web interface |
| google-play-scraper | Google Play data collection |
| pandas | Data processing |
| Plotly | Interactive visualizations |
| SQLite | Relational database |
| openpyxl | Excel reporting |
| Google Gemini API | AI market insights |

## Project Structure

text
Market_Intelligence_App/
|
|-- app.py
|-- market_engine.py
|-- market_ai.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|
|-- .streamlit/
|   |-- secrets.toml (local only)
|
|-- competitor_intelligence.db (generated)


## Installation

### 1. Clone the Repository

bash
git clone YOUR_REPOSITORY_URL
cd Market_Intelligence_App


### 2. Create a Virtual Environment

bash
python -m venv .venv


### 3. Activate the Environment

On Windows PowerShell:

powershell
.\.venv\Scripts\Activate.ps1


### 4. Install Dependencies

bash
python -m pip install -r requirements.txt


### 5. Configure Gemini API

Create a file at:

.streamlit/secrets.toml

Add your Gemini API key:

toml
GEMINI_API_KEY = "YOUR_API_KEY"


Never commit this file or expose your API key.

### 6. Run the Application

bash
python -m streamlit run app.py


Open the local URL displayed in the terminal.

## How to Use

1. Enter an application name or market keyword.
2. Click "Search Apps".
3. Select 2 to 4 competing applications.
4. Choose the target number of reviews.
5. Click "Run Competitor Analysis".
6. Explore the charts and customer reviews.
7. Click "Generate AI Recommendations".
8. Download the Excel report.

## Technical Architecture

The application follows a modular architecture:

- *app.py:* Streamlit user interface and dashboard.
- *market_engine.py:* Application discovery, review collection, sentiment classification, SQLite storage, and Excel reporting.
- *market_ai.py:* Gemini API integration and strategic market gap analysis.

### Data Processing Workflow

Google Play Search
→ Competitor Selection
→ Review Collection
→ Text Cleaning
→ Sentiment Classification
→ SQLite Storage
→ Dashboard and Excel Reporting
→ Gemini AI Insights

## Limitations

- Review availability depends on Google Play.
- Some applications may return fewer reviews than requested.
- Sentiment classification is based on star ratings rather than linguistic sentiment analysis.
- Gemini recommendations depend on the supplied customer reviews and API availability.
- The application requires an internet connection for live data collection and AI analysis.

## Security

- API keys are stored in Streamlit secrets.
- Sensitive configuration files are excluded using .gitignore.
- Local database files are excluded from Git tracking.

## Future Improvements

- Multilingual text-based sentiment analysis.
- Historical competitor tracking.
- Additional market comparison metrics.
- Automated recurring competitor reports.
- More advanced complaint clustering.

## Author

Individual Data Analysis Final Project

## License

Developed for educational and demonstration purposes.
```