import numpy as np


class InvertedPendlumModel:
    @staticmethod
    def state_space_model_matrices(mass_cart, mass_pendulum, length_pendulum, gravity):
        """
        Create state space matricses for
        linearized inverted pendulum system in unstable equilibrium

        :param mass_cart: float
        :param mass_pendulum: float
        :param length_pendulum: float
        :param gravity: float
        :return:
        :rtype: tuple[NDArray[Any], tuple, NDArray[Any], _Array1D[float64]]
        """
        M = mass_cart
        m = mass_pendulum
        L = length_pendulum
        g = gravity
        print(f"M: {M}, m: {m}, L: {L}, g: {g}")
        A = np.array(
            [
                [0, 1, 0, 0],
                [0, 0, -(m * g) / M, 0],
                [0, 0, 0, 1],
                [
                    0,
                    0,
                    (M + m) * g / (M * L),
                    0,
                ],
            ]
        )
        B = np.transpose(np.array([0, 1 / M, 0, 1 / (L * M)]))
        C = np.array([[1, 0, 0, 0], [0, 0, 1, 0]])
        D = np.array([[0], [0]])
        return (A, B, C, D)
