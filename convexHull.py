"""
Convex Hull in R3 of 15 points lifted onto S2
via inverse stereographic projection.

Points are chosen so roughly half have r<1 (lower hemisphere)
and half have r>1 (upper hemisphere), giving a proper spread over S2.

Run:  manim -pql convex_hull_s2.py ConvexHullS2
"""

from manim import *
import numpy as np
from scipy.spatial import ConvexHull


def inverse_stereo(x, y):
    """
    τ_N(x,y) = ( 2x/(r²+1),  2y/(r²+1),  (r²-1)/(r²+1) )
    r<1 → lower hemisphere (z<0)
    r>1 → upper hemisphere (z>0)
    """
    r2 = x**2 + y**2
    denom = r2 + 1
    return np.array([2*x/denom, 2*y/denom, (r2-1)/denom])


# 7 points INSIDE unit circle  (r<1) → lower hemisphere
# 8 points OUTSIDE unit circle (r>1) → upper hemisphere
PLANE_PTS = [
    # inside unit circle → lower hemisphere
    ( 0.30,  0.25),   # r=0.39
    (-0.50,  0.35),   # r=0.61
    ( 0.55, -0.45),   # r=0.71
    (-0.30, -0.60),   # r=0.67
    ( 0.70,  0.40),   # r=0.81
    (-0.65, -0.30),   # r=0.72
    ( 0.20, -0.75),   # r=0.78
    # outside unit circle → upper hemisphere
    ( 1.60,  0.50),   # r=1.68
    (-1.40,  0.80),   # r=1.61
    ( 0.60,  1.70),   # r=1.80
    (-0.70, -1.60),   # r=1.74
    ( 1.80, -1.00),   # r=2.06
    (-1.90,  0.30),   # r=1.92
    ( 0.40, -1.80),   # r=1.84
    (-1.20,  1.50),   # r=1.92
]

COLORS = [
    # lower hemisphere — warm tones
    YELLOW, ORANGE, RED_B, GOLD, GREEN_B, TEAL_B, PINK,
    # upper hemisphere — cool tones
    BLUE_B, PURPLE_B, MAROON_B, GREEN, BLUE_C, TEAL, YELLOW_B, PURPLE_A,
]

SPHERE_SCALE = 1.4
N_SPHERE     = np.array([0.0, 0.0, SPHERE_SCALE])   # north pole on scaled sphere
SPHERE_PTS   = np.array([inverse_stereo(x, y) for x, y in PLANE_PTS])
SCALED_PTS   = SPHERE_PTS * SPHERE_SCALE
ALL_SCALED   = np.vstack([SCALED_PTS, np.array([0.0, 0.0, SPHERE_SCALE])])  # 16 pts incl. N


class ConvexHullS2(ThreeDScene):
    def construct(self):

        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)

        sphere = Surface(
            lambda u, v: SPHERE_SCALE * np.array([
                np.cos(v) * np.sin(u),
                np.sin(v) * np.sin(u),
                np.cos(u),
            ]),
            u_range=[0.05, PI - 0.05],
            v_range=[0, TAU],
            resolution=(20, 40),
            fill_opacity=0.08,
            stroke_color=BLUE_B,
            stroke_width=0.3,
            fill_color=BLUE_E,
        )

        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1], y_range=[-2.5, 2.5, 1], z_range=[-2, 2, 1],
            x_length=5, y_length=5, z_length=4,
            axis_config={"stroke_width": 1.0, "color": GRAY},
        )

        N_pos  = np.array([0.0, 0.0,  SPHERE_SCALE])
        N_dot  = Dot3D(N_pos, color=RED, radius=0.06)
        N_label = Text("N", font_size=24, color=RED)
        self.add_fixed_orientation_mobjects(N_label)
        N_label.move_to([0.18, 0.05, SPHERE_SCALE + 0.18])

        title = Text("Convex Hull of 16 Lifted Points on S²",
                     font_size=26, color=YELLOW).to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)

        self.play(Create(axes), Create(sphere), run_time=1.5)
        self.play(FadeIn(N_dot), FadeIn(N_label), Write(title))
        self.wait(0.3)

        # ── Step 1: lift all 15 points + include N ───────────────────────────────────
        step1 = Text("Lifting P ⊂ ℝ² onto S² via τ_N",
                     font_size=20, color=TEAL).next_to(title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(step1)
        self.play(Write(step1))
        self.wait(0.2)

        sphere_dots = []
        for i, ((px, py), col) in enumerate(zip(PLANE_PTS, COLORS)):
            Q = np.array([px, py, 0.0])
            P = SCALED_PTS[i]

            q_dot = Dot3D(Q, color=col, radius=0.07)
            p_dot = Dot3D(P, color=col, radius=0.055)
            ray   = Line3D(start=N_pos, end=Q + 0.1*(Q - N_pos),
                           color=col, stroke_width=1.2)

            self.play(FadeIn(q_dot), run_time=0.15)
            self.play(Create(ray),   run_time=0.30)
            self.play(FadeIn(p_dot), run_time=0.20)
            self.play(FadeOut(ray), FadeOut(q_dot), run_time=0.20)
            sphere_dots.append(p_dot)

        # N is already shown — flash it to mark it as part of the set
        self.play(N_dot.animate.scale(1.6).set_color(YELLOW), run_time=0.3)
        self.play(N_dot.animate.scale(1/1.6).set_color(RED),  run_time=0.3)

        self.wait(0.4)

        # ── Step 2: build convex hull ─────────────────────────────────────
        self.play(FadeOut(step1))
        step2 = Text("Building conv( τ_N(P) ) in ℝ³",
                     font_size=20, color=TEAL).next_to(title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(step2)
        self.play(Write(step2))
        self.wait(0.2)

        hull = ConvexHull(ALL_SCALED)
        for simplex in hull.simplices:
            v0, v1, v2 = ALL_SCALED[simplex[0]], ALL_SCALED[simplex[1]], ALL_SCALED[simplex[2]]
            face = Polygon(v0, v1, v2,
                           fill_color=BLUE_C, fill_opacity=0.30,
                           stroke_color=WHITE, stroke_width=1.2)
            self.play(Create(face), run_time=0.20)

        self.wait(0.5)
        self.play(FadeOut(step2))
        step3 = Text("conv(τ_N(P))  —  convex polytope in ℝ³",
                     font_size=20, color=YELLOW).next_to(title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(step3)
        self.play(Write(step3))

        self.begin_ambient_camera_rotation(rate=0.18)
        self.wait(12)
        self.stop_ambient_camera_rotation()
        self.wait(1)