"""
Continuation of HighlightNFaces — projects the non-N faces of the
convex hull back down to R2 via central projection from N,
revealing the Delaunay triangulation.

Run:  manim -pql delaunay_projection.py DelaunayProjection
"""

from manim import *
import numpy as np
from scipy.spatial import ConvexHull


def inverse_stereo(x, y):
    r2 = x**2 + y**2
    denom = r2 + 1
    return np.array([2*x/denom, 2*y/denom, (r2-1)/denom])


def project_from_N(v, N, z_plane=0.0):
    """Central projection: shoot ray from N through v, land on z=z_plane."""
    t = (z_plane - N[2]) / (v[2] - N[2])
    return N + t * (v - N)


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
N_IDX        = 15

HULL         = ConvexHull(ALL_SCALED)
TOUCHING     = [s for s in HULL.simplices if N_IDX in s]
NOT_TOUCHING = [s for s in HULL.simplices if N_IDX not in s]


class DelaunayProjection(ThreeDScene):
    def construct(self):

        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)

        # ── Rebuild ending state of HighlightNFaces ──────────────────────
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

        N_dot = Dot3D(N_POS, color=YELLOW, radius=0.09)
        N_label = Text("N", font_size=24, color=YELLOW)
        self.add_fixed_orientation_mobjects(N_label)
        N_label.move_to([0.18, 0.05, SPHERE_SCALE + 0.18])

        sphere_dots = VGroup(*[
            Dot3D(SCALED_PTS[i], color=COLORS[i], radius=0.055)
            for i in range(len(PLANE_PTS))
        ])

        # Dim non-N faces (grey)
        dim_faces = VGroup()
        for simplex in NOT_TOUCHING:
            v0, v1, v2 = ALL_SCALED[simplex[0]], ALL_SCALED[simplex[1]], ALL_SCALED[simplex[2]]
            dim_faces.add(Polygon(v0, v1, v2,
                                  fill_color=BLUE_E, fill_opacity=0.12,
                                  stroke_color=GRAY, stroke_width=0.6))

        # N-touching faces (yellow)
        N_faces = VGroup()
        for simplex in TOUCHING:
            v0, v1, v2 = ALL_SCALED[simplex[0]], ALL_SCALED[simplex[1]], ALL_SCALED[simplex[2]]
            N_faces.add(Polygon(v0, v1, v2,
                                fill_color=YELLOW, fill_opacity=0.60,
                                stroke_color=WHITE, stroke_width=2.2))

        title = Text("Convex Hull of 16 Lifted Points on S²",
                     font_size=26, color=YELLOW).to_corner(UL)
        explain = Text(
            f"{len(TOUCHING)} faces touch N  →  unbounded Voronoi regions in ℝ²",
            font_size=19, color=YELLOW,
        ).next_to(title, DOWN, aligned_edge=LEFT)
        sub = Text(
            "Removing these faces leaves the Delaunay complex C(P)",
            font_size=17, color=TEAL,
        ).next_to(explain, DOWN, aligned_edge=LEFT)

        self.add_fixed_in_frame_mobjects(title, explain, sub)
        self.add(axes, sphere, dim_faces, N_faces, sphere_dots, N_dot, N_label)
        self.wait(1.5)

        # ── Step 1: fade out N-faces and labels, keep only non-N faces ───
        self.play(FadeOut(explain), FadeOut(sub))

        new_label = Text("Project non-N faces down to ℝ² from N",
                         font_size=21, color=TEAL).next_to(title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(new_label)
        self.play(Write(new_label), FadeOut(N_faces), run_time=0.8)
        self.wait(0.4)

        # Brighten the non-N faces so we can see what we're projecting
        bright_faces = VGroup()
        for simplex in NOT_TOUCHING:
            v0, v1, v2 = ALL_SCALED[simplex[0]], ALL_SCALED[simplex[1]], ALL_SCALED[simplex[2]]
            bright_faces.add(Polygon(v0, v1, v2,
                                     fill_color=BLUE_C, fill_opacity=0.40,
                                     stroke_color=WHITE, stroke_width=1.4))

        self.play(FadeOut(dim_faces), FadeIn(bright_faces), run_time=0.6)
        self.wait(0.5)

        # ── Step 2: tilt camera to more top-down view ────────────────────
        self.move_camera(phi=50 * DEGREES, theta=-60 * DEGREES, run_time=2)
        self.wait(0.5)

        # ── Step 3: for each non-N face, shoot rays and draw projected tri─
        delaunay_tris = VGroup()

        for simplex in NOT_TOUCHING:
            sv0 = ALL_SCALED[simplex[0]]
            sv1 = ALL_SCALED[simplex[1]]
            sv2 = ALL_SCALED[simplex[2]]

            # Central projection of each vertex from N to z=0
            pv0 = project_from_N(sv0, N_POS, z_plane=0.0)
            pv1 = project_from_N(sv1, N_POS, z_plane=0.0)
            pv2 = project_from_N(sv2, N_POS, z_plane=0.0)

            # Rays from N through sphere vertices down to plane
            ray0 = Line3D(N_POS, pv0, color=WHITE, stroke_width=0.8)
            ray1 = Line3D(N_POS, pv1, color=WHITE, stroke_width=0.8)
            ray2 = Line3D(N_POS, pv2, color=WHITE, stroke_width=0.8)

            # Projected triangle on the z=0 plane
            tri = Polygon(pv0, pv1, pv2,
                          fill_color=GREEN_C, fill_opacity=0.45,
                          stroke_color=GREEN, stroke_width=1.8)

            self.play(
                Create(ray0), Create(ray1), Create(ray2),
                run_time=0.25,
            )
            self.play(FadeIn(tri), run_time=0.25)
            self.play(
                FadeOut(ray0), FadeOut(ray1), FadeOut(ray2),
                run_time=0.15,
            )
            delaunay_tris.add(tri)

        self.wait(0.5)

        # ── Step 4: fade out sphere geometry, show only the triangulation ─
        self.play(FadeOut(new_label))
        result_label = Text("Delaunay triangulation of P in ℝ²",
                            font_size=22, color=GREEN).next_to(title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(result_label)
        self.play(Write(result_label))
        self.wait(0.3)

        self.play(
            FadeOut(sphere),
            FadeOut(bright_faces),
            FadeOut(sphere_dots),
            FadeOut(N_dot),
            FadeOut(N_label),
            run_time=1.2,
        )

        # Show original plane points for reference
        plane_dots = VGroup(*[
            Dot3D(np.array([px, py, 0.0]), color=COLORS[i], radius=0.07)
            for i, (px, py) in enumerate(PLANE_PTS)
        ])
        self.play(FadeIn(plane_dots), run_time=0.8)
        self.wait(0.5)

        # ── Step 5: top-down view to see the 2D triangulation clearly ─────
        self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, run_time=2.5)
        self.wait(1)

        sub2 = Text("Viewed from above: the Delaunay triangulation in ℝ²",
                    font_size=18, color=TEAL).next_to(result_label, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(sub2)
        self.play(Write(sub2))

        # Orbit gently in top-down mode
        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(8)
        self.stop_ambient_camera_rotation()
        self.wait(1)