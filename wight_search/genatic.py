import numpy as np



def genrate_population(size, num_dim):
    population = np.random.uniform(1, 100, size=(size, num_dim))
    population = np.sort(population, axis=1)
    return population


def fitness(win, draw, size):
    return (win + 0.5 * draw) / size ** 2



def tournament(population, size):
    pass