import numpy as np
import streamlit as st

import quantum_engine as qe
import bloch_renderer as br

# --- Page Configuration ---
st.set_page_config(
    page_title="Bloch Sphere Visualizer",
    layout="wide"
)

# --- Session State Initialization ---
if "rho" not in st.session_state:
    st.session_state.rho = qe.psi_to_density(qe.state_0())

if "trajectory" not in st.session_state:
    rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
    st.session_state.trajectory = [(rx, ry, rz)]


# --- Helper Callbacks ---
def apply_discrete_gate(U: np.ndarray):
    st.session_state.rho = qe.apply_gate(st.session_state.rho, U)
    rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
    st.session_state.trajectory.append((rx, ry, rz))


def apply_rotation_gate(axis: str, theta: float):
    path = qe.get_rotation_trajectory(st.session_state.rho, axis, theta, steps=30)
    st.session_state.trajectory.extend(path)

    if axis == 'x':
        U = qe.gate_rx(theta)
    elif axis == 'y':
        U = qe.gate_ry(theta)
    else:
        U = qe.gate_rz(theta)

    st.session_state.rho = qe.apply_gate(st.session_state.rho, U)


def reset_state(initial_state_func):
    st.session_state.rho = qe.psi_to_density(initial_state_func())
    rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
    st.session_state.trajectory = [(rx, ry, rz)]


# --- SIDEBAR: Control Panel ---
with st.sidebar:
    st.header("Control Panel")

    # 1. Reset
    st.markdown("**1. Initialize State**")
    r_cols = st.columns(4)
    if r_cols[0].button("|0⟩", use_container_width=True):
        reset_state(qe.state_0)
        st.rerun()
    if r_cols[1].button("|1⟩", use_container_width=True):
        reset_state(qe.state_1)
        st.rerun()
    if r_cols[2].button("|+⟩", use_container_width=True):
        reset_state(qe.state_plus)
        st.rerun()
    if r_cols[3].button("|+i⟩", use_container_width=True):
        reset_state(qe.state_plus_i)
        st.rerun()

    st.divider()

    # 2. Discrete Gates
    st.markdown("**2. Discrete Unitary Gates**")
    g_cols = st.columns(6)
    if g_cols[0].button("H", use_container_width=True):
        apply_discrete_gate(qe.H)
        st.rerun()
    if g_cols[1].button("X", use_container_width=True):
        apply_discrete_gate(qe.pauli_x)
        st.rerun()
    if g_cols[2].button("Y", use_container_width=True):
        apply_discrete_gate(qe.pauli_y)
        st.rerun()
    if g_cols[3].button("Z", use_container_width=True):
        apply_discrete_gate(qe.pauli_z)
        st.rerun()
    if g_cols[4].button("S", use_container_width=True):
        apply_discrete_gate(qe.S)
        st.rerun()
    if g_cols[5].button("T", use_container_width=True):
        apply_discrete_gate(qe.T)
        st.rerun()

    st.divider()

    # 3. Continuous Rotations
    st.markdown("**3. Parametric Rotations $R_k(\\theta)$**")
    rx_angle = st.slider("Rotate around X-axis (θ in rad):", 0.0, 2 * np.pi, np.pi / 2, step=0.1)
    if st.button("Apply Rₓ(θ)", use_container_width=True):
        apply_rotation_gate('x', rx_angle)
        st.rerun()

    ry_angle = st.slider("Rotate around Y-axis (θ in rad):", 0.0, 2 * np.pi, np.pi / 2, step=0.1)
    if st.button("Apply R_y(θ)", use_container_width=True):
        apply_rotation_gate('y', ry_angle)
        st.rerun()

    rz_angle = st.slider("Rotate around Z-axis (θ in rad):", 0.0, 2 * np.pi, np.pi / 2, step=0.1)
    if st.button("Apply R_z(θ)", use_container_width=True):
        apply_rotation_gate('z', rz_angle)
        st.rerun()

    st.divider()

    if st.button("Clear Trajectory Trail", use_container_width=True):
        rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
        st.session_state.trajectory = [(rx, ry, rz)]
        st.rerun()

# --- MAIN BODY: Visualization ---
st.title("Single-Qubit State Visualization")
st.markdown("Interactive simulation of single-qubit dynamics and unitary transformations.")

# Extract current coordinates and purity
rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
purity = qe.get_purity(st.session_state.rho)

# Render large Plotly Figure
fig = br.create_bloch_sphere(rx, ry, rz, trajectory=st.session_state.trajectory)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- Mathematical Readouts ---
st.subheader("State Diagnostics")

# Metric columns
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("r_x", f"{rx:.3f}")
m_col2.metric("r_y", f"{ry:.3f}")
m_col3.metric("r_z", f"{rz:.3f}")
m_col4.metric("Purity", f"{purity:.4f}")

# Format complex numbers neatly for LaTeX
rho = st.session_state.rho
r00, r01 = np.round(rho[0, 0], 3), np.round(rho[0, 1], 3)
r10, r11 = np.round(rho[1, 0], 3), np.round(rho[1, 1], 3)


def fmt_c(c: complex) -> str:
    if c.imag == 0:
        return f"{c.real}"
    sign = "+" if c.imag >= 0 else "-"
    return f"{c.real} {sign} {abs(c.imag)}i"


# Render LaTeX matrix natively in Streamlit
latex_str = f"""
\\rho = \\begin{{bmatrix}}
{fmt_c(r00)} & {fmt_c(r01)} \\\\
{fmt_c(r10)} & {fmt_c(r11)}
\\end{{bmatrix}}
"""
st.latex(latex_str)