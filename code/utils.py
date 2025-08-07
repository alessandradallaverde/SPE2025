import random

# create an exponential delay
def delay(mean):
    return random.expovariate(1/mean);

# compares two integers
def cmp(a, b):
    return (a > b) - (a < b)