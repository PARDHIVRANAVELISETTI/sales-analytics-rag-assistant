# sales-analytics-rag-assistant
RAG assistant that answers questions on revenue, products, customers &amp; trends from sales data and business documents, built with Python, Pandas, SQL, LangChain, Gemini and FAISS.

Topics: rag, langchain, gemini, faiss, sales-analytics, pandas, sql, power-bi, streamlit, google-colab, llm, data-analytics

Model names: they are set at the top of rag_core.py (gemini-2.5-flash for answers and gemini-embedding-001 for embeddings). If Google retires one, copy a current name from AI Studio.

Accuracy limits: the assistant answers from KPI summaries plus sample rows. Very custom aggregations can be approximate, so use the SQL cells when you need exact numbers.

Power BI: I can't build the .pbix file here. Import the exported CSVs and make a card for total revenue, a line chart by month, and bar charts by product, region and customer
