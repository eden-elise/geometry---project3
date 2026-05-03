"""
Inverse Stereographic Projection  R2 -> S2
Each plane point Q is lifted to the sphere by:
  - Drawing a ray from N through Q
  - The sphere point is where that ray crosses S2

Run:  manim -pql inverse_stereo.py InverseStereoProjection
"""

from manim import *
import numpy as np


def inverse_stereo(x, y):
    r2 = x**2 + y**2
    t = 2.0 / (r2 + 1)
    return np.array([t * x, t * y, 1 - t])


class InverseStereoProjection(ThreeDScene):
    def construct(self):

        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)

        sphere = Surface(
            lambda u, v: np.array([
                np.cos(v) * np.sin(u),
                np.sin(v) * np.sin(u),
                np.cos(u),
            ]),
            u_range=[0.05, PI - 0.05],
            v_range=[0, TAU],
            resolution=(18, 36),
            fill_opacity=0.15,
            stroke_color=BLUE_B,
            stroke_width=0.4,
            fill_color=BLUE_E,
        )

        plane = Surface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-2.8, 2.8],
            v_range=[-2.8, 2.8],
            resolution=(2, 2),
            fill_opacity=0.10,
            stroke_color=GRAY,
            stroke_width=0.4,
            fill_color=GRAY_D,
        )

        axes = ThreeDAxes(
            x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[-1.5, 1.5, 1],
            x_length=6, y_length=6, z_length=3,
            axis_config={"stroke_width": 1.2, "color": GRAY},
        )

        N_pos = np.array([0.0, 0.0, 1.0])
        N_dot = Dot3D(N_pos, color=RED, radius=0.08)
        N_label = Text("N", font_size=28, color=RED)
        self.add_fixed_orientation_mobjects(N_label)
        N_label.move_to([0.2, 0.05, 1.2])

        plane_points_2d = [
            (-1.5,  0.5),
            ( 1.2,  1.3),
            ( 1.8, -0.8),
            (-0.6, -1.6),
            ( 0.2,  0.7),
        ]
        colors = [YELLOW, GREEN, ORANGE, PINK, TEAL]

        self.play(Create(axes), Create(sphere), Create(plane), run_time=2)
        self.play(FadeIn(N_dot), FadeIn(N_label))
        self.wait(0.5)

        title = Text("Inverse Stereographic Projection  R2 -> S2",
                     font_size=26, color=YELLOW).to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))

        formula = Text("t(x,y): ray from N through Q hits S2",
                       font_size=20, color=TEAL).next_to(title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(formula)
        self.play(Write(formula))
        self.wait(0.5)

        for (px, py), col in zip(plane_points_2d, colors):

            Q = np.array([px, py, 0.0])
            P = inverse_stereo(px, py)

            # 1. plane point appears
            q_dot = Dot3D(Q, color=col, radius=0.10)
            self.play(FadeIn(q_dot), run_time=0.5)

            # 2. ray from N down through sphere point and on to Q
            ray = Line3D(
                start=N_pos,
                end=Q + 0.15 * (Q - N_pos),
                color=col,
                stroke_width=1.8,
            )
            self.play(Create(ray), run_time=0.8)

            # 3. sphere intersection lights up
            p_dot = Dot3D(P, color=col, radius=0.10)
            self.play(FadeIn(p_dot), run_time=0.5)
            self.wait(0.4)

        self.wait(0.5)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(9)
        self.stop_ambient_camera_rotation()
        self.wait(1)