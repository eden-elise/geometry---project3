import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle

# --- CONFIGURATION ---
# Define the circle parameters (a, b, c, d)
# a(x^2 + y^2) + bx + cy + d = 0
# For a standard circle centered at (x0, y0) with radius R:
# x0 = -b/(2a), y0 = -c/(2a)
# R^2 = (b^2 + c^2 - 4ad) / (4a^2)

# Standard Circle example: x^2 + y^2 - 4x + 6y + 4 = 0
# Centered at (2, -3), Radius R=3
a_val, b_val, c_val, d_val = 1.0, -4.0, 6.0, 4.0

# 1. Circle Analysis in R^2
if a_val == 0:
    raise ValueError("Parameter 'a' cannot be zero for a standard circle.")

x0 = -b_val / (2 * a_val)
y0 = -c_val / (2 * a_val)
r_sq = (b_val**2 + c_val**2 - 4 * a_val * d_val) / (4 * a_val**2)

if r_sq < 0:
    raise ValueError("Parameters define an imaginary circle (b^2 + c^2 - 4ad < 0).")

radius = np.sqrt(r_sq)
print(f"Circle detected: Center=({x0}, {y0}), Radius={radius:.2f}")


# 2. Setup Figures
fig = plt.figure(figsize=(16, 8))

# --- LEFT PLOT: R^2 Circle ---
ax_2d = fig.add_subplot(1, 2, 1)

# Set plot limits based on circle dimensions
margin = radius * 0.5
ax_2d.set_xlim(x0 - radius - margin, x0 + radius + margin)
ax_2d.set_ylim(y0 - radius - margin, y0 + radius + margin)

# Create and add the circle patch
circle_patch = Circle((x0, y0), radius, edgecolor='darkblue', facecolor='royalblue', alpha=0.6, lw=2, label='Circle')
ax_2d.add_patch(circle_patch)

# Plot center point
ax_2d.plot(x0, y0, 'ko', markersize=6)
ax_2d.text(x0+0.1, y0+0.1, f'Center ({x0:.1f}, {y0:.1f})', fontsize=10)

# Formatting 2D
title_2d = f'2D Geometry: $a(x^2+y^2) + bx + cy + d = 0$\n$a={a_val}, b={b_val}, c={c_val}, d={d_val}$'
ax_2d.set_title(title_2d, fontsize=14)
ax_2d.set_xlabel('$x$', fontsize=12)
ax_2d.set_ylabel('$y$', fontsize=12)
ax_2d.set_aspect('equal', adjustable='box')
ax_2d.grid(True, linestyle='--', alpha=0.5)
ax_2d.legend()


# --- RIGHT PLOT: R^4 Lifting & Tangent Plane ---
ax_3d = fig.add_subplot(1, 2, 2, projection='3d')

# Define the "Circle Vector" n = (a, b, c, d)
n = np.array([a_val, b_val, c_val, d_val])

# Vector visualization setup
origin = np.zeros(4)
v_start = origin[:3] # We only plot a 3D projection: (a, b, c)
v_end = n[:3]

# Plot the vector (representing n) in 3D projection
ax_3d.quiver(0, 0, 0, v_end[0], v_end[1], v_end[2], color='red', lw=3, label='Circle Vector $\\mathbf{n}=(a,b,c)$ (Proj.)')

# Define Tangent Plane using meshgrid
# We define a plane normal to n=(a,b,c,d) at a point. For lifting to light cone,
# we need a canonical point. Let's use origin P_base=(0,0,0,d) for simplicity of visual.
# General equation: (P - P_base) . n = 0

# Create mesh in xy (b, c dimension in the vector space)
grid_lim = 10
X, Y = np.meshgrid(np.linspace(-grid_lim, grid_lim, 20),
                   np.linspace(-grid_lim, grid_lim, 20))

# Solve for Z (a dimension) using (P-0).n = 0
# a*X + b*Y + c*Z = 0 => Z = -(a*X + b*Y) / c (Assuming c!=0, otherwise transpose)
# Here, we need to map our variables (a, b, c, d) to (X, Y, Z, W).
# Since we plot 3D, we must project n. Let's make n_proj = (a, b, c).
# Tangent plane projection at origin: a*X + b*Y + c*Z = 0.
Z = -(n[0] * X + n[1] * Y) / n[2]

# Plot the Tangent Plane
ax_3d.plot_surface(X, Y, Z, color='lightgray', alpha=0.4, shade=True, label='Tangent Plane at Origin')

# Plot Tangent Point (Origin projection)
ax_3d.scatter(0, 0, 0, color='black', s=100)

# Adjust 3D View and Labels
view_scale = grid_lim * 1.5
ax_3d.set_xlim(-view_scale, view_scale)
ax_3d.set_ylim(-view_scale, view_scale)
ax_3d.set_zlim(-view_scale, view_scale)

ax_3d.set_title('3D Representation: Lifted Vector Space', fontsize=14)
ax_3d.set_xlabel('Component $a$ (quadratic)', fontsize=12)
ax_3d.set_ylabel('Component $b$ (linear X)', fontsize=12)
ax_3d.set_zlabel('Component $c$ (linear Y)', fontsize=12)

# Fix 3D aspect ratio to equal
# (This requires a workaround in older matplotlib, setting equal limits helps)
ax_3d.set_box_aspect([1,1,1])

plt.tight_layout()
plt.show()
