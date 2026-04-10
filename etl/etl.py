# ============================================================
# ETL Pipeline: Life Expectancy, GDP & Working Hours
# ============================================================

import wbgapi as wb
import pandas as pd
from sqlalchemy import create_engine


# ── Configuration ────────────────────────────────────────────

TIME_RANGE = range(2014, 2024)  # Covers 2014–2023 (2024 is exclusive)
DB_URL = "postgresql://postgres:mysecretpassword@db:5432/postgres"
# ⚠️  EDUCATIONAL USE ONLY — use environment variables in production


# ── Extract ──────────────────────────────────────────────────

life_expectancy = wb.data.DataFrame(
    "SP.DYN.LE00.IN",
    economy="all",
    time=TIME_RANGE,
    labels=True,
)

gdp = wb.data.DataFrame(
    "NY.GDP.PCAP.CD",
    economy="all",
    time=TIME_RANGE,
    labels=True,
)

oecd_hours = pd.read_csv("/app/oecd_hours_transformed.csv")


# ── Transform ─────────────────────────────────────────────────

def unpivot_wb(df: pd.DataFrame, value_name: str) -> pd.DataFrame:
    """Unpivot a World Bank wide DataFrame and clean the YEAR column."""
    year_cols = [c for c in df.columns if c != "Country"]
    df = df.melt(id_vars="Country", value_vars=year_cols, var_name="YEAR", value_name=value_name)
    df["YEAR"] = df["YEAR"].str.replace("YR", "", regex=False).astype(int)
    return df


life_expectancy = unpivot_wb(life_expectancy, "LIFE_EXPECTANCY")
gdp = unpivot_wb(gdp, "GDP")


# ── Merge ─────────────────────────────────────────────────────

master = (
    life_expectancy
    .merge(oecd_hours, on=["Country", "YEAR"], how="inner")
    .merge(gdp,        on=["Country", "YEAR"], how="inner")
)

# Filter & select
master = (
    master
    .loc[master["Worker status"] == "Total"]
    .loc[master["YEAR"] >= 2013]
    [["Country", "YEAR", "LIFE_EXPECTANCY", "HOURS_YEARLY", "GDP"]]
)

print(master.head())


# ── Load ──────────────────────────────────────────────────────

engine = create_engine(DB_URL)
master.to_sql("master_table", engine, if_exists="replace", index=False)

print("✓ Data loaded to PostgreSQL table 'master_table'")