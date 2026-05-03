"""
Stereographic Projection  S² → ℝ²
Run:  manim -pql stereo_s2.py StereoProjection
"""

from manim import *
import numpy as np


def stereo_project(point_3d):
    """Map (x, y, z) on unit sphere to (X, Y) in plane via north-pole projection.
    Formula: X = x/(1-z),  Y = y/(1-z)
    """
    x, y, z = point_3d
    denom = 1 - z
    return np.array([x / denom, y / denom, 0])


class StereoProjection(ThreeDScene):
    def construct(self):

        # ── Camera ──────────────────────────────────────────────────────────
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        # ── Sphere ──────────────────────────────────────────────────────────
        sphere = Surface(
            lambda u, v: np.array([
                np.cos(v) * np.sin(u),
                np.sin(v) * np.sin(u),
                np.cos(u)
            ]),
            u_range=[0.05, PI - 0.05],   # avoid poles for mesh
            v_range=[0, TAU],
            resolution=(18, 36),
            fill_opacity=0.15,
            stroke_color=BLUE_B,
            stroke_width=0.4,
            fill_color=BLUE_E,
        )

        # ── Projection plane  z = -1 ─────────────────────────────────────
        plane = Surface(
            lambda u, v: np.array([u, v, -1]),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(2, 2),
            fill_opacity=0.12,
            stroke_color=GRAY,
            stroke_width=0.3,
            fill_color=GRAY_D,
        )
        plane_label = Text("ℝ²", font_size=22, color=GRAY_B).move_to([2.6, 2.6, -1])

        # ── Axes ─────────────────────────────────────────────────────────
        axes = ThreeDAxes(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[-2, 2, 1],
            x_length=6, y_length=6, z_length=4,
            axis_config={"stroke_width": 1.2, "color": GRAY},
        )

        # ── North Pole ───────────────────────────────────────────────────
        N_dot = Dot3D(point=np.array([0, 0, 1]), color=RED, radius=0.08)
        N_label = Text("N", font_size=26, color=RED)
        self.add_fixed_orientation_mobjects(N_label)
        N_label.move_to([0.22, 0, 1.2])

        # ── Sample points on the sphere  (avoid north pole: z < 0.85) ───
        # Format: (theta from z-axis, phi from x-axis)
        sample_angles = [
            (2.2,  0.5),    # lower-left front
            (1.4,  2.3),    # mid-left back
            (2.6,  3.8),    # lower-right back
            (1.0,  5.0),    # upper-right front
            (2.0,  1.5),    # mid-front
        ]
        colors = [YELLOW, GREEN, ORANGE, PINK, TEAL]

        sphere_pts = []
        plane_pts  = []
        for (u, v) in sample_angles:
            p = np.array([np.cos(v)*np.sin(u), np.sin(v)*np.sin(u), np.cos(u)])
            q = stereo_project(p)
            q[2] = -1          # sit on projection plane
            sphere_pts.append(p)
            plane_pts.append(q)

        # ── Build scene objects ──────────────────────────────────────────
        self.play(Create(axes), Create(sphere), Create(plane), run_time=2)
        self.play(FadeIn(N_dot), FadeIn(N_label))
        self.wait(0.5)

        # Add title (fixed to camera)
        title = Text("Stereographic Projection  S² → ℝ²", font_size=28, color=YELLOW)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))

        # Formula
        formula = Text(
    "σ_N(x,y,z) = ( x/(1-z),  y/(1-z) )",
    font_size=22, color=TEAL
).next_to(title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(formula)
        self.play(Write(formula))
        self.wait(0.5)

        # ── Animate each point one at a time ────────────────────────────
        for i, (sp, pp, col) in enumerate(zip(sphere_pts, plane_pts, colors)):
            # Dot on sphere
            s_dot = Dot3D(sp, color=col, radius=0.09)
            self.play(FadeIn(s_dot), run_time=0.4)

            # Ray from N through sphere point to plane
            N_pos = np.array([0, 0, 1])
            # extend ray: parameterise  N + t*(sp - N),  hit z=-1
            # -1 = 1 + t*(sp[2]-1)  =>  t = -2/(sp[2]-1) = 2/(1-sp[2])
            t_end = 2.0 / (1 - sp[2]) + 0.05   # slightly past plane
            ray_end = N_pos + t_end * (sp - N_pos)

            ray = Line3D(
                start=N_pos, end=ray_end,
                color=col, stroke_width=1.5,
            )
            self.play(Create(ray), run_time=0.7)

            # Dot on plane
            p_dot = Dot3D(pp, color=col, radius=0.09)
            self.play(FadeIn(p_dot), run_time=0.4)

            self.wait(0.3)

        # ── Slow orbit ───────────────────────────────────────────────────
        self.wait(0.5)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(8)
        self.stop_ambient_camera_rotation()
        self.wait(1)