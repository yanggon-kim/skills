#!/usr/bin/env python3
"""
Generate execution timeline and kernel breakdown visualizations.

Usage:
  # With JSON profiling results:
  python scripts/plot_timeline.py --data analysis/profiling_results_single-step.json

  # Demo mode:
  python scripts/plot_timeline.py --demo
"""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "analysis"


def plot_phase_timeline(phases, output_path, title="Inference Timeline"):
    """
    Plot a horizontal bar timeline of inference phases.

    phases: list of (name, start_ms, duration_ms, color)
    """
    fig, ax = plt.subplots(figsize=(14, 3))

    for name, start, duration, color in phases:
        rect = mpatches.FancyBboxPatch(
            (start, 0.2), duration, 0.6,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor='black', linewidth=1
        )
        ax.add_patch(rect)
        if duration > 2:
            ax.text(start + duration / 2, 0.5, f"{name}\n{duration:.1f}ms",
                    ha='center', va='center', fontsize=7, fontweight='bold', color='white')

    total_ms = max(s + d for _, s, d, _ in phases) if phases else 50
    ax.set_xlim(-1, total_ms * 1.1)
    ax.set_ylim(0, 1)
    ax.set_xlabel('Time (ms)', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_yticks([])
    for t in range(0, int(total_ms) + 10, 10):
        ax.axvline(x=t, color='gray', linestyle=':', alpha=0.3)

    plt.tight_layout()
    OUTPUT_DIR.mkdir(exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"Timeline saved to: {output_path}")


def plot_batch_comparison(batch_data, output_path, title="Batch Size Scaling"):
    """
    Stacked bar chart comparing phases across batch sizes.

    batch_data: dict of {batch_size: {phase_name: ms, ...}}
    """
    batch_sizes = sorted(batch_data.keys())
    phase_names = list(batch_data[batch_sizes[0]].keys())
    colors = plt.cm.Set2(np.linspace(0, 1, len(phase_names)))

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(batch_sizes))
    bottom = [0] * len(batch_sizes)

    for phase_name, color in zip(phase_names, colors):
        values = [batch_data[bs].get(phase_name, 0) for bs in batch_sizes]
        ax.bar(x, values, bottom=bottom, label=phase_name, color=color, edgecolor='black')

        # Label on bar
        for i, (v, b) in enumerate(zip(values, bottom)):
            if v > 3:
                ax.text(i, b + v / 2, f'{v:.0f}ms', ha='center', va='center',
                        fontsize=7, color='black', fontweight='bold')

        bottom = [b + v for b, v in zip(bottom, values)]

    # Total labels
    for i, bs in enumerate(batch_sizes):
        total = sum(batch_data[bs].values())
        ax.text(i, bottom[i] + 2, f'{total:.0f}ms', ha='center', fontweight='bold', fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels([f'BS={bs}' for bs in batch_sizes])
    ax.set_ylabel('Latency (ms)')
    ax.set_title(title, fontweight='bold')
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"Batch comparison saved to: {output_path}")


def plot_kernel_breakdown(categories, output_path, title="Kernel Time Distribution"):
    """
    Pie chart of kernel categories.

    categories: dict of {category_name: percentage_or_duration}
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.Set1(np.linspace(0, 1, len(categories)))

    wedges, texts, autotexts = ax.pie(
        categories.values(), labels=categories.keys(),
        autopct='%1.1f%%', colors=colors,
        textprops={'fontsize': 9}, pctdistance=0.75,
    )
    ax.set_title(title, fontsize=12, fontweight='bold')

    plt.tight_layout()
    OUTPUT_DIR.mkdir(exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"Kernel breakdown saved to: {output_path}")


def demo():
    """Generate demo plots with sample data."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Demo timeline
    phases = [
        ("Prepare", 0, 0.5, "#95a5a6"),
        ("Encoder", 0.5, 15.0, "#2980b9"),
        ("Decoder", 15.5, 25.0, "#e74c3c"),
        ("Post", 40.5, 1.0, "#95a5a6"),
    ]
    plot_phase_timeline(phases, OUTPUT_DIR / "demo_timeline.png",
                        title="Demo: Inference Timeline (batch=1)")

    # Demo batch comparison
    batch_data = {
        1: {"Encoder": 15, "Decoder": 25, "Other": 1.5},
        2: {"Encoder": 22, "Decoder": 28, "Other": 2},
        4: {"Encoder": 38, "Decoder": 42, "Other": 3},
        8: {"Encoder": 65, "Decoder": 70, "Other": 5},
    }
    plot_batch_comparison(batch_data, OUTPUT_DIR / "demo_batch_comparison.png",
                          title="Demo: Batch Size Scaling")

    # Demo kernel breakdown
    categories = {
        'GEMM/MatMul': 65,
        'Elementwise': 15,
        'Flash Attention': 8,
        'LayerNorm': 5,
        'Other': 4,
        'Memory Ops': 3,
    }
    plot_kernel_breakdown(categories, OUTPUT_DIR / "demo_kernel_breakdown.png",
                          title="Demo: Kernel Time Distribution")


def main():
    parser = argparse.ArgumentParser(description="Generate timeline and breakdown plots")
    parser.add_argument("--data", help="JSON profiling results file")
    parser.add_argument("--demo", action="store_true", help="Generate demo plots")
    args = parser.parse_args()

    if args.demo:
        demo()
    elif args.data:
        with open(args.data) as f:
            data = json.load(f)
        # Auto-generate from profiling results
        if "single_inference" in data:
            timing = data["single_inference"]["timing"]
            cumulative = 0
            phases = []
            c_palette = ['#2980b9', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#95a5a6']
            for i, (name, info) in enumerate(sorted(timing.items(), key=lambda x: x[0])):
                ms = info["avg_ms"]
                color = c_palette[i % len(c_palette)]
                phases.append((name, cumulative, ms, color))
                cumulative += ms
            plot_phase_timeline(phases, OUTPUT_DIR / "timeline.png")
    else:
        print("Use --demo for sample plots or --data <file.json> for real data")


if __name__ == "__main__":
    main()
