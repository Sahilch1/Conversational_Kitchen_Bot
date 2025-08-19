"""
index_builder.py
Build and persist the FAISS vector index for the Kitchen Assistant.
"""

import os
from vectorstore import build_recipe_index

# Path to your recipes dataset
CSV_FILE = "recipes.csv"

# Directory to save the FAISS index
INDEX_DIR = "faiss_index"

def main():
    """Builds the FAISS index from recipes.csv and saves it."""
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"Recipes file not found: {CSV_FILE}")

    print("🔄 Loading recipes and building index...")
    index = build_recipe_index(CSV_FILE)

    print(f"💾 Saving FAISS index to: {INDEX_DIR}")
    index.save_local(INDEX_DIR)

    print("✅ Index built and saved successfully.")

if __name__ == "__main__":
    main()
