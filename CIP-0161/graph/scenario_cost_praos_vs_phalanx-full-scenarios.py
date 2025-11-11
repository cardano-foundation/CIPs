import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Range for rho (Grinding Depth)
rho = np.linspace(1, 256, 1000)
f = 0.05
cost_per_cpu_hour = 0.01  # $0.01 per CPU-hour

# Time window for computation (w_O)
w_O = 20 * (2 * rho - 1)
w_O_hours = w_O / 3600

# PRAOS cost functions
def ant_glance_praos(rho): return 5e-10 * 2**(rho - 2)
def ant_patrol_praos(rho): return ant_glance_praos(rho) + 2.16e-2 * 2**(rho - 1) / rho
def owl_stare_praos(rho): return ant_glance_praos(rho) + 5e-2 * 2**(rho - 1) / rho
def owl_survey_praos(rho): return ant_glance_praos(rho) + 7.16e-2 * 2**(rho - 1) / rho

# PHALANX curves (generalized)
def phalanx_curve(multiplier):
    return lambda rho: (multiplier * 2**(rho - 1)) / rho

phalanx_1_100 = phalanx_curve(2.16e2)
phalanx_1_10 = phalanx_curve(2.16e3)
phalanx_max = phalanx_curve(2.16e4)

# Convert to log10 cost
def compute_log_cost(n_cpu):
    return np.log10(np.maximum(n_cpu * cost_per_cpu_hour * w_O_hours, 1e-100))

# Scenario definitions
scenarios = {
    "Ant Glance Praos": compute_log_cost(ant_glance_praos(rho)),
    "Ant Patrol Praos": compute_log_cost(ant_patrol_praos(rho)),
    "Owl Stare Praos": compute_log_cost(owl_stare_praos(rho)),
    "Owl Survey Praos": compute_log_cost(owl_survey_praos(rho)),
    "Phalanx$_{1/100}$": compute_log_cost(phalanx_1_100(rho)),
    "Phalanx$_{1/10}$": compute_log_cost(phalanx_1_10(rho)),
    "Phalanx$_{max}$": compute_log_cost(phalanx_max(rho)),
}

# Color map for plot lines
color_map = {
    "Ant Glance Praos": "blue",
    "Ant Patrol Praos": "orange",
    "Owl Stare Praos": "green",
    "Owl Survey Praos": "red",
    "Phalanx$_{1/100}$": '#6A5ACD',
    "Phalanx$_{1/10}$": '#228B22',
    "Phalanx$_{max}$": "#B22222"
}

# Feasibility zones
zones = [
    (-10, 4, 'green', 'Trivial'),
    (4, 6, 'yellow', 'Feasible'),
    (6, 9, '#FFA07A', 'Possible'),
    (9, 12, '#FF6347', 'Borderline Infeasible'),
    (12, 90, 'red', 'Infeasible')
]

# Plot
plt.figure(figsize=(12, 7))

# Draw curves
for label, log_cost in scenarios.items():
    style = "-" if "Praos" in label else "--"
    plt.plot(rho, log_cost, label=label, color=color_map[label], linestyle=style, linewidth=2)

# Draw feasibility zones
for y0, y1, color_zone, label in zones:
    plt.axhspan(y0, y1, color=color_zone, alpha=0.1, label=label)

# Axis labels and title
plt.xlabel(r'$\rho$ (Grinding Depth)', fontsize=14)
plt.ylabel(r'$\log_{10}(\mathrm{Cost\ (USD)})$', fontsize=14)
plt.title('Cost of Grinding Attacks: Praos vs Phalanx Configurations', fontsize=16)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xlim(0, 256)
y_max = max(np.max(v[np.isfinite(v)]) for v in scenarios.values()) + 5
plt.ylim(-5, y_max)

# Delta annotations
def draw_delta(rho_val, praos_label, phalanx_label, x_offset=3):
    idx = np.argmin(np.abs(rho - rho_val))
    delta = scenarios[phalanx_label][idx] - scenarios[praos_label][idx]
    mid = scenarios[phalanx_label][idx] - delta / 2
    plt.annotate('', xy=(rho_val, scenarios[phalanx_label][idx]),
                 xytext=(rho_val, scenarios[praos_label][idx]),
                 arrowprops=dict(arrowstyle='<->', color='black', lw=1))
    plt.text(rho_val + x_offset, mid, f'$\\Delta \\approx {delta:.1f}$', fontsize=12, color='black',
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'), verticalalignment='center')

draw_delta(50, "Ant Glance Praos", "Phalanx$_{1/100}$")
draw_delta(125, "Owl Survey Praos", "Phalanx$_{1/100}$")
draw_delta(150, "Owl Survey Praos", "Phalanx$_{1/10}$")
draw_delta(175, "Owl Survey Praos", "Phalanx$_{max}$")

# Legend
legend_elements = [
    plt.Line2D([0], [0], color='blue', lw=2, label='Ant Glance Praos'),
    plt.Line2D([0], [0], color='orange', lw=2, label='Ant Patrol Praos'),
    plt.Line2D([0], [0], color='green', lw=2, label='Owl Stare Praos'),
    plt.Line2D([0], [0], color='red', lw=2, label='Owl Survey Praos'),
    plt.Line2D([0], [0], color='#6A5ACD', lw=2, linestyle='--', label='Phalanx$_{1/100}$'),
    plt.Line2D([0], [0], color='#228B22', lw=2, linestyle='--', label='Phalanx$_{1/10}$'),
    plt.Line2D([0], [0], color='#B22222', lw=2, linestyle='--', label='Phalanx$_{max}$'),
    *[Patch(facecolor=color, alpha=0.1, label=label) for _, _, color, label in zones]
]
plt.legend(handles=legend_elements, fontsize=10, loc='lower right', bbox_to_anchor=(1, 0), ncol=2)

plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2)
plt.show()
