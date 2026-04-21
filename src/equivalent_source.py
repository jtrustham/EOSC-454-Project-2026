import numpy as np
from scipy.interpolate import LinearNDInterpolator
from simpeg.potential_fields import magnetics
from pathlib import Path
from discretize import TensorMesh
from discretize.utils import mkvc, active_from_xyz
import pandas as pd


from simpeg import (
    maps,
    data,
    data_misfit,
    inverse_problem,
    regularization,
    optimization,
    directives,
    inversion,
)

import sys
sys.path.append("../src")

import init_utils

########################################################################################################
#Fix path to data directory
NOTEBOOK_DIR = Path().resolve()
DATA_DIR = NOTEBOOK_DIR.parent / "data" / "raw"

########################################################################################################
#Read in data
observations = init_utils.read_obs_mag("obs.mag")
topography = init_utils.read_topo("topo.dat")
mesh_data = init_utils.read_tensor_mesh(DATA_DIR / "sus.msh")

x_topo = topography['X'].values
y_topo = topography['Y'].values
z_topo = topography['Z'].values

topo_xyz = np.c_[x_topo, y_topo, z_topo]

########################################################################################################
# Define obervation locations

#For a ground survey (like Mt. Milligan), topo and observation locations are the same except spaced out. 
#Sampled every 10 meters, on surface.
x_obs = observations['X'].values
y_obs = observations['Y'].values

fun_interp = LinearNDInterpolator(np.c_[x_topo, y_topo], z_topo)
z_obs = fun_interp(np.c_[x_obs, y_obs])  

mask = ~np.isnan(z_obs) #be careful of NANs from the interpolation
receiver_locations = np.c_[x_obs[mask], y_obs[mask], z_obs[mask]] 


# Define the component(s) of the field we want to simulate as a list of strings.
# Here we simulation total magnetic intensity data.
components = ["tmi"]

# Use the observation locations and components to define the receivers. To
# simulate data, the receivers must be defined as a list.
receiver_list = magnetics.receivers.Point(receiver_locations, components=components) #List of receivers from locations
receiver_list = [receiver_list]

########################################################################################################
#Define Survey
# Define the inducing field
inclination = 75  # inclination [deg]
declination = 25.73  # declination [deg]
amplitude = 58193  # amplitude [nT]

source_field = magnetics.sources.UniformBackgroundField(
    receiver_list=receiver_list,
    amplitude=amplitude,
    inclination=inclination,
    declination=declination,
)

# Define the survey
survey = magnetics.survey.Survey(source_field)

########################################################################################################
# Define the mesh

nx, ny, nz = mesh_data["nx"], mesh_data["ny"], mesh_data["nz"]
dx, dy, dz = mesh_data["dx"], mesh_data["dy"], mesh_data["dz"]
x0, y0, z0 = mesh_data["x0"], mesh_data["y0"], mesh_data["z0"]


x_mesh = [(dx, 5, -1.3), (dx, nx), (dx, 5, 1.3)] 
y_mesh = [(dy, 5, -1.3), (dy, ny), (dy, 5, 1.3)]
z_mesh = [(dz, 5, -1.3), (dz, nz)]

tensor_mesh = TensorMesh([x_mesh, y_mesh, z_mesh], "CCN")

hx, hy, hz = tensor_mesh.h

tensor_mesh.origin = np.r_[
    x0 - np.sum(hx[:5]),
    y0 - np.sum(hy[:5]),
    z0 - np.sum(hz),
]

########################################################################################################
# Define active cells and mapping

#By active cells, we mean the cells that are below the topography. Air cells should not have a suceptibility value.
# Indices of the active mesh cells from topography (e.g. cells below surface), boolenans
active_cells = active_from_xyz(tensor_mesh, topo_xyz) #simpeg function

# Define mapping from model to active cells. The model consists of a
# susceptibility value for each cell below the Earth's surface.
n_active = int(active_cells.sum())
model_map = maps.IdentityMap(nP=n_active) #simpeg identity map

########################################################################################################
# Define the simulation (for equivalent source layer)

initial_simulation = magnetics.simulation.Simulation3DIntegral(
    survey=survey,
    mesh=tensor_mesh,
    model_type="scalar",
    chiMap=model_map,
    active_cells=active_cells,
    store_sensitivities="forward_only",
    engine="choclo",
)

########################################################################################################
# Define Data and Errors
# Filter NANs

dobs_full = observations['MAG'].values
errors_full = observations['ERR'].values
dobs = dobs_full[mask]
errors = errors_full[mask]

# detect and drop bad dpred point 
starting_tensor_model = 1e-4 * np.ones(n_active)

dpred0 = initial_simulation.dpred(starting_tensor_model)
good = ~np.isnan(dpred0)

# Filter receivers and data
receiver_locations_good = receiver_locations[good]
dobs_good = dobs[good]
errors_good = errors[good]

# Rebuild receiver list, source field, survey
receiver_list = magnetics.receivers.Point(
    receiver_locations_good, components=["tmi"]
)
source_field = magnetics.sources.UniformBackgroundField(
    receiver_list=[receiver_list],
    amplitude=amplitude,
    inclination=inclination,
    declination=declination,
)
survey = magnetics.survey.Survey(source_field)

# Rebuild simulation with cleaned survey
simulation = magnetics.simulation.Simulation3DIntegral(
    survey=survey,
    mesh=tensor_mesh,
    model_type="scalar",
    chiMap=model_map,
    active_cells=active_cells,
    store_sensitivities="forward_only",
    engine="choclo",
)

# Replace dobs/errors with cleaned versions
dobs = dobs_good
errors = errors_good

########################################################################################################
# Equivalent Source Simulation

# 1. Define the Height Shift
z_lift = 20.0  # The total height you want to shift data to

# 2. Create the "Equivalent Source" Simulation
# We simulate a thin layer of cells just below the topography
# to capture the signal without a full 3D inversion.

# Find the "top" layer of the active cells
# We can do this by finding the highest active cell in every x,y column
# Or more simply: just pick cells within one cell-height (dz) of the surface


# This utility finds the indices of the very top layer of active cells
# 1. Get the cell centers of all cells
cc = tensor_mesh.gridCC

# 2. Get the centers of ONLY the active cells
active_cc = cc[active_cells]

# 3. We want the highest cell (max Z) for every unique (X, Y)
# We can use a pandas groupby or a simple loop. Since your mesh is structured:

# Create a dataframe of active cell centers and their original indices
df_active = pd.DataFrame(active_cc, columns=['x', 'y', 'z'])
df_active['original_index'] = np.where(active_cells)[0]

# Group by X and Y, and find the index where Z is maximum
# This identifies the "skin" of the earth (We are taking 1 cell beelow the surface)
surf_layer_inds = df_active.sort_values('z').groupby(['x', 'y']).nth(-2)['original_index'].values

# Now proceed with the rest of your code:
eq_active_cells = np.zeros(tensor_mesh.n_cells, dtype=bool)
eq_active_cells[surf_layer_inds.astype(int)] = True

n_eq_active = int(eq_active_cells.sum())
eq_model_map = maps.IdentityMap(nP=n_eq_active)

# Use existing topography and survey setup
eq_receiver_list = magnetics.receivers.Point(receiver_locations, components=["tmi"])
eq_source_field = magnetics.sources.UniformBackgroundField(
    receiver_list=[eq_receiver_list],
    amplitude=amplitude, inclination=inclination, declination=declination
)
eq_survey = magnetics.survey.Survey(eq_source_field)

# Use a very simple mesh for the layer: just the top of your existing tensor_mesh
# or use the Integral simulation directly on active_cells restricted to the surface
eq_simulation = magnetics.simulation.Simulation3DIntegral(
    survey=eq_survey,
    mesh=tensor_mesh,
    model_type="scalar",
    chiMap=eq_model_map,
    active_cells=eq_active_cells,
    store_sensitivities="forward_only",
    engine="choclo",
)


Upward_continuation_start_model = 1e-4 * np.ones(n_eq_active)
Up_cont_reference_model = np.zeros_like(Upward_continuation_start_model)

# 3. Run a quick L2 inversion to get the "Equivalent Model"
# Note: We use a high alpha_s (smallness) to keep it near the surface
eq_data_obj = data.Data(eq_survey, dobs=dobs, standard_deviation=errors)
eq_misfit = data_misfit.L2DataMisfit(data=eq_data_obj, simulation=eq_simulation)
eq_reg = regularization.WeightedLeastSquares(tensor_mesh, active_cells=eq_active_cells, 
                                             reference_model= Up_cont_reference_model,
                                            alpha_s=1e-4,# Smallness
                                            alpha_x=0.5,  # We don't care about smoothness for an eq source
                                            alpha_y=0.5,
                                            alpha_z=0.5)

# Removed lower bound, bc we do not something physically meaningful, 
# just want to fit the data with a thin layer. 
eq_opt = optimization.ProjectedGNCG(maxIter=50, lower = 0.0) 

eq_inv_prob = inverse_problem.BaseInvProblem(eq_misfit, eq_reg, eq_opt)

eq_beta = directives.BetaEstimate_ByEig(beta0_ratio=1e-4)  #Super small beta, focus on misfit only
target = directives.TargetMisfit(chifact=1.0) #Run inversion until it actually fits data to thin layer

eq_inv = inversion.BaseInversion(eq_inv_prob, [eq_beta, target])


# This model just needs to recreate your ground data
m_eq = eq_inv.run(Upward_continuation_start_model)

# 4. Predict data at the new height (20m lift)
new_locs = receiver_locations.copy()
new_locs[:, 2] += z_lift 

up_receiver_list = magnetics.receivers.Point(new_locs, components=["tmi"])
up_source_field = magnetics.sources.UniformBackgroundField(
    receiver_list=[up_receiver_list],
    amplitude=amplitude, inclination=inclination, declination=declination
)
up_survey = magnetics.survey.Survey(up_source_field)

up_sim = magnetics.simulation.Simulation3DIntegral(
    survey=up_survey, mesh=tensor_mesh, chiMap=eq_model_map, 
    active_cells=eq_active_cells, model_type="scalar"
)

# This is your new "dobs" for the real 3D inversion
dobs_upward_continued = up_sim.dpred(m_eq)