import argparse

print("hey, I'm from python")
print("Added second line")

p = argparse.ArgumentParser()

p.add_argument('--var1', type=str, required=True, help='Just a var')

args = p.parse_args()

print(args.var1)
