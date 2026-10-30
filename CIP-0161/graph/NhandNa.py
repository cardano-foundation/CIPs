import matplotlib.pyplot as plt

# Adjusted data to ensure matching lengths
s_a_values = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.25, 0.3, 0.33, 0.4, 0.45, 0.49, 0.5]
N_a_values = [269, 434, 730, 1537, 2794, 5204, 6384, 7554, 8252, 9872, 11024, 11942, 12171]
N_h_values = [19645, 19541, 18713, 17680, 15618, 14590, 13563, 12949, 11517, 10498, 9685, 9482, 9482]

# Plot
plt.figure(figsize=(14, 6))

# Left plot: Max #Adversarial blocks
plt.subplot(1, 2, 1)
plt.plot([x * 100 for x in s_a_values], N_a_values, marker='o', label="N_a")
plt.title("Nₐ s.t. Pr(Xₐ < Nₐ) = 1 - 2⁻¹²⁸")
plt.xlabel("Adversarial stake sₐ (%)")
plt.ylabel("Max #Adversarial blocks")
plt.grid(True)
plt.legend()

# Right plot: Min #Honest blocks
plt.subplot(1, 2, 2)
plt.plot([x * 100 for x in s_a_values], N_h_values, marker='o', color='orange', label="N_h")
plt.title("Nₕ s.t. Pr(Xₕ > Nₕ) = 2⁻¹²⁸")
plt.xlabel("Adversarial stake sₐ (%)")
plt.ylabel("Min #Honest blocks")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
