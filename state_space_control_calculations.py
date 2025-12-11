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


def plot_lti_poles(system: control.lti):
    poles = system.poles()
    plt.figure(figsize=(8, 6))
    plt.scatter(poles.real, poles.imag, marker="x", color="red", s=100)
    plt.title("Pole Locations")
    plt.xlabel("Real Part")
    plt.ylabel("Imaginary Part")
    plt.axhline(y=0, color="k", linestyle="--")
    plt.axvline(x=0, color="k", linestyle="--")
    plt.grid(True)
    plt.show()
