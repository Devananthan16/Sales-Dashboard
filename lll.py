import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Dashboard – Cleaned Dataset")


@st.cache_data
def load_data():
    df = pd.read_excel("cleaned_data.xlsx")
    df = df.drop_duplicates()
    df = df[df["Product Amount with GST"].notna() & (df["Product Amount with GST"] > 0)]
    df["Sales Date"] = pd.to_datetime(df["Sales Date"], errors="coerce")
    df["Lead Registered Time"] = pd.to_datetime(df["Lead Registered Time"], errors="coerce")
    df["Payment Status"] = df["Payment Status"].str.lower().str.strip()
    df["Source"] = df["Source"].astype(str).str.title().str.strip()
    return df

df = load_data()

st.sidebar.header("🔍 Filter Options")

status_filter = st.sidebar.multiselect(
    "Select Payment Status:", options=df["Payment Status"].unique(), default=["paid"]
)
source_filter = st.sidebar.multiselect(
    "Select Source:", options=df["Source"].unique(), default=df["Source"].unique()
)
date_range = st.sidebar.date_input(
    "Select Date Range:",
    [df["Sales Date"].min(), df["Sales Date"].max()]
)

df_filtered = df[
    (df["Payment Status"].isin(status_filter))
    & (df["Source"].isin(source_filter))
    & (df["Sales Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]


col1, col2, col3, col4 = st.columns(4)

total_sales = df_filtered[df_filtered["Payment Status"] == "paid"]["Product Amount with GST"].sum()
total_orders = df_filtered[df_filtered["Payment Status"] == "paid"].shape[0]
refunds = df_filtered[df_filtered["Payment Status"] == "refund"]["Product Amount with GST"].sum()
initiated = df_filtered[df_filtered["Payment Status"] == "initiated"].shape[0]
aov = total_sales / total_orders if total_orders > 0 else 0
conversion_rate = (total_orders / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0

col1.metric("Total Sales (₹)", f"{total_sales:,.2f}")
col2.metric("Paid Orders", total_orders)
col3.metric("Refund Amount (₹)", f"{refunds:,.2f}")
col4.metric("Average Order Value (₹)", f"{aov:,.2f}")

st.markdown(f"**💡 Conversion Rate:** {conversion_rate:.2f}%")


st.markdown("### 🏷️ Top 10 Products by Sales")
top_products = (
    df_filtered[df_filtered["Payment Status"] == "paid"]
    .groupby("Product Code")["Product Amount with GST"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
fig1 = px.bar(top_products, x="Product Code", y="Product Amount with GST", text_auto=True)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("### 📅 Daily Sales Trend")
daily_sales = (
    df_filtered[df_filtered["Payment Status"] == "paid"]
    .groupby("Sales Date")["Product Amount with GST"]
    .sum()
    .reset_index()
)
fig2 = px.line(daily_sales, x="Sales Date", y="Product Amount with GST", markers=True)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("### 🌐 Sales by Source")
source_sales = (
    df_filtered[df_filtered["Payment Status"] == "paid"]
    .groupby("Source")["Product Amount with GST"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
fig3 = px.bar(source_sales, x="Source", y="Product Amount with GST", text_auto=True)
st.plotly_chart(fig3, use_container_width=True)


st.markdown("## 📈 Automated Sales Insights")

if total_sales > 0:
    st.success(f"✅ Total sales generated: ₹{total_sales:,.2f} with {total_orders} paid orders.")
else:
    st.warning("No paid transactions found for the selected filters.")

if conversion_rate < 50:
    st.info("💡 Conversion rate is below 50% — consider follow-up strategies for initiated users.")
else:
    st.success("🔥 Great! High conversion rate observed.")

if refunds > 0:
    st.error(f"⚠️ Refunds recorded: ₹{refunds:,.2f}. Investigate reasons for returns or failed transactions.")

# Top-selling product
if not top_products.empty:
    top_product = top_products.iloc[0]["Product Code"]
    top_value = top_products.iloc[0]["Product Amount with GST"]
    st.markdown(f"🏆 **Top Product:** {top_product} with total sales of ₹{top_value:,.2f}")
else:
    st.info("No top-selling product data available.")

# Source performance
if not source_sales.empty:
    best_source = source_sales.iloc[0]["Source"]
    st.markdown(f"🚀 **Best Performing Source:** {best_source}")
else:
    st.info("No source data found.")


with st.expander("📄 View Filtered Data"):
    st.dataframe(df_filtered)


csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Filtered Data as CSV", csv, "filtered_sales_data.csv", "text/csv")
