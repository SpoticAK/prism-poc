import streamlit as st
import pandas as pd

# Load data from your exact CSV files
product_df = pd.read_csv("products.csv")
supplier_df = pd.read_csv("suppliers.csv")

# Product scoring function based on your columns
def score_product(row):
    score = 0
    # Price scoring
    if 200 <= row['Price'] <= 350:
        score += 4
    elif 175 <= row['Price'] <= 199 or 351 <= row['Price'] <= 400:
        score += 2

    # Reviews scoring using 'Review no'
    if row['Review no'] >= 100:
        score += 4
    elif 50 <= row['Review no'] < 100:
        score += 2

    # Review Rating scoring
    if row['Review Rating'] >= 4.2:
        score += 3
    elif 4.0 <= row['Review Rating'] < 4.2:
        score += 1

    # Weight scoring (in grams)
    if row['Weight'] <= 500:
        score += 4
    elif 500 < row['Weight'] <= 700:
        score += 2

    # Listing Quality scoring
    listing_quality = str(row['Listing Quality']).strip().lower()
    if listing_quality == 'good':
        score += 2
    elif listing_quality == 'average':
        score += 1

    return score

# Supplier scoring function based on your columns
def score_supplier(row):
    score = 0
    # Region scoring
    region = str(row['Region']).lower()
    if 'delhi' in region:
        score += 4

    # Verified status scoring
    verified = str(row['Verified']).strip().lower()
    if verified == 'yes':
        score += 4

    # MOQ scoring, handle NA gracefully
    try:
        moq = int(row['MOQ'])
        if moq <= 100:
            score += 2
        elif moq <= 500:
            score += 1
    except:
        pass  # Ignore non-integer or NA MOQ

    return score

# Add product scores
product_df['Product Score'] = product_df.apply(score_product, axis=1)

# Find top scoring supplier per product
def find_top_supplier(product_name):
    matches = supplier_df[supplier_df['Product Name'] == product_name].copy()
    if matches.empty:
        return "No Supplier Found"
    matches['Supplier Score'] = matches.apply(score_supplier, axis=1)
    top_supplier = matches.sort_values('Supplier Score', ascending=False).iloc[0]
    return f"{top_supplier['Supplier']} (Score: {top_supplier['Supplier Score']})"

product_df['Top Supplier'] = product_df['Product Name'].apply(find_top_supplier)

# Categorize products by opportunity based on score
def get_opportunity(score):
    if score >= 22:
        return "High"
    elif score >= 15:
        return "Medium"
    else:
        return "Low"

product_df['Opportunity'] = product_df['Product Score'].apply(get_opportunity)

# Streamlit UI
st.title("PRISM Product Discovery Dashboard")

for opportunity, color in zip(['High', 'Medium', 'Low'], ['#90ee90', '#FFFF99', '#FFB6C1']):
    st.header(f"{opportunity} Opportunity Products")
    subset = product_df[product_df['Opportunity'] == opportunity]
    if subset.empty:
        st.write("No products in this category.")
    else:
        for idx, row in subset.iterrows():
            st.markdown(
                f"<div style='background-color:{color}; padding:12px; border-radius:6px;'>"
                f"<strong>{row['Product Name']}</strong><br>"
                f"Score: {row['Product Score']}<br>"
                f"Price: ₹{row['Price']}<br>"
                f"Monthly Sale: {row['Monthly Sale']}<br>"
                f"Reviews: {row['Review no']} | Rating: {row['Review Rating']}<br>"
                f"Weight: {row['Weight']} g | Listing Quality: {row['Listing Quality']}<br>"
                f"Top Supplier: {row['Top Supplier']}"
                f"</div><br>", unsafe_allow_html=True)

# Download button for export
st.markdown("---")
st.header("Export Scored Products")

csv = product_df.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="prism_scored_products.csv",
    mime="text/csv"
)
