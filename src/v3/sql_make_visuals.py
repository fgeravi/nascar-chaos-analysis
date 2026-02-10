import argparse
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--sql", default="src/v3/queries_v3.sql")
    p.add_argument("--outdir", default="output/v3_daytona_trucks/figures_sql")
    return p.parse_args()


def main():
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # DuckDB in-memory connection
    con = duckdb.connect(database=":memory:")
    con.execute(Path(args.sql).read_text())


    # Visual 1: Pace vs Consistency (colored with respect to confidence)
    df1 = con.execute("SELECT * FROM q_pace_vs_consistency").df()

    # Canvas adjustments/sizing
    fig, ax = plt.subplots(figsize=(8, 9))

    sc = ax.scatter(
        df1["avg_green_lap"],
        df1["std_green_lap"],
        c=df1["ci95_halfwidth_green_lap"],
        cmap="viridis",
        alpha=0.85,
        edgecolor="k",
        linewidth=0.4,
    )

    fig.colorbar(sc, ax=ax, label="95% CI half-width on mean lap (s)")
    ax.set_xlabel("Average green lap time (s) — lower is better")
    ax.set_ylabel("Std dev of green lap time (s) — lower is more consistent")
    ax.set_title(
    "Green-Running Pace vs Consistency\n"
    "Color = Confidence (Purple = more confident, Yellow = less confident)"
)

    # Median quadrant lines
    x_med = df1["avg_green_lap"].median()
    y_med = df1["std_green_lap"].median()
    ax.axvline(x_med, linestyle="--", linewidth=1)
    ax.axhline(y_med, linestyle="--", linewidth=1)

    # Labeling quadrants
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    ax.text(
        xmin + 0.02 * (xmax - xmin),
        ymin + 0.02 * (ymax - ymin),
        "Fast + Consistent",
        fontsize=9,
        weight="bold",
    )
    ax.text(
        xmin + 0.02 * (xmax - xmin),
        ymax - 0.06 * (ymax - ymin),
        "Fast + Inconsistent",
        fontsize=9,
    )
    ax.text(
        xmax - 0.30 * (xmax - xmin),
        ymin + 0.02 * (ymax - ymin),
        "Slow + Consistent",
        fontsize=9,
    )
    ax.text(
        xmax - 0.30 * (xmax - xmin),
        ymax - 0.06 * (ymax - ymin),
        "Slow + Inconsistent",
        fontsize=9,
    )

    # --- Numbered labels for top 8 drivers ---
    top8 = df1.head(8).reset_index(drop=True)
    label_map = []

    for i, r in top8.iterrows():
        label_num = i + 1
        ax.annotate(
            str(label_num),
            (r["avg_green_lap"], r["std_green_lap"]),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=10,
            weight="bold",
            bbox=dict(boxstyle="circle,pad=0.2", fc="white", ec="black", lw=0.5),
        )

        clean_name = (
            str(r["name"])
            .replace("(i)", "")
            .replace("#", "")
            .strip()
        )
        label_map.append(f"{label_num} – {clean_name}")

    # Key below plot for readability, names cluster on plot
    left_col = "\n".join(label_map[:4])
    right_col = "\n".join(label_map[4:8])

    fig.subplots_adjust(bottom=0.22)

    # Header 
    fig.text(
        0.50,
        0.085,
        "Driver Key",
        fontsize=11,
        weight="bold",
        ha="center",
        va="top",
    )

    # Key placement
    fig.text(
        0.35,
        0.04,
        left_col,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round", fc="white", ec="black", alpha=0.9),
    )
    fig.text(
        0.60,
        0.04,
        right_col,
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="round", fc="white", ec="black", alpha=0.9),
    )

    # Include text outside axes in saved image
    fig.savefig(outdir / "01_pace_vs_consistency_sql.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # Visual 2: Top 10 pace with 95% CI integrated
    df2 = con.execute("SELECT * FROM q_top10_ci").df()
    df2 = df2.iloc[::-1]  # fastest at bottom

    means = df2["avg_green_lap"].to_numpy()
    lows = df2["ci95_low_green_lap"].to_numpy()
    highs = df2["ci95_high_green_lap"].to_numpy()
    y = range(len(df2))

    fig2, ax2 = plt.subplots(figsize=(8, 8.5))
    ax2.errorbar(means, y, xerr=[means - lows, highs - means], fmt="o", capsize=3)
    ax2.set_yticks(list(y))
    ax2.set_yticklabels([str(n).replace("(i)", "").strip() for n in df2["name"]])
    ax2.set_xlabel("Average green lap time (s) with 95% CI — lower is better")
    ax2.set_title("Top 10 Green-Running Pace (95% CI) — SQL")
    fig2.tight_layout()
    fig2.savefig(outdir / "02_top10_ci_sql.png", dpi=200)
    plt.close(fig2)

    # Visual 3: Confidence compared to Sample Size
    df3 = con.execute("SELECT * FROM q_confidence_vs_n").df()

    fig3, ax3 = plt.subplots(figsize=(7, 5))
    ax3.scatter(df3["green_laps"], df3["ci95_halfwidth_green_lap"], alpha=0.8)
    ax3.set_xlabel("Green-running lap count (n)")
    ax3.set_ylabel("95% CI half-width on mean lap time (s)")
    ax3.set_title("Confidence vs Sample Size (SQL)")
    fig3.tight_layout()
    fig3.savefig(outdir / "03_confidence_vs_n_sql.png", dpi=200)
    plt.close(fig3)

    # Visual 4: Average green lap time by lap number
    df4 = con.execute("SELECT * FROM q_avg_by_lap").df()

    fig4, ax4 = plt.subplots(figsize=(8, 5))
    ax4.plot(df4["lap"], df4["avg_lap_time"])
    ax4.set_xlabel("Lap number")
    ax4.set_ylabel("Average green lap time across all drivers (s)")
    ax4.set_title("Average Green Lap Time by Lap Number (SQL)")
    fig4.tight_layout()
    fig4.savefig(outdir / "04_avg_by_lap_sql.png", dpi=200)
    plt.close(fig4)

    print(f"Wrote SQL visuals to: {outdir}")


if __name__ == "__main__":
    main()