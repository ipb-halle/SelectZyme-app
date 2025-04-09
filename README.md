# SelectZyme-demo-app
Minimal demonstration of pre-build plots, served interactively with dash components, extracted from SelectZyme project to create a minimal viable app.

## Install
Prerequisite for all installs is to clone the repository with the corresponding submodule SelectZyme.
```
git clone --recurse-submodules https://github.com/fmoorhof/SelectZyme-demo-app.git
cd SelectZyme-demo-app
```
### Local
Install dependencies defined in the `pyproject.toml` and SelectZyme without dependencies.
```
pip install .
pip install --no-dependencies external/selectzyme/
```

### Docker
Requires cloning the repository (see above).
```
docker build -t ipb-halle/selectzyme-demo-app:development .
docker run -it --rm -p 8050:8050 ipb-halle/selectzyme-demo-app:development --input_dir=/app/data/blast_psi
```

### Usage
```
python app.py  # runs example analysis by default
python app.py -i=/your/out_files/from/selectzyme_backend
```

## Development
This project uses the following tools to improve code quality:
- [ruff](https://docs.astral.sh/ruff/tutorial/)

# License
MIT License