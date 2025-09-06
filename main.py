import streamlit as st
import pandas as pd

# --- Load Data ---
product_df = pd.read_csv("products.csv")
supplier_df = pd.read_csv("suppliers.csv")

# --- Scoring Functions (customize as needed) ---
def score_product(row):
    score = 0
    # Sample scoring logic; replace numbers/thresholds as per your PDF criteria
    # Price scoring
    if 200 <= row['Price'] <= 350:
        score += 4
    elif 175 <= row['Price'] <= 199 or 351 <= row['Price'] <= 400:
        score += 2

    # Reviews scoring
    if row['Reviews'] >= 100:
        score += 4
    elif 50 <= row['Reviews'] < 100:
        score += 2

    # Rating
    if row['Rating'] >= 4.2:
        score += 3
    elif 4.0 <= row['Rating'] < 4.2:
        score += 1

    # Weight & Size Tier
    if row['Weight(g)'] <= 500 and row['Size Tier'] == 'small_standard':
        score += 4
    elif 500 < row['Weight(g)'] <= 700:
        score += 2

    # Listing Quality (example: 'Poor', 'Average', 'Good')
    if row['Listing Quality'].lower() == 'good':
        score += 2
    elif row['Listing Quality'].lower() == 'average':
        score += 1

    return score

def score_supplier(row):
    score = 0
    # Region scoring
    if row['Region'].lower() == 'delhi-ncr':
        score += 4
    # Verification
    if row['Verified'].lower() == 'yes':
        score += 4
    # MOQ
    if row['MOQ'] <= 100:
        score += 2
    elif row['MOQ'] <= 500:
        score += 1
    return score

# --- Apply Scoring ---
product_df['Product Score'] = product_df.apply(score_product, axis=1)

# Attach top supplier to each product for display
def find_top_supplier(product_name):
    matches = supplier_df[supplier_df['Associated Product'] == product_name].copy()
    if not matches.empty:
        matches['Supplier Score'] = matches.apply(score_supplier, axis=1)
        top = matches.sort_values('Supplier Score', ascending=False).iloc[0]
        return f"{top['Supplier Name']} (Score: {top['Supplier Score']})"
    return "No Supplier Found"
product_df['Top Supplier'] = product_df['Product Name'].apply(find_top_supplier)

# --- Categorize Products by Opportunity ---
def get_opportunity(score):
    if score >= 22:
        return 'High'
    elif score >= 15:
        return 'Medium'
    else:
        return 'Low'
product_df['Opportunity'] = product_df['Product Score'].apply(get_opportunity)

# --- Build Streamlit Dashboard ---
st.title("PRISM PoC Product Discovery Dashboard")
st.write("Automated scoring and supplier matching based on your CSV data.")

for category, color in zip(['High', 'Medium', 'Low'], ['#90ee90', '#FFFF99', '#FFB6C1']):
    st.header(f"{category} Opportunity Products")
    cat_df = product_df[product_df['Opportunity'] == category]
    if cat_df.empty:
        st.info("No products found in this opportunity bucket.")
    else:
        for _, row in cat_df.iterrows():
            st.markdown(
                f"<div style='background-color:{color};padding:12px;border-radius:6px'>"
                f"<strong>{row['Product Name']}</strong><br>"
                f"Score: {row['Product Score']}<br>"
                f"Price: ₹{row['Price']}<br>"
                f"Reviews: {row['Reviews']}, Rating: {row['Rating']}<br>"
                f"Weight: {row['Weight(g)']}g, Size: {row['Size Tier']}<br>"
                f"Listing Quality: {row['Listing Quality']}<br>"
                f"Top Supplier: {row['Top Supplier']}"
                f"</div><br>", unsafe_allow_html=True
            )

# --- Export Feature ---
st.markdown("---")
st.header("Download results as CSV")
st.download_button(
    label="Export Product Scores",
    data=product_df.to_csv(index=False),
    file_name="scored_products.csv",
    mime="text/csv"
)
