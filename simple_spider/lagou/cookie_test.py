with open('cookies') as f:
    for line in f.readlines():
        line = line.strip()
        # cookies = dict([c.split('=') for c in line.split(';')])
        # print cookies
        cs = line.split(';')
        cs.sort(cmp=None, key=None, reverse=False)
        print cs