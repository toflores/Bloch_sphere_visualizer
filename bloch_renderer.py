import numpy as np
import plotly.graph_objects as go
import streamlit as st


def _generate_sphere_mesh(resolution: int = 24):
    theta = np.linspace(0, np.pi, resolution)
    phi = np.linspace(0, 2 * np.pi, resolution)
    THETA, PHI = np.meshgrid(theta, phi)
    X = np.sin(THETA) * np.cos(PHI)
    Y = np.sin(THETA) * np.sin(PHI)
    Z = np.cos(THETA)
    return X, Y, Z


def _generate_circle(plane: str = 'z', radius: float = 1.0, points: int = 60):
    t = np.linspace(0, 2 * np.pi, points)
    if plane == 'z':
        return np.cos(t) * radius, np.sin(t) * radius, np.zeros_like(t)
    elif plane == 'x':
        return np.zeros_like(t), np.cos(t) * radius, np.sin(t) * radius
    elif plane == 'y':
        return np.cos(t) * radius, np.zeros_like(t), np.sin(t) * radius


@st.cache_resource
def _get_static_traces(show_wireframe: bool = True):
    """Sphere, wireframe, axes, labels — built once per session, never regenerated per frame."""
    traces = []

    X, Y, Z = _generate_sphere_mesh()
    traces.append(go.Surface(
        x=X, y=Y, z=Z, opacity=0.12,
        colorscale=[[0, 'lightgrey'], [1, 'lightgrey']],
        showscale=False, hoverinfo='none', name='Bloch Surface'
    ))

    if show_wireframe:
        for plane, color in [('z', '#60A5FA'), ('x', '#34D399'), ('y', '#F87171')]:
            cx, cy, cz = _generate_circle(plane=plane)
            traces.append(go.Scatter3d(
                x=cx, y=cy, z=cz, mode='lines',
                line=dict(color=color, width=2, dash='dot'),
                hoverinfo='none', showlegend=False
            ))

    axis_line = dict(color='#9CA3AF', width=2)
    for axis in [[[-1.2, 1.2], [0, 0], [0, 0]],
                 [[0, 0], [-1.2, 1.2], [0, 0]],
                 [[0, 0], [0, 0], [-1.2, 1.2]]]:
        traces.append(go.Scatter3d(
            x=axis[0], y=axis[1], z=axis[2], mode='lines',
            line=axis_line, hoverinfo='none', showlegend=False
        ))

    labels = [
        (0, 0, 1.28, "|0⟩ (+Z)", "top center"),
        (0, 0, -1.28, "|1⟩ (-Z)", "bottom center"),
        (1.28, 0, 0, "|+⟩ (+X)", "middle right"),
        (-1.28, 0, 0, "|-⟩ (-X)", "middle left"),
        (0, 1.28, 0, "|+i⟩ (+Y)", "top right"),
        (0, -1.28, 0, "|-i⟩ (-Y)", "bottom left"),
    ]
    for lx, ly, lz, text, pos in labels:
        traces.append(go.Scatter3d(
            x=[lx], y=[ly], z=[lz], mode='text',
            text=[f"<b>{text}</b>"], textposition=pos,
            textfont=dict(size=13, color='#374151'),
            hoverinfo='none', showlegend=False
        ))

    return tuple(traces)


def create_bloch_sphere(rx, ry, rz, trajectory=None, show_wireframe: bool = True) -> go.Figure:
    fig = go.Figure(data=_get_static_traces(show_wireframe))

    if trajectory and len(trajectory) > 1:
        tx, ty, tz = zip(*trajectory)
        fig.add_trace(go.Scatter3d(
            x=tx, y=ty, z=tz, mode='lines',
            line=dict(color='#F59E0B', width=5),
            name='Trajectory', hoverinfo='none'
        ))

    fig.add_trace(go.Scatter3d(
        x=[0, rx], y=[0, ry], z=[0, rz], mode='lines',
        line=dict(color='#EF4444', width=7), name='State Ray', hoverinfo='none'
    ))

    fig.add_trace(go.Scatter3d(
        x=[rx], y=[ry], z=[rz], mode='markers',
        marker=dict(size=8, color='#B91C1C', symbol='circle'),
        name='State Vector',
        hovertemplate="<b>(x, y, z):</b> (%{x:.3f}, %{y:.3f}, %{z:.3f})<extra></extra>"
    ))

    fig.update_layout(
        height=600,
        uirevision='constant',
        scene=dict(
            aspectmode='cube',
            xaxis=dict(visible=False, range=[-1.1, 1.1]),
            yaxis=dict(visible=False, range=[-1.1, 1.1]),
            zaxis=dict(visible=False, range=[-1.1, 1.1]),
            camera=dict(eye=dict(x=1.2, y=1.2, z=1.0))
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    return fig