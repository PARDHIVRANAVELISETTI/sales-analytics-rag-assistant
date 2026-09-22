"""Core RAG logic for the AI-Powered Sales Analytics Assistant."""
import pandas as pd
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# If Google retires a model, pick a current one in https://aistudio.google.com
CHAT_MODEL = "gemini-3.6-flash"
EMBED_MODEL = "models/gemini-embedding-001"
DIMENSIONS = ["Month", "Product", "Category", "Region", "Customer"]


# ---------- 1. Load & clean ----------
def load_sales_file(name, fileobj):
    """Read a CSV or Excel file into a DataFrame."""
    if name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(fileobj)
    return pd.read_csv(fileobj)


def prepare_sales_df(df):
    """Standardise columns: parse dates, add Month, make sure Revenue exists."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    date_col = next((c for c in df.columns if "date" in c.lower()), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df["Month"] = df[date_col].dt.to_period("M").astype(str)
    if "Revenue" not in df.columns:
        if {"Quantity", "Unit_Price"}.issubset(df.columns):
            df["Revenue"] = df["Quantity"] * df["Unit_Price"]
        else:
            raise ValueError("Need a 'Revenue' column, or 'Quantity' and 'Unit_Price'.")
    return df.dropna(subset=["Revenue"])


def load_business_doc(name, fileobj):
    """Read a PDF / TXT / MD business document into a Document."""
    if name.lower().endswith(".pdf"):
        text = "\n".join((p.extract_text() or "") for p in PdfReader(fileobj).pages)
    else:
        text = fileobj.read().decode("utf-8", errors="ignore")
    return [Document(page_content=text, metadata={"source": name})]


# ---------- 2. Turn tables into searchable text ----------
def sales_to_documents(df):
    docs = []
    total = df["Revenue"].sum()
    kpi = [f"OVERALL KPIs: total revenue = {total:,.2f}; rows/orders = {len(df)}; "
           f"average order value = {df['Revenue'].mean():,.2f}."]
    if "Month" in df:
        kpi.append(f"Data covers {df['Month'].min()} to {df['Month'].max()}.")
    kpi.append("Columns: " + ", ".join(df.columns))
    docs.append(Document(page_content=" ".join(kpi), metadata={"source": "sales_summary:kpis"}))

    for dim in DIMENSIONS:
        if dim not in df.columns:
            continue
        g = df.groupby(dim)["Revenue"].agg(["sum", "count"])
        if dim == "Month":
            g = g.sort_index()
            g["mom_%"] = (g["sum"].pct_change() * 100).round(1)
        else:
            g = g.sort_values("sum", ascending=False).head(40)
        lines = [f"REVENUE BY {dim.upper()}:"]
        for k, r in g.iterrows():
            extra = f", MoM growth={r['mom_%']}%" if "mom_%" in g.columns and pd.notna(r["mom_%"]) else ""
            lines.append(f"{k}: revenue={r['sum']:,.2f}, orders={int(r['count'])}{extra}")
        docs.append(Document(page_content="\n".join(lines), metadata={"source": f"sales_summary:{dim}"}))

    if {"Month", "Category"}.issubset(df.columns):
        pv = df.pivot_table(index="Month", columns="Category", values="Revenue", aggfunc="sum").round(0)
        docs.append(Document(page_content="MONTHLY REVENUE BY CATEGORY:\n" + pv.to_string(),
                             metadata={"source": "sales_summary:month_x_category"}))

    for i in range(0, min(len(df), 200), 20):  # a few raw rows for detail questions
        docs.append(Document(page_content="SAMPLE ORDER ROWS:\n" + df.iloc[i:i + 20].to_csv(index=False),
                             metadata={"source": f"sales_rows:{i}-{i + 19}"}))
    return docs


# ---------- 3. Index & answer ----------
def build_index(sales_df, business_docs, api_key):
    docs = sales_to_documents(sales_df) + list(business_docs)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL, google_api_key=api_key)
    return FAISS.from_documents(chunks, embeddings), len(chunks)


PROMPT = """You are a senior sales analyst. Answer the question using ONLY the context below.
Quote exact numbers, name products/customers/regions, and describe trends clearly.
If the context does not contain the answer, say so instead of guessing.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""


def _as_text(content):
    if isinstance(content, list):
        return "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in content)
    return content


def ask(question, store, api_key, k=6):
    hits = store.similarity_search(question, k=k)
    context = "\n\n---\n\n".join(d.page_content for d in hits)
    llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, google_api_key=api_key, temperature=0.2)
    reply = llm.invoke(PROMPT.format(context=context, question=question))
    return _as_text(reply.content), hits
