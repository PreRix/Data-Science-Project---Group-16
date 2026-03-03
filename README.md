# Data-Science-Project---Group-16

## Using Anaconda

### Copying an existing Environment

```powershell
conda create --name envname --file requirements.txt
```

### Creating a new Environment

```powershell
conda create --name dsp python=3.11
conda activate dsp
conda install numpy
conda install jupyter
conda install matplotlib
conda install polars
conda install ipykernel
python -m ipykernel install --user --name my_env --display-name "dsp 3.11"
conda list --export > requirements.txt
```
