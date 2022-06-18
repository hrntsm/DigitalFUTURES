import optuna


def objective(trial):
    x = trial.suggest_float('x', -10, 10)
    return (x - 2) ** 2


sampler = optuna.samplers.NSGAIISampler(
    population_size=10,
    mutation_prob=0.1,
    crossover_prob=0.8,
    swapping_prob=0.4,
)
study = optuna.create_study(sampler=sampler)
study.optimize(objective, n_trials=100)

print("Best param: ", study.best_params)
print("Best value: ", study.best_value)

vis = optuna.visualization.plot_optimization_history(study)
vis.show()
