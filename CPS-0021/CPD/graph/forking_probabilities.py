#!/usr/bin/python

import sys
import math
import scipy
from decimal import Decimal
from joblib import Parallel, delayed
import scipy.special
import argparse
from tabulate import tabulate


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
 results = Parallel(n_jobs=cores)(delayed(eg)(s, precision) for s in stakes)
 res = sorted(results, key=lambda x : x[0])
 # Printing tables (use tabulate's option tablefmt="plain" to have no lines)
 headers = ["stake (%)"] + ["{:.1f}%".format(s*100) for s in stakes]
 table = [["E(g)"] + ["{0:.2E}".format(r[1]) for r in res]]
 print("\nTable of grinding attempts")
 print(tabulate(table, headers, tablefmt='orgtbl'))


def proba_diff(diff, s, precision=10):
 ps = []
 for i in range(precision+1):
  acc = Decimal(1)
  for j in range(1,i+1):
   acc = acc * Decimal((diff+2*i+1-j)/j) * Decimal(s) * Decimal(1-s)
  for j in range(i+1,diff+i+1):
   acc = acc * Decimal((diff+2*i+1-j)/j) * Decimal(s)
  for (j, di) in enumerate(ps):
   acc_d = di
   for l in range(1, i-j+1):
    acc_d = Decimal(acc_d) * Decimal((2*i-2*j+1-l)/l) * Decimal(s) * Decimal(1-s)
   acc = acc - acc_d
  ps.append(acc)
 return (s, sum(ps))

def tables(precision=10, cores=1):
 # Computing the tables of probabilities
 table = []
 pows = [1,2,4,8,16,32,64,128,256]
 for p in pows:
  results = Parallel(n_jobs=cores)(delayed(proba_diff)(p, s, precision) for s in stakes)
  row = sorted(results, key=lambda x: x[0])
  table.append([r[1] for r in row])
 # Printing tables (use tabulate's option tablefmt="plain" to have no lines)
 headers = ["|Xa - Xh| vs stake"] + ["{:.1f}%".format(s*100) for s in stakes]
 # Printing the tables of probabilities
 table_proba = [[pows[i]] + ["{:.3E}".format(el) for el in row] for (i,row) in enumerate(table)]
 print("\nTable of probabilities")
 print(tabulate(table_proba, headers, tablefmt='orgtbl'))
 # Printing the tables of frequencies (per year)
 table_year = [[pows[i]] + ["{:.2E}".format(5./(float(el)*365.0)) if float(el) !=0 else "-" for el in row] for (i,row) in enumerate(table)]
 print("\nTable of frequencies (year)")
 print(tabulate(table_year, headers, tablefmt='orgtbl'))


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
  precision = args.precision
  cores = min(args.cores, nb_stakes)
  print("Printing forking's figures with precision={}".format(precision))
  
  # Run function
  all_egs(precision, cores)
  
  # Run tables
  tables(precision, cores)
