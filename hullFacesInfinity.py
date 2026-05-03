"""
Continuation of ConvexHullS2 — starts at the final polytope and
highlights all faces containing N (the unbounded Voronoi regions in R2).

Run:  manim -pql highlight_N_faces.py HighlightNFaces
"""

from manim import *
import numpy as np
from scipy.spatial import ConvexHull


def inverse_stereo(x, y):
    r2 = x**2 + y**2
    denom = r2 + 1
    return np.array([2*x/denom, 2*y/denom, (r2-1)/denom])


PLANE_PTS = [
    ( 0.30,  0.25), (-0.50,  0.35), ( 0.55, -0.45), (-0.30, -0.60),
    ( 0.70,  0.40), (-0.65, -0.30), ( 0.20, -0.75),
    ( 1.60,  0.50), (-1.40,  0.80), ( 0.60,  1.70), (-0.70, -1.60),
    ( 1.80, -1.00), (-1.90,  0.30), ( 0.40, -1.80), (-1.20,  1.50),
]

COLORS = [
    YELLOW, ORANGE, RED_B, GOLD, GREEN_B, TEAL_B, PINK,
    BLUE_B, PURPLE_B, MAROON_B, GREEN, BLUE_C, TEAL, YELLOW_B, PURPLE_A,
]

SPHERE_SCALE = 1.4
SCALED_PTS   = np.array([inverse_stereo(x, y) for x, y in PLANE_PTS]) * SPHERE_SCALE
N_POS        = np.array([0.0, 0.0, SPHERE_SCALE])
ALL_SCALED   = np.vstack([SCALED_PTS, N_POS])
N_IDX        = 15   # index of N in ALL_SCALED

HULL = ConvexHull(ALL_SCALED)
TOUCHING     = [s for s in HULL.simplices if N_IDX in s]
NOT_TOUCHING = [s for s in HULL.simplices if N_IDX not in s]


class HighlightNFaces(ThreeDScene):
    def construct(self):

        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)

        # ── Rebuild the exact ending state of ConvexHullS2 ───────────────
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

        N_dot = Dot3D(N_POS, color=RED, radius=0.06)
        N_label = Text("N", font_size=24, color=RED)
        self.add_fixed_orientation_mobjects(N_label)
        N_label.move_to([0.18, 0.05, SPHERE_SCALE + 0.18])

        sphere_dots = VGroup(*[
            Dot3D(SCALED_PTS[i], color=COLORS[i], radius=0.055)
            for i in range(len(PLANE_PTS))
        ])

        # All hull faces in plain blue — the ending state
        all_faces = VGroup()
        for simplex in HULL.simplices:
            v0, v1, v2 = ALL_SCALED[simplex[0]], ALL_SCALED[simplex[1]], ALL_SCALED[simplex[2]]
            face = Polygon(v0, v1, v2,
                           fill_color=BLUE_C, fill_opacity=0.30,
                           stroke_color=WHITE, stroke_width=1.2)
            all_faces.add(face)

        title = Text("Convex Hull of 16 Lifted Points on S²",
                     font_size=26, color=YELLOW).to_corner(UL)
        end_label = Text("conv(τ_N(P))  —  convex polytope in ℝ³",
                         font_size=20, color=YELLOW).next_to(title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(title, end_label)

        # Add everything instantly — this is the start state
        self.add(axes, sphere, all_faces, sphere_dots, N_dot, N_label)
        self.wait(1.5)

        # ── Transition: new label ─────────────────────────────────────────
        self.play(FadeOut(end_label))
        new_label = Text("Which faces contain N?",
                         font_size=22, color=TEAL).next_to(title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(new_label)
        self.play(Write(new_label))
        self.wait(0.5)

        # ── Dim non-N faces, highlight N faces ───────────────────────────
        # Build dimmed versions of non-touching faces
        dim_faces = VGroup()
        for simplex in NOT_TOUCHING:
            v0, v1, v2 = ALL_SCALED[simplex[0]], ALL_SCALED[simplex[1]], ALL_SCALED[simplex[2]]
            face = Polygon(v0, v1, v2,
                           fill_color=BLUE_E, fill_opacity=0.12,
                           stroke_color=GRAY, stroke_width=0.6)
            dim_faces.add(face)

        # Build bright highlighted N-touching faces
        N_faces = VGroup()
        for simplex in TOUCHING:
            v0, v1, v2 = ALL_SCALED[simplex[0]], ALL_SCALED[simplex[1]], ALL_SCALED[simplex[2]]
            face = Polygon(v0, v1, v2,
                           fill_color=YELLOW, fill_opacity=0.60,
                           stroke_color=WHITE, stroke_width=2.2)
            N_faces.add(face)

        # Swap all_faces → dim + highlighted in one smooth play
        self.play(
            FadeOut(all_faces),
            FadeIn(dim_faces),
            run_time=0.7,
        )
        self.play(
            FadeIn(N_faces),
            N_dot.animate.scale(2.0).set_color(YELLOW),
            run_time=1.2,
        )
        self.wait(0.6)

        # ── Explanation label ─────────────────────────────────────────────
        self.play(FadeOut(new_label))
        explain = Text(
            f"{len(TOUCHING)} faces touch N  →  unbounded Voronoi regions in ℝ²",
            font_size=19, color=YELLOW,
        ).next_to(title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(explain)
        self.play(Write(explain))
        self.wait(0.5)

        sub = Text(
            "Removing these faces leaves the Delaunay complex C(P)",
            font_size=17, color=TEAL,
        ).next_to(explain, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(sub)
        self.play(Write(sub))
        self.wait(0.5)

        # ── Orbit ─────────────────────────────────────────────────────────
        self.begin_ambient_camera_rotation(rate=0.18)
        self.wait(12)
        self.stop_ambient_camera_rotation()
        self.wait(1)