import random

def model(input):
    i = random.randint(0, 2)
    risposte = ["Non lo so :D", "Interessante...", "Fantastico!"]
    return risposte[i]
