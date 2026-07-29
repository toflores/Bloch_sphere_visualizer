import numpy as np
import streamlit as st
from collections import deque

import quantum_engine as qe
import bloch_renderer as br

TRAIL_LENGTH = 150
FRAME_INTERVAL = 0.05  # seconds between fragment reruns while playing

st.set_page_config(page_title="Bloch Sphere Visualizer", layout="wide")

if "rho" not in st.session_state:
    st.session_state.rho = qe.psi_to_density(qe.state_0())
if "trajectory" not in st.session_state:
    rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
    st.session_state.trajectory = deque([(rx, ry, rz)] * TRAIL_LENGTH, maxlen=TRAIL_LENGTH)
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False


def reset_state(initial_state_func):
    st.session_state.is_playing = False
    st.session_state.rho = qe.psi_to_density(initial_state_func())
    rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
    st.session_state.trajectory = deque([(rx, ry, rz)] * TRAIL_LENGTH, maxlen=TRAIL_LENGTH)


def apply_discrete_gate(U):
    st.session_state.is_playing = False
    st.session_state.rho = qe.apply_gate(st.session_state.rho, U)
    rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
    st.session_state.trajectory.append((rx, ry, rz))


with st.sidebar:
    st.header("Control Panel")

    st.markdown("**1. Initialize State**")
    r_cols = st.columns(4)
    if r_cols[0].button("|0⟩", use_container_width=True):
        reset_state(qe.state_0)
    if r_cols[1].button("|1⟩", use_container_width=True):
        reset_state(qe.state_1)
    if r_cols[2].button("|+⟩", use_container_width=True):
        reset_state(qe.state_plus)
    if r_cols[3].button("|+i⟩", use_container_width=True):
        reset_state(qe.state_plus_i)

    st.divider()

    st.markdown("**2. Discrete Unitary Gates**")
    g_cols = st.columns(6)
    if g_cols[0].button("H", use_container_width=True):
        apply_discrete_gate(qe.H)
    if g_cols[1].button("X", use_container_width=True):
        apply_discrete_gate(qe.pauli_x)
    if g_cols[2].button("Y", use_container_width=True):
        apply_discrete_gate(qe.pauli_y)
    if g_cols[3].button("Z", use_container_width=True):
        apply_discrete_gate(qe.pauli_z)
    if g_cols[4].button("S", use_container_width=True):
        apply_discrete_gate(qe.S)
    if g_cols[5].button("T", use_container_width=True):
        apply_discrete_gate(qe.T)

    st.divider()

    st.markdown("**3. Rabi Oscillations (Hamiltonian drive)**")
    st.slider("Ω_x (X-Drive)", -5.0, 5.0, 2.0, step=0.5, key="omega_x")
    st.slider("Ω_y (Y-Drive)", -5.0, 5.0, 0.0, step=0.5, key="omega_y")
    st.slider("Ω_z (Z-Detuning)", -5.0, 5.0, 0.0, step=0.5, key="omega_z")

    p_col1, p_col2 = st.columns(2)
    if p_col1.button("▶️ Play", use_container_width=True):
        st.session_state.is_playing = True
    if p_col2.button("⏹️ Stop", use_container_width=True):
        st.session_state.is_playing = False

    st.divider()
    if st.button("Clear Trajectory Trail", use_container_width=True):
        rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
        st.session_state.trajectory = deque([(rx, ry, rz)] * TRAIL_LENGTH, maxlen=TRAIL_LENGTH)


st.title("Single-Qubit State Visualization")
st.markdown("Interactive simulation of single-qubit dynamics and unitary transformations.")


@st.fragment(run_every=FRAME_INTERVAL if st.session_state.is_playing else None)
def render_visualization():
    if st.session_state.is_playing:
        st.session_state.rho = qe.evolve_hamiltonian(
            st.session_state.rho,
            st.session_state.omega_x,
            st.session_state.omega_y,
            st.session_state.omega_z,
            FRAME_INTERVAL,
        )
        rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
        st.session_state.trajectory.append((rx, ry, rz))
    else:
        rx, ry, rz = qe.density_to_bloch(st.session_state.rho)

    purity = qe.get_purity(st.session_state.rho)

    fig = br.create_bloch_sphere(rx, ry, rz, trajectory=st.session_state.trajectory)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")
    st.subheader("State Diagnostics")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("r_x", f"{rx:.3f}")
    m_col2.metric("r_y", f"{ry:.3f}")
    m_col3.metric("r_z", f"{rz:.3f}")
    m_col4.metric("Purity", f"{purity:.4f}")

    rho = st.session_state.rho
    r00, r01 = np.round(rho[0, 0], 3), np.round(rho[0, 1], 3)
    r10, r11 = np.round(rho[1, 0], 3), np.round(rho[1, 1], 3)

    def fmt_c(c: complex) -> str:
        if c.imag == 0:
            return f"{c.real:.3f}"
        sign = "+" if c.imag >= 0 else "-"
        return f"{c.real:.3f} {sign} {abs(c.imag):.3f}i"

    st.latex(rf"""
    \rho = \begin{{bmatrix}}
    {fmt_c(r00)} & {fmt_c(r01)} \\
    {fmt_c(r10)} & {fmt_c(r11)}
    \end{{bmatrix}}
    """)


render_visualization()