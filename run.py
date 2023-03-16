import os

experiments = [
    {
        "model": "xlnet",
        "plot_type": "wiki",
        "freeze": True,
        "max_length": 400
    },
    {
        "model": "xlnet",
        "plot_type": "wiki",
        "freeze": False,
        "max_length": 400
    },
    {
        "model": "xlnet",
        "plot_type": "tmdb",
        "freeze": True,
        "max_length": 60
    },
    {
        "model": "xlnet",
        "plot_type": "tmdb",
        "freeze": False,
        "max_length": 60
    },
    {
        "model": "bert",
        "plot_type": "wiki",
        "freeze": True,
        "max_length": 400
    },
    {
        "model": "bert",
        "plot_type": "wiki",
        "freeze": False,
        "max_length": 400
    },
    {
        "model": "bert",
        "plot_type": "tmdb",
        "freeze": True,
        "max_length": 60
    },
    {
        "model": "bert",
        "plot_type": "tmdb",
        "freeze": False,
        "max_length": 60
    },
    {
        "model": "roberta",
        "plot_type": "wiki",
        "freeze": True,
        "max_length": 400
    },
    {
        "model": "roberta",
        "plot_type": "wiki",
        "freeze": False,
        "max_length": 400
    },
    {
        "model": "roberta",
        "plot_type": "tmdb",
        "freeze": True,
        "max_length": 60
    },
    {
        "model": "roberta",
        "plot_type": "tmdb",
        "freeze": False,
        "max_length": 60
    }
]

for exp in experiments:
    os.system(f'python classification.py \
              --model {exp["model"]} --plot_type {exp["plot_type"]} \
              --file_name {exp["model"]}_{exp["plot_type"]}_results_{exp["max_length"]}{"_freeze" if exp["freeze"] else ""}.pkl \
              --balanced --max_length {exp["max_length"]} \
              {"--freeze" if exp["freeze"] else ""}')