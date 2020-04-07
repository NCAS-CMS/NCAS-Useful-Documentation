# Pre-built environment on CEDA-Jasmin
## Load environment
A pre-built environment already exists so just do:
```
source /home/users/valeriu/covid_install/load_environment.sh
```
then you are ready to run the covid19 tool by pointing to the pre-built installation eg:
```
cd data
python run_sample.py --spatialsim /home/users/valeriu/covid-19-spatial-sim/build/SpatialSim --outputdir ~/covid_output United_States
```

# Create your own environment
## Create conda environment and activate it
First get `miniconda` with Python3 for linux64:
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

Then create an environment - this will install `cmake` and `r-base` in an environment named `covid19`:
```
conda env create -n covid19 -f /home/users/valeriu/covid_install/conda_setup/conda_environment.yml
conda activate covid19
```
NOTE: you can add more packages to the conda environment file and update
the environment via `conda env update -n covid19 -f conda_environment.yml`
or you can simply install them manually via `conda install -c conda-forge PACKAGE`.

Then install the covid-19 tool:
```
cd $COVID-19-DIR
mkdir build
cd build
cmake ../src
make
```

## Installing the R scripts

Once in the conda environment you can install the R packages needed:
```
Rscript /home/users/valeriu/covid_install/Rinstall/setup.R
```
NOTE: you can add more R packages to the list in `Rinstall/r_requirements.txt` (your custom copy)
and rerun the command.
