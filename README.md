# EOSC-454-Project-2026

This repository contains the data and code for my course project for EOSC 454 at the University of British Columbia. The aim of the project is to set up a forward and inverse workflow to recover a 3d susceptibility model, from total magnetic field measurements. Secondly, we attempt to use our workflow to invert the data obtained at Mt.milligan and recover a susecptibility model obtained in Oldenburg et. al.’s ‘Inversion of geophysical data over a copper gold porphyry deposit: A case history for Mt. Milligan’.

# Installation instructions

Pre-Requisties:
conda (Anaconda or miniconda)

1. Clone the repository

git clone https://github.com/jtrustham/EOSC-454-Project-2026.git

cd EOSC-454-Project-2026

2. Create the new environment

conda env create -f environment.yml

3. activate the new environment

conda activate EOSC454-Project-Jtrustham

# Usage

1. Launch Jupyter (or any equivalent platform to run a .ipynb file)

2. Open Synthetic_Problem.ipynb

Run all cells top to bottom. 
This is the forward and inverse problems for synthetic data.

# Project Structure

- `data/` – input datasets
- `notebooks/` – analysis notebooks
- `src/` – core code (functions to import)
- `environment.yml` – dependencies
