# Install Dependecies

## MAC and Windows

To install all dependencies, run:

`pip install -r requirements.txt`


## Debian and Ubuntu

* Follow these instructions to install **Pyo**:
    * http://ajaxsoundstudio.com/pyodoc/compiling.html#debian-ubuntu-apt-get

* Install Numpy:
    * `sudo apt install python-numpy`
    * *Remember to replace `python-numpy` with `python3-numpy` if you have multiple Python versions installed.*


# CSound - Debian (This will be removed when Pyo is up and running in the Jetson)

## Install CSound

1. `sudo apt-get install csound`
2. Update the package manager: `sudo apt-get update`
3. Setup CSoundQT (front-end for CSound): `sudo apt-get install qutecsound`

## Execute CSound from the command line

* For real-time performance, execute CSound from the command line: `csound -odac -+rtaudio=alsa -B2048 -b2048 /path/to/csound/file.csd`
* Alternatively, add the command line flags to the CsOptions section of the CSD, simplifying the command to: `csound /path/to/csound/file.csd`
