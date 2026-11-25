import contextlib
import numpy as np
from .genatic import *


import numpy as np
from .genatic import *


def main(max_itrations=100, population_size=20, epslione=0.00001, patience=20):

    population = genrate_population(population_size)

    current_fitness = float("-inf")
    no_improvement = 0

    for generation in range(max_itrations):

        results = tournament(population, population_size)
        fitness = cal_fitness(results, population_size)

        max_fitness = np.max(fitness)
        best_of_n = get_best_individuals(population, fitness)

        if max_fitness > current_fitness + epslione:
            current_fitness = max_fitness
            no_improvement = 0
        else:
            no_improvement += 1

        print(f"Generation: {generation + 1}")
        print(f"Best fitness: {max_fitness}")
        print(f"No improvement: {no_improvement}")

        if no_improvement >= patience:
            print("Converged!")
            print(f"Best weight: {best_of_n[0]}")
            break

        new_weights = genetic_alg(best_of_n, population_size)
        population = new_weights

    return best_of_n[0], current_fitness


if __name__ == "__main__":
    with open("results.txt", "a") as file:
        file.write("\n-----------------------------------------\n")

        with contextlib.redirect_stdout(file):
            best_weight, fitness = main()
            print(best_weight)
            print(fitness)

        file.write("\n-----------------------------------------\n")
