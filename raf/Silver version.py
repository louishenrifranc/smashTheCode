import sys
import random
import copy
import time

# ------------Paramètres Algorithme Génétique--------------------------------------------------------------------------#

NBGENOME = 10
NBGEN = 10
MUTRATE = 5
CROSSRATE = 25

PREV = 5


# ------------Fonctions du problème------------------------------------------------------------------------------------#

def ori_from_col(col):
    if col == 5:
        ori = random.randint(1, 3)
    elif col == 0:
        ori = random.randint(0, 2)
        if ori == 2:
            ori += 1
    else:
        ori = random.randint(0, 3)
    return ori


def input_to_grid():
    Grid = {i: [] for i in range(6)}
    for _ in range(12):
        line = input()
        for i in range(6):
            if line[i] != '.':
                Grid[i] = [int(line[i])] + Grid[i]
    return Grid


def output(genome):
    print(str(genome[0]) + " " + str(genome[0 + PREV]))


def eval_grid(grid, genome, couls):
    Grid = copy.deepcopy(grid)
    res = 0
    for i in range(PREV):
        B, CP, GB = add_to_grid(Grid, genome[i], genome[PREV + i], couls[i])
        if max([len(Grid[i]) for i in Grid]) >= 12:
            return 1
        if CP != 1:
            CP = 2 ** (CP + 1)
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


def clean_grid_double(grid, x1, y1, x2, y2, coul1, coul2, B=0, CP=0, GB=0):
    delete = []
    visited = {i: set() for i in range(6)}
    bloc1 = dfs(grid, x1, y1, coul1, visited)
    visited = {i: set() for i in range(6)}
    bloc2 = dfs(grid, x2, y2, coul2, visited)
    lon1 = len(bloc1)
    lon2 = len(bloc2)
    if lon1 >= 4:
        GB += lon1 - 4
        CP += 1
        for x, y in bloc1:
            B += 1
            delete.append((x, y))
    if lon2 >= 4:
        GB += lon2 - 4
        CP += 1
        for x, y in bloc2:
            B += 1
            delete.append((x, y))
    CP = min([1, CP])
    delete = sorted(delete, key=lambda x: x[1], reverse=True)
    for x, y in delete:
        if y < len(grid[x]):
            del grid[x][y]
        if y < len(grid[x]):
            B, CP, GB = clean_grid(grid, x, y, grid[x][y], B, CP, GB)
    return [B, CP, GB]


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


def add_to_grid(grid, col, ori, coul):
    if ori == 0:
        grid[col] += [coul[0]]
        grid[col + 1] += [coul[1]]
        return clean_grid_double(grid, col, len(grid[col]) - 1, col + 1, len(grid[col + 1]) - 1, coul[0], coul[1])

    elif ori == 1:
        grid[col] += [coul[0], coul[1]]
        return clean_grid_double(grid, col, len(grid[col]) - 2, col, len(grid[col]) - 1, coul[0], coul[1])

    elif ori == 2:
        grid[col] += [coul[0]]
        grid[col + -1] += [coul[1]]
        return clean_grid_double(grid, col, len(grid[col]) - 1, col - 1, len(grid[col - 1]) - 1, coul[0], coul[1])

    else:
        grid[col] += [coul[1], coul[0]]
        return clean_grid_double(grid, col, len(grid[col]) - 2, col, len(grid[col]) - 1, coul[1], coul[0])


def to_string(grid):
    res = ""
    for i in grid:
        res += str(i) + " : " + str(grid[i]) + "\n"
    return res


# ------------Fonctions Génétiques-------------------------------------------------------------------------------------#

def randomgen():
    temp = [random.randint(0, 5) for _ in range(PREV)]
    for i in range(PREV):
        temp += [ori_from_col(temp[i])]
    return temp


def fitness(genome, couls, grid):
    return eval_grid(grid, genome, couls)


def fitnessPop(population, couls, grid):
    return [fitness(population[i], couls, grid) for i in range(NBGENOME)]


def randompop():
    return [randomgen() for _ in range(NBGENOME)]


def crossover(population):
    temp = []
    for k in range(NBGENOME // 2):
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
    for i in range(PREV):
        if random.randrange(0, 100) <= MUTRATE:
            genome[i] = random.randint(0, 3)
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
        temp.append(population[i - 1])
    return temp


def to_string_pop(population, couls, grid):
    for ind in population:
        print(str(ind) + " " + str(fitness(ind, couls, grid)))


def hill_climbing(grid, couls):
    genome = randomgen()
    bestfit = 0
    for _ in range(50):
        new_try = randomgen()
        new_try_fit = fitness(new_try, couls, grid)
        if new_try_fit > bestfit:
            genome = new_try
            bestfit = new_try_fit
    return genome


def algo_gen(grid, couls):
    pop = randompop()
    for i in range(NBGEN):
        pop = crossover(pop)
        pop = mutatepop(pop)
        pop = select(pop, couls, grid)
    to_string_pop(pop, couls, Grid)
    return bestgenome(pop, couls, grid)


def next_turn(genome):
    col = random.randint(0, 5)
    ori = ori_from_col(col)
    return genome[1:PREV] + [col] + genome[PREV + 1:2 * PREV] + [ori]


# ---------------------------------------------------------------------------------------------------------------------#
gen = [1] * PREV * 2

while True:
    couls = []
    for i in range(8):
        color_a, color_b = [int(j) for j in input().split()]
        if i < PREV: couls.append((color_a, color_b))

    print("couleurs :" + str(couls), file=sys.stderr)

    Grid = input_to_grid()
    for i in range(12):
        row = input()

    gen = next_turn(gen)
    better_gen = hill_climbing(Grid, couls)

    print("next turn gen :" + str(gen) + " " + str(fitness(gen, couls, Grid)), file=sys.stderr)
    print("algo gen      :" + str(better_gen) + " " + str(fitness(better_gen, couls, Grid)), file=sys.stderr)
    if fitness(better_gen, couls, Grid) > fitness(gen, couls, Grid):
        gen = better_gen

    print("genome choisis :" + str(gen), file=sys.stderr)
    print(fitness(gen, couls, Grid), file=sys.stderr)

    output(gen)

    print(to_string(Grid), file=sys.stderr)
