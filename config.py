file = open("config.ini", 'r')
lines = file.readlines()
config = {}
for line in lines:
    # remove trailing newline
    line = line.replace("\n", "")
    # remove leading and trailing spaces
    line = line.strip()
    # skip empty lines
    if len(line) == 0:
        continue
    # skip lines starting with #
    if line[0] == "#":
        continue
    # get rid of spaces around equal sign
    line = line.replace(" =", "=")
    line = line.replace("= ", "=")
    (k, v) = line.split("=")
    config[k] = v
file.close()
