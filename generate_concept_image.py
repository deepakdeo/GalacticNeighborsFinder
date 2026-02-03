"""
Generate a visualization showing the neighbor-finding concept.

Creates an illustration of galaxies and their neighbors based on proximity,
useful for including in documentation.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch
import matplotlib.patches as mpatches

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('GalacticNeighborsFinder: Neighbor Identification Concept', 
             fontsize=14, fontweight='bold')

# ============================================================================
# LEFT PLOT: Spatial Distribution
# ============================================================================
ax1.set_title('Spatial Distribution\n(RA, DEC, Distance)', fontsize=11, fontweight='bold')

# Create random galaxy positions
np.random.seed(42)
n_galaxies = 20
x = np.random.uniform(0, 100, n_galaxies)
y = np.random.uniform(0, 100, n_galaxies)

# Highlight target galaxy and neighbors
target_idx = 5
target_x, target_y = x[target_idx], y[target_idx]

# Calculate distances from target
distances = np.sqrt((x - target_x)**2 + (y - target_y)**2)
neighbor_indices = np.argsort(distances)[1:6]  # 5 nearest neighbors

# Plot all galaxies
ax1.scatter(x, y, s=100, alpha=0.6, c='lightblue', edgecolors='blue', linewidth=1.5, label='Other Galaxies')

# Plot target galaxy
ax1.scatter(target_x, target_y, s=300, c='red', marker='*', edgecolors='darkred', 
           linewidth=2, label='Target Galaxy', zorder=5)

# Plot neighbors
ax1.scatter(x[neighbor_indices], y[neighbor_indices], s=150, c='lime', edgecolors='green', 
           linewidth=2, label='Neighbors Found', zorder=4)

# Draw search radius
search_radius = 25
circle = Circle((target_x, target_y), search_radius, fill=False, 
               edgecolor='orange', linestyle='--', linewidth=2, label='Search Radius')
ax1.add_patch(circle)

# Draw connections to neighbors
for idx in neighbor_indices:
    ax1.plot([target_x, x[idx]], [target_y, y[idx]], 'g--', alpha=0.5, linewidth=1)

ax1.set_xlim(-10, 110)
ax1.set_ylim(-10, 110)
ax1.set_xlabel('Right Ascension (RA)', fontsize=10)
ax1.set_ylabel('Declination (DEC)', fontsize=10)
ax1.legend(loc='upper right', fontsize=9)
ax1.grid(True, alpha=0.3)

# ============================================================================
# RIGHT PLOT: Proximity Score Distribution
# ============================================================================
ax2.set_title('Proximity Scores\n(Spatial + Kinematic)', fontsize=11, fontweight='bold')

# Generate proximity scores for neighbors
neighbor_distances = distances[neighbor_indices]
neighbor_scores = 1 - (neighbor_distances / np.max(distances))

# Sort by score
sorted_indices = np.argsort(neighbor_scores)[::-1]
sorted_scores = neighbor_scores[sorted_indices]
ranks = np.arange(1, len(sorted_scores) + 1)

# Create bar plot
colors = plt.cm.RdYlGn(sorted_scores)
bars = ax2.barh(ranks, sorted_scores, color=colors, edgecolor='black', linewidth=1.5)

# Add value labels on bars
for i, (bar, score) in enumerate(zip(bars, sorted_scores)):
    ax2.text(score + 0.02, bar.get_y() + bar.get_height()/2, 
            f'{score:.3f}', va='center', fontweight='bold', fontsize=10)

ax2.set_ylabel('Neighbor Rank', fontsize=10)
ax2.set_xlabel('Proximity Score', fontsize=10)
ax2.set_ylim(0.5, len(sorted_scores) + 0.5)
ax2.set_xlim(0, 1.15)
ax2.invert_yaxis()
ax2.grid(True, alpha=0.3, axis='x')

# Add legend with explanation
legend_text = (
    'Proximity Score = 0.5 × (Rproj/Rmax) + 0.5 × (Vdiff/Vmax)\n'
    'Combines spatial and kinematic proximity'
)
ax2.text(0.5, -0.25, legend_text, transform=ax2.transAxes, 
        fontsize=9, ha='center', style='italic',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()

# Save figure
output_path = 'gnf_concept.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✓ Visualization saved to {output_path}")

plt.show()
