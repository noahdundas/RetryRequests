import time

# This is a small selection of utility methods, limited to those used by fetchGet/fetchPost

# Log the given data to file
def log(file, data):
    if(file is None):
        return
    data = cleanData(data)
    log = open(file, "a")
    output = time.asctime( time.localtime(time.time())) + " | " + data + "\n"
    log.write(output)
    log.close()

# Extracts and redacts authkey information from log output
def cleanData(data):
    index = data.find("authKey=")
    while(index != -1):
        endIndex = data.find("&", index)
        if(endIndex == -1):
            data = data[0:index]
        else:
            data = data[0:index] + data[endIndex+1:]
    return data
