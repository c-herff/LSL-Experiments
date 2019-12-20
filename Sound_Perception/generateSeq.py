import numpy as np
import time

def check(a):
    return ~(np.sum(np.diff(a)==0)>0)

def generateSequence():
    a=np.array([0,1,2,3,4,5]*12)
    t = time.time()
    np.random.shuffle(a)
    i=0
    while ~check(a):
        np.random.shuffle(a)
        i+=1
    print('Required %d shuffles in %f seconds' % (i,time.time()-t))
    return a


categories = ['animal', 'music','nature', 'speech','tools','voice']
for reps in range(6):
    file=open('stimSequence' + str(reps+1) + '.txt','w')
    seq=[]
    for block in range(1,48,12):
        stims = [np.random.permutation(np.arange(block,block+12)).tolist() for c in categories]
        a=generateSequence()
        idx = np.arange(len(a))
        to_double = np.random.choice(idx[1:-1],9)
        for i, item in enumerate(a):
            f = 's2_' + categories[item] + '_'  + str(stims[item].pop()) + '.wav'
            seq.append(f)
            if i in to_double:
                seq.append(f)
    for l in seq:
        file.write(l + '\n')
    file.close()