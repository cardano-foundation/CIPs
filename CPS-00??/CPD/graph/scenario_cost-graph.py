import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Define the range for rho (Grinding Depth), starting at 1 to avoid underflow issues
rho = np.linspace(1, 256, 1000)  # 1000 points for smooth curve, starts at 1, ends at 256

# Define f and cost per CPU-hour
f = 0.05
cost_per_cpu_hour = 0.01  # $0.01 per CPU-hour

# Compute w_O in seconds for each rho
w_O = 20 * (2 * rho - 1)  # w_O = (2 * rho - 1) / f, f = 0.05
w_O_hours = w_O / 3600  # Convert to hours for cost calculation

# Define N_CPU functions for each scenario based on the developed formulas
def ant_glance(rho):
    return 5e-10 * 2**(rho - 1) + 1.8e-11 * 2**(rho - 1)

def ant_patrol(rho):
    return 5e-10 * 2**(rho - 1) + 2.16e-9 * 2**(rho - 1)

def owl_stare(rho):
    return 5e-10 * 2**(rho - 1) + 1.8e-11 * 2**(rho - 1) + 5e-2 * 2**(rho - 1) / rho

def owl_survey(rho):
    return 5e-10 * 2**(rho - 1) + 2.16e-9 * 2**(rho - 1) + 5e-2 * 2**(rho - 1) / rho

# Compute N_CPU for each scenario
n_cpu_ant_glance = ant_glance(rho)
n_cpu_ant_patrol = ant_patrol(rho)
n_cpu_owl_stare = owl_stare(rho)
n_cpu_owl_survey = owl_survey(rho)

# Compute cost in USD for each scenario
cost_ant_glance = n_cpu_ant_glance * cost_per_cpu_hour * w_O_hours
cost_ant_patrol = n_cpu_ant_patrol * cost_per_cpu_hour * w_O_hours
cost_owl_stare = n_cpu_owl_stare * cost_per_cpu_hour * w_O_hours
cost_owl_survey = n_cpu_owl_survey * cost_per_cpu_hour * w_O_hours

# Calculate log10(Cost) for each scenario, adding a small epsilon to avoid log of zero
epsilon = 1e-100  # Small positive value to prevent log(0)
log_cost_ant_glance = np.log10(np.maximum(cost_ant_glance, epsilon))
log_cost_ant_patrol = np.log10(np.maximum(cost_ant_patrol, epsilon))
log_cost_owl_stare = np.log10(np.maximum(cost_owl_stare, epsilon))
log_cost_owl_survey = np.log10(np.maximum(cost_owl_survey, epsilon))

# Create the plot with improved aesthetics
plt.figure(figsize=(12, 7))
plt.plot(rho, log_cost_ant_glance, label='Ant Glance', color='blue', linewidth=2)
plt.plot(rho, log_cost_ant_patrol, label='Ant Patrol', color='orange', linewidth=2)
plt.plot(rho, log_cost_owl_stare, label='Owl Stare', color='green', linewidth=2)
plt.plot(rho, log_cost_owl_survey, label='Owl Survey', color='red', linewidth=2)

# Add feasibility threshold layers as horizontal spans based on log10(Cost USD)
plt.axhspan(-10, 2, color='green', alpha=0.1)         # Trivial (< $100)
plt.axhspan(2, 6, color='yellow', alpha=0.1)          # Feasible ($10,000 to $1M)
plt.axhspan(6, 9, color='#FFA07A', alpha=0.1)         # Possible ($1M to $1B) - Light salmon
plt.axhspan(9, 12, color='#FF6347', alpha=0.1)        # Borderline Infeasible ($1B to $1T) - Tomato
plt.axhspan(12, 90, color='red', alpha=0.1)           # Infeasible (> $1T) - Red

# Add labels and title with larger font
plt.xlabel('$\\rho$ (Grinding Depth)', fontsize=14)
plt.ylabel('$\\log_{10}(\\text{Cost (USD)})$', fontsize=14)
plt.title('Cost of Grinding Attacks Across Scenarios with Feasibility Thresholds', fontsize=16)
plt.grid(True, linestyle='--', alpha=0.7)

# Set axis limits to ensure full range is visible
plt.xlim(0, 256)  # X-axis from 0 to 256
# Compute y_max by taking the maximum of valid log cost values
valid_log_costs = np.concatenate([
    log_cost_ant_glance[np.isfinite(log_cost_ant_glance)],
    log_cost_ant_patrol[np.isfinite(log_cost_ant_patrol)],
    log_cost_owl_stare[np.isfinite(log_cost_owl_stare)],
    log_cost_owl_survey[np.isfinite(log_cost_owl_survey)]
])
y_max = np.max(valid_log_costs) + 5 if valid_log_costs.size > 0 else 90  # Fallback to 90 if no valid values
plt.ylim(-5, y_max)  # Y-axis starts at -5 to match the range of data

# Add annotation for the delta at rho = 50 (where curves are more separated)
rho_idx = np.argmin(np.abs(rho - 50))  # Index closest to rho = 50
delta_log_cost = log_cost_owl_survey[rho_idx] - log_cost_ant_glance[rho_idx]
mid_y = log_cost_owl_survey[rho_idx] - (delta_log_cost / 2) + 0.5  # Position slightly above mid-point

# Draw a thinner double-headed arrow in purple with smaller arrowheads
plt.annotate('', xy=(50, log_cost_owl_survey[rho_idx]), xytext=(50, log_cost_ant_glance[rho_idx]),
             arrowprops=dict(arrowstyle='<->', color='purple', lw=1, shrinkA=0, shrinkB=0))

# Add the delta label in purple, slightly offset to the right
plt.text(53, mid_y-3.5, f'$\\Delta \\log_{{10}}(\\text{{Cost (USD)}}) \\approx {delta_log_cost:.1f}$',
         fontsize=12, color='purple', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
         verticalalignment='center')

# Create a custom legend with all labels, placed at bottom right
legend_elements = [
    plt.Line2D([0], [0], color='blue', lw=2, label='Ant Glance'),
    plt.Line2D([0], [0], color='orange', lw=2, label='Ant Patrol'),
    plt.Line2D([0], [0], color='green', lw=2, label='Owl Stare'),
    plt.Line2D([0], [0], color='red', lw=2, label='Owl Survey'),
    Patch(facecolor='green', alpha=0.1, label='Trivial'),
    Patch(facecolor='yellow', alpha=0.1, label='Feasible'),
    Patch(facecolor='#FFA07A', alpha=0.1, label='Possible'),
    Patch(facecolor='#FF6347', alpha=0.1, label='Borderline Infeasible'),
    Patch(facecolor='red', alpha=0.1, label='Infeasible')
]
plt.legend(handles=legend_elements, fontsize=10, loc='lower right',
           bbox_to_anchor=(1, 0), ncol=2, handletextpad=0.5, columnspacing=1.5)

# Adjust layout to prevent overlap, with manual padding
plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2)

# Save the plot as an image with higher resolution
plt.savefig('grinding_depth_scenarios_cost_with_feasibility_layers_gradient.png', dpi=300, bbox_inches='tight')
plt.show()