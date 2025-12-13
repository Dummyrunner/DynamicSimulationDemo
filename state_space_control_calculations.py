import numpy as np
import control
import matplotlib.pyplot as plt


def evaluate_controllability_observability(A, B, C):
    controllability_matrix = control.ctrb(A, B)
    observability_matrix = control.obsv(A, C)
    print("Controllability Matrix:")
    print(controllability_matrix)
    print("Observability Matrix:")
    print(observability_matrix)
    rank_observability_matrix = np.linalg.matrix_rank(observability_matrix)
    rank_controllability_matrix = np.linalg.matrix_rank(controllability_matrix)

    print(f"Rank of controllability matrix: {rank_controllability_matrix}")
    print(f"Rank of observability matrix: {rank_observability_matrix}")
    # (A, B) controllable iff Kalman Matrix has full row rank
    # (A, C) observable iff Kalman Matrix has full column rank
    number_of_ctrb_matrix_rows = controllability_matrix.shape[0]
    number_of_obsv_matrics_cols = observability_matrix.shape[1]
    system_observable = rank_observability_matrix == number_of_obsv_matrics_cols
    system_controllable = rank_controllability_matrix == number_of_ctrb_matrix_rows
    print(f"System Controllable: {system_controllable}")
    print(f"System Observable: {system_observable}")
    return system_controllable, system_observable


def plot_lti_poles(system: control.lti, title="System Pole Locations", figtext=None):
    poles = system.poles()

    # Create the figure and axis
    fig = plt.figure(figsize=(8, 6))
    plt.figtext(
        0.5, 0.01, figtext, wrap=True, horizontalalignment="center", fontsize=12
    )
    # Determine the extent of the plot based on pole locations
    max_real = max(abs(poles.real.max()), 1)  # Ensure at least 1 unit coverage
    max_imag = max(abs(poles.imag.max()), 1)  # Ensure at least 1 unit coverage

    # Color the right half-plane light red with low opacity
    HUGE_VALUE_FOR_X_AXIS = 1e6
    plt.axvspan(0, HUGE_VALUE_FOR_X_AXIS, facecolor="red", alpha=0.1)

    # Plot the poles
    plt.scatter(poles.real, poles.imag, marker="x", color="red", s=100)

    # Set axis limits to provide some padding
    plt.xlim(min(poles.real.min() * 1.2, -0.5), max_real * 1.2)
    plt.ylim(-max_imag * 1.2, max_imag * 1.2)

    # Add labels and styling
    plt.title(title)
    plt.xlabel("Real Part")
    plt.ylabel("Imaginary Part")
    plt.axhline(y=0, color="k", linestyle="--")
    plt.axvline(x=0, color="k", linestyle="--")
    plt.grid(True)
    plt.draw()
