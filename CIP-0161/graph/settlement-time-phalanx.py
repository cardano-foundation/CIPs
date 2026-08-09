import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Provided data
K_data = np.array([i for i in range(1, 101)])
ErrorUB_data = np.array([0.8676736300353218, 0.7665170928550862, 0.6892413553587529, 0.6233636971643736,
                         0.5657163917284088, 0.5148322413203136, 0.4695420424714478, 0.42897234102210713,
                         0.3924626607691574, 0.35948902156200147, 0.32962278029962017, 0.3025063659506419,
                         0.27783698249825733, 0.25535514591273023, 0.23483635661765484, 0.2160848560472272,
                         0.19892882408177393, 0.18321660886850946, 0.1688137167962222, 0.15560037467673365,
                         0.14346953077207325, 0.13232519782380092, 0.12208106635957837, 0.11265933425039264,
                         0.10398971121778951, 0.09600856630132028, 0.08865819321256681, 0.08188617370925678,
                         0.07564482309177875, 0.06989070498353891, 0.06458420493919947, 0.05968915429847635,
                         0.05517249718980014, 0.05100399477754493, 0.047155961805507976, 0.043603031268163416,
                         0.04032194367801183, 0.03729135792136073, 0.03449168112865765, 0.031904915346616804,
                         0.029514519101649903, 0.02730528219838205, 0.025263212311976303, 0.023375432115528862,
                         0.02163008583947576, 0.02001625429329978, 0.018523877494483327, 0.01714368414861849,
                         0.015867127310310914, 0.014686325629034798, 0.013594009649070085, 0.012583472689500249,
                         0.011648525880117402, 0.010783456972956714, 0.009982992587887582, 0.009242263584923428,
                         0.008556773286253361, 0.007922368297970843, 0.007335211705481949, 0.006791758438006847,
                         0.006288732616743953, 0.0058231067184273, 0.0053920824014072844, 0.0049930728552227905,
                         0.0046236865470955305, 0.004281712250008304, 0.003965105247171995, 0.003671974616856373,
                         0.003400571509858656, 0.0031492783394076493, 0.0029165988101272316, 0.002701148718882468,
                         0.0025016474659702898, 0.002316910220247162, 0.0021458406864612394, 0.0019874244273183433,
                         0.0018407226967006522, 0.0017048667440089573, 0.0015790525528455637, 0.001462535980224325,
                         0.0013546282652105925, 0.0012546918783826707, 0.0011621366857862258, 0.0010764164031429315,
                         0.0009970253179921987, 0.0009234952592045347, 0.0008553927949202647, 0.0007923166414519593,
                         0.0007338952670522856, 0.0006797846757031187, 0.000629666357234632, 0.0005832453911440828,
                         0.0005402486924603261, 0.0005004233888988434, 0.000463535319379835, 0.00042936764474434813,
                         0.0003977195622058752, 0.0003684051157223931, 0.0003412520950705765, 0.00031610101695421933])
ErrorLB_data = np.array([0.8121889413522433, 0.6876416416654816, 0.5976483327753178, 0.5254324374189145,
                         0.4645063982661716, 0.4123629938648501, 0.3673985960267712, 0.3283163309200733,
                         0.2940989122957397, 0.2639674748869409, 0.23731513349944836, 0.21365535630042634,
                         0.1925895067761664, 0.17378603461408476, 0.15696596625862824, 0.14189226025810497,
                         0.12836183039592358, 0.11619947047643561, 0.10525314223559275, 0.09539025430277556,
                         0.08649467767079334, 0.07846432047056445, 0.07120913531665457, 0.06464946639023633,
                         0.05871466691555115, 0.05334193434216965, 0.04847532258446165, 0.04406489953310157,
                         0.04006602469376975, 0.03643872686089284, 0.03314716563020274, 0.030159163591783687,
                         0.02744579843693806, 0.024981046110909504, 0.022741467662164762, 0.020705933661954723,
                         0.018855381059125348, 0.017172598143457285, 0.015642033953809715, 0.014249629014225416,
                         0.01298266473472342, 0.011829629191657766, 0.0107800973193869, 0.009824623811787224,
                         0.008954647257799136, 0.008162404226884964, 0.0074408521837850275, 0.006783600251963899,
                         0.006184846965458831, 0.005639324252597922, 0.005142246984816187, 0.0046892675016852355,
                         0.0042764345910511585, 0.003900156462313562, 0.003557167302609378, 0.003244497051022336,
                         0.0029594440657968193, 0.0026995503946340197, 0.0024625793891173684, 0.002246495431690644,
                         0.0020494455678550915, 0.0018697428577553032, 0.0017058512804271969, 0.0015563720409779223,
                         0.0014200311461102907, 0.001295668126913479, 0.001182225799908241, 0.0010787409681255011,
                         0.0009843359736577389, 0.0008982110217798201, 0.0008196372045025135, 0.0007479501583952579,
                         0.0006825442977817404, 0.0006228675700485774, 0.0005684166848811588, 0.0005187327738111813,
                         0.0004733974405802858, 0.0004320291665403726, 0.0003942800386652276, 0.0003598327707770982,
                         0.0003283979913287651, 0.00029971177355593483, 0.00027353338605271704, 0.00024964324384800285,
                         0.00022784104189382066, 0.00020794405453700824, 0.000189785586049734, 0.00017321355865768014,
                         0.000158089225740669, 0.0001442859990014865, 0.00013168837941555155, 0.00012019098269693178,
                         0.00010969765085385743, 0.00010012064216746174, 9.137989261820874e-05, 8.34023424119521e-05,
                         7.612132182768348e-05, 6.947599112718069e-05, 6.341082973775746e-05, 5.787517034753198e-05])

# Log-linear fit for ErrorUB (ln(y) = ln(a) - b * K)
log_y_UB = np.log(ErrorUB_data)
coeff_UB = np.polyfit(K_data, log_y_UB, 1)  # slope = -b, intercept = ln(a)
b_UB = -coeff_UB[0]
a_UB = np.exp(coeff_UB[1])

print(f"Fitted for ErrorUB: a={a_UB:.6f}, b={b_UB:.6f}")

# Log-linear fit for ErrorLB
log_y_LB = np.log(ErrorLB_data)
coeff_LB = np.polyfit(K_data, log_y_LB, 1)
b_LB = -coeff_LB[0]
a_LB = np.exp(coeff_LB[1])

print(f"Fitted for ErrorLB: a={a_LB:.6f}, b={b_LB:.6f}")

# Generate extended K values (101 to 2500)
K_extended = np.arange(101, 2501)

# Extrapolate
ErrorUB_extended = a_UB * np.exp(-b_UB * K_extended)
ErrorLB_extended = a_LB * np.exp(-b_LB * K_extended)

# Combine original and extended data
K_all = np.concatenate((K_data, K_extended))
ErrorUB_all = np.concatenate((ErrorUB_data, ErrorUB_extended))
ErrorLB_all = np.concatenate((ErrorLB_data, ErrorLB_extended))

# Save to CSV
data = np.column_stack((K_all, ErrorUB_all, ErrorLB_all))
np.savetxt('extended_error_series_corrected.csv', data, delimiter=',', 
           header='Number of Blocks,ErrorUB,ErrorLB', comments='')

# Plot for verification with professional legend and power of 2 y-axis
fig, ax = plt.subplots(figsize=(10, 6))
ax.semilogy(K_all, ErrorUB_all, 'b-', label='Upper Bound')
ax.semilogy(K_all, ErrorLB_all, 'k-', label='Lower Bound')

# Set y-axis to base 2
ax.set_yscale('log', base=2)

# Formatter for y-ticks as 2^{exponent}
def formatter(y, pos):
    if y <= 0:
        return '0'
    exponent = np.log2(y)
    return r'$2^{{{:.0f}}}$'.format(exponent)

ax.yaxis.set_major_formatter(ticker.FuncFormatter(formatter))

# Minor ticks for finer grid
ax.yaxis.set_minor_locator(ticker.LogLocator(base=2.0, subs=np.arange(2, 10) * .1, numticks=100))

ax.set_xlabel('Number of Blocks (K)', fontsize=12)
ax.set_ylabel('Probability of Failure', fontsize=12)
ax.set_title('Cardano PoS Settlement Failure (30% Adversary, 5s Delay)', fontsize=14)
ax.legend(loc='upper right', fontsize=12)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)
ax.set_ylim([2**(-150), 1])  # Adjusted to show down to 2^{-150}

# Add horizontal line at 2^{-60}
target_prob_60 = 2**(-60)
ax.axhline(y=target_prob_60, color='r', linestyle='--', label='Without Grinding($2^{-60}$)')

# Add horizontal line at 2^{-139.4}
target_prob_1394 = 2**(-139.4)
ax.axhline(y=target_prob_1394, color='m', linestyle='--', label='Praos($2^{-139.4}$)')

# Add horizontal line at 2^{-105.4}
target_prob_1054 = 2**(-105.4)
ax.axhline(y=target_prob_1054, color='c', linestyle='--', label='$Phalanx_{1/100}$($2^{-105.4}$)')

# Add horizontal line at 2^{-102.9}
target_prob_1029 = 2**(-102.9)
ax.axhline(y=target_prob_1029, color='orange', linestyle='--', label='$Phalanx_{1/100}$($2^{-102.9}$)')

# Add horizontal line at 2^{-99.5}
target_prob_995 = 2**(-99.5)
ax.axhline(y=target_prob_995, color='purple', linestyle='--', label='$Phalanx_{max}$($2^{-99.5}$)')

# Find approximate K where curves cross 2^{-60}
K_UB_60 = np.interp(np.log(target_prob_60), np.log(ErrorUB_all)[::-1], K_all[::-1])  # Reverse for increasing log
K_LB_60 = np.interp(np.log(target_prob_60), np.log(ErrorLB_all)[::-1], K_all[::-1])

# Find approximate K where curves cross 2^{-139.4}
K_UB_1394 = np.interp(np.log(target_prob_1394), np.log(ErrorUB_all)[::-1], K_all[::-1])
K_LB_1394 = np.interp(np.log(target_prob_1394), np.log(ErrorLB_all)[::-1], K_all[::-1])

# Find approximate K where curves cross 2^{-105.4}
K_UB_1054 = np.interp(np.log(target_prob_1054), np.log(ErrorUB_all)[::-1], K_all[::-1])
K_LB_1054 = np.interp(np.log(target_prob_1054), np.log(ErrorLB_all)[::-1], K_all[::-1])

# Find approximate K where curves cross 2^{-102.9}
K_UB_1029 = np.interp(np.log(target_prob_1029), np.log(ErrorUB_all)[::-1], K_all[::-1])
K_LB_1029 = np.interp(np.log(target_prob_1029), np.log(ErrorLB_all)[::-1], K_all[::-1])

# Find approximate K where curves cross 2^{-99.5}
K_UB_995 = np.interp(np.log(target_prob_995), np.log(ErrorUB_all)[::-1], K_all[::-1])
K_LB_995 = np.interp(np.log(target_prob_995), np.log(ErrorLB_all)[::-1], K_all[::-1])

# Add vertical lines and annotations for 2^{-60}
ax.axvline(x=K_UB_60, color='b', linestyle=':', alpha=0.5)
ax.axvline(x=K_LB_60, color='k', linestyle=':', alpha=0.5)
ax.annotate(f'Upper Bound K ≈ {K_UB_60:.0f}', xy=(K_UB_60, target_prob_60), xytext=(K_UB_60 + 150, target_prob_60 * 2**10),
            arrowprops=dict(facecolor='blue', shrink=0.05, width=2, headwidth=8), fontsize=12, color='b', bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.5'))
ax.annotate(f'Lower Bound K ≈ {K_LB_60:.0f}', xy=(K_LB_60, target_prob_60), xytext=(K_LB_60 - 450, target_prob_60 / 2**10),
            arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8), fontsize=12, color='k', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))


# Add vertical lines and annotations for 2^{-139.4}
ax.axvline(x=K_UB_1394, color='b', linestyle=':', alpha=0.5)
ax.axvline(x=K_LB_1394, color='k', linestyle=':', alpha=0.5)
ax.annotate(f'Upper Bound K ≈ {K_UB_1394:.0f}', xy=(K_UB_1394, target_prob_1394), xytext=(K_UB_1394 + 50, target_prob_1394 * 2**10 ),
            arrowprops=dict(facecolor='blue', shrink=0.05, width=2, headwidth=8), fontsize=12, color='b', bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.5'))
ax.annotate(f'Lower Bound K ≈ {K_LB_1394:.0f}', xy=(K_LB_1394, target_prob_1394), xytext=(K_LB_1394 - 450, target_prob_1394 / 2**10),
            arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8), fontsize=12, color='k', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

# Add vertical lines and annotations for 2^{-105.4}
ax.axvline(x=K_UB_1054, color='b', linestyle=':', alpha=0.5)
ax.axvline(x=K_LB_1054, color='k', linestyle=':', alpha=0.5)
ax.annotate(f'Upper Bound K ≈ {K_UB_1054:.0f}', xy=(K_UB_1054, target_prob_1054), xytext=(K_UB_1054 + 150, target_prob_1054 * 2**3),
            arrowprops=dict(facecolor='blue', shrink=0.05, width=2, headwidth=8), fontsize=12, color='b', bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.5'))
ax.annotate(f'Lower Bound K ≈ {K_LB_1054:.0f}', xy=(K_LB_1054, target_prob_1054), xytext=(K_LB_1054 - 450, target_prob_1054 / 2**15),
            arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8), fontsize=12, color='k', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

# Add vertical lines and annotations for 2^{-102.9}
ax.axvline(x=K_UB_1029, color='b', linestyle=':', alpha=0.5)
ax.axvline(x=K_LB_1029, color='k', linestyle=':', alpha=0.5)
ax.annotate(f'Upper Bound K ≈ {K_UB_1029:.0f}', xy=(K_UB_1029, target_prob_1029), xytext=(K_UB_1029 + 150, target_prob_1029 * 2**10),
            arrowprops=dict(facecolor='blue', shrink=0.05, width=2, headwidth=8), fontsize=12, color='b', bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.5'))
ax.annotate(f'Lower Bound K ≈ {K_LB_1029:.0f}', xy=(K_LB_1029, target_prob_1029), xytext=(K_LB_1029 - 450, target_prob_1029 / 2**10),
            arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8), fontsize=12, color='k', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

# Add vertical lines and annotations for 2^{-99.5}
ax.axvline(x=K_UB_995, color='b', linestyle=':', alpha=0.5)
ax.axvline(x=K_LB_995, color='k', linestyle=':', alpha=0.5)
ax.annotate(f'Upper Bound K ≈ {K_UB_995:.0f}', xy=(K_UB_995, target_prob_995), xytext=(K_UB_995 + 150, target_prob_995 * 2**15),
            arrowprops=dict(facecolor='blue', shrink=0.05, width=2, headwidth=8), fontsize=12, color='b', bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.5'))
ax.annotate(f'Lower Bound K ≈ {K_LB_995:.0f}', xy=(K_LB_995, target_prob_995), xytext=(K_LB_995 - 450, target_prob_995 / 2**3),
            arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=8), fontsize=12, color='k', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

ax.legend(fontsize=12)  # Update legend with the new lines

plt.show()