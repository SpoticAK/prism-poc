import streamlit as st
import pandas as pd

# Load data
product_df = pd.read_csv("products.csv")
supplier_df = pd.read_csv("suppliers.csv")

# Product scoring function with updated rules
def score_product(row):
    score = 0

    # Price scoring
    if 200 <= row['Price'] <= 350:
        score += 4
    elif 175 <= row['Price'] <= 199 or 351 <= row['Price'] <= 400:
        score += 2

    # Number of reviews scoring
    if row['Review no'] >= 100:
        score += 3
    elif 50 <= row['Review no'] < 100:
        score += 2
    else:
        score += 1

    # Rating scoring
    if row['Review Rating'] > 4.2:
        score += 3
    elif 4.0 <= row['Review Rating'] <= 4.19:
        score += 2
    elif 3.8 <= row['Review Rating'] < 4.0:
        score += 1
    else:
        score += 0

    # Weight scoring
    if row['Weight'] > 500:
        score += 1
    else:
        score += 3

    # Listing Quality scoring
    quality = str(row['Listing Quality']).strip().lower()
    if quality == 'good':
        score += 2
    elif quality == 'average':
        score += 1

    return score

# Supplier scoring function with updated rules
def score_supplier(row):
    score = 0

    # Region scoring
    region = str(row['Region']).lower()
    if 'delhi' in region:
        score += 2
    else:
        score += 1

    # Verified status scoring
    if str(row['Verified']).strip().lower() == 'yes':
        score += 4

    # MOQ scoring (handle NA/potential non-integers)
    try:
        moq = int(row['MOQ'])
        if moq <= 100:
            score += 2
        elif moq <= 500:
            score += 1
    except:
        pass

    return score

# Calculate product scores
product_df['Product Score'] = product_df.apply(score_product, axis=1)

# Find top scoring supplier per product
def find_top_supplier(product_name):
    matches = supplier_df[supplier_df['Product Name'] == product_name].copy()
    if matches.empty:
        return "No Supplier Found"
    matches['Supplier Score'] = matches.apply(score_supplier, axis=1)
    top = matches.sort_values('Supplier Score', ascending=False).iloc[0]
    return f"{top['Supplier']} (Score: {top['Supplier Score']})"

product_df['Top Supplier'] = product_df['Product Name'].apply(find_top_supplier)

# Opportunity buckets
def get_opportunity(score):
    if score >= 18:
        return "High"
    elif 12 <= score < 18:
        return "Medium"
    else:
        return "Low"

product_df['Opportunity'] = product_df['Product Score'].apply(get_opportunity)

# Streamlit dashboard
st.title("PRISM Product Discovery Dashboard")

for opportunity, color in zip(['High', 'Medium', 'Low'], ['#90ee90', '#FFFF99', '#FFB6C1']):
    st.header(f"{opportunity} Opportunity Products")
    sub_df = product_df[product_df['Opportunity'] == opportunity]
    if sub_df.empty:
        st.info("No products found in this category.")
    else:
        for _, row in sub_df.iterrows():
            st.markdown(
                f"<div style='background-color:{color}; padding:12px; border-radius:6px;'>"
                f"<strong>{row['Product Name']}</strong><br>"
                f"Score: {row['Product Score']}<br>"
                f"Price: ₹{row['Price']}<br>"
                f"Monthly Sale: {row['Monthly Sale']}<br>"
                f"Reviews: {row['Review no']} | Rating: {row['Review Rating']}<br>"
                f"Weight: {row['Weight']} g | Listing Quality: {row['Listing Quality']}<br>"
                f"Top Supplier: {row['Top Supplier']}"
                f"</div><br>",
                unsafe_allow_html=True
            )

# Export scored data option
st.markdown("---")
st.header("Export scored product data")
csv = product_df.to_csv(index=False)
st.download_button(label="Download CSV", data=csv, file_name="prism_scored_products.csv", mime="text/csv")
