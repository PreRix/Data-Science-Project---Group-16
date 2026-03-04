# Data-Science-Project Group-16

## Using Anaconda

### Copying an existing Environment

```powershell
conda create --name <envname> --file requirements.txt
python -m ipykernel install --user --name <kernelname> --display-name "<displayname>"
```

### Creating a new Environment

```powershell
conda create --name <name> python=3.11
conda activate <name>
conda install numpy
conda install jupyter
conda install matplotlib
conda install polars
conda install ipykernel
python -m ipykernel install --user --name <kernelname> --display-name "<displayname>"
conda list --export > requirements.txt
```

### For using openmeteo

```powershell
conda install numpy pandas requests-cache
pip install openmeteo-requests retry-requests
```

#### For updating an Environment to a new requirements.txt

```powershell
conda install --name <envname> --file requirements.txt
```
