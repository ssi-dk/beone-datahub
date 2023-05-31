import json
import random
import string

def rndstr(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def rndpct():
    i: int = random.randint(0, 9999)
    f: float = i / 100
    s: str = '{:.2f}'.format(f)
    return f

def allele_generator():
    locus = 31717
    while locus <= 40274:
        yield "INNUENDO_cgMLST-000" + str(locus), str(999)
        locus += 1

run_name = rndstr(10)
sample = json.load(open('sample_template.json', 'r'))
sample_name = rndstr(10)
sample['name'] = sample_name
sample['categories']['sample_info']['summary']['sample_name'] = run_name + '_' + sample_name
sample['categories']['cgmlst']['summary']['call_percent'] = rndpct()
for (locus, value) in allele_generator():
     sample['categories']['cgmlst']['report']['data']['alleles'][locus] = str(random.randint(1, 1000))

json.dump(sample, open('fake_sample_1.json', 'w'))