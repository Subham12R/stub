from email.policy import strict
import os
import sys

from json import loads
from tabnanny import verbose

def greet(name):
    return f"Hello, {name}"

def add(a, b):
    return a + b

def process_data(items, threshold, mode, verbose):
    results = []

    for item in items:
        if item > threshold:
            if mode == "strict":
                results.append(item * 2)
            else:
                results.append(item)
    if verbose:
        print(results)
    total = sum(results)
    return total

def tiny():
    pass


items = [20, 40, 50, 20, 10 ,5]
verbose = True

process_data(items, 15, strict, verbose)