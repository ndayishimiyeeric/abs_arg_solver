import argparse
import sys
sys.setrecursionlimit(10000)

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--problem", required=True,
                    help='problem type (SE-CO, DC-CO, DS-CO, SE-ST, DC-ST, DS-ST)')
parser.add_argument("-f", "--file", required=True,
                    help='input file with argumentation framework')
parser.add_argument("-a", "--argument",
                    help='query argument for DC-CO, DS-CO, DC-ST, DS-ST problems')
args = parser.parse_args()

# Parse input file to extract arguments and attacks
af = {}
with open(args.file, "r") as f:
    for line in f:
        if line.startswith('arg('):
            # Extract argument name
            argument = line[4:-3]
            af[argument] = []
        elif line.startswith('att('):
            # Extract attacked source and target
            attack = line[4:-2].split(',')
            if attack[1][-1] == ')':
                attack[1] = attack[1][:-1]
            af[attack[0]].append(attack[1])
