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


# 🎭 Chart 3: Minimum Age Rating per Genre (Heatmap)
# --------------------------------------------------
"""
Genres target different audiences — while some categories like Animation or Kids
skew toward younger ratings, others like Drama and Horror cater to mature viewers.
This heatmap shows the distribution of minimum age categories by genre.
"""


# 📊 Preprocess genre and rating combination
# Use the first listed genre and map its ratings
df['main_genre'] = df['listed_in'].str.split(',').str[0].str.strip()


# Filter out rows with missing genres or simplified ratings
genre_rating = df[df['main_genre'].notna() & df['simple_rating'].notna()]


# Create a crosstab of genre × rating
genre_rating_crosstab = pd.crosstab(
genre_rating['main_genre'],
genre_rating['simple_rating'],
normalize='index'
)


# Reorder columns to match rating_order
genre_rating_crosstab = genre_rating_crosstab[rating_order]


# 🎨 Plot Heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(
genre_rating_crosstab,
cmap="Reds",
annot=True,
fmt=".0%",
linewidths=0.5,
linecolor='gray'
)


plt.title("🎭 Genre vs. Minimum Age Rating (Proportional)", fontsize=16)
plt.xlabel("Age Rating")
plt.ylabel("Main Genre")

# ➕ Add custom legend below the plot to explain age ratings
#legend_text = (
#"G = General Audiences\n"
#"PG = Parental Guidance Suggested\n"
#"PG-13 = Parents Strongly Cautioned\n"
#"R = Restricted (17+)\n"
#"TV-MA = Mature Audiences Only"
#)


plt.figtext(0.5, -0.05, legend_text, wrap=True, horizontalalignment='center', fontsize=10)
plt.tight_layout()
plt.show()

plt.tight_layout()
plt.show()


# 📌 Section 9: Interpretation (Chart 3)
"""
Genres like Horror, Drama, and Thrillers are dominated by TV-MA ratings,
while Animation, Kids, and Family genres cluster around G and PG.
This confirms that genre choice directly shapes the intended audience maturity.
"""