import pandas as pd

# Load the CSV file
df = pd.read_csv("C:/Users/ram90/Desktop/MLOps Project/Data/data_with_20k_each_category.csv")  # Use sep='\t' if it's tab-separated


df.columns = df.columns.str.strip()

# Confirm column names
print("Cleaned Columns:", df.columns.tolist())

# Group and aggregate review text by product (parent_asin)
grouped_reviews = df.groupby('parent_asin')['text'].apply(lambda texts: ' '.join(str(t) for t in texts)).reset_index()

# Save the result to a new CSV
grouped_reviews.to_csv("grouped_reviews_by_product.csv", index=False)

print("Aggregation complete!")
