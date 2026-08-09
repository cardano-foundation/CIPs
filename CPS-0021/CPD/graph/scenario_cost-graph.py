import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Define the range for rho (Grinding Depth), starting at 1 to avoid underflow issues
rho = np.linspace(1, 256, 1000)  # 1000 points for smooth curve, starts at 1, ends at 256

# Define f and cost per CPU-hour
f = 0.05
cost_per_cpu_hour = 0.01  # $0.01 per CPU-hour

# Compute w_O in seconds for each rho
w_O = 20 * (2 * rho - 1)  # w_O = 20 * (2 * rho - 1)
w_O_hours = w_O / 3600  # Convert to hours for cost calculation

# Define N_CPU functions for Praos scenarios
def ant_glance_praos(rho):
    return 5e-10 * 2**(rho - 2) 

def ant_patrol_praos(rho):
    return 5e-10 * 2**(rho - 1) + 2.16e-2 * 2**(rho - 1) / rho

def owl_stare_praos(rho):
    return 5e-10 * 2**(rho - 2) + 5e-2 * 2**(rho - 1) / rho

def owl_survey_praos(rho):
    return 5e-10 * 2**(rho - 2) + 7.16e-2 * 2**(rho - 1) / rho

# Compute N_CPU for all Praos scenarios
n_cpu_ant_glance_praos = ant_glance_praos(rho)
n_cpu_ant_patrol_praos = ant_patrol_praos(rho)
n_cpu_owl_stare_praos = owl_stare_praos(rho)
n_cpu_owl_survey_praos = owl_survey_praos(rho)

# Compute cost in USD for all Praos scenarios
cost_ant_glance_praos = n_cpu_ant_glance_praos * cost_per_cpu_hour * w_O_hours
cost_ant_patrol_praos = n_cpu_ant_patrol_praos * cost_per_cpu_hour * w_O_hours
cost_owl_stare_praos = n_cpu_owl_stare_praos * cost_per_cpu_hour * w_O_hours
cost_owl_survey_praos = n_cpu_owl_survey_praos * cost_per_cpu_hour * w_O_hours

# Calculate log10(Cost) for all scenarios, adding a small epsilon to avoid log of zero
epsilon = 1e-100  # Small positive value to prevent log(0)
log_cost_ant_glance_praos = np.log10(np.maximum(cost_ant_glance_praos, epsilon))
log_cost_ant_patrol_praos = np.log10(np.maximum(cost_ant_patrol_praos, epsilon))
log_cost_owl_stare_praos = np.log10(np.maximum(cost_owl_stare_praos, epsilon))
log_cost_owl_survey_praos = np.log10(np.maximum(cost_owl_survey_praos, epsilon))

# Create the plot with improved aesthetics
plt.figure(figsize=(12, 7))
# Plot Praos scenarios with solid lines
plt.plot(rho, log_cost_ant_glance_praos, label='Ant Glance Praos', color='blue', linewidth=2)
plt.plot(rho, log_cost_ant_patrol_praos, label='Ant Patrol Praos', color='orange', linewidth=2)
plt.plot(rho, log_cost_owl_stare_praos, label='Owl Stare Praos', color='green', linewidth=2)
plt.plot(rho, log_cost_owl_survey_praos, label='Owl Survey Praos', color='red', linewidth=2)

# Add feasibility threshold layers as horizontal spans based on log10(Cost USD)
plt.axhspan(-10, 4, color='green', alpha=0.1, label='Trivial')         # Trivial (< $10,000)
plt.axhspan(4, 6, color='yellow', alpha=0.1, label='Feasible')          # Feasible ($10,000 to $1M)
plt.axhspan(6, 9, color='#FFA07A', alpha=0.1, label='Possible')         # Possible ($1M to $1B) - Light salmon
plt.axhspan(9, 12, color='#FF6347', alpha=0.1, label='Borderline Infeasible')  # Borderline Infeasible ($1B to $1T) - Tomato
plt.axhspan(12, 90, color='red', alpha=0.1, label='Infeasible')         # Infeasible (> $1T) - Red

# Add labels and title with larger font
plt.xlabel('$\\rho$ (Grinding Depth)', fontsize=14)
plt.ylabel('$\\log_{10}(\\text{Cost (USD)})$', fontsize=14)
plt.title('Cost of Grinding Attacks Across Praos Scenarios with Feasibility Thresholds', fontsize=16)
plt.grid(True, linestyle='--', alpha=0.7)

# Set axis limits to ensure full range is visible
plt.xlim(0, 256)  # X-axis from 0 to 256
# Compute y_max considering all Praos scenarios
valid_log_costs = np.concatenate([
    log_cost_ant_glance_praos[np.isfinite(log_cost_ant_glance_praos)],
    log_cost_ant_patrol_praos[np.isfinite(log_cost_ant_patrol_praos)],
    log_cost_owl_stare_praos[np.isfinite(log_cost_owl_stare_praos)],
    log_cost_owl_survey_praos[np.isfinite(log_cost_owl_survey_praos)]
])
y_max = np.max(valid_log_costs) + 5 if valid_log_costs.size > 0 else 90
plt.ylim(-5, y_max)  # Y-axis starts at -5

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
                         xytext=(rho_val - 1, threshold + 0.5),
                         fontsize=8, color=color)

# Annotate crossings for Praos curves
thresholds = [
    (4, "Trivial to Feasible"),
    (6, "Feasible to Possible"),
    (9, "Possible to Borderline"),
    (12, "Borderline to Infeasible")
]

curves = [
    (log_cost_ant_glance_praos, 'blue', 'above'),
    (log_cost_ant_patrol_praos, 'orange', 'below'),
    (log_cost_owl_stare_praos, 'green', 'green'),
    (log_cost_owl_survey_praos, 'red', 'above')
]

# Annotate crossings
for threshold, threshold_name in thresholds:
    for log_costs, color, position in curves:
        annotate_crossings(log_costs, color, threshold, position)

# Create a custom legend with Praos labels and feasibility thresholds
legend_elements = [
    plt.Line2D([0], [0], color='blue', lw=2, label='Ant Glance Praos'),
    plt.Line2D([0], [0], color='orange', lw=2, label='Ant Patrol Praos'),
    plt.Line2D([0], [0], color='green', lw=2, label='Owl Stare Praos'),
    plt.Line2D([0], [0], color='red', lw=2, label='Owl Survey Praos'),
    Patch(facecolor='green', alpha=0.1, label='Trivial'),
    Patch(facecolor='yellow', alpha=0.1, label='Feasible'),
    Patch(facecolor='#FFA07A', alpha=0.1, label='Possible'),
    Patch(facecolor='#FF6347', alpha=0.1, label='Borderline Infeasible'),
    Patch(facecolor='red', alpha=0.1, label='Infeasible')
]
plt.legend(handles=legend_elements, fontsize=10, loc='lower right',
           bbox_to_anchor=(1, 0), ncol=2, handletextpad=0.5, columnspacing=1.5)

# Adjust layout to prevent overlap
plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2)

# Save the plot
plt.savefig('grinding_depth_scenarios_cost_praos_annotated.png', dpi=300, bbox_inches='tight')
plt.show()