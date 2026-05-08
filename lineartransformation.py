import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import string

# --- INPUT: Matrix Transformation ---
# Define your 2x2 Linear Transformation Matrix here:
# (e.g., Rotation by approx 45 deg)
# M = np.array([[0.7, -0.7],
#               [0.7,  0.7]])

# Example: A Shear Matrix
M = np.array([[1.0, 1.2],
              [0.0, 1.0]])

# General settings
N_POINTS = 10
SEED = 42

# 1. Generate and Analyze Original Points
np.random.seed(SEED)
points_orig = np.random.rand(N_POINTS, 2)
hull_orig = ConvexHull(points_orig)
indices_orig = hull_orig.vertices # Sorted counter-clockwise indices

# 2. Apply Linear Transformation
# Points are (N, 2). Transform is M @ Vector.
# Matrix mult requires (2, 2) @ (2, N), then transpose back.
points_trans = (M @ points_orig.T).T

# 3. Analyze Transformed Points
hull_trans = ConvexHull(points_trans)
indices_trans = hull_trans.vertices # Sorted order might change

# --- Mapping Identity (The Labeling Strategy) ---
# We map the data point indices of the ORIGINAL hull to alphabetical labels (A, B, C...)
letters = string.ascii_uppercase
# Create a fixed identity dictionary: e.g., points_orig[5] is 'A'
identity_map = {idx: letters[i] for i, idx in enumerate(indices_orig)}

# --- 4. Plotting Function ---
def draw_hull_plot(ax, pts, hull_indices, title, color_scheme):
    # Plot all points in background
    ax.plot(pts[:, 0], pts[:, 1], 'o', color='gray', alpha=0.3)

    # Draw Hull Boundary (closed loop)
    n_hull = len(hull_indices)
    for i in range(n_hull):
        p1 = pts[hull_indices[i]]
        p2 = pts[hull_indices[(i + 1) % n_hull]]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color_scheme['edge'], lw=2.5)

    # Plot & Label Hull Vertices by ID
    for idx in hull_indices:
        pt = pts[idx]
        # Retrieve the canonical alphabetical label assigned to this point index
        label = identity_map[idx]
        
        ax.plot(pt[0], pt[1], 'o', color=color_scheme['pt'], markersize=8)
        
        # Apply offset for readability
        ax.text(pt[0] + 0.02, pt[1] + 0.02, label, 
                fontsize=13, fontweight='bold', color='black')

    ax.set_title(title)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_aspect('equal', adjustable='box') # Preserve geometry

# --- 5. Visualization Setup ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

# Define colors
colors_orig = {'pt': 'navy', 'edge': 'royalblue'}
colors_trans = {'pt': 'darkred', 'edge': 'salmon'}

# Plot 1: Original Space
draw_hull_plot(ax1, points_orig, indices_orig, 
               "Original Space", colors_orig)

# Plot 2: Transformed Space
matrix_str = f"M = [[{M[0,0]:.1f}, {M[0,1]:.1f}], [{M[1,0]:.1f}, {M[1,1]:.1f}]]"
draw_hull_plot(ax2, points_trans, indices_trans, 
               f"Linear Transformation\n{matrix_str}", colors_trans)

plt.tight_layout()
plt.show()
