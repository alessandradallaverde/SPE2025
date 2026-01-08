import random
from scipy.stats import expon

# create an exponential delay
#   params:
#       mean - exponential mean
#       rng - random number generator
def delay(mean, rng = None):
    if rng==None:
        return random.expovariate(1/mean)
    else:
        return rng.expovariate(1/mean)

# compares two integers
#   params:
#       a - first integer
#       b - second integer
def cmp(a, b):
    return (a > b) - (a < b)

# compute the quantile of an exponential function
#   params:
#       quantile - quantile desired
#       mean - exponential mean
def max_delay(quantile, mean):
    return expon.ppf(quantile, loc = 0, scale = mean)