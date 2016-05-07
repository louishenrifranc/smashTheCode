import sys
import random
import copy

# ------------Paramètres Algorithme Génétique--------------------------------------------------------------------------#

NBGENOME = 10
NBGEN = 10
MUTRATE = 5
CROSSRATE = 25

PREV = 6

# ------------Fonctions du problème------------------------------------------------------------------------------------#

def input_to_grid():
    Grid = {i: [] for i in range(6)}
    for _ in range(12):
        line = input()
        for i in range(6):
            if line[i] != '.':
                Grid[i] = [int(line[i])] + Grid[i]
    return Grid


def eval_grid(grid, genome, couls):
    Grid = copy.deepcopy(grid)
    res = 0
    for i in range(PREV):
        B, CP, GB = add_to_grid(Grid, genome[i], couls[i])
        if max([len(Grid[i]) for i in Grid]) >= 12:
            return 1
        if CP != 1:
            CP = 2**(CP+1)
        else:
            CP = 0
        res += (10 * B) * (CP + GB)
    return 10 + res

def dfs(grid, x, y, coul, visited):
    if (x >= 0) & (x <= 5):
        if (y >= 0) & (y < len(grid[x])):
            if y not in visited[x]:
                visited[x].add(y)
                if grid[x][y] == coul:
                    su = [(x, y)]
                    su += dfs(grid, x + 1, y, coul, visited)
                    su += dfs(grid, x, y + 1, coul, visited)
                    su += dfs(grid, x - 1, y, coul, visited)
                    su += dfs(grid, x, y - 1, coul, visited)
                    return su
    return ()


def clean_grid(grid, x, y, coul, B=0, CP=0, GB=0):
    visited = {i: set() for i in range(6)}
    bloc = sorted(dfs(grid, x, y, coul, visited), key=lambda x: x[1], reverse=True)
    lon = len(bloc)
    if lon >= 4:
        GB += lon - 4
        CP += 1
        for x, y in bloc:
            if y < len(grid[x]):
                B += 1
                del grid[x][y]
        for x, y in bloc:
            if y < len(grid[x]):
                B, CP, GB = clean_grid(grid, x, y, grid[x][y], B, CP, GB)
    return [B, CP, GB]


def add_to_grid(grid, col, coul):
    grid[col] += [coul, coul]
    return clean_grid(grid, col, len(grid[col]) - 1, coul)


def to_string(grid):
    res = ""
    for i in grid:
        res += str(i) + " : " + str(grid[i]) + "\n"
    return res


# ------------Fonctions Génétiques-------------------------------------------------------------------------------------#

def randomgen():
    return [random.randint(0, 5) for _ in range(PREV)]

def fitness(genome, couls, grid):
    return eval_grid(grid, genome, couls)

def fitnessPop(population, couls, grid):
    return [fitness(population[i], couls, grid) for i in range(NBGENOME)]

def randompop():
    return [randomgen() for _ in range(NBGENOME)]

def crossover(population):
    temp = []
    for k in range(len(population) // 2):
        p1, p2 = list(population[2 * k]), list(population[2 * k + 1])
        if random.randint(0, 100) < CROSSRATE:
            pas = random.randint(1, PREV - 1)
            temp += [p1[:pas] + p2[pas:], p2[:pas] + p1[pas:]]
        else:
            temp += [p1, p2]
    return temp

def mutatepop(population):
    return [mutate(i) for i in population]

def mutate(genome):
    for i in range(PREV):
        if random.randrange(0, 100) <= MUTRATE:
            genome[i] = random.randint(0, 5)
    return genome

def bestgenome(population, couls, grid):
    temp = fitnessPop(population, couls, grid)
    return population[temp.index(max(temp))]

def select(population, couls, grid):
    temp = []
    fitnesspop = fitnessPop(population, couls, grid)
    sumfit = int((sum(fitnesspop), 1)[sum(fitnesspop) == 0])
    for _ in range(len(population)):
        G = random.randrange(0, sumfit)
        res = 0
        i = 0
        while res < G:
            res += fitnesspop[i]
            i += 1
        temp.append(population[i-1])
    return temp

def to_string_pop(population, couls, grid):
    for ind in population:
        print(str(ind) + " " + str(fitness(ind, couls, grid)))

def algo_gen(grid, couls):
    pop = randompop()
    for i in range(NBGEN):
        pop = crossover(pop)
        pop = mutatepop(pop)
        pop = select(pop, couls, grid)
    # to_string_pop(pop, couls, Grid)
    return bestgenome(pop, couls, grid)

def next_turn(genome):
    return genome[1:] + [random.randint(0,5)]

# ---------------------------------------------------------------------------------------------------------------------#

gen = [0]*PREV

while True:
    couls = []
    for i in range(8):
        color_a, color_b = [int(j) for j in input().split()]
        if i < PREV:couls.append(color_a)

    print("couleurs :" + str(couls), file=sys.stderr)

    Grid = input_to_grid()
    for i in range(12):
        row = input()

    gen = next_turn(gen)
    better_gen = algo_gen(Grid, couls)

    print("next turn gen :"+ str(gen) + " " +str(fitness(gen, couls, Grid)) , file=sys.stderr)
    print("algo gen      :"+ str(better_gen) + " " + str(fitness(better_gen, couls, Grid)), file=sys.stderr)
    if fitness(better_gen, couls, Grid) > fitness(gen, couls, Grid):
        gen = better_gen


    print("genome choisis :"+ str(gen), file=sys.stderr)
    print(fitness(gen, couls, Grid),file=sys.stderr)
    print(gen[0])

    print(to_string(Grid),file=sys.stderr)


