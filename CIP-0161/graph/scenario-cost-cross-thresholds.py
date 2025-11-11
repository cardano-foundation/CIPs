import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Define the range for rho (Grinding Depth)
rho = np.linspace(1, 256, 1000)
f = 0.05
cost_per_cpu_hour = 0.01
w_O = 20 * (2 * rho - 1)
w_O_hours = w_O / 3600
epsilon = 1e-100  # Avoid log(0)

# Praos cost functions
def ant_glance_praos(rho): return 5e-10 * 2**(rho - 2)
def ant_patrol_praos(rho): return 5e-10 * 2**(rho - 1) + 2.16e-2 * 2**(rho - 1) / rho
def owl_stare_praos(rho): return 5e-10 * 2**(rho - 2) + 5e-2 * 2**(rho - 1) / rho
def owl_survey_praos(rho): return 5e-10 * 2**(rho - 2) + 7.16e-2 * 2**(rho - 1) / rho

# Phalanx cost function
def phalanx_cost(rho, scale): return (scale * 2**(rho - 1)) / rho

# Compute log10(Cost) from CPU count
def log_cost(n_cpu): return np.log10(np.maximum(n_cpu * cost_per_cpu_hour * w_O_hours, epsilon))

# Curves for Praos
praos_curves = {
    'Ant Glance Praos': ('blue', log_cost(ant_glance_praos(rho))),
    'Ant Patrol Praos': ('orange', log_cost(ant_patrol_praos(rho))),
    'Owl Stare Praos': ('green', log_cost(owl_stare_praos(rho))),
    'Owl Survey Praos': ('red', log_cost(owl_survey_praos(rho))),
}

# Curves for Phalanx configurations
phalanx_curves = {
    'Phalanx$_{1/100}$': ('#6A5ACD', log_cost(phalanx_cost(rho, 2.16e2))),
    'Phalanx$_{1/10}$': ('#228B22', log_cost(phalanx_cost(rho, 2.16e3))),
    'Phalanx$_{max}$': ('#B22222', log_cost(phalanx_cost(rho, 2.16e4))),
}

# Feasibility zones
zones = [
    (-10, 4, 'green', 'Trivial'),
    (4, 6, 'yellow', 'Feasible'),
    (6, 9, '#FFA07A', 'Possible'),
    (9, 12, '#FF6347', 'Borderline Infeasible'),
    (12, 90, 'red', 'Infeasible')
]

# Function to find crossing points and annotate
def annotate_crossings(log_costs, color, threshold, position='above'):
    # Find indices where the curve crosses the threshold
    indices = np.where((log_costs[:-1] < threshold) & (log_costs[1:] >= threshold))[0]
    if len(indices) > 0:
        idx = indices[0]
        rho_val = rho[idx]
        plt.scatter(rho_val, threshold, color=color, marker='o', s=50, zorder=5)
        # Position above or below based on the curve
        if position == 'below':
            plt.annotate(f'{rho_val:.1f}',
                         xy=(rho_val, threshold),
                         xytext=(rho_val + 1.1, threshold - 0.4),
                         fontsize=8, color=color)
        elif position == 'green':
            plt.annotate(f'{rho_val:.1f}',
                         xy=(rho_val, threshold),
                         xytext=(rho_val - 0.6, threshold - 0.9),
                         fontsize=8, color=color)
        else:
            plt.annotate(f'{rho_val:.1f}',
                         xy=(rho_val, threshold),
                         xytext=(rho_val - 1, threshold + 0.3),
                         fontsize=8, color=color)


# # Annotate where curves cross threshold lines
# def annotate_crossings(log_costs, color, threshold, position='above'):
#     indices = np.where((log_costs[:-1] < threshold) & (log_costs[1:] >= threshold))[0]
#     if len(indices) > 0:
#         idx = indices[0]
#         rho_val = rho[idx]
#         plt.scatter(rho_val, threshold, color=color, marker='o', s=50, zorder=5)
#         offset = {'above': (1, 0.5), 'below': (1.1, -0.4), 'green': (-0.6, -0.9)}.get(position, (1, 0.5))
#         plt.annotate(f'{rho_val:.1f}', xy=(rho_val, threshold),
#                      xytext=(rho_val + offset[0], threshold + offset[1]),
#                      fontsize=8, color=color)

# Unified curve list for annotation logic
curves = [
    (praos_curves['Ant Glance Praos'][1], 'blue', 'above'),
    (praos_curves['Ant Patrol Praos'][1], 'orange', 'below'),
    (praos_curves['Owl Stare Praos'][1], 'green', 'green'),
    (praos_curves['Owl Survey Praos'][1], 'red', 'above'),
    (phalanx_curves['Phalanx$_{1/100}$'][1], '#6A5ACD', 'above'),
    (phalanx_curves['Phalanx$_{1/10}$'][1], '#228B22', 'above'),
    (phalanx_curves['Phalanx$_{max}$'][1], '#B22222', 'above')
]

# Plotting
plt.figure(figsize=(12, 7))

# Plot each Praos and Phalanx curve
for label, (color, values) in praos_curves.items():
    plt.plot(rho, values, label=label, color=color, linewidth=2)
for label, (color, values) in phalanx_curves.items():
    plt.plot(rho, values, label=label, color=color, linestyle='--', linewidth=2)

# Add feasibility zones
for y0, y1, color, label in zones:
    plt.axhspan(y0, y1, color=color, alpha=0.1, label=label)

# Annotate crossings
for threshold, _, _, _ in zones:
    for log_costs, color, position in curves:
        annotate_crossings(log_costs, color, threshold, position)

# Axis labels and title
plt.xlabel(r'$\rho$ (Grinding Depth)', fontsize=14)
plt.ylabel(r'$\log_{10}(\mathrm{Cost\ (USD)})$', fontsize=14)
plt.title('Cost of Grinding Attacks Across Praos and Phalanx Scenarios', fontsize=16)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xlim(0, 256)
y_max = max(np.max(v[np.isfinite(v)]) for _, v in list(praos_curves.values()) + list(phalanx_curves.values())) + 5
plt.ylim(-5, y_max)

# Custom legend
legend_elements = [
    *[plt.Line2D([0], [0], color=color, lw=2, label=label) for label, (color, _) in praos_curves.items()],
    *[plt.Line2D([0], [0], color=color, lw=2, linestyle='--', label=label) for label, (color, _) in phalanx_curves.items()],
    *[Patch(facecolor=color, alpha=0.1, label=label) for _, _, color, label in zones]
]
plt.legend(handles=legend_elements, fontsize=10, loc='lower right',
           bbox_to_anchor=(1, 0), ncol=2, handletextpad=0.5, columnspacing=1.5)

# Final layout and save
plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2)

plt.show()
