"""
Generate loop_animation.gif: a 10-second visual of the tool-use loop.

This script is run by maintainers (not by students) to (re)generate the
animated GIF that is displayed in exercise0.ipynb. Run with:

    uv run --with matplotlib --with Pillow python loop_animation.py

The output (loop_animation.gif) is checked into the repo so the notebook
itself has no matplotlib dependency.
"""
from pathlib import Path
import io

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image

OUT = Path(__file__).parent / "loop_animation.gif"

USER = (1.5, 5.0)
LLM = (5.0, 5.0)
TOOL = (8.5, 5.0)
BW, BH = 1.6, 0.8

C_USER = "#4A90E2"
C_LLM = "#7ED321"
C_TOOL = "#F5A623"
C_LOOP = "#E74C3C"
C_TEXT = "#222"


def draw_box(ax, pos, color, label):
    x, y = pos
    ax.add_patch(FancyBboxPatch(
        (x - BW / 2, y - BH / 2), BW, BH,
        boxstyle="round,pad=0.05",
        facecolor=color, edgecolor="black", linewidth=1.5,
    ))
    ax.text(x, y, label, ha="center", va="center",
            fontsize=14, fontweight="bold", color="white")


def arrow(ax, start, end, color="#222", lw=2.5):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="->",
        color=color, lw=lw, mutation_scale=22,
    ))


def bubble(ax, pos, text, color):
    ax.text(pos[0], pos[1], text, ha="center", va="center",
            fontsize=10, color="white",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=color, edgecolor="black"))


MSG_USER = ("user", 'content="Calculate 17 * 23"', C_USER)
MSG_TC = ("asst", 'tool_calls=[calc("17*23")]', C_LLM)
MSG_TOOL = ("tool", 'content="391"', C_TOOL)
MSG_ANS = ("asst", 'content="17 * 23 = 391"', C_LLM)


def draw_messages(ax, items):
    ax.text(0.4, 2.9, "messages:", ha="left", va="center",
            fontsize=11, fontweight="bold")
    for i, (role, text, color) in enumerate(items):
        y = 2.45 - i * 0.45
        ax.text(0.55, y, f"{i}.", ha="left", va="center", fontsize=9, color="gray")
        ax.text(1.0, y, role, ha="left", va="center", fontsize=10, color="white",
                bbox=dict(boxstyle="round,pad=0.15", facecolor=color, edgecolor="none"))
        ax.text(2.2, y, text, ha="left", va="center", fontsize=10, family="monospace")


def render(stage):
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=100)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(5, 6.2, "The Tool-Use Loop", ha="center", va="center",
            fontsize=15, fontweight="bold")

    draw_box(ax, USER, C_USER, "USER")
    draw_box(ax, LLM, C_LLM, "LLM")
    draw_box(ax, TOOL, C_TOOL, "TOOL")

    if stage == 1:
        arrow(ax, (USER[0] + BW / 2 + 0.05, USER[1]),
              (LLM[0] - BW / 2 - 0.05, LLM[1]))
        bubble(ax, (3.25, 4.1), '"Calculate 17 * 23"', C_USER)
        ax.text(5, 5.85, "step 1: user asks", ha="center", va="center",
                fontsize=10, style="italic", color=C_TEXT)
        draw_messages(ax, [MSG_USER])
    elif stage == 2:
        arrow(ax, (LLM[0] + BW / 2 + 0.05, LLM[1]),
              (TOOL[0] - BW / 2 - 0.05, TOOL[1]))
        bubble(ax, (6.75, 4.1), 'tool_call:\ncalculator("17*23")', C_LLM)
        ax.text(5, 5.85, "step 2: LLM emits a tool call (not an answer!)",
                ha="center", va="center", fontsize=10, style="italic", color=C_TEXT)
        draw_messages(ax, [MSG_USER, MSG_TC])
    elif stage == 3:
        arrow(ax, (TOOL[0] - BW / 2 - 0.05, TOOL[1] - 0.15),
              (LLM[0] + BW / 2 + 0.05, LLM[1] - 0.15))
        bubble(ax, (6.75, 4.1), 'returns "391"', C_TOOL)
        ax.text(5, 5.85, "step 3: we run the tool, append result, call LLM again",
                ha="center", va="center", fontsize=10, style="italic", color=C_TEXT)
        draw_messages(ax, [MSG_USER, MSG_TC, MSG_TOOL])
    elif stage == 4:
        arrow(ax, (LLM[0] - BW / 2 - 0.05, LLM[1] - 0.15),
              (USER[0] + BW / 2 + 0.05, USER[1] - 0.15))
        bubble(ax, (3.25, 4.1), '"17 * 23 = 391"', C_LLM)
        ax.text(5, 5.85, "step 4: LLM now answers, having seen the tool result",
                ha="center", va="center", fontsize=10, style="italic", color=C_TEXT)
        draw_messages(ax, [MSG_USER, MSG_TC, MSG_TOOL, MSG_ANS])
    elif stage == 5:
        arrow(ax, (LLM[0] + BW / 2 + 0.05, LLM[1] + 0.18),
              (TOOL[0] - BW / 2 - 0.05, TOOL[1] + 0.18),
              color=C_LOOP, lw=3)
        arrow(ax, (TOOL[0] - BW / 2 - 0.05, TOOL[1] - 0.18),
              (LLM[0] + BW / 2 + 0.05, LLM[1] - 0.18),
              color=C_LOOP, lw=3)
        ax.text(5, 5.85, "the loop: repeat while the LLM keeps requesting tools",
                ha="center", va="center", fontsize=10, style="italic", color=C_TEXT)
        ax.text(6.75, 3.7,
                "while response.tool_calls:\n    run tool, append result,\n    call LLM",
                ha="center", va="center", fontsize=11,
                family="monospace", color=C_LOOP)
        draw_messages(ax, [MSG_USER, MSG_TC, MSG_TOOL, MSG_ANS])

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    img = Image.open(buf).convert("P", palette=Image.ADAPTIVE)
    plt.close(fig)
    return img


def main():
    frames = [render(s) for s in range(1, 6)]
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=2000,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
