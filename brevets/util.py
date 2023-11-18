import copy
import random

def random_worksheet_rows():
    datum = {'km': 1, 'loc': '', 'row_id': 0}
    worksheet_rows = []
    dist = 0
    max_rows = 20
    for i in range(0, max_rows):
        d = copy.deepcopy(datum)
        d['row_id'] += i
        if i == 0:
            d['km'] = 0
        elif i == max_rows - 1 and dist < 200:
            d['km'] = 200
        else:
            dist = random.randrange(dist, (i*10)+8, 1)
            d['km'] = dist

        dist = d['km']
        worksheet_rows.append(d)
    return worksheet_rows
