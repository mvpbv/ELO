import random as rand
import numpy as np
import pandas as pd
rng = np.random.default_rng()

players = {i : [1000, x := rand.randint(0,70), rand.randint(20,80), rand.randint(20,80), x, 0, rand.randint(0, 100), rand.randint(0,12)] for i in range(1, 10001)}

league_size = len(players) - 1
consistency_to_std = {i : i // 5 for i in range(20, 81)}

def play(a, b):
    a_skill = players[a][1]  
    b_skill = players[b][1]
    b_var = consistency_to_std[players[b][2]]
    a_var = consistency_to_std[players[a][2]]
    a_score = rng.normal(a_skill, a_var)
    b_score = rng.normal(b_skill, b_var)
    return a_score > b_score
            
def match(a, b, k):
    players[a][5] += 1
    players[b][5] += 1
    expected_a = expected(a, b)
    expected_b = expected(b, a)
    #print(f"expected_a: {expected_a}\nexpected_b: {expected_b}")
    a_won = play(a,b)
    if a_won:
        a_float = k * (1 - expected_a)
        b_float = k * (0 - expected_b)
        players[a][0] += int(a_float)
        players[b][0] += int(b_float)
    else:
        a_float = k * (0 - expected_a)
        b_float = k * (1 - expected_b)
        players[a][0] += int(a_float)
        players[b][0] += int(b_float)

def improve(a, b):
    improve_factor = rand.randint(1, 5000)
    if players[a][1] < players[a][6]:
        if players[a][3] > improve_factor:
            players[a][1] += 1
    if players[b][1] < players[b][6]:
        if players[b][3] > improve_factor:
            players[b][1] += 1

def expected(a, b):
    dif = (players[b][0] - players[a][0])
    #print(f'dif: {dif}')
    dif_frac = dif / 400
    #print(f'dif_frac: {dif_frac}')
    inv = 1 + 10 ** dif_frac
    #print(f'inv: {inv}')
    e = 1 / inv
    #print(f'e: {e}')
    return e
def matchmake(a):
    elo = players[a][0]
    while True:
        b = rand.randint(1, league_size)
        if players[b][0] < 100:
            
        if abs(players[b][0] - elo) < 200:
            return b
    
dropouts = []
for i in range(10000000):
    a = rand.randint(1, league_size)
    if players[a][0] < 100:
        dropouts.append(players[a])
        players[a] = [1000, x := rand.randint(0,70), rand.randint(20,80), rand.randint(20,80), x, 0, rand.randint(0, 100), rand.randint(0,12)]
    b = matchmake(a)
    match(a, b, 32)
    improve(a, b)         

             
            
    
    #print(players)
dropouts_dict = {i : dropouts[i] for i in range(len(dropouts))}

matchmake = pd.DataFrame(players).transpose()
dropouts = pd.DataFrame(dropouts_dict).transpose()
dropouts.columns = ['elo', 'skill', 'consistency', 'aptitude', 'floor', 'matches', 'ceiling', 'interest']
matchmake.columns = ['elo', 'skill', 'consistency', 'aptitude', 'floor', 'matches', 'ceiling', 'interest']
matchmake['elo'] = matchmake['elo'].astype(int)
matchmake['skill'] = matchmake['skill'].astype(int)
matchmake['consistency'] = matchmake['consistency'].astype(int)
matchmake = pd.concat([matchmake, dropouts])

matchmake['reached_ceiling'] = matchmake['skill'] == matchmake['ceiling']
count = matchmake['reached_ceiling'].value_counts()
matchmake = matchmake.sort_values('elo', ascending=False)
skill = matchmake['elo'].corr(matchmake['skill'])
floor = matchmake['elo'].corr(matchmake['floor'])
aptitude = matchmake['elo'].corr(matchmake['aptitude'])
consistency = matchmake['elo'].corr(matchmake['consistency'])
ceiling = matchmake['elo'].corr(matchmake['ceiling'])
interest = matchmake['elo'].corr(matchmake['interest'])
matchmake.to_csv('elo.csv')
print(f'skill: {skill}\nfloor: {floor}\naptitude: {aptitude}\nconsistency: {consistency}\nceiling: {ceiling}\n interest: {interest}')
print(f'ceiling reached: {count[True]}')



