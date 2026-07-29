import time
import numpy as np
import streamlit as st
import quantum_engine as qe
import bloch_renderer as br
from collections import deque

TRAIL_LENGTH = 150  # fixed size -> array length never changes -> no WebGL rebuild

st.set_page_config(
    page_title="Bloch Sphere Visualizer",
    page_icon="⚛️",
    layout="wide"
)

if "rho" not in st.session_state:
    st.session_state.rho = qe.get_initial_state()  # Default |0>
if "trajectory" not in st.session_state:
    rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
    st.session_state.trajectory = deque([(rx, ry, rz)] * TRAIL_LENGTH, maxlen=TRAIL_LENGTH)
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False


with st.sidebar:
    st.header("Control Panel")

    if st.button("🔄 Reset to |0⟩", use_container_width=True):
        st.session_state.is_playing = False
        st.session_state.rho = qe.get_initial_state()
        rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
        st.session_state.trajectory = deque([(rx, ry, rz)] * TRAIL_LENGTH, maxlen=TRAIL_LENGTH)
        st.rerun()

    st.divider()

    st.subheader("1. Discrete Unitary Gates")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("H (Hadamard)", use_container_width=True):
            st.session_state.is_playing = False
            st.session_state.rho = qe.apply_gate(st.session_state.rho, qe.H_gate)
            rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
            st.session_state.trajectory.append((rx, ry, rz))
        if st.button("X (NOT)", use_container_width=True):
            st.session_state.is_playing = False
            st.session_state.rho = qe.apply_gate(st.session_state.rho, qe.X_gate)
            rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
            st.session_state.trajectory.append((rx, ry, rz))
        if st.button("S (Phase)", use_container_width=True):
            st.session_state.is_playing = False
            st.session_state.rho = qe.apply_gate(st.session_state.rho, qe.S_gate)
            rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
            st.session_state.trajectory.append((rx, ry, rz))
    with col2:
        if st.button("Y Gate", use_container_width=True):
            st.session_state.is_playing = False
            st.session_state.rho = qe.apply_gate(st.session_state.rho, qe.Y_gate)
            rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
            st.session_state.trajectory.append((rx, ry, rz))
        if st.button("Z (Phase Flip)", use_container_width=True):
            st.session_state.is_playing = False
            st.session_state.rho = qe.apply_gate(st.session_state.rho, qe.Z_gate)
            rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
            st.session_state.trajectory.append((rx, ry, rz))
        if st.button("T (π/8)", use_container_width=True):
            st.session_state.is_playing = False
            st.session_state.rho = qe.apply_gate(st.session_state.rho, qe.T_gate)
            rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
            st.session_state.trajectory.append((rx, ry, rz))

    st.divider()

    st.subheader("2. Rabi Oscillations ($H$)")
    omega_x = st.slider("Ω_x (X-Drive)", -5.0, 5.0, 2.0, step=0.5)
    omega_y = st.slider("Ω_y (Y-Drive)", -5.0, 5.0, 0.0, step=0.5)
    omega_z = st.slider("Ω_z (Z-Detuning)", -5.0, 5.0, 0.0, step=0.5)

    col_play1, col_play2 = st.columns(2)
    if col_play1.button("▶️ Play", use_container_width=True):
        st.session_state.is_playing = True
    if col_play2.button("⏹️ Stop", use_container_width=True):
        st.session_state.is_playing = False
        st.rerun()


# 4. Main Display Setup
st.title("Interactive Single-Qubit Visualizer")

vis_col, diag_col = st.columns([2.2, 1])

# Create dedicated placeholders for the chart and text diagnostics
with vis_col:
    chart_placeholder = st.empty()
with diag_col:
    diag_placeholder = st.empty()


def render_diagnostics(rx, ry, rz, purity):
    """Updates only the text/LaTeX metrics in the right column."""
    with diag_placeholder.container():
        st.subheader("State Diagnostics")
        st.metric("r_x (X-axis)", f"{rx:.3f}")
        st.metric("r_y (Y-axis)", f"{ry:.3f}")
        st.metric("r_z (Z-axis)", f"{rz:.3f}")
        st.metric("Purity P", f"{purity:.4f}")

        r00, r01 = np.round(st.session_state.rho[0, 0], 3), np.round(
            st.session_state.rho[0, 1], 3
        )
        r10, r11 = np.round(st.session_state.rho[1, 0], 3), np.round(
            st.session_state.rho[1, 1], 3
        )

        def fmt_c(c: complex) -> str:
            real_part = f"{c.real:.3f}"
            if c.imag == 0:
                return real_part
            sign = "+" if c.imag >= 0 else "-"
            return f"{real_part} {sign} {abs(c.imag):.3f}i"

        latex_matrix = (
            r"\begin{bmatrix}"
            + "\n"
            + f"{fmt_c(r00)} & {fmt_c(r01)} \\\\"
            + "\n"
            + f"{fmt_c(r10)} & {fmt_c(r11)}"
            + "\n"
            + r"\end{bmatrix}"
        )
        st.latex(r"\rho = " + latex_matrix)


def render_sphere(rx, ry, rz):
    """Updates the Plotly chart smoothly without dropping the DOM element."""
    fig = br.create_bloch_sphere(
        rx, ry, rz, trajectory=st.session_state.trajectory
    )
    # NO key=... argument here! This allows Streamlit to patch the existing figure smoothly.
    chart_placeholder.plotly_chart(
        fig, use_container_width=True, config={"displayModeBar": False}
    )


# 5. Animation Driver / Rendering Logic
if st.session_state.is_playing:
    for _ in range(100):
        if not st.session_state.is_playing:
            break

        # Advance state by timestep dt
        dt = 0.15
        st.session_state.rho = qe.evolve_hamiltonian(
            st.session_state.rho, omega_x, omega_y, omega_z, dt
        )

        # Update trajectory trail
        rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
        st.session_state.trajectory.append((rx, ry, rz))

        # Smoothly update visual frame
        render_sphere(rx, ry, rz)
        purity = qe.get_purity(st.session_state.rho)
        render_diagnostics(rx, ry, rz, purity)

        time.sleep(0.05)
else:
    # Static render when paused/stopped
    rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
    purity = qe.get_purity(st.session_state.rho)
    render_sphere(rx, ry, rz)
    render_diagnostics(rx, ry, rz, purity)