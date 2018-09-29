import json
import itertools
from collections import defaultdict,Counter
from string import strip
import numpy as np
import csv

data = json.load(open('../section_a.json'))

roles = set()

rolePairs = defaultdict(Counter)
roleMovement = defaultdict(Counter)
roleTimes = defaultdict(list)
careerProportions = defaultdict(list)
roleNumTo = Counter()
roleNumFrom = Counter()

for entry in data:
    if 'seg' in entry:
        theseRoles = list()
        theseRoleTimes = Counter()
        previousRole = None
        for seg in entry['seg']:
            thisRole =strip(seg['rs'])
            theseRoles.append(thisRole)
            if seg['date_from'] != '' and seg['date_to'] != '':
                date_from = int (seg['date_from'])
                date_to = int (seg['date_to'])
                roleTimes[thisRole] += [(date_to-date_from) + .5,]
                theseRoleTimes[thisRole] += (date_to-date_from) + .5
            roles.add(thisRole)
            if previousRole:
                roleMovement[thisRole][previousRole] += 1
                roleNumTo[thisRole]+= 1
                roleNumFrom[previousRole]+=1
            previousRole = thisRole
        for entry in itertools.combinations(theseRoles,2):
            entries = list(entry)
            entries.sort()
            rolePairs[entries[0]][entries[1]] += 1
        careerLength = np.sum(theseRoleTimes.values())
        for role,length in theseRoleTimes.items():
            careerProportions[role] += [length/careerLength,]
    
            
finalPairsList = list()
finalMovementsList = list()

for position,nextPositions in roleMovement.items():
    for nextpos,count in nextPositions.items():
        finalMovementsList.append((count,position,nextpos))

for position,nextPositions in rolePairs.items():
    for nextpos,count in nextPositions.items():
        finalPairsList.append((count,position,nextpos))
        
finalPairsList.sort(reverse=True)
finalMovementsList.sort(reverse=True)

roleScores = list()

csvout=csv.writer(open('roleData.csv','w'))

csvout.writerow(['myScore','Num. people in role','Num. transfers to role','Num. transfers from role','Total years in role','Mean years in role','Mean % career in role','Role'])

for role in roles:
    numFrom = roleNumFrom[role]
    numTo = roleNumTo[role]
    if numFrom == 0:
        numFrom = 1
    aveYearsSpentInRole = np.mean(roleTimes[role])
    aveCareerProportionInRole = np.mean(careerProportions[role])
    score = aveCareerProportionInRole*numTo/numFrom
#    if role == 'Ambassador to the U.S.A.':
#        print score,numFrom,numTo,np.mean(roleTimes[role])
    if not np.isnan(score):
#        roleScores.append([score,role,numFrom,numTo,aveYearsSpentInRole,aveCareerProportionInRole])
        roleScores.append([score,len(roleTimes[role]),numTo,numFrom,sum(roleTimes[role]),aveYearsSpentInRole,100*aveCareerProportionInRole,role.encode('utf-8'),])

roleScores.sort(reverse=True)
csvout.writerows(roleScores)
