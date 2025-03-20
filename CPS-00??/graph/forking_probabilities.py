#!/usr/bin/python

import sys
import math
import time
import scipy
from decimal import Decimal
from joblib import Parallel, delayed
import scipy.special
import argparse

# Considered adversaral stakes in percentage
stakes = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.25, 0.3, 0.33, 0.4, 0.45, 0.49] 
nb_stakes = len(stakes)

# Probability to have x out of w blocks, with stake s: 
# B_{w, s}(x) = (x out of w) * s^x * (1-s)^{w-x}
# This function uses decimal to work with small numbers
def proba_attempts(w,x,s):
  return Decimal(scipy.special.binom(w,x)) * Decimal(s)**x * Decimal(1-s)**(w-x)

# Number of grinding attempts for an interval of size w blocks
# and x blocks controlled by the adversary: 
# S(w, x) = Sum_{i >= w-x}^{x} (i out of x)
def number_attempts_adv(w, x):
 acc = Decimal(0)
 for i in range(w-x, x+1):
  acc += Decimal(scipy.special.binom(x, i))
 return acc

# Total number of grinding attempts for an interval of w blocks:
# S(w) = Sum_{x = w/2}^w S(w,x)
def number_attempts(w):
  acc = Decimal(0)
  # For an adversary having between w/2 to w blocks
  for x in range(math.ceil(w/2), w+1):
    # Number of combinaisons possible
    acc += number_attempts_adv(w,x)
  return acc

# Expected number of grinding attempts for an interval of size w blocks,
# and x blocks controlled by the adversary with stake s:
def expectation(w,x,s):
    return proba_attempts(w, x, s) * number_attempts_adv(w, x)

# The expected number of grinding attempt for an interval of size d
# and an adversary with s stake:
# C(w, s) = Sum_{d=1}^w ( Sum_{x=d/2}^d B_{d,s}(x) * S(d,x) )
# For Praos, s ~= 21600 * 4 / 10, but this number is too high for scipy
# This function can still be used to show the convergence with increasingly high s however
def eg(s, precision=10, cores=2):
 p = Decimal(0)
 for w in range(1, precision):
  results = Parallel(n_jobs=cores)(delayed(expectation)(w, x, s) for x in range(math.ceil(w/2),w+1))
  for res in results:
    p += res
 return (s, Decimal(1-s) * p)  

# Computes and print the expectation of grinding attempts for all adversaries
def all_egs(precision=10, cores=1):
 start = time.time()
 results = Parallel(n_jobs=cores)(delayed(eg)(s, precision) for s in stakes)
 res = sorted(results, key=lambda x : x[0])
 end = time.time()
 print("\n--- precision={0} computed in {1:.2f}s".format(precision, end-start))
 print("stake \t E(#grinding attempts)")
 for r in res:
  print("{0:.3f}:\t {1:.3E}".format(r[0], r[1]))

def parseArguments():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Optional arguments
    parser.add_argument("-c", "--cores", help="number of threads", type=int, default=1)
    parser.add_argument("-p", "--precision", help="interval to compute E(g) on", type=int, default=32)

    # Print version
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    # Parse arguments
    args = parser.parse_args()

    return args

if __name__ == '__main__':
  # Parse arguments
  args = parseArguments()
  
  # Run function
  all_egs(precision=args.precision, cores=min(args.cores, nb_stakes))
