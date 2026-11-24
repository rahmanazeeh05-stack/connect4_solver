
import contextlib
import numpy as np
from .genatic import *


def main(max_itrations=100, population_size=20,
         epslione=0.00001, patience=25):

    population = genrate_population(population_size)

    global_best_fitness = float('-inf')
    global_best_weights = None
    no_improvement = 0
    best_of_n = None

    for generation in range(max_itrations):

        results = tournament(population, population_size)
        fitness = cal_fitness(results, population_size)

        max_fitness = np.max(fitness)
        best_of_n = get_best_individuals(population, fitness)

        if max_fitness > global_best_fitness + epslione:
            global_best_fitness = max_fitness
            global_best_weights = best_of_n[0].copy()
            no_improvement = 0
        else:
            no_improvement += 1

        print(f"Generation: {generation + 1}")
        print(f"Best fitness: {max_fitness}")
        print(f"Global best fitness: {global_best_fitness}")
        print(f"No improvement: {no_improvement}")

        if no_improvement >= patience:
            print("Converged!")
            break

        population = genetic_alg(best_of_n, population_size)

    return best_of_n[0], global_best_fitness, global_best_weights


if __name__ == "__main__":
    with open("results.txt", "a") as file:
        file.write("\n-----------------------------------------\n")

        with contextlib.redirect_stdout(file):
            best_weight, fitness, best_weight_over_all = main()

            print(f"Best weight of last generation: {best_weight}")
            print(f"Best fitness overall: {fitness}")
            print(f"Best weight overall: {best_weight_over_all}")

        file.write("\n-----------------------------------------\n")
