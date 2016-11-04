import time

lastPrint = time.time() * 1000
counter = 0
lastPercPrint = 0

def progressRatio(currentNb, total, message = "", granularity = 10):
    global lastPercPrint
    perc = int(currentNb / total * 100)
    if lastPercPrint != perc and perc % granularity == 0 :
        print(message + " : " + str(currentNb) + "/" + str(total) + " : " + str(perc) + "% completed")
        lastPercPrint = perc

def razIndicatorCounter():
    global counter
    counter = 0

def progressIndicator(message,delta,printCounter = False):
    global lastPrint
    global counter
    current = time.time() * 1000
    if current-lastPrint < delta:
        return

    text = message
    if printCounter:
        text += " " + str(counter)

    counter += 1
    print(text)

