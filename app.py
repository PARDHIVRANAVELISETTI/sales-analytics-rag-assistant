"""Streamlit UI: upload sales data + business docs, then chat with them."""
import os
import streamlit as st
from rag_core import (load_sales_file, prepare_sales_df, load_business_doc,
                      build_index, ask)

st.set_page_config(page_title="Sales Analytics RAG Assistant", page_icon="📊", layout="wide")
st.title("📊 AI-Powered Sales Analytics RAG Assistant")
st.caption("Upload sales data and business documents, then ask about revenue, products, customers and trends.")

with st.sidebar:
    st.header("1. Setup")
    api_key = st.text_input("Gemini API key", type="password",
                            value=os.environ.get("GOOGLE_API_KEY", ""),
                            help="Free key: https://aistudio.google.com/apikey")
    sales_file = st.file_uploader("Sales data (CSV / Excel)", type=["csv", "xlsx", "xls"])
    doc_files = st.file_uploader("Business documents (PDF / TXT / MD)",
                                 type=["pdf", "txt", "md"], accept_multiple_files=True)
    top_k = st.slider("Chunks retrieved (k)", 3, 12, 6)
    build = st.button("Build knowledge base", type="primary")

if build:
    if not api_key or not sales_file:
        st.sidebar.error("Provide an API key and a sales file.")
    else:
        try:
            with st.spinner("Cleaning data, embedding and indexing..."):
                df = prepare_sales_df(load_sales_file(sales_file.name, sales_file))
                extra = [d for f in doc_files for d in load_business_doc(f.name, f)]
                store, n = build_index(df, extra, api_key)
            st.session_state.update(df=df, store=store, messages=[], api_key=api_key)
            st.sidebar.success(f"Indexed {n} chunks from {len(df):,} rows.")
        except Exception as e:
            st.sidebar.error(f"Failed: {e}")

if "store" not in st.session_state:
    st.info("👈 Add your API key, upload files and click **Build knowledge base**.")
    st.stop()

df = st.session_state["df"]
c1, c2, c3 = st.columns(3)
c1.metric("Total revenue", f"{df['Revenue'].sum():,.0f}")
c2.metric("Orders", f"{len(df):,}")
c3.metric("Avg order value", f"{df['Revenue'].mean():,.0f}")
if "Month" in df:
    st.bar_chart(df.groupby("Month")["Revenue"].sum(), height=220)

st.subheader("💬 Ask your data")
for m in st.session_state["messages"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if q := st.chat_input("e.g. Which product earned the most revenue last quarter?"):
    st.session_state["messages"].append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer, hits = ask(q, st.session_state["store"], st.session_state["api_key"], top_k)
            except Exception as e:
                answer, hits = f"Error: {e}", []
        st.markdown(answer)
        if hits:
            with st.expander("Sources used"):
                for h in hits:
                    st.markdown(f"**{h.metadata.get('source')}**")
                    st.code(h.page_content[:600])
    st.session_state["messages"].append({"role": "assistant", "content": answer})
