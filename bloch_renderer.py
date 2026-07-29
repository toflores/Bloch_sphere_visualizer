import numpy as np
import plotly.graph_objects as go
import streamlit as st


def _generate_sphere_mesh(resolution: int = 24):
    """Generates parameterized meshgrid coordinates for a unit sphere."""
    theta = np.linspace(0, np.pi, resolution)
    phi = np.linspace(0, 2 * np.pi, resolution)
    THETA, PHI = np.meshgrid(theta, phi)
    X = np.sin(THETA) * np.cos(PHI)
    Y = np.sin(THETA) * np.sin(PHI)
    Z = np.cos(THETA)
    return X, Y, Z


def _generate_circle(plane: str = 'z', radius: float = 1.0, points: int = 60):
    """Generates 3D coordinates for equator and meridian wireframe rings."""
    t = np.linspace(0, 2 * np.pi, points)
    if plane == 'z':
        return np.cos(t) * radius, np.sin(t) * radius, np.zeros_like(t)
    elif plane == 'x':
        return np.zeros_like(t), np.cos(t) * radius, np.sin(t) * radius
    elif plane == 'y':
        return np.cos(t) * radius, np.zeros_like(t), np.sin(t) * radius
    return np.zeros_like(t), np.zeros_like(t), np.zeros_like(t)


@st.cache_data
def _get_static_traces(show_wireframe: bool = True):
    """Sphere, wireframe, axes, labels — computed once and cached immutably."""
    traces = []

    # 1. Translucent Surface Mesh
    X, Y, Z = _generate_sphere_mesh()
    traces.append(go.Surface(
        x=X, y=Y, z=Z, opacity=0.12,
        colorscale=[[0, 'lightgrey'], [1, 'lightgrey']],
        showscale=False, hoverinfo='none', name='Bloch Surface'
    ))

    # 2. Great Circle Wireframes
    if show_wireframe:
        for plane, color in [('z', '#60A5FA'), ('x', '#34D399'), ('y', '#F87171')]:
            cx, cy, cz = _generate_circle(plane=plane)
            traces.append(go.Scatter3d(
                x=cx, y=cy, z=cz, mode='lines',
                line=dict(color=color, width=2, dash='dot'),
                hoverinfo='none', showlegend=False
            ))

    # 3. Cartesian Coordinate Axes
    axis_line = dict(color='#9CA3AF', width=2)
    for axis in [[[-1.2, 1.2], [0, 0], [0, 0]],
                 [[0, 0], [-1.2, 1.2], [0, 0]],
                 [[0, 0], [0, 0], [-1.2, 1.2]]]:
        traces.append(go.Scatter3d(
            x=axis[0], y=axis[1], z=axis[2], mode='lines',
            line=axis_line, hoverinfo='none', showlegend=False
        ))

    # 4. Basis State Labels
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
    """Builds the complete 3D Plotly Figure by layering dynamic traces onto cached static traces."""
    # Convert cached tuple to list to safely append dynamic traces
    fig = go.Figure(data=list(_get_static_traces(show_wireframe)))

    # 1. Trajectory Trail (if >= 2 points exist)
    if trajectory and len(trajectory) > 1:
        tx, ty, tz = zip(*trajectory)
        fig.add_trace(go.Scatter3d(
            x=tx, y=ty, z=tz, mode='lines',
            line=dict(color='#F59E0B', width=5),
            name='Trajectory', hoverinfo='none'
        ))

    # 2. State Vector Ray (Origin -> Surface)
    fig.add_trace(go.Scatter3d(
        x=[0, rx], y=[0, ry], z=[0, rz], mode='lines',
        line=dict(color='#EF4444', width=7),
        name='State Ray', hoverinfo='none'
    ))

    # 3. State Vector Endpoint Marker
    fig.add_trace(go.Scatter3d(
        x=[rx], y=[ry], z=[rz], mode='markers',
        marker=dict(size=8, color='#B91C1C', symbol='circle'),
        name='State Vector',
        hovertemplate="<b>(x, y, z):</b> (%{x:.3f}, %{y:.3f}, %{z:.3f})<extra></extra>"
    ))

    # 4. Scene Layout & Camera Locking
    fig.update_layout(
        height=600,
        uirevision='constant',  # Preserves user's camera angle across fragment refreshes
        scene=dict(
            aspectmode='cube',
            # Expanded ranges to [-1.35, 1.35] so labels at ±1.28 never get clipped or cause box resizing
            xaxis=dict(visible=False, range=[-1.35, 1.35]),
            yaxis=dict(visible=False, range=[-1.35, 1.35]),
            zaxis=dict(visible=False, range=[-1.35, 1.35]),
            camera=dict(eye=dict(x=1.2, y=1.2, z=1.0))
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    return fig