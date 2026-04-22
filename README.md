# EOSC-454-Project-2026

This project develops a forward and inverse workflow to recover a 3D susceptibility model from total magnetic field data.
The workflow is first validated on synthetic data, and then applied to field data from the Mt. Milligan copper-gold porphyry system. The results are compared with an accepted model from a separate study.

Magnetic inversion is a key tool in mineral exploration to obtain resource estimates and deposit structures. However, obtaining reliable models is challenging due to the fundamental non-uniqueness of the inverse problem. This project demonstrates a workflow that inverts real field data using modern techniques.

## Installation instructions

Prerequisties:
conda (Anaconda or miniconda)

1. Clone the repository

git clone https://github.com/jtrustham/EOSC-454-Project-2026.git

cd EOSC-454-Project-2026

2. Create the new environment

conda env create -f environment.yml

3. activate the new environment

conda activate EOSC454-Project-Jtrustham

## Usage

Launch Jupyter (or any equivalent platform to run a .ipynb file)

#### Synthetic_Problem.ipynb

This is the forward and inverse problems for synthetic data.

#### Upward_continuation.ipynb

This notebook follows basic setup of survey, topography, tensor mesh and forward simulation. All of which remains the same in the full inversion workflow (visualizations included in Mt_Milligan_Inversion.ipynb). Finally, the equivalent source upward continuation is implemented.

#### Mt_Milligan_Inversion.ipynb

This notebook contains the full inversion and results of the field (upward continued) data.

-> Note: All models have been cached, and inversions in Mt_Milligan_Inversion.ipynb have been commented out because of long run times. If desired, uncomment the inversion cells and comment out the cell that loads the cached models.

## Project Structure

- `data/` – input datasets
- `notebooks/` – analysis notebooks
- `outputs/` - Models, figures, and pre-computed arrays for reproducibility
- `src/` – core code (functions to import)
- `environment.yml` – dependencies

## Tests

This repository uses GitHub Actions to automatically test the notebooks.

On every push and pull request, the following checks run:
- Environment creation from `environment.yml`
- Execution of all Jupyter notebooks using `nbconvert`

If the build passes, all notebooks run successfully in a clean environment.
