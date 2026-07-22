from numbers import Complex

import numpy as np

# we first define our fundamental matrices and basic checks.
I = np.array([[1, 0], [0,1]])
pauli_x = np.array([[0,1],[1,0]])
pauli_y = np.array([[0,-1j],[1j,0]])
pauli_z = np.array([[1, 0],[0,-1]])

#normalization function for our complex valued ket vector
def normalize(psi):
    norm = np.linalg.norm(psi)
    if norm == 0:
        raise ValueError("Cannot normalize a zero vector.")

    return psi / norm

def state_0() -> np.ndarray:
    return np.array([[1], [0]], dtype= complex)

def state_1() -> np.ndarray:
    return np.array([[0],[1]], dtype= complex)

def state_plus() -> np.ndarray:
    return normalize(np.array([[1], [1]], dtype= complex))

def state_minus() -> np.ndarray:
    return normalize(np.array([[1], [-1]], dtype= complex))

def state_plus_i() -> np.ndarray:
    return normalize(np.array([[1], [1j]], dtype=complex))

def state_minus_i() -> np.ndarray:
    return normalize(np.array([[1], [-1j]], dtype= complex))


def psi_to_density(psi):
    rho = np.outer(psi, np.conj(psi))
    return rho


def density_to_bloch(rho, decimals:int = 10):
    rx = float(np.round(np.trace(rho @ pauli_x).real, decimals))
    ry = float(np.round(np.trace(rho @ pauli_y).real, decimals))
    rz = float(np.round(np.trace(rho @ pauli_z).real, decimals))

    return rx, ry, rz


def get_purity(rho):
    P = float(np.trace(rho @ rho).real)
    return P


H = np.array([[(1/np.sqrt(2)),(1/np.sqrt(2))],[(1/np.sqrt(2)), -(1/np.sqrt(2))]], dtype=complex)
S = np.array([[1, 0],[0, 1j]], dtype=complex)
T = np.array([[1,0],[0, np.exp(1j*np.pi/4)]],dtype=complex)


def gate_rx(theta:float) -> np.ndarray:
    return np.cos(theta/2)*I - 1j*np.sin(theta/2)*pauli_x

def gate_ry(theta:float) -> np.ndarray:
    return np.cos(theta/2)*I - 1j*np.sin(theta/2)*pauli_y

def gate_rz(theta:float) -> np.ndarray:
    return np.cos(theta/2)*I - 1j*np.sin(theta/2)*pauli_z


def apply_gate(rho:np.ndarray, U:np.ndarray)->np.ndarray:
    return U @ rho @ U.conj().T

def get_rotation_trajectory(
    rho: np.ndarray,
    axis: str,
    total_theta: float,
    steps: int = 30
) -> list[tuple[float, float, float]]:

    trajectory = []
    angles = np.linspace(0, total_theta, steps)

    for angle in angles:
        if axis == 'x':
            U = gate_rx(angle)
        elif axis == 'y':
            U = gate_ry(angle)
        elif axis == 'z':
            U = gate_rz(angle)
        else:
            raise ValueError(f"Unknown axis '{axis}'. Must be 'x', 'y', or 'z'.")

        rho_step = apply_gate(rho, U)
        coords = density_to_bloch(rho_step)
        trajectory.append(coords)

    return trajectory
