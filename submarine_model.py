import numpy as np


class SubmarineModel:
    @staticmethod
    def state_space_model_matrices(mass_submarine):
        A = np.array([[0, 1], [0, 0]])
        B = np.transpose(np.array([0, 1 / mass_submarine]))
        C = np.array([[1, 0]])
        D = np.array([[0]])
        return (A, B, C, D)
