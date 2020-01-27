import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def c_of_d(ys_orig, ys_line):
    """Compute the line R squared."""
    y_mean_line = [np.mean(ys_orig) for y in ys_orig]
    squared_error_regr = sum((ys_line - ys_orig) * (ys_line - ys_orig))
    squared_error_y_mean = sum((y_mean_line - ys_orig) * \
                               (y_mean_line - ys_orig))
    return 1 - (squared_error_regr / squared_error_y_mean)


# days in January
x = [np.float(x) for x in range(16, 27)]
# reported number of cases
y0 = [45., 62., 121., 198., 291., 440., 571., 830., 1287., 1975., 2827.]

# natural log of number of reported cases
y = np.log(y0)

coef = np.polyfit(x, y, 1)
poly1d_fn = np.poly1d(coef)

# statistical parameters
R = c_of_d(y, poly1d_fn(x))  # R squared
yerr = poly1d_fn(x) - y  # error
slope = coef[0]  # slope
d_time = np.log(2.) / slope  # doubling time
R0 = np.exp(slope) - 1.

plot_suptitle = "Linear fit of natural log of cases $N=Ce^{bt}$ with $b=$%.2f day$^{-1}$" % slope
plot_title = "Coefficient of determination R=%.3f" % R + "\n" + \
             "Population Doubling time: %.1f days" % d_time + "\n" + \
             "Estimated Daily $R_0=$%.1f" % R0

# plotting
plt.plot(x, y, 'yo', x, poly1d_fn(x), '--k')
plt.errorbar(x, y, yerr=yerr, fmt='o', color='r')
plt.grid()
plt.xlim(15., 27.)
plt.ylim(3.5, 10.)
plt.yticks(y, [np.int(y0) for y0 in y0])
plt.xlabel("January Date (DD/01/2020)")
plt.ylabel("Number of 2019-nCov cases on given day DD")
plt.suptitle("2019-nCoV")
plt.title(plot_suptitle)
plt.text(16., 9., plot_title)
plt.show()
