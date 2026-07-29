import numpy as np
import streamlit as st

import quantum_engine as qe
import bloch_renderer as br

st.set_page_config(
    page_title="Bloch Sphere Visualizer",
    layout="wide"
)

if "rho" not in st.session_state:
    st.session_state.rho = qe.psi_to_density(qe.state_0())

if "trajectory" not in st.session_state:
    rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
    st.session_state.trajectory = [(rx, ry, rz)]


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


with st.sidebar:
    st.header("Control Panel")

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

rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
purity = qe.get_purity(st.session_state.rho)

vis_col, diag_col = st.columns([2.2, 1])

with vis_col:
    fig = br.create_bloch_sphere(rx, ry, rz, trajectory=st.session_state.trajectory)
    st.plotly_chart(fig, use_container_width=True, key="bloch_sphere_plot")

with diag_col:
    st.subheader("State Diagnostics")

    st.metric("r_x (X-axis)", f"{rx:.3f}")
    st.metric("r_y (Y-axis)", f"{ry:.3f}")
    st.metric("r_z (Z-axis)", f"{rz:.3f}")
    st.metric("State Purity", f"{purity:.4f}")

    st.divider()

    st.markdown("**Density Matrix $\\rho$:**")


    rho = st.session_state.rho
    r00, r01 = np.round(rho[0, 0], 3), np.round(rho[0, 1], 3)
    r10, r11 = np.round(rho[1, 0], 3), np.round(rho[1, 1], 3)


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

    import time
    import numpy as np
    import streamlit as st
    import quantum_engine as qe
    import bloch_renderer as br


    # --- SIDEBAR: Control Panel ---
    with st.sidebar:
        st.header("Control Panel")


        st.divider()
        st.markdown("**4. Continuous Rabi Oscillations ($H$)**")

        omega_x = st.slider("Ω_x (X-Field Strength)", -5.0, 5.0, 2.0, step=0.5)
        omega_y = st.slider("Ω_y (Y-Field Strength)", -5.0, 5.0, 0.0, step=0.5)
        omega_z = st.slider("Ω_z (Z-Field Detuning)", -5.0, 5.0, 0.0, step=0.5)

        col_play1, col_play2 = st.columns(2)
        if col_play1.button("▶️ Play Animation", use_container_width=True):
            st.session_state.is_playing = True
        if col_play2.button("⏹️ Stop", use_container_width=True):
            st.session_state.is_playing = False

    if "is_playing" not in st.session_state:
        st.session_state.is_playing = False

    # --- MAIN BODY: Dynamic Rendering ---
    st.title("Single-Qubit State Visualization")

    animation_placeholder = st.empty()


    def render_ui_frame():
        with animation_placeholder.container():
            vis_col, diag_col = st.columns([2.2, 1])

            rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
            purity = qe.get_purity(st.session_state.rho)

            with vis_col:
                fig = br.create_bloch_sphere(rx, ry, rz, trajectory=st.session_state.trajectory)
                st.plotly_chart(fig, use_container_width=True, key=f"bloch_plot_{len(st.session_state.trajectory)}")

            with diag_col:
                st.subheader("State Diagnostics")
                st.metric("r_x (X-axis)", f"{rx:.3f}")
                st.metric("r_y (Y-axis)", f"{ry:.3f}")
                st.metric("r_z (Z-axis)", f"{rz:.3f}")
                st.metric("State Purity", f"{purity:.4f}")

                # Formatted Density Matrix Display
                r00, r01 = np.round(st.session_state.rho[0, 0], 3), np.round(st.session_state.rho[0, 1], 3)
                r10, r11 = np.round(st.session_state.rho[1, 0], 3), np.round(st.session_state.rho[1, 1], 3)

                def fmt_c(c: complex) -> str:
                    real_part = f"{c.real:.3f}"
                    if c.imag == 0: return real_part
                    sign = "+" if c.imag >= 0 else "-"
                    return f"{real_part} {sign} {abs(c.imag):.3f}i"

                latex_matrix = (
                        r"\begin{bmatrix}" + "\n" +
                        f"{fmt_c(r00)} & {fmt_c(r01)} \\\\" + "\n" +
                        f"{fmt_c(r10)} & {fmt_c(r11)}" + "\n" +
                        r"\end{bmatrix}"
                )
                st.latex(r"\rho = " + latex_matrix)


    if st.session_state.is_playing:
        for _ in range(150):
            if not st.session_state.is_playing:
                break

            dt = 0.05
            st.session_state.rho = qe.evolve_hamiltonian(
                st.session_state.rho, omega_x, omega_y, omega_z, dt
            )

            rx, ry, rz = qe.density_to_bloch(st.session_state.rho)
            st.session_state.trajectory.append((rx, ry, rz))

            render_ui_frame()

            time.sleep(0.03)
    else:
        render_ui_frame()

