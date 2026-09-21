# 📊 AI-Powered Sales Analytics RAG Assistant

Upload sales data and business documents, then ask natural-language questions about **revenue, products, customers and trends**. Answers are grounded in your data using Retrieval-Augmented Generation (RAG).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PARDHIVRANAVELISETTI/sales-analytics-rag-assistant/blob/main/Sales_Analytics_RAG_Assistant.ipynb)

**Tech stack:** Python · SQL · Pandas · Power BI · LangChain · Google Gemini · FAISS · Streamlit

![Workflow](images/workflow.png)

## ✨ Features
- Upload sales data (CSV / Excel) and business documents (PDF / TXT / MD)
- Pandas cleans the data and builds KPI summaries (by month, product, category, region, customer, MoM growth)
- LangChain splits content into chunks → Gemini embeddings → FAISS vector index
- Ask questions in chat and see the source chunks behind every answer
- SQL (SQLite) exploration and Power BI-ready CSV export in the notebook
- Runs free in Google Colab; optional Streamlit web app

## 🔄 How it works
1. **Ingest** – load sales table + business documents
2. **Prepare** – clean with Pandas, compute aggregated KPI text summaries
3. **Chunk & embed** – LangChain text splitter + `gemini-embedding-001`
4. **Index** – store vectors in FAISS
5. **Retrieve** – top-k chunks most relevant to the question
6. **Generate** – `gemini-2.5-flash` answers using only the retrieved context

## 🚀 Quick start (Google Colab)
1. Get a free key at [Google AI Studio](https://aistudio.google.com/apikey) → **Create API key**.
2. Open `Sales_Analytics_RAG_Assistant.ipynb` in Colab (use the badge above).
4. **Runtime → Run all**. Set `USE_SAMPLE = False` to upload your own files.

## 💻 Run locally
```bash
git clone https://github.com/YOUR_USERNAME/sales-analytics-rag-assistant.git
cd sales-analytics-rag-assistant
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export GOOGLE_API_KEY="your_key"                     # Windows: set GOOGLE_API_KEY=your_key
streamlit run app.py
```

## 📁 Expected data
A CSV/Excel file with a `Revenue` column (or `Quantity` + `Unit_Price`). Optional columns used automatically: `Date`, `Product`, `Category`, `Region`, `Customer`. See `sample_data/sales_data.csv`.

## 💬 Example questions
- Which product generates the most revenue?
- Which region is weakest and what does our strategy document say about it?
- Who are the top 5 customers?
- How is monthly revenue trending?

## 📈 Power BI
The notebook exports `powerbi_sales_clean.csv` and `powerbi_sales_summary.csv`. In Power BI Desktop: **Get data → Text/CSV**, then build cards (total revenue), a line chart (revenue by month), and bar charts (product / region / customer).

## 📂 Structure
```
├── app.py                              # Streamlit UI
├── rag_core.py                         # loading, chunking, embeddings, FAISS, answering
├── Sales_Analytics_RAG_Assistant.ipynb # step-by-step Colab notebook
├── requirements.txt
├── sample_data/                        # demo CSV, business notes, generator script
└── images/workflow.png
```

## ⚠️ Notes & limitations
- Answers come from KPI summaries plus sample rows, so very custom aggregations may be approximate; use the SQL cells for exact figures.
- Model names live at the top of `rag_core.py`; update them if Google retires a model.
- Never commit your API key. Use Colab Secrets or environment variables.

## 🔮 Future work
Text-to-SQL agent, auto-generated charts, forecasting, multi-file comparison, deployment on Streamlit Community Cloud.

## 📄 License
MIT
