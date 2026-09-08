import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons, Button
import Data_Analysis as DA

# ---- Dark template / styling ----
plt.rcParams.update({
    'figure.facecolor': 'black',
    'axes.facecolor': 'black',
    'savefig.facecolor': 'black',
    'text.color': 'white',
    'axes.labelcolor': 'white',
    'axes.edgecolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 16,
    'axes.grid': True,
    'grid.color': '#444444',
    'grid.alpha': 0.5,
    'grid.linestyle': '--',
})

TRUE_COLOR = '#51CF66'
FALSE_COLOR = '#FF6B6B'
ACCENT_COLOR = '#B197FC'
HEAT_CMAP = 'inferno'

all_categories = sorted(DA.df['Category'].unique())
all_levels = sorted(DA.df['Level'].unique())  # adjust column name if yours differs (e.g. 'Difficulty')
selected = set(all_levels)

# fixed color per category, reused across every subplot and the legend
_cmap = plt.get_cmap('tab10' if len(all_categories) <= 10 else 'tab20')
category_colors = {cat: _cmap(i % _cmap.N) for i, cat in enumerate(all_categories)}

fig, axes = plt.subplots(2, 3, figsize=(20, 11))
plt.subplots_adjust(left=0.16, bottom=0.16, wspace=0.4, hspace=0.75, top=0.9)
fig.suptitle("Quiz Dataset Dashboard", fontweight='bold')


def draw_dashboard():
    # clean up artifacts from the previous redraw (colorbars + legend)
    for extra_ax in list(fig.axes):
        if extra_ax not in list(axes.flat) and extra_ax is not check_ax:
            fig.delaxes(extra_ax)
    for leg in fig.legends[:]:
        leg.remove()

    df = DA.df[DA.df['Level'].isin(selected)]
    for ax in axes.flat:
        ax.clear()

    if df.empty:
        for ax in axes.flat:
            ax.text(0.5, 0.5, "No data", ha='center', va='center', color='white')
        fig.canvas.draw_idle()
        return

    category_counts = df['Category'].value_counts().reindex(
        [c for c in all_categories if c in df['Category'].unique()])
    category_answer_counts = (
        df.groupby(['Category', 'Answer']).size().unstack(fill_value=0)
        .reindex(category_counts.index)
    )
    answer_counts = df['Answer'].value_counts()

    # 1. Questions per Category — colored by category, full names on axis
    ax = axes[0, 0]
    bar_colors = [category_colors[c] for c in category_counts.index]
    bars = ax.bar(range(len(category_counts)), category_counts.values,
                   color=bar_colors, edgecolor='white')
    ax.set_title("Questions per Category")
    ax.set_ylabel("Number of Questions")
    ax.set_xlabel("Category")
    ax.set_xticks(range(len(category_counts)))
    ax.set_xticklabels(category_counts.index, rotation=45, ha='right')
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h, str(int(h)),
                 ha='center', va='bottom', fontsize=8, color='white')

    # 2. True vs False Answers per Category
    ax = axes[0, 1]
    cols = list(category_answer_counts.columns)
    colors_by_col = [FALSE_COLOR if str(c) == 'False' else TRUE_COLOR for c in cols]
    category_answer_counts.plot(kind='bar', ax=ax, color=colors_by_col, legend=True)
    ax.set_title("True vs False Answers per Category")
    ax.set_ylabel("Count")
    ax.set_xlabel("Category")
    ax.set_xticklabels(category_answer_counts.index, rotation=45, ha='right')
    leg = ax.legend(title="Answer")
    leg.get_frame().set_facecolor('black')
    leg.get_frame().set_edgecolor('white')
    for text in leg.get_texts():
        text.set_color('white')

    # 3. Category share (pie) — colors only on the wedges; legend sits below, out of the way
    ax = axes[0, 2]
    wedges3, _texts3, _autotexts3 = ax.pie(
        category_counts.values, colors=[category_colors[c] for c in category_counts.index],
        startangle=90, wedgeprops={'edgecolor': 'black'},
        autopct='%1.0f%%', pctdistance=0.75, textprops={'color': 'white', 'fontsize': 8})
    ax.set_title("Category Share of Questions")
    leg3 = ax.legend(wedges3, category_counts.index, title="Category",
                      loc='upper center', bbox_to_anchor=(0.5, -0.08),
                      ncol=min(len(category_counts), 3), fontsize=8)
    leg3.get_frame().set_facecolor('black')
    leg3.get_frame().set_edgecolor('white')
    leg3.get_title().set_color('white')
    for text in leg3.get_texts():
        text.set_color('white')

    # 4. Overall Answer distribution (pie)
    ax = axes[1, 0]
    ans_order = list(answer_counts.index)
    ans_colors = [FALSE_COLOR if str(a) == 'False' else TRUE_COLOR for a in ans_order]
    wedges2, _, _ = ax.pie(answer_counts.values, colors=ans_colors, startangle=90,
                            wedgeprops={'edgecolor': 'black'}, autopct='%1.0f%%',
                            textprops={'color': 'white', 'fontsize': 8})
    ax.set_title("Overall Answer Distribution")
    leg2 = ax.legend(wedges2, [str(a) for a in ans_order], title="Answer",
                      loc='upper center', bbox_to_anchor=(1.0, 1.0))
    leg2.get_frame().set_facecolor('black')
    leg2.get_frame().set_edgecolor('white')
    for text in leg2.get_texts():
        text.set_color('white')

    # 5. Categories ranked by question count (horizontal bar)
    ax = axes[1, 1]
    sorted_counts = category_counts.sort_values()
    ax.barh(range(len(sorted_counts)), sorted_counts.values,
             color=[category_colors[c] for c in sorted_counts.index], edgecolor='white')
    ax.set_yticks(range(len(sorted_counts)))
    ax.set_yticklabels(sorted_counts.index)
    ax.set_xlabel("Number of Questions")
    ax.set_ylabel("Category")
    ax.set_title("Categories Ranked by Question Count")

    # 6. Category x Answer heatmap
    ax = axes[1, 2]
    im = ax.imshow(category_answer_counts.values, cmap=HEAT_CMAP, aspect='auto')
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(cbar.ax.get_yticklabels(), color='white')
    ax.set_xticks(range(len(category_answer_counts.columns)))
    ax.set_xticklabels([str(c) for c in category_answer_counts.columns])
    ax.set_yticks(range(len(category_answer_counts.index)))
    ax.set_yticklabels(category_answer_counts.index)
    ax.set_ylabel("Category")
    ax.set_title("Category vs Answer Heatmap")
    vmax = category_answer_counts.values.max() if category_answer_counts.size else 0
    for i in range(category_answer_counts.shape[0]):
        for j in range(category_answer_counts.shape[1]):
            val = category_answer_counts.values[i, j]
            txt_color = 'white' if val < vmax / 2 else 'black'
            ax.text(j, i, val, ha='center', va='center', fontsize=7, color=txt_color)

    fig.canvas.draw_idle()


def on_slicer_click(label):
    if label in selected:
        selected.remove(label)
    else:
        selected.add(label)
    draw_dashboard()


# Slicer panel on the left edge of the figure
check_ax = plt.axes([0.01, 0.35, 0.12, 0.4])
check_ax.set_facecolor('black')
n = len(all_levels)
check = CheckButtons(
    check_ax, all_levels, [True] * n,
    label_props={'color': ['white'] * n, 'fontsize': [10] * n},
    frame_props={'edgecolor': ['white'] * n, 'facecolor': ['#222222'] * n, 'linewidth': [1.5] * n},
    check_props={'facecolor': ['#51CF66'] * n},
)
check.on_clicked(on_slicer_click)

# Save-to-file button, sits just below the slicer
save_ax = plt.axes([0.01, 0.22, 0.12, 0.06])
save_button = Button(save_ax, 'Save as PNG', color='#222222', hovercolor='#444444')
save_button.label.set_color('white')


def on_save_click(event):
    out_path = 'quiz_dashboard_output.png'
    fig.savefig(out_path, facecolor=fig.get_facecolor(), dpi=150, bbox_inches='tight')
    print(f"Saved current view to {out_path}")


save_button.on_clicked(on_save_click)

draw_dashboard()
plt.savefig("Quiz_dashboard_output.png")
plt.show()