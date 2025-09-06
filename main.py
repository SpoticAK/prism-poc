import streamlit as st
import pandas as pd

# --- Load Data ---
product_df = pd.read_csv("products.csv")
supplier_df = pd.read_csv("suppliers.csv")

# --- Scoring Functions (customize as needed) ---
def score_product(row):
    score = 0
    # Price scoring
    if 200 <= row['Price'] <= 350:
        score += 4
    elif 175 <= row['Price'] <= 199 or 351 <= row['Price'] <= 400:
        score += 2

    # Reviews scoring (column 'Review no')
    if row['Review no'] >= 100:
        score += 4
    elif 50 <= row['Review no'] < 100:
        score += 2

    # Rating (column 'Review Rating')
    if row['Review Rating'] >= 4.2:
        score += 3
    elif 4.0 <= row['Review Rating'] < 4.2:
        score += 1

    # Weight (column 'Weight')
    if row['Weight'] <= 500:
        score += 4
    elif 500 < row['Weight'] <= 700:
        score += 2

    # Listing Quality (e.g. 'Poor', 'Average', 'Good')
    quality = str(row['Listing Quality']).lower()
    if quality == 'good':
        score += 2
    elif quality == 'average':
        score += 1

    return score

def score_supplier(row):
    score = 0
    # Region scoring (column 'Region')
    if 'delhi' in str(row['Region']).lower():
        score += 4
    # Verification (column 'Verified')
    if str(row['Verified']).strip().lower() == 'yes':
        score += 4
    # MOQ scoring (column 'MOQ')
    try:
        moq = int(row['MOQ'])
        if moq <= 100:
            score += 2
        elif moq <= 500:
            score += 1
    except:
        pass  # Ignore if MOQ is NA or not integer
    return score

# --- Apply Scoring ---
product_df['Product Score'] = product_df.apply(score_product, axis=1)

# Attach top supplier to each product for display
def find_top_supplier(product_name):
    matches = supplier_df[supplier_df['Product Name'] == product_name].copy()
    if not matches.empty:
        matches['Supplier Score'] = matches.apply(score_supplier, axis=1)
        top = matches.sort_values('Supplier Score', ascending=False).iloc[0]
        return f"{top['Supplier']} (Score: {top['Supplier Score']})"
    return "No Supplier Found"
product_df['Top Supplier'] = product_df['Product Name'].apply(find_top_supplier)

# --- Categorize products by opportunity based on total product score
