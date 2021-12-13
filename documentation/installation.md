# Installation

## MAC and Windows

*Note that you will need at least Python 3.8 to run STCV-Synth, as it heavily relies on the `asyncio` module. If you have a previous Python 3 version, you will need to update it. You may check you Python 3 by running `python3 -V` in a terminal prompt.*

* To install all **synth** dependencies, run: `pip install -r requirements_synth.txt`

* To install all **analysis** dependencies, run: `pip install -r requirements_analysis.txt`


## Debian and Ubuntu

**NEEDS UPDATE**

1. Follow these instructions to install **Pyo**:
    * http://ajaxsoundstudio.com/pyodoc/compiling.html#debian-ubuntu-apt-get
    * *Note that this series of commands will also install pip, which is required for step 2.*

2. Run: `pip install -r requirements_linux.txt`


## NVIDIA Jetson Nano

1. Update and upgrade apt and apt-get. Run:
    * `sudo apt update && sudo apt upgrade`
    * `sudo apt-get update && sudo apt-get upgrade`

2. Install Python 3.8 and pip:
    1. Run: `sudo apt install python3.8`

    2. Add Python 3.6 and 3.8 to update-alternatives. Run:
        * `sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1`
        * `sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2`

    3. Run `python3 -V`. If the output reads `Python 3.8.0`, you may skip to step 5 of this section.

    4. Update Python 3 to point to Python 3.8, so that when running `python3` we execute Python 3.8. Run:
        * `sudo update-alternatives --config python3`
        * You will see a `*` to the left of the selected version. Input the selection value that matchs **/usr/bin/python3.8** at the prompt.

    5. To ensure that you don't have any issues opening a terminal in the future, open `/usr/bin/gnome-terminal` in a text editor, and change the first line so that it matches: `#!/usr/bin/python3.6`

    6. Install Python 3.8 dev library. Run: `sudo apt install libpython3.8-dev`

    7. Install curl. Run: `sudo apt install curl`

    8. Get pip installer: `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`

    9. Install **pip** for the new version of Python. Run: `python3 get-pip.py`
        * If you get a warning telling you that the pip scripts are not on the PATH, you can add it by using `export PATH=/put/the/path/in/quotes/here:$PATH`

    10. Remove installer: `sudo rm get-pip.py`

    11. Verify Python3 and pip3 versions. Run: `python3 -V && pip3 -V`. Your output should be: *Python 3.8.0 pip 21.3.1 from ...* or similar.

3. Install Shapely dependencies.
    * Install GEOS: `sudo apt install libgeos-dev`
    * Install cython: `sudo apt install cython`

4. Install virtualenv: `sudo pip3 install virtualenv`

5. Go to the STCV-Synth root directory and create a venv: `virtualenv venv`
    * Verify that your virtualenv was created with Python 3.8 by running `python3 -V`. If your output is not *Python 3.8.0*, then delete the newly created virtualenv using `sudo rm -r venv`, and create a new one using `python3.8 -m virtualenv venv`.

6. Activate your virtual environment: `source venv/bin/activate`

7. Run `pip install -r requirements_synth_nano.txt`

8. Install MediaPipe
    1. Install ‘npm’: `sudo apt install npm`

    2. Install ‘bazelisk’: `sudo npm install -g @bazel/bazelisk`

    3. Copy MediaPipe directory: `git clone https://github.com/google/mediapipe.git`

    4. Use the package manager to install pre-compiled OpenCV libraries. Run: `sudo apt-get install -y libopencv-core-dev libopencv-highgui-dev libopencv-calib3d-dev libopencv-features2d-dev libopencv-imgproc-dev libopencv-video-dev`

    5. Go to the **mediapipe/third-party** directory: `cd mediapipe/third-party`

    6. Open `opencv_linux.BUILD` with a text editor, and uncomment the following two lines (uncomment by deleting the '#' prefixing the line):
        * `"include/aarch64-linux-gnu/opencv4/opencv2/cvconfig.h"`
        * `"include/aarch64-linux-gnu/opencv4/"`

    7. Install **protobuf**. Run:
        * `sudo apt install protobuf-compiler`
        * `sudo apt install libprotobuf-dev`

    8. (*Your venv should be activated. If not, activate it in step 6 above. Make sure you're in the 'mediapipe' directory when you execute this command.*) Install mediapipe dependencies: `pip install -r requirements.txt`

    9. Generate and Install the MediaPipe package. Run:
        * `python setup.py gen_protos`
        * `python setup.py bdist_wheel`

8. Install MediaPipe from pre-built wheel:
    1. Download wheel from GitHub. Run: `git clone https://github.com/jiuqiant/mediapipe_python_aarch64.git`
    
    2. Go to cloned repo: `cd mediapipe_python_aarch64`
    
    3. Install wheel. Run: `pip install