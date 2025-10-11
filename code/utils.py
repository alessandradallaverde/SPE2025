import random
from scipy.stats import expon

# create an exponential delay
def delay(mean):
    return random.expovariate(1/mean)

# compares two integers
def cmp(a, b):
    return (a > b) - (a < b)

# compute the mquantile of an exponential function
def max_delay(quantile, mean):
    return expon.ppf(quantile, loc = 0, scale = mean)