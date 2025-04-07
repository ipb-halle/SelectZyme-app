# SelectZyme-demo-app
Minimal demonstration of pre-build plots, served interactively with dash components, extracted from SelectZyme project to create a minimal viable app.

## Install
Install dependencies defined in the `pyproject.toml` and add SelectZyme functionality (without installing dependencies of SelectZyme).
```
git clone https://github.com/fmoorhof/SelectZyme.git
cd SelectZyme-demo-app

# install dependencies
pip install .

# get and install SelectZyme
git submodule add https://github.com/fmoorhof/SelectZyme external/selectzyme
pip install --no-dependencies external/selectzyme/
```