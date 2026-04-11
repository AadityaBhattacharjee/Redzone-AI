# SF Fire Intelligence Dashboard

A production-ready Streamlit dashboard that connects to Databricks with the Databricks SQL Connector, reads Gold-layer tables through SQL, and presents a dark black-and-red command center for fire risk analysis.

## Project Structure

```text
project_root/
│
├── app.py
├── db_connect.py
├── data_loader.py
├── components/
│   ├── overview.py
│   ├── district.py
│   ├── compliance.py
│   ├── response.py
│   ├── inspection.py
│   ├── ml_predictor.py
├── utils/
│   ├── filters.py
├── requirements.txt
├── .env
└── README.md
```

## Features

- Databricks SQL API connectivity through `databricks-sql-connector`
- Cached Gold-table loading with `st.cache_data`
- Global filters for risk category, district, and minimum risk score
- Dark professional UI with red accent styling
- Overview KPIs, charting, map, and top-risk table
- District, compliance, response, and inspection tabs
- Local rule-based ML predictor UI plus confusion-matrix visualization

## Databricks Tables Queried

- `sf_fire_gold.property_risk_master_v2`
- `sf_fire_gold.district_risk_summary`
- `sf_fire_gold.compliance_tracking`
- `sf_fire_gold.response_optimization`
- `sf_fire_gold.inspection_effectiveness`
- `sf_fire_gold.ml_risk_predictions`

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Update `.env` with your Databricks SQL warehouse or all-purpose compute credentials:

```env
DATABRICKS_SERVER_HOSTNAME=YOUR_HOST
DATABRICKS_HTTP_PATH=YOUR_HTTP_PATH
DATABRICKS_TOKEN=YOUR_TOKEN
```

4. Start the app:

```bash
streamlit run app.py
```

## How To Get Databricks Credentials

1. Open Databricks.
2. Go to your SQL Warehouse or compatible compute connection details.
3. Copy:
   - `Server Hostname`
   - `HTTP Path`
4. Create or use a personal access token from Databricks user settings.
5. Paste those values into `.env`.

The Databricks SQL Connector pattern used in this project follows the official Databricks documentation:
[Databricks SQL Connector for Python](https://docs.databricks.com/aws/en/dev-tools/python-sql-connector)

## Notes

- Queries are capped with `LIMIT 10000` for responsive local loading.
- The local predictor is intentionally rule-based because the Spark model is not executed in Streamlit.
- If the Gold schema uses slightly different column names, the loader normalizes common aliases such as `risk_band -> risk_category`.
