# 📦 Section 2: Imports & Setup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (12, 6)


# 🎬 Section 3: Load and Inspect Data
df = pd.read_csv("data/netflix1.csv")
df.head()


# 🔍 Section 4: Preprocessing - Clean Ratings and Years
# Keep only rows with valid release years and ratings
df = df[df['release_year'].notna() & df['rating'].notna()]
df['release_year'] = df['release_year'].astype(int)


# Filter to focus on modern streaming years (e.g., 2010+)
df = df[df['release_year'] >= 2010]


# Simplify ratings to standard categories (group variations)
rating_map = {
'TV-G': 'G', 'G': 'G',
'TV-Y': 'G', 'TV-Y7': 'G',
'PG': 'PG', 'TV-PG': 'PG',
'PG-13': 'PG-13',
'R': 'R', 'TV-14': 'PG-13',
'NC-17': 'R', 'TV-MA': 'TV-MA'
}
df['simple_rating'] = df['rating'].map(rating_map)
df = df[df['simple_rating'].notna()]


# 🧮 Section 5: Prepare Data for Plotting
rating_by_year = df.groupby(['release_year', 'simple_rating']).size().unstack(fill_value=0)


# Sort rating categories for visual consistency
rating_order = ['G', 'PG', 'PG-13', 'R', 'TV-MA']
rating_by_year = rating_by_year[rating_order]




# 📊 Chart 2: Composition of Age Ratings Over Time (Normalized Stacked Bar)
# -------------------------------------------------------------------------
"""
While the absolute number of titles increased, the composition of age categories
has also shifted significantly. This chart shows the *proportion* of each rating
per year, highlighting how the catalog matured structurally.
"""


# 🧮 Prepare normalized data for Chart 2
rating_by_year_norm = rating_by_year.div(rating_by_year.sum(axis=1), axis=0)


# 🎨 Plotting - Normalized Stacked Bar Chart (Chart 2)
rating_by_year_norm.plot(
kind="bar",
stacked=True,
color=["#76b5c5", "#f7b267", "#f79d65", "#d85d56", "#e50914"]
)


plt.title("🎯 Composition of Netflix Age Ratings by Year (Normalized)", fontsize=16)
plt.xlabel("Release Year")
plt.ylabel("Share of Total Titles")
plt.legend(title="Age Rating", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()


# 📌 Section 8: Interpretation (Chart 2)
"""
This normalized chart confirms the trend: mature-rated content (especially TV-MA)
has become the majority share of Netflix releases in recent years. Family content,
on the other hand, has decreased proportionally, even if the raw count stayed flat.
"""