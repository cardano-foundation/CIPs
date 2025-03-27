import matplotlib.pyplot as plt
import numpy as np

# Parameters
f = 1/20  # Active slot coefficient

# Range of rho values (grinding depth)
rho_values = np.arange(1, 257, 5)  # From 1 to 256, step size 5

# Calculate w_O for worst-case and best-case scenarios (in seconds)
w_O_worst = rho_values / f  # Worst case: rho / f
w_O_best = (2 * rho_values - 1) / f  # Best case: (2 * rho - 1) / f

# Convert to hours
w_O_worst_hours = w_O_worst / 3600
w_O_best_hours = w_O_best / 3600

# Special value at rho = 256
rho_special = 256
w_O_worst_special = (rho_special / f) / 3600  # Worst case at rho = 256 (~1.42 hours)
w_O_best_special = ((2 * rho_special - 1) / f) / 3600  # Best case at rho = 256 (~2.84 hours)

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(w_O_worst_hours, rho_values, color='red', linestyle='-', linewidth=2, label=r'Worst Case: $w_O = \frac{\rho}{f}$')
plt.plot(w_O_best_hours, rho_values, color='blue', linestyle='--', linewidth=2, label=r'Best Case: $w_O = \frac{2\rho - 1}{f}$')

# Add vertical lines at rho = 256
plt.axvline(x=w_O_worst_special, color='red', linestyle=':', linewidth=1.5, ymax=256/260)  # Scale to rho = 256
plt.axvline(x=w_O_best_special, color='blue', linestyle=':', linewidth=1.5, ymax=256/260)

# Add x-axis labels for special values, offset to the right
offset = 0.01  # Small offset in hours to the right
plt.text(w_O_worst_special + offset, -15, f'{w_O_worst_special:.2f} h', color='red', ha='left', va='top', fontsize=12)
plt.text(w_O_best_special + offset, -15, f'{w_O_best_special:.2f} h', color='blue', ha='left', va='top', fontsize=12)

# Customize the plot
plt.xlabel(r'Grinding Opportunity Window ($w_O$, hours)', fontsize=12)
plt.ylabel(r'Grinding Depth ($\rho$)', fontsize=12)
plt.legend(fontsize=10, loc='upper left')  # Add legend in upper left corner
plt.grid(True, linestyle='--', alpha=0.7)

# Set reasonable axis limits
plt.xlim(0, max(w_O_best_hours) * 1.1)  # Add 10% headroom on x-axis
plt.ylim(-30, 260)  # Extend y-axis bottom to show labels clearly

# Show the plot
plt.tight_layout()
plt.show()

# Optional: Save the plot
# plt.savefig('w_O_graph_hours_lines_legend.png')