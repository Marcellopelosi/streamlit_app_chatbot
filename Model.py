import random

def model(input):
    i = random.randint(0, 6)
    risposte = ["Non lo so :D", "Interessante...", "Fantastico!", "Dimmi", "Tutto quello che vuoi", "Mi piaci tanto", "Flora ti amo"]
    return risposte[i]
