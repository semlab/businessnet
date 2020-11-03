# Print iteration prograss
def printProgressBar(iteration, total, prefix="", suffix="", decimals=1, length=100, fill='█', printEnd='\r'):
    """
    Call in a loop to create a terminal prograssbar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iteration (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimal in percent complete (Int)
        length      - Optional  : character length of the bar
        fill        - Optional  : bar fill character
        printEnd    - Optional  : end character (e.g. '\r', '\r\n')
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    #print new line on complete
    if iteration == total:
        print()
