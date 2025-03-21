import csv



def getColumn(filename, column, delimiter=',', skipinitialspace=False, skipheader=1):
    results = csv.reader(open(filename),delimiter=delimiter,skipinitialspace=skipinitialspace)
    while skipheader>0:
        next(results, None)
        skipheader=skipheader-1
    
    return [result[column] for result in results]
