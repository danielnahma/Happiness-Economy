# Work & Life — Global Balance Report
### Does working more mean living longer?

> **Bootcamp Final Project** · Data Engineering + Data Analysis  
> Daniel Nahmani · *Analysis direction in collaboration with Batel Bazri*

---

## Research Question

**Does average annual work hours per worker correlate with life expectancy — and which countries have the worst work-life balance despite economic success?**

---

## Live Demo

> 📸 *Screenshot coming soon*

---

## Project Architecture

The project follows a full data pipeline from raw data to interactive dashboard:

```
Extract (World Bank API + OECD CSV)
        ↓
Transform & Load → PostgreSQL (Docker)
        ↓
Analysis → Visualizations & Insights
        ↓
Streamlit App → Dockerized & Deployed
```

The full project flow was designed and documented using draw.io:

![Project Flow](./images/Happiness economy flow.png)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Extraction | Python, `wbgapi` (World Bank API), OECD CSV |
| Transformation | `pandas` |
| Database | PostgreSQL 15 (Docker) |
| Analysis | `pandas`, `seaborn` |
| Dashboard | Streamlit, Plotly |
| Infrastructure | Docker, Docker Compose |

---

## What's Inside the Dashboard

- **KPI Cards** — instant summary: countries, avg work hours, life expectancy, GDP, and Pearson correlation
- **Work Intensity Map** — choropleth world map colored by annual work hours
- **Correlations** — scatterplots for Hours vs Life Expectancy and GDP vs Life Expectancy, with OLS trendlines and a correlation heatmap
- **Trends Over Time** — line charts and a dual-axis view per country or global average
- **Country Rankings** — ranked bar charts for work hours and life expectancy
- **Overworked & Rich** — paradox countries: high GDP, high hours, but below-median life expectancy. Includes a quadrant scatter, data table, and radar profile comparison

---

## How to Run

**Requirements:** Docker Desktop installed and running.

```bash
# 1. Clone the repo
git clone https://github.com/danielnahmani/work-and-life.git
cd work-and-life

# 2. Start everything
docker-compose up --build
```

The sequence is fully automated:
1. PostgreSQL starts and becomes healthy
2. ETL runs and loads data into the database
3. Streamlit app starts automatically

Then open your browser at:
```
http://localhost:8501
```

---

## Data Sources

- **World Bank API** — GDP per capita, Life Expectancy (via `wbgapi`)
- **OECD** — Average annual working hours per worker (`oecd_hours_transformed.csv`)

---

## Project Structure

```
project/
├── docker-compose.yml
├── etl/
│   ├── Dockerfile
│   ├── etl.py
│   └── oecd_hours_transformed.csv
└── app/
    ├── Dockerfile
    └── app.py
```

---

## About

Built as the final project for a Data Analyst Bootcamp.  
The goal was to combine data engineering (ETL pipeline, PostgreSQL, Docker) with data analysis and a production-ready interactive dashboard.

**Daniel Nahmani** — ETL pipeline, database architecture, Docker infrastructure, Streamlit dashboard  
**Batel Bazri** — Analysis direction and research insights


## ⚠️ Security Note
This project was built for educational purposes as part of a Data Analyst Bootcamp.
Database credentials are hardcoded for simplicity only.
In production, always use environment variables (.env) or a secrets manager.
