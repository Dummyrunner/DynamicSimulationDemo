#!/usr/bin/env python3
"""
Pole placement optimization for submarine depth control.
Searches a grid of pole locations to find the configuration that minimizes least squares error.
Runs simulations as fast as possible without rendering and parallelizes across multiple cores.
"""

import numpy as np
import pymunk
from typing import Tuple
import control
from multiprocessing import Pool, cpu_count
import time
import json
from dataclasses import dataclass

from submarine_model import SubmarineModel
from game_controller import StateFeedbackController, GameControllerBase
from submarine_pole_placement import (
    DefaultSubmarineModelParams,
    SubmarineInput,
    SubmarineState,
    SubmarinePlant,
    ReferenceSignal,
    _create_step_reference_mapping,
    SAMPLE_TIME,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)

# Pole search parameters - individual min/max for each pole
PARAM1_MIN = -9980
PARAM1_MAX = -9940
PARAM1_STEP = 0.1

PARAM2_MIN = -3
PARAM2_MAX = -2
PARAM2_STEP = 0.1

# Generate ranges for each pole
PARAM1_RANGE = np.arange(PARAM1_MIN, PARAM1_MAX + PARAM1_STEP, PARAM1_STEP)
PARAM2_RANGE = np.arange(PARAM2_MIN, PARAM2_MAX + PARAM2_STEP, PARAM2_STEP)


@dataclass
class SimulationRunConfig:
    param_set: Tuple[float, float]
    plant: SubmarinePlant
    controller: GameControllerBase


def run_single_simulation_headless(
    simulation_run_config: SimulationRunConfig,
) -> Tuple[float, float, float]:
    """
    Run a single simulation with given poles and return the least squares score.
    This version runs without rendering for maximum speed.

    Args:
        pole_config: Tuple of (param1, param2)

    Returns:
        Tuple of (param1, param2, least_squares_score)
    """
    cfg = simulation_run_config
    param1, param2 = cfg.param_set
    plant = cfg.plant
    controller = cfg.controller

    # Create reference signal
    reference_signal = ReferenceSignal(
        _create_step_reference_mapping(
            window_height=WINDOW_HEIGHT,
            step_height=-WINDOW_HEIGHT // 4,
            step_position=WINDOW_WIDTH // 2,
        )
    )

    # Run simulation without rendering
    least_squares_score = 0.0

    while plant.submarine.body.position.x <= WINDOW_WIDTH:
        plant.state = SubmarineState(
            depth=plant.submarine.body.position.y,
            vertical_velocity=plant.submarine.body.velocity.y,
        )

        reference_signal_value = reference_signal.evaluate(
            plant.submarine.body.position.x
        )
        current_system_state = plant.get_state()
        position_error = current_system_state.depth - reference_signal_value

        current_system_state_error = SubmarineState(
            depth=position_error,
            vertical_velocity=current_system_state.vertical_velocity,
        )

        input_from_controller = controller.get_control_input(current_system_state_error)

        plant.set_input(SubmarineInput(vertical_thrust=input_from_controller))
        least_squares_score += position_error**2
        plant.step(SAMPLE_TIME)

    return param1, param2, least_squares_score / 1e5


def save_results_to_file(results_list: list, filename: str = None):
    """
    Save pole search results to a JSON file.

    Args:
        results_list: List of tuples (pole1, pole2, score)
        filename: Output filename for results. If None, generates name from pole ranges.
    """
    if filename is None:
        filename = (
            f"pole_search_results_"
            f"p1_{PARAM1_MIN}_to_{PARAM1_MAX}_s{PARAM1_STEP}_"
            f"p2_{PARAM2_MIN}_to_{PARAM2_MAX}_s{PARAM2_STEP}.json"
        )
    data = {
        "grid_parameters": {
            "param1_min": float(PARAM1_MIN),
            "param1_max": float(PARAM1_MAX),
            "param1_step": float(PARAM1_STEP),
            "param2_min": float(PARAM2_MIN),
            "param2_max": float(PARAM2_MAX),
            "param2_step": float(PARAM2_STEP),
            "num_param1_values": len(PARAM1_RANGE),
            "num_param2_values": len(PARAM2_RANGE),
            "total_simulations": len(results_list),
        },
        "results": [
            {"pole1": float(p1), "pole2": float(p2), "score": float(score)}
            for p1, p2, score in results_list
        ],
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Results saved to {filename}")


def create_heatmap(results_list: list, filename: str = None):
    """
    Create a heatmap visualization of the pole search results.

    Args:
        results_list: List of tuples (pole1, pole2, score)
        filename: Output filename for the heatmap image. If None, generates name from pole ranges.
    """
    if filename is None:
        filename = (
            f"pole_search_heatmap_"
            f"p1_{PARAM1_MIN}_to_{PARAM1_MAX}_s{PARAM1_STEP}_"
            f"p2_{PARAM2_MIN}_to_{PARAM2_MAX}_s{PARAM2_STEP}.png"
        )
    import matplotlib.pyplot as plt

    # Create 2D grid
    pole1_values = sorted(set(p1 for p1, p2, _ in results_list))
    pole2_values = sorted(set(p2 for p1, p2, _ in results_list))

    # Create score matrix (not currently used but kept for future contour plots)
    score_matrix = np.full((len(pole2_values), len(pole1_values)), np.nan)

    for p1, p2, score in results_list:
        i = pole1_values.index(p1)
        j = pole2_values.index(p2)
        score_matrix[j, i] = score

    # Create figure and plot
    fig, ax = plt.subplots(figsize=(12, 10))

    # Filter out infinite scores for visualization
    valid_results = [
        (p1, p2, score) for p1, p2, score in results_list if np.isfinite(score)
    ]

    if valid_results:
        valid_pole1 = [p1 for p1, _, _ in valid_results]
        valid_pole2 = [p2 for _, p2, _ in valid_results]
        valid_scores = [score for _, _, score in valid_results]

        # Normalize scores for coloring (green=low, red=high)
        from matplotlib.colors import Normalize

        norm = Normalize(vmin=min(valid_scores), vmax=max(valid_scores))

        scatter = ax.scatter(
            valid_pole1,
            valid_pole2,
            c=valid_scores,
            cmap="RdYlGn_r",
            norm=norm,
            s=100,
            alpha=0.8,
            edgecolors="black",
            linewidth=0.5,
        )

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Least Squares Error Score", rotation=270, labelpad=20)

        # Mark the best result
        best_result = min(valid_results, key=lambda x: x[2])
        best_pole1, best_pole2, best_score = best_result
        ax.scatter(
            [best_pole1],
            [best_pole2],
            s=300,
            marker="*",
            c="gold",
            edgecolors="black",
            linewidth=2,
            label=f"Best: ({best_pole1:.1f}, {best_pole2:.1f}) = {best_score:.2f}",
            zorder=5,
        )

    ax.set_xlabel("Pole 1", fontsize=12, fontweight="bold")
    ax.set_ylabel("Pole 2", fontsize=12, fontweight="bold")
    ax.set_title(
        "Pole Placement Optimization Heatmap\n(Green = Low Error, Red = High Error)",
        fontsize=14,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print(f"Heatmap saved to {filename}")
    plt.close()


def param_search(num_workers: int = None):
    """
    Run param search over a grid of param values using parallel processing.

    Args:
        num_workers: Number of worker processes. If None, uses all available cores.
    """
    if num_workers is None:
        num_workers = cpu_count()

    print("param Search:")
    print(f"  param 1: [{PARAM1_MIN}, {PARAM1_MAX}] with step {PARAM1_STEP}")
    print(f"  param 2: [{PARAM2_MIN}, {PARAM2_MAX}] with step {PARAM2_STEP}")
    print(
        f"Grid size: {len(PARAM1_RANGE)} x {len(PARAM2_RANGE)} = {len(PARAM1_RANGE) * len(PARAM2_RANGE)} simulations"
    )
    print(f"Using {num_workers} worker processes")
    print("=" * 80)

    # Create all pole configurations
    run_configs = []
    for pole1 in PARAM1_RANGE:
        for pole2 in PARAM2_RANGE:
            A, B, _, _ = SubmarineModel.state_space_model_matrices(
                DefaultSubmarineModelParams.SUMBARINE_MASS
            )
            gain_matrix = control.place(A, B, (pole1, pole2))
            run_configs.append(
                SimulationRunConfig(
                    param_set=(pole1, pole2),
                    plant=SubmarinePlant(
                        pymunk.Space(),
                        window_size=(WINDOW_WIDTH, WINDOW_HEIGHT),
                        sample_time=SAMPLE_TIME,
                    ),
                    controller=StateFeedbackController(gain_matrix, SAMPLE_TIME),
                ),
            )

    # Run simulations in parallel
    start_time = time.time()

    with Pool(processes=num_workers) as pool:
        results = pool.imap_unordered(run_single_simulation_headless, run_configs)

        results_list = []
        for i, result in enumerate(results, 1):
            pole1, pole2, score = result
            results_list.append((pole1, pole2, score))

            # Print progress
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (len(run_configs) - i) / rate if rate > 0 else 0

            print(
                f"[{i}/{len(run_configs)}] Poles: ({pole1:6.1f}, {pole2:6.1f}) -> "
                f"Score: {score:10.2f} | "
                f"Elapsed: {elapsed:6.1f}s | "
                f"Remaining: {remaining:6.1f}s"
            )

    elapsed_total = time.time() - start_time

    # Find best result
    print("=" * 80)
    best_result = min(results_list, key=lambda x: x[2])
    best_pole1, best_pole2, best_score = best_result

    print("BEST RESULT:")
    print(f"  Pole 1: {best_pole1:.1f}")
    print(f"  Pole 2: {best_pole2:.1f}")
    print(f"  Least Squares Score: {best_score:.2f}")
    print(f"  Total Time: {elapsed_total:.2f}s")
    print(f"  Average Time per Simulation: {elapsed_total / len(run_configs):.3f}s")
    print("=" * 80)

    # Print top 10 results
    print("\nTop 10 Results:")
    sorted_results = sorted(results_list, key=lambda x: x[2])
    for i, (p1, p2, score) in enumerate(sorted_results[:10], 1):
        print(f"  {i:2d}. Poles: ({p1:6.1f}, {p2:6.1f}) -> Score: {score:10.2f}")

    # Save results to file and create heatmap
    print("\n" + "=" * 80)
    save_results_to_file(results_list, "pole_search_results.json")
    create_heatmap(results_list, "pole_search_heatmap.png")
    print("=" * 80)

    return best_result, sorted_results


if __name__ == "__main__":
    print("Starting Pole Search Optimization...")
    print(f"CPU Cores Available: {cpu_count()}")
    print()

    best_result, all_results = param_search()

    print("\nParameter search complete!")
