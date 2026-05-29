import os
import uuid
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime

CHART_DIR = os.path.join(os.path.dirname(__file__), "static", "charts")
os.makedirs(CHART_DIR, exist_ok=True)

COLORS = [
    "#4F86C6", "#F4845F", "#5DBB8C", "#F9C74F", "#9B72CF",
    "#E07A5F", "#3D405B", "#81B29A", "#F2CC8F", "#118AB2",
]


def generate_expense_chart(categories: list, phone: str, month_name: str) -> str:
    """
    categories: list of (category_name, total_amount)
    Retorna o nome do arquivo gerado.
    """
    if not categories:
        return None

    labels = [c[0] for c in categories]
    values = [c[1] for c in categories]
    total = sum(values)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    fig.patch.set_facecolor("#F8F9FA")

    # --- Pizza ---
    ax1 = axes[0]
    wedges, texts, autotexts = ax1.pie(
        values,
        labels=None,
        autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
        colors=COLORS[: len(labels)],
        startangle=140,
        pctdistance=0.82,
        wedgeprops=dict(width=0.6, edgecolor="white", linewidth=2),
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color("white")
        at.set_fontweight("bold")

    ax1.set_title(
        f"Gastos por Categoria\n{month_name}",
        fontsize=13, fontweight="bold", pad=15, color="#2D3142",
    )

    patches = [
        mpatches.Patch(color=COLORS[i], label=f"{labels[i]}  R$ {values[i]:,.2f}")
        for i in range(len(labels))
    ]
    ax1.legend(
        handles=patches, loc="lower center", bbox_to_anchor=(0.5, -0.18),
        ncol=2, fontsize=8, frameon=False,
    )

    # --- Barras ---
    ax2 = axes[1]
    ax2.set_facecolor("#F8F9FA")

    bars = ax2.barh(
        labels[::-1], values[::-1],
        color=COLORS[: len(labels)][::-1],
        edgecolor="white", linewidth=0.8, height=0.6,
    )

    for bar, val in zip(bars, values[::-1]):
        ax2.text(
            bar.get_width() + total * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"R$ {val:,.2f}",
            va="center", ha="left", fontsize=9, color="#2D3142",
        )

    ax2.set_xlabel("Valor (R$)", fontsize=10, color="#555")
    ax2.set_title(
        "Comparativo de Gastos",
        fontsize=13, fontweight="bold", pad=15, color="#2D3142",
    )
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_color("#DDD")
    ax2.spines["bottom"].set_color("#DDD")
    ax2.tick_params(colors="#555", labelsize=9)
    ax2.xaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: f"R$ {x:,.0f}")
    )

    plt.suptitle(
        f"Total gasto: R$ {total:,.2f}",
        fontsize=11, color="#666", y=0.02,
    )
    plt.tight_layout(rect=[0, 0.05, 1, 1])

    filename = f"chart_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(CHART_DIR, filename)
    plt.savefig(filepath, dpi=130, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return filename
