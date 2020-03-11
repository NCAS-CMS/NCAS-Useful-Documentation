import numpy as np
import matplotlib
import matplotlib.pyplot as plt

month = "01"

def c_of_d(ys_orig, ys_line):
    """Compute the line R squared."""
    y_mean_line = [np.mean(ys_orig) for y in ys_orig]
    squared_error_regr = sum((ys_line - ys_orig) * (ys_line - ys_orig))
    squared_error_y_mean = sum((y_mean_line - ys_orig) * \
                               (y_mean_line - ys_orig))
    return 1 - (squared_error_regr / squared_error_y_mean)


# days in January
x1 = [np.float(x) for x in range(1, 12)]
# reported number of cases
y01 = [35., 40., 51., 85., 114., 160., 206.,
      271., 321., 373., 460., ]
#x2 = [np.float(x) for x in range(27, 33)]
#y02 = [4515., 5974., 7711., 9692., 11791., 14380., ]
#ytot = []
#ytot.extend(y01)
#ytot.extend(y02)

# natural log of number of reported cases
y1 = np.log(y01)
#y2 = np.log(y02)
#ytotlog = np.log(ytot)

coef1 = np.polyfit(x1, y1, 1)
poly1d_fn1 = np.poly1d(coef1)
#coef2 = np.polyfit(x2, y2, 1)
#poly1d_fn2 = np.poly1d(coef2)

# statistical parameters first line
R1 = c_of_d(y1, poly1d_fn1(x1))  # R squared
yerr1 = poly1d_fn1(x1) - y1  # error
slope1 = coef1[0]  # slope
d_time1 = np.log(2.) / slope1  # doubling time
R01 = np.exp(slope1) - 1.

# statistical parameters second line
#R2 = c_of_d(y2, poly1d_fn2(x2))  # R squared
#yerr2 = poly1d_fn2(x2) - y2  # error
#slope2 = coef2[0]  # slope
#d_time2 = np.log(2.) / slope2  # doubling time
#R02 = np.exp(slope2) - 1.

#plot_suptitle = "Linear fit of " + \
#                "log cases $N=Ce^{bt}$ with " + \
#                "$b=$%.2f day$^{-1}$ (red) and $b=$%.2f day$^{-1}$ (green)" % (slope1, slope2)
plot_suptitle = "Linear fit of " + \
                "log cases $N=Ce^{bt}$ with " + \
                "$b=$%.2f day$^{-1}$ (red)" % slope1
plot_title1 = "Coefficient of determination R=%.3f" % R1 + "\n" + \
              "Population Doubling time: %.1f days" % d_time1 + "\n" + \
              "Estimated Daily $R_0=$%.1f" % R01
#plot_title2 = "Coefficient of determination R=%.3f" % R2 + "\n" + \
#              "Population Doubling time: %.1f days" % d_time2 + "\n" + \
#              "Estimated Daily $R_0=$%.1f" % R02
plot_name = "2019-ncov_lin_{}-{}-2020_UK.png".format(str(int(x1[-1] + 1.)), month)

# plotting
plt.plot(x1, y1, 'yo', x1, poly1d_fn1(x1), '--k')
plt.errorbar(x1, y1, yerr=yerr1, fmt='o', color='r')
#plt.plot(x2, y2, 'yo', x2, poly1d_fn2(x2), '--k')
#plt.errorbar(x2, y2, yerr=yerr2, fmt='o', color='g')
plt.grid()
plt.axvline(27, color='red')
plt.xlim(x1[0] - 1.5, x1[-1] + 1.5)  # x2[-1] + 1.5)
plt.ylim(2.5, 8.)
plt.yticks(y1, [np.int(y01) for y01 in y01])  # ytot])
plt.xlabel("March Date (DD/03/2020)")
plt.ylabel("Number of 2019-nCov cases on given day DD")
plt.suptitle("2019-nCoV in UK")
plt.title(plot_suptitle)
plt.text(2., 7., plot_title1)
#plt.text(16., 7.5, plot_title2)
plt.savefig(plot_name)
plt.show()
