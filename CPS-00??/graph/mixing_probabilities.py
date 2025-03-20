#!/usr/bin/python

import sys
import math
import time
import scipy
from decimal import Decimal
from joblib import Parallel, delayed
import scipy.special
import argparse

# Considered adversarial stakes in percentage
stakes = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.25, 0.3, 0.33, 0.4, 0.45, 0.49] 
nb_stakes = len(stakes)

# Probability to have x trailing blocks, with stake s: 
# This function uses decimal to work with small numbers
def proba_attempts(x,s):
  return s, Decimal(s)**x * Decimal(1-s)

def eg(w,s):
 acc = Decimal(0)
 for x in range(w+1):
  acc += Decimal(x) * proba_attempts(x,s)[1]
 return s, acc

# Computes and print the expectation of grinding attempts for all adversaries
def all_egs(cores=1):
 start = time.time()
 results = Parallel(n_jobs=cores)(delayed(eg)(21600, s) for s in stakes)
 res = sorted(results, key=lambda x : x[0])
 end = time.time()
 print("\n--- computed in {0:.2f}s".format(end-start))
 print("stake \t E(#grinding attempts)")
 for r in res:
  print("{0:.3f}:\t {1:.3E}".format(r[0], r[1])) 

pows = [1,2,4,8,16,32,64,128,256]

def proba_table(cores=1):
    table = []
    row = ["N \ stake"]
    for s in stakes:
        row.append("{}%".format(s*100))
    table.append(row)
    for p in pows:
        row = [str(p)]
        results = Parallel(n_jobs=cores)(delayed(proba_attempts)(p, s) for s in stakes)
        res = sorted(results, key=lambda x: x[0])
        for r in res:
            row.append("{0:.2E}".format(r[1]))
        table.append(row)
    for row in table:
        for element in row:
            print(element, "\t", end="")
        print()

def year_table(cores=1):
    table = []
    row = ["N \ stake"]
    for s in stakes:
        row.append("{}%".format(s*100))
    table.append(row)
    for p in pows:
        row = [str(p)]
        results = Parallel(n_jobs=cores)(delayed(proba_attempts)(p, s) for s in stakes)
        res = sorted(results, key=lambda x: x[0])
        for r in res:
            row.append("{0:.2E}".format(5/(365*r[1])))
        table.append(row)
    for row in table:
        for element in row:
            print(element, "\t", end="")
        print()


def parseArguments():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Optional arguments
    parser.add_argument("-c", "--cores", help="number of threads", type=int, default=1)

    # Print version
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    # Parse arguments
    args = parser.parse_args()

    return args

if __name__ == '__main__':
  # Parse arguments
  args = parseArguments()
  
  # Optimize threads
  cores = min(args.cores, nb_stakes)
  
  # Run function
  all_egs(cores)
  print("\n--------------------- Table of probabilities")
  proba_table(cores)
  print("\n--------------------- Table of years")
  year_table(cores)