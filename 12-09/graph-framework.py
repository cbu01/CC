import matplotlib
import pylab

x_values1 = [1,2,3,4,5,6]
y_values1 = [1,2,1,2,1,2]

x_values2 = [1,2,3,4,5,6]
y_values2 = [1,2,3,3,2,1]

pylab.plot(x_values1, y_values1, '.b-')
pylab.plot(x_values2, y_values2, '.r-')
# ... repeat pylab.plot for all functions: b = blue, r = red, g = green
axis1_min = 0
axis1_max = 7
axis2_min = 0
axis2_max = 4

pylab.axis([axis1_min,axis1_max,axis2_min,axis2_max])
pylab.savefig('filename.png')