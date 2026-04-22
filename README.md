# EOSC-454-Project-2026

This repository contains the data and code for my course project for EOSC 454 at the University of British Columbia. The aim of the project is to set up a forward and inverse workflow to recover a 3d susceptibility model, from total magnetic field measurements. Secondly, we attempt to use our workflow to invert the data obtained at Mt.milligan and recover a susecptibility model obtained in Oldenburg et. al.’s ‘Inversion of geophysical data over a copper gold porphyry deposit: A case history for Mt. Milligan’.

## Installation instructions

Pre-Requisties:
conda (Anaconda or miniconda)

1. Clone the repository

git clone https://github.com/jtrustham/EOSC-454-Project-2026.git

cd EOSC-454-Project-2026

2. Create the new environment

conda env create -f environment.yml

3. activate the new environment

conda activate EOSC454-Project-Jtrustham

## Usage

1. Launch Jupyter (or any equivalent platform to run a .ipynb file)

2. Open Synthetic_Problem.ipynb

Run all cells top to bottom. 
This is the forward and inverse problems for synthetic data.

3. Open Upward_continuation.ipynb

This notebook follows basic setup of survey, topography, tensor mesh and forward simulation. All of which remains the same in the full inversion workflow (visualizations included in Mt_Milligan_Inversion.ipynb). Finnally, the equivalent source upward continuation is implemented.

4. Open Mt_Milligan_Inversion.ipynb

Run all cells top to bottom. Full inversion and results.

** Note: All models have been cached, and inversions in Mt_Milligan_Inversion.ipynb have been commented out because of long run times. If desired, uncomment the inversion cells and comment out the cell that loads the cached models.

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
