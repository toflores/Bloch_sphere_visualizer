import time
import numpy as np
import streamlit as st
import quantum_engine as qe
import bloch_renderer as br

# 1. Page Configuration
st.set_page_config(
    page_title="Bloch Sphere Visualizer",
    layout="wide"
)

# 2. Initialize Session State
if "rho" not in st.session_state:
    st.session_state.rho = qe.get_initial_state()
if "trajectory" not in st.session_state:
    rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
    st.session_state.trajectory = [(rx, ry, rz)]
if "is_playing" not in st.session_state:
    st.session_state.is_playing = False
if "pulse_target_time" not in st.session_state:
    st.session_state.pulse_target_time = 0.0  # Used for finite pulse execution

# 3. Sidebar Control Panel
with st.sidebar:
    st.header("Control Panel")

    # --- Reset State ---
    if st.button("🔄 Reset to |0⟩", use_container_width=True):
        st.session_state.is_playing = False
        st.session_state.pulse_target_time = 0.0
        st.session_state.rho = qe.get_initial_state()
        rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
        st.session_state.trajectory = [(rx, ry, rz)]
        st.rerun()

    st.divider()

    # --- 1. Discrete Gates ---
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

    # --- 2. Continuous Rabi Controls ---
    st.subheader("2. Continuous Rabi Oscillations")
    omega_x = st.slider("Ω_x (X-Drive)", -5.0, 5.0, 2.0, step=0.5)
    omega_y = st.slider("Ω_y (Y-Drive)", -5.0, 5.0, 0.0, step=0.5)
    omega_z = st.slider("Ω_z (Z-Detuning)", -5.0, 5.0, 0.0, step=0.5)

    col_play1, col_play2 = st.columns(2)
    if col_play1.button("▶ Play Cont.", use_container_width=True):
        st.session_state.is_playing = True
        st.session_state.pulse_target_time = 0.0
        st.rerun()
    if col_play2.button("⏹️ Stop", use_container_width=True):
        st.session_state.is_playing = False
        st.rerun()

    st.divider()

    # --- 3. Calibrated Pulse Sandbox (NEW!) ---
    st.subheader("3. Calibrated Pulse Sandbox")
    st.caption("Simulate finite-duration microwave gate calibration.")

    # Calculate exact theoretical durations based on current Omega magnitude
    omega_mag = np.sqrt(omega_x ** 2 + omega_y ** 2 + omega_z ** 2)
    t_pi = np.pi / omega_mag if omega_mag > 0 else 0.0
    t_pi_half = (np.pi / 2.0) / omega_mag if omega_mag > 0 else 0.0

    # Duration slider
    pulse_duration = st.slider(
        "Pulse Duration Δt (seconds)",
        min_value=0.0,
        max_value=5.0,
        value=float(np.round(t_pi, 2)) if t_pi > 0 else 1.0,
        step=0.05
    )

    # Preset calibration helper buttons
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        if st.button(f"π-Pulse ({t_pi:.2f}s)", use_container_width=True, help="180° inversion pulse"):
            st.session_state.is_playing = False
            st.session_state.pulse_target_time = t_pi
            st.rerun()
    with p_col2:
        if st.button(f" π/2-Pulse ({t_pi_half:.2f}s)", use_container_width=True, help="90° superposition pulse"):
            st.session_state.is_playing = False
            st.session_state.pulse_target_time = t_pi_half
            st.rerun()

    if st.button("Fire Custom Pulse (Δt)", use_container_width=True, type="primary"):
        st.session_state.is_playing = False
        st.session_state.pulse_target_time = pulse_duration
        st.rerun()

# 4. Main Display Setup
st.title("Interactive Single-Qubit Visualizer")
app_container = st.empty()


def render_current_frame():
    """Renders the 3D Bloch sphere and diagnostics strictly into the placeholder."""
    with app_container.container():
        vis_col, diag_col = st.columns([2.2, 1])

        rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
        purity = qe.get_purity(st.session_state.rho)

        with vis_col:
            fig = br.create_bloch_sphere(
                rx, ry, rz, trajectory=st.session_state.trajectory
            )
            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"bloch_chart_{len(st.session_state.trajectory)}"
            )

        with diag_col:
            st.subheader("State Diagnostics")
            st.metric("r_x (X-axis)", f"{rx:.3f}")
            st.metric("r_y (Y-axis)", f"{ry:.3f}")
            st.metric("r_z (Z-axis)", f"{rz:.3f}")
            st.metric("Purity P", f"{purity:.4f}")

            # LaTeX Density Matrix Formatting
            r00, r01 = np.round(st.session_state.rho[0, 0], 3), np.round(st.session_state.rho[0, 1], 3)
            r10, r11 = np.round(st.session_state.rho[1, 0], 3), np.round(st.session_state.rho[1, 1], 3)

            def fmt_c(c: complex) -> str:
                real_part = f"{c.real:.3f}"
                if c.imag == 0:
                    return real_part
                sign = "+" if c.imag >= 0 else "-"
                return f"{real_part} {sign} {abs(c.imag):.3f}i"

            latex_matrix = (
                    r"\begin{bmatrix}" + "\n" +
                    f"{fmt_c(r00)} & {fmt_c(r01)} \\\\" + "\n" +
                    f"{fmt_c(r10)} & {fmt_c(r11)}" + "\n" +
                    r"\end{bmatrix}"
            )
            st.latex(r"\rho = " + latex_matrix)


# 5. Animation Driver / Rendering Logic
if st.session_state.is_playing:
    # --- CONTINUOUS PLAY MODE ---
    for _ in range(100):
        if not st.session_state.is_playing:
            break
        dt = 0.05
        st.session_state.rho = qe.evolve_hamiltonian(
            st.session_state.rho, omega_x, omega_y, omega_z, dt
        )
        rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
        st.session_state.trajectory.append((rx, ry, rz))
        render_current_frame()
        time.sleep(0.03)

elif st.session_state.pulse_target_time > 0:
    # --- FINITE PULSE CALIBRATION MODE (NEW!) ---
    total_time = st.session_state.pulse_target_time
    steps = int(max(15, total_time / 0.04))  # Smooth animation over ~15-40 frames
    dt = total_time / steps

    for _ in range(steps):
        st.session_state.rho = qe.evolve_hamiltonian(
            st.session_state.rho, omega_x, omega_y, omega_z, dt
        )
        rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
        st.session_state.trajectory.append((rx, ry, rz))
        render_current_frame()
        time.sleep(0.03)

    # Reset target time after pulse completes
    st.session_state.pulse_target_time = 0.0
    st.rerun()

else:
    # --- STATIC VIEW ---
    render_current_frame()