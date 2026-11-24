import numpy as np


from board import *
from alphabeta import *
from hurastic import *
AI1=1
AI2=2

def genrate_population(population_size, num_dim=4):
    population = np.random.uniform(1, 100, size=(population_size, num_dim))
    population = np.sort(population, axis=1)
    return population

ef tournament(population, population_size):

    results = np.zeros((population_size, 2), dtype=int) #[win, draw]


    for i, wp1 in enumerate(population):
        for j, wp2 in enumerate(population):

            if i == j:
                continue

             
            state = play(wp1, wp2)
            if(state == 0):
                results[i][1] += 1
                results[j][1] += 1
            elif(state == 1):
                results[i][0] += 1
            else:
                results[j][0] += 1


    return results

def fitness_fun(win, draw, population_size):
    return (win + 0.5 * draw) / (2 * (population_size - 1))

def cal_fitness(results, population_size):
    fitness = np.zeros(population_size)

    for i in range(len(results)):
        fitness[i] = fitness_fun(results[i][0], results[i][1], population_size)

    return fitness

def get_best_individuals(population, fitness, num_selected=10):
    ranking = np.argsort(fitness)[::-1]
    best_indices = ranking[:num_selected]
    best_of_n = population[best_indices]

    return best_of_n


def genetic_alg(best_of_n, population_size):
    new_population = []

    for _ in range(population_size // 2):

        indices = np.random.choice(
            len(best_of_n),
            size=2,
            replace=False
        )

        parent1, parent2 = best_of_n[indices]

        child1, child2 = crossover(parent1, parent2)

        child1 = mutation(child1)
        child2 = mutation(child2)

        new_population.extend([child1, child2])

    return np.array(new_population)


def crossover(parent1, parent2):
    point = np.random.randint(1, len(parent1))

    child1 = np.concatenate((
        parent1[:point],
        parent2[point:]
    ))

    child2 = np.concatenate((
        parent2[:point],
        parent1[point:]
    ))

    child1 = np.sort(child1)
    child2 = np.sort(child2)

    return child1, child2

def mutation(child):
    child = child.copy()

    idx = np.random.randint(0, len(child))
    child[idx] = np.random.uniform(1, 100)

    return np.sort(child)

ef gameStats(weights,k):
    n=len(weights)
    status=[[0,0] for _ in range (n)]
    for i in range (n):
        for j in range(i+1,n):
            if i==j:
                continue

            board = initilize_board()
            while not isboardfilled(board):
   
              ai1_turn = bestmove(board, k, AI1, weights[i])
              makemove(board, ai1_turn, AI1)
    
              if isboardfilled(board):
                 break

              ai2_turn = bestmove(board, k, AI2, weights[j])
              makemove(board, ai2_turn, AI2)
    

              if isboardfilled(board):
                     break

            ai1_final, ai2_final = get_all_windows(board)
            score = ai1_final[3] - ai2_final[3]

            if score > 0:
                status[i][0]+=1
    
            elif score < 0:
                status[j][0] +=1
             
            else:
              status[i][1] +=1
              status[j][1] +=1
    return status       




def fitness(win, draw, size):
    return (win + 0.5 * draw) / size ** 2



def tournament(population, size):
    pass