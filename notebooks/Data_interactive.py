import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import Data_Analysis as DA

st.set_page_config(page_title="Quiz Dataset Dashboard", layout="wide")

# ---- Dark theme for embedded matplotlib charts ----
plt.rcParams.update({
    'figure.facecolor': 'black', 'axes.facecolor': 'black', 'savefig.facecolor': 'black',
    'text.color': 'white', 'axes.labelcolor': 'white', 'axes.edgecolor': 'white',
    'xtick.color': 'white', 'ytick.color': 'white', 'font.size': 10,
    'axes.titlesize': 12, 'axes.titleweight': 'bold', 'axes.labelsize': 10,
    'xtick.labelsize': 8, 'ytick.labelsize': 8, 'legend.fontsize': 8,
    'axes.grid': True, 'grid.color': '#444444', 'grid.alpha': 0.5, 'grid.linestyle': '--',
})

TRUE_COLOR = '#51CF66'
FALSE_COLOR = '#FF6B6B'
HEAT_CMAP = 'inferno'


@st.cache_data
def load_data():
    return DA.df.copy()


df = load_data()

all_categories = sorted(df['Category'].unique())
all_levels = sorted(df['Level'].unique())  # adjust column name if yours differs (e.g. 'Difficulty')
_cmap = plt.get_cmap('tab10' if len(all_categories) <= 10 else 'tab20')
category_colors = {cat: _cmap(i % _cmap.N) for i, cat in enumerate(all_categories)}

# ---- Sidebar slicers ----
st.sidebar.header("Filters")
selected_categories = st.sidebar.multiselect("Category", all_categories, default=all_categories)
selected_levels = st.sidebar.multiselect("Level", all_levels, default=all_levels)

filtered = df[df['Category'].isin(selected_categories) & df['Level'].isin(selected_levels)]

st.title("Quiz Dataset Dashboard")

if filtered.empty:
    st.warning("No data for the selected filters.")
    st.stop()

category_counts = filtered['Category'].value_counts().reindex(
    [c for c in all_categories if c in filtered['Category'].unique()])
category_answer_counts = (
    filtered.groupby(['Category', 'Answer']).size().unstack(fill_value=0)
    .reindex(category_counts.index)
)
answer_counts = filtered['Answer'].value_counts()

# ---- KPIs ----
total_questions = len(filtered)
total_categories = filtered['Category'].nunique()
true_pct = (filtered['Answer'].astype(str) == 'True').mean() * 100
top_category = category_counts.idxmax()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Questions", f"{total_questions:,}")
k2.metric("Categories Shown", total_categories)
k3.metric("True Answer Rate", f"{true_pct:.1f}%")
k4.metric("Top Category", top_category)

st.divider()

row1 = st.columns(3)
row2 = st.columns(3)


def style_dark_legend(leg):
    leg.get_frame().set_facecolor('black')
    leg.get_frame().set_edgecolor('white')
    if leg.get_title() is not None:
        leg.get_title().set_color('white')
    for text in leg.get_texts():
        text.set_color('white')


# 1. Questions per Category
with row1[0]:
    st.subheader("Questions per Category")
    fig, ax = plt.subplots(figsize=(5, 4))
    bar_colors = [category_colors[c] for c in category_counts.index]
    bars = ax.bar(range(len(category_counts)), category_counts.values, color=bar_colors, edgecolor='white')
    ax.set_xticks(range(len(category_counts)))
    ax.set_xticklabels(category_counts.index, rotation=45, ha='right')
    ax.set_ylabel("Number of Questions")
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h, str(int(h)), ha='center', va='bottom', fontsize=7, color='white')
    st.pyplot(fig)

# 2. True vs False per Category
with row1[1]:
    st.subheader("True vs False Answers per Category")
    fig, ax = plt.subplots(figsize=(5, 4))
    cols = list(category_answer_counts.columns)
    colors_by_col = [FALSE_COLOR if str(c) == 'False' else TRUE_COLOR for c in cols]
    category_answer_counts.plot(kind='bar', ax=ax, color=colors_by_col, legend=True)
    ax.set_xticklabels(category_answer_counts.index, rotation=45, ha='right')
    ax.set_ylabel("Count")
    leg = ax.legend(title="Answer")
    style_dark_legend(leg)
    st.pyplot(fig)

# 3. Category share pie
with row1[2]:
    st.subheader("Category Share of Questions")
    fig, ax = plt.subplots(figsize=(5, 4))
    wedges, _, _ = ax.pie(
        category_counts.values, colors=[category_colors[c] for c in category_counts.index],
        startangle=90, wedgeprops={'edgecolor': 'black'},
        autopct='%1.0f%%', pctdistance=0.75, textprops={'color': 'white', 'fontsize': 7})
    leg = ax.legend(wedges, category_counts.index, title="Category", loc='upper center',
                     bbox_to_anchor=(0.5, -0.05), ncol=min(len(category_counts), 3), fontsize=7)
    style_dark_legend(leg)
    st.pyplot(fig)

# 4. Overall Answer distribution
with row2[0]:
    st.subheader("Overall Answer Distribution")
    fig, ax = plt.subplots(figsize=(5, 4))
    ans_order = list(answer_counts.index)
    ans_colors = [FALSE_COLOR if str(a) == 'False' else TRUE_COLOR for a in ans_order]
    wedges2, _, _ = ax.pie(answer_counts.values, colors=ans_colors, startangle=90,
                            wedgeprops={'edgecolor': 'black'}, autopct='%1.0f%%',
                            textprops={'color': 'white', 'fontsize': 7})
    leg2 = ax.legend(wedges2, [str(a) for a in ans_order], title="Answer",
                      loc='upper center', bbox_to_anchor=(1.0, 1.0), fontsize=7)
    style_dark_legend(leg2)
    st.pyplot(fig)

# 5. Categories ranked by question count
with row2[1]:
    st.subheader("Categories Ranked by Question Count")
    fig, ax = plt.subplots(figsize=(5, 4))
    sorted_counts = category_counts.sort_values()
    ax.barh(range(len(sorted_counts)), sorted_counts.values,
            color=[category_colors[c] for c in sorted_counts.index], edgecolor='white')
    ax.set_yticks(range(len(sorted_counts)))
    ax.set_yticklabels(sorted_counts.index)
    ax.set_xlabel("Number of Questions")
    st.pyplot(fig)

# 6. Category x Answer heatmap
with row2[2]:
    st.subheader("Category vs Answer Heatmap")
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(category_answer_counts.values, cmap=HEAT_CMAP, aspect='auto')
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(cbar.ax.get_yticklabels(), color='white')
    ax.set_xticks(range(len(category_answer_counts.columns)))
    ax.set_xticklabels([str(c) for c in category_answer_counts.columns])
    ax.set_yticks(range(len(category_answer_counts.index)))
    ax.set_yticklabels(category_answer_counts.index)
    vmax = category_answer_counts.values.max() if category_answer_counts.size else 0
    for i in range(category_answer_counts.shape[0]):
        for j in range(category_answer_counts.shape[1]):
            val = category_answer_counts.values[i, j]
            txt_color = 'white' if val < vmax / 2 else 'black'
            ax.text(j, i, val, ha='center', va='center', fontsize=7, color=txt_color)
    st.pyplot(fig)