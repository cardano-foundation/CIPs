import numpy as np
import matplotlib.pyplot as plt

# Define the range for rho (Grinding Depth), starting at 0.1 to avoid division by zero
rho = np.linspace(0.1, 256, 1000)  # 1000 points for smooth curve

# Define N_CPU functions for each scenario based on the developed formulas
def ant_glance(rho):
    return 5e-10 * 2**(rho - 1) + 1.8e-11 * 2**(rho - 1)

def ant_patrol(rho):
    return 5e-10 * 2**(rho - 1) + 2.16e-9 * 2**(rho - 1)

def owl_stare(rho):
    return 5e-10 * 2**(rho - 1) + 1.8e-11 * 2**(rho - 1) + 5e-2 * 2**(rho - 1) / rho

def owl_survey(rho):
    return 5e-10 * 2**(rho - 1) + 2.16e-9 * 2**(rho - 1) + 5e-2 * 2**(rho - 1) / rho

# Calculate log10(N_CPU) for each scenario
log_ant_glance = np.log10(ant_glance(rho))
log_ant_patrol = np.log10(ant_patrol(rho))
log_owl_stare = np.log10(owl_stare(rho))
log_owl_survey = np.log10(owl_survey(rho))

# Create the plot with improved aesthetics
plt.figure(figsize=(12, 7))
plt.plot(rho, log_ant_glance, label='Ant Glance', color='blue', linewidth=2)
plt.plot(rho, log_ant_patrol, label='Ant Patrol', color='orange', linewidth=2)
plt.plot(rho, log_owl_stare, label='Owl Stare', color='green', linewidth=2)
plt.plot(rho, log_owl_survey, label='Owl Survey', color='red', linewidth=2)

# Add labels and title with larger font
plt.xlabel('$\\rho$ (Grinding Depth)', fontsize=14)
plt.ylabel('$\\log_{10}(N_{\\text{CPU}})$', fontsize=14)
plt.title('Behavior of $N_{\\text{CPU}}$ Across Scenarios', fontsize=16)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=12)

# Add annotation for the delta at rho = 50 (where curves are more separated)
rho_idx = np.argmin(np.abs(rho - 50))  # Index closest to rho = 50
delta_log_ncpu = log_owl_survey[rho_idx] - log_ant_glance[rho_idx]
mid_y = log_owl_survey[rho_idx] - (delta_log_ncpu / 2) + 0.5  # Position slightly above mid-point

# Draw a thinner double-headed arrow in purple with smaller arrowheads
plt.annotate('', xy=(50, log_owl_survey[rho_idx]), xytext=(50, log_ant_glance[rho_idx]),
             arrowprops=dict(arrowstyle='<->', color='purple', lw=1, shrinkA=0, shrinkB=0))

# Add the delta label in purple, slightly offset to the right
plt.text(53, mid_y-3.5, f'$\\Delta \\log_{{10}}(N_{{CPU}}) \\approx {delta_log_ncpu:.1f}$',
         fontsize=12, color='purple', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
         verticalalignment='center')

# Adjust layout to prevent overlap
plt.tight_layout()

# Save the plot as an image with higher resolution
plt.savefig('grinding_depth_scenarios_with_delta.png', dpi=300)
plt.show()