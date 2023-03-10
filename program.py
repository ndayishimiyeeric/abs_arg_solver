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

admissibles = []
c_f_list = []
substitutes = []


def generate_subsets(af, subset):
    args = set(af.keys())
    if len(subset) >= len(af):
        return
    if is_admissible(af, subset):
        admissibles.append(subset)

    if is_conflit_free(af, subset):
        c_f_list.append(subset)
    for arg in args:
        if arg not in subset:
            new_subset = subset + [arg]
            generate_subsets(af, new_subset)


def is_admissible(af, subset):
    return is_conflit_free(af, subset) and is_self_defending(af, subset)


def is_conflit_free(af, subset):
    for arg in subset:
        if any(attacked in subset for attacked in af[arg]):
            return False
    return True


def is_self_defending(af, subset):
    for arg in af:
        if any(attacked in subset for attacked in af[arg]):
            if not any(attacker in subset for attacker in af[arg]):
                return False
    return True


def get_arg_attackers(af, arg):
    return set(attacker for attacker in af if arg in af[attacker])


def is_arg_attacked(af, arg):
    return any(arg in af[attacker] for attacker in af)


def get_arg_attacked_by_subset(af, subset):
    return [arg for arg in af if is_arg_attacked(af, arg) and arg not in subset]


def is_arg_acceptable(af, arg, subset):
    attackers = get_arg_attackers(af, arg)
    subsetAtt = get_arg_attacked_by_subset(af, subset)
    if attackers:
        return all(attacker in subsetAtt and any(att in subset for att in get_arg_attackers(af, attacker)) for attacker in attackers)


def check_args_in_relation(af, args):
    # get all attack relations
    attacks = []
    for arg in af:
        for attacked in af[arg]:
            attacks.append((arg, attacked))
    return all(i[0] in args or i[1] in args for i in attacks)


def com_ex():
    complete_extensions = []
    subset = []
    generate_subsets(af, subset)

    if check_args_in_relation(af, af.keys()):
        if len(admissibles) > 0:
            for adm in admissibles:
                trueAdm = set()
                if len(adm) > 0:
                    for i in af.keys():
                        if is_arg_acceptable(af, i, adm):
                            trueAdm.add(i)

                    if trueAdm == set(adm):
                        adm.sort()
                        if adm not in complete_extensions:
                            complete_extensions.append(adm)
                else:
                    complete_extensions.append(adm)
    return complete_extensions


def sta_ex():
    complete_extensions = com_ex()

    stable_extensions = []
    subset = []
    generate_subsets(af, subset)

    for se in c_f_list:
        if all(any(attacked in se for attacked in af[arg]) for arg in af if arg not in se):
            se.sort()
            if se not in stable_extensions:
                if se in complete_extensions:
                    stable_extensions.append(se)

    return stable_extensions


if args.problem == "SE-CO":
    complete_extensions = com_ex()
    complete_extensions.sort(key=len)
    # substitutes = complete_extensions
    if complete_extensions:
        for extension in complete_extensions:
            print(extension)
            substitutes.append(extension)
    else:
        print("None.")

elif args.problem == "DC-CO":

    complete_extensions = com_ex()

    complete_extensions.sort(key=len)
    substitutes = complete_extensions
    if complete_extensions:
        for extension in complete_extensions:
            if args.argument in extension:
                print("YES")
                break
        else:
            print("NO")


elif args.problem == "DS-CO":

    complete_extensions = com_ex()
    complete_extensions.sort(key=len)
    substitutes = complete_extensions
    if complete_extensions:
        for extension in complete_extensions:
            if args.argument not in extension:
                print("NO")
                break
        else:
            print("YES")


elif args.problem == "SE-ST":
    stable_extensions = sta_ex()

    stable_extensions.sort(key=len)
    if stable_extensions:
        for extension in stable_extensions:
            print(extension)

elif args.problem == "DC-ST":

    stable_extensions = sta_ex()
    stable_extensions.sort(key=len)
    if stable_extensions:
        for extension in stable_extensions:
            if args.argument in extension:
                print("YES")
                break
        else:
            print("NO")

elif args.problem == "DS-ST":

    stable_extensions = sta_ex()
    stable_extensions.sort(key=len)
    if stable_extensions:
        for extension in stable_extensions:
            if args.argument not in extension:
                print("NO")
                break
        else:
            print("YES")
