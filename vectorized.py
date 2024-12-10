import random as rand
import numpy as np
import pandas as pd
rng = np.random.default_rng()
league_size = 2000
generations = 2000
#players = {i : [1000, x := rand.randint(0,70), rand.randint(20,80), rand.randint(20,80), x, 0, rand.randint(0, 100), rand.randint(0,12)] for i in range(1, 10001)}
lower_bounds = [0, 16, 10, 20, 0, 0, 16, 120]
upper_bounds = [1, 60, 40, 80, 80, 80, 120, 800]
players = np.random.randint(lower_bounds, upper_bounds, size = (league_size, 8))
players[:, 0] = 1500
players[:, 5] = 0
players[:, 4] = players[:, 1]
init_sum = np.sum(players[:, 0])


consistency_to_std = {i : i // 5 for i in range(20, 81)}
dropouts = np.zeros((300, 8), dtype=int)
d_counter = 0
def dropout(a):
    global d_counter
    d_counter += 1
    if d_counter > dropouts.shape[0] - 1:
        dropouts.resize((d_counter + 2, 8))
    print(f'player {players[a]} is a dropout')
    dropouts[d_counter] = np.array(players[a])
    players[a] = np.random.randint(lower_bounds, upper_bounds, 8)
    players[a][0] = 1500
    players[a][5] = 0
    players[a][4] = players[a][1]
def play(a, b, games):
    a_skill = players[a,1]  
    b_skill = players[b,1]
    a_score = rng.normal(a_skill, players[a, 2], games)
    b_score = rng.normal(b_skill, players[b, 2], games)
    return a_score - b_score 
            
def match(a, b, k):
    interest_factor = (players[a, 7] + players[b, 7]) // 80
    games = int(rng.normal(interest_factor, 3)) 
    if games > 12:
        games = 12
    if games < 1:
        games = 1
    print(games)
    players[a][5] += games
    players[b][5] += games

    
    scores = play(a,b,games)

    for score in scores:
        expected_a = expected(a, b)
        expected_b = 1 - expected_a
        if score > 0:
            a_float = k * (1 - expected_a)
            b_float = k * (0 - expected_b)
            players[a][0] += int(a_float)
            players[b][0] += int(b_float)
        else:
            a_float = k * (0 - expected_a)
            b_float = k * (1 - expected_b)
            players[a][0] += int(a_float)
            players[b][0] += int(b_float)
    if players[a][0] < 500:
        dropout(a)
        #players = players[players[:, 0].argsort()]
    if players[b][0] < 500:
        dropout(b)
        #players = players[players[:, 0].argsort()]

def improve(a, b):
    improve_factor = rand.randint(1, 6000)
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

max_waste = {}
def matchmake(a, i):
    waste = 0
    edges = 50
    elo = players[a][0]
    leinency = abs(elo - 1500) // 5
    upper = league_size // 10 * 9
    lower = league_size // 10
    border = league_size // 10
    if a > league_size - edges: 
        return rand.randint(league_size * .97, league_size - 1)
    if a < edges and a > 0:
        return rand.randint(0, edges)
    while True:
        if a > lower and a < upper:
            b = rand.randint(a - border, a + border)
            #print(f'border: {border} a: {a}')
        elif a <= lower:
            b = rand.randint(1, lower * 2)
        else: 
            b = rand.randint(len(players - 1) - border * 2,len(players) - 1)
        if players[b][0] < 500:
            dropout(b)
            continue
        if abs(players[b][0] - elo) < 250 + leinency:
            break
        waste += 1
    if waste > 1:
        max_waste[i] = (waste, a, int(players[a][0]))    
    return b
    

for i in range(1,5):
    battles = rng.normal(players[:, 1], players[:, 2], league_size)
    battles = battles.astype(int)
    battles2 = np.roll(battles, league_size // 2)
    mask = battles > battles2
    players[mask, 0] += 10
    players[~mask, 0] -= 10
    players[:, 5] += 1
    np.random.shuffle(players)
         
for i in range(league_size * generations):
    while True: 
        #waste = 0
        a = rand.randint(2, len(players) - 1)
        interest_bar = rand.randint(0, 160)
        #print(f'iterations:{i}, a: {a} elo: {players[a][0]}')
        if players[a][7] < interest_bar:
            if interest_bar % 2 == 0:
                players[a][7] -= 1
            if players[a][0] < 1500:
                players[a][7] -= 1
            if players[a][0] < 1300:
                players[a][7] -= 1
            if players[a][0] < 1100:
                players[a][7] -= 1
            if players[a][0] < 900:
                players[a][7] -= 1

            if players[a][7] < 0:
                dropout(a)
                players = players[players[:, 0].argsort()]
            #waste += 1
            continue
        if players[a][0] < 500 :
            dropout(a)
            players = players[players[:, 0].argsort()]
            continue
        break  
    b = matchmake(a,i)
    match(a, b, 40)
    improve(a, b)
    #max_waste.append(waste)
    if i % league_size // 10 == 0:
        players = players[players[:, 0].argsort()]         
    #if i % league_size == 0:
        #print(f'iteration: {i}')
        #print(f'elo distance: {np.max(players[:, 0]) - np.min(players[:, 0])}')
        #players = players[players[:, 0].argsort()]

            
        
    
    #print(players)
#dropouts_dict = {i : dropouts[i] for i in range(len(dropouts))}

dropouts = pd.DataFrame(dropouts)
matchmake = pd.DataFrame(players)
#dropouts = pd.DataFrame(dropouts_dict).transpose()
dropouts.columns = ['elo', 'skill', 'consistency', 'aptitude', 'floor', 'matches', 'ceiling', 'interest']
matchmake.columns = ['elo', 'skill', 'consistency', 'aptitude', 'floor', 'matches', 'ceiling', 'interest']
matchmake['elo'] = matchmake['elo'].astype(int)
matchmake['skill'] = matchmake['skill'].astype(int)
matchmake['consistency'] = matchmake['consistency'].astype(int)
matchmake = pd.concat([matchmake, dropouts])

matchmake['reached_ceiling'] = matchmake['skill'] == matchmake['ceiling']
matchmake['improvement'] = matchmake['skill'] - matchmake['floor']
count = matchmake['reached_ceiling'].value_counts()
matchmake = matchmake.sort_values('elo', ascending=False)
skill = matchmake['elo'].corr(matchmake['skill'])
floor = matchmake['elo'].corr(matchmake['floor'])
aptitude = matchmake['elo'].corr(matchmake['aptitude'])
consistency = matchmake['elo'].corr(matchmake['consistency'])
ceiling = matchmake['elo'].corr(matchmake['ceiling'])
interest = matchmake['elo'].corr(matchmake['interest'])
match_count = matchmake['matches'].max() - matchmake['matches'].min()
matchmake.to_csv('elo.csv')
print(f'skill: {skill}\nfloor: {floor}\naptitude: {aptitude}\nconsistency: {consistency}\nceiling: {ceiling}\n interest: {interest}')
print(f'ceiling reached: {count[True]}\ndropouts: {d_counter}')
print(f'improvement {matchmake["improvement"].mean()}')
print(f'Match count range {match_count}')
matchmake_report = pd.DataFrame(max_waste).transpose()
matchmake_report = matchmake_report.to_csv('waste.csv')
"""
print(f'Mean matchmaking waste {np.mean(matchmake_report)}')
print(f'Standard Deviation of waste {np.std(matchmake_report)}')
print(f'Maximum waste {np.max(max_waste)}')
"""
