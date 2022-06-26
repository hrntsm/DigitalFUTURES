import compute_rhino3d.Util
import compute_rhino3d.Grasshopper as gh
import rhino3dm
import json
import optuna

compute_rhino3d.Util.url = 'http://localhost:6500/'


def objective(trial):
    ''' 目的関数の作成
    '''
    variables = []

    for i in range(10):
        variables.append(trial.suggest_uniform('genepool' + str(i), 500, 1500))

    result = run_gh(variables)
    return float(result[1])


def run_gh(variables):
    ''' Grasshopper でのモデル評価の実行
    '''
    result = []

    input_trees = []
    tree = gh.DataTree("MoveHeight")

    tree.Append([{0}], variables)
    input_trees.append(tree)

    output = gh.EvaluateDefinition('Path\\to\\ShellOpt.gh', input_trees)
    errors = output['errors']
    if errors:
        print('ERRORS')
        for error in errors:
            print(error)
    warnings = output['warnings']
    if warnings:
        print('WARNINGS')
        for warning in warnings:
            print(warning)

    values = output['values']
    for value in values:
        name = value['ParamName']
        inner_tree = value['InnerTree']
        for path in inner_tree:
            values_at_path = inner_tree[path]
            for value_at_path in values_at_path:
                data = value_at_path['data']
                if isinstance(data, str) and 'archive3dm' in data:
                    obj = rhino3dm.CommonObject.Decode(json.loads(data))
                    result.append(obj)
                else:
                    result.append(data)

    return result


def save_result(study):
    ''' 結果の保存
    '''
    best_variables = [float(v) for v in study.best_params.values()]
    save_rhino_model(best_variables)

    with open('param.json', 'w') as f:
        json.dump(study.best_params, f)
    with open('value.json', 'w') as f:
        json.dump(study.best_value, f)


def save_rhino_model(best_variables):
    ''' 作成したのモデルの 3dm での保存 
    '''
    brep = run_gh(best_variables)[0]

    doc = rhino3dm.File3dm()
    doc.Objects.Add(brep)
    doc.Write("./test.3dm", 7)


if __name__ == "__main__":
    sampler = optuna.samplers.TPESampler(n_startup_trials=50)
    study = optuna.create_study(
        sampler=sampler, storage='sqlite:///optuna.db', load_if_exists=True, study_name='test')
    study.optimize(objective, n_trials=10)

    print("Best param: ", study.best_params)
    print("Best value: ", study.best_value)

    vis = optuna.visualization.plot_optimization_history(study)
    vis.show()

    save_result(study)
