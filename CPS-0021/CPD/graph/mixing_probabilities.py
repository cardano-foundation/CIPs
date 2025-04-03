#!/usr/bin/python

import sys
import math
import time
import scipy
from decimal import Decimal
from joblib import Parallel, delayed
import scipy.special
import argparse
from tabulate import tabulate

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
 results = Parallel(n_jobs=cores)(delayed(eg)(21600, s) for s in stakes)
 res = sorted(results, key=lambda x : x[0])
 # Printing tables (use tabulate's option tablefmt="plain" to have no lines)
 headers = ["stake (%)"] + ["{:.1f}%".format(s*100) for s in stakes]
 table = [["E(g)"] + ["{0:.2E}".format(r[1]) for r in res]]
 print("\nTable of grinding attempts")
 print(tabulate(table, headers, tablefmt='orgtbl'))


def tables(cores=1):
 table = []
 pows = [1,2,4,8,16,32,64,128,256]
 for p in pows:
  results = Parallel(n_jobs=cores)(delayed(proba_attempts)(p, s) for s in stakes)
  row = sorted(results, key=lambda x: x[0])
  table.append([r[1] for r in row])
 # Printing tables (use tabulate's option tablefmt="plain" to have no lines)
 headers = ["N vs stake"] + ["{:.1f}%".format(s*100) for s in stakes]
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
  print("Printing self-mixing's figures")

  # Run function
  all_egs(cores)

  # Run tables
  tables(cores)