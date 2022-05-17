##User guide
Steps:

1. Unzip CytonSolver v1.1.3b (choose one that appropriate for your OS) in 'release' folder
   1. (MAC) Simply double click CytonSolver application
   2. (WIN) Navigate to CytonSolver folder -> scroll down to find CytonSolver.exe (do NOT move this file! Make a shortcut to the desktop if you wish)

IMPORTANT!! (At this point please have a look at the example data files, and interrogate the data format)

2. Import example data file 
   1. You can directly import the provided files by "File->Open..." or Ctrl+O/CMD+O. However, importing this data format is not recommended.
   2. Instead drag & drop data file into "Cohort Explorer v2018.05.09" and wait for it to finish the analysis
   3. Notice the new folder (same name as the input data file) located in the same folder as the data file. 
     Note that the program will NOT overwrite if it has exisiting folder.
   4. Find an output excel file. It should also be named after the input data file with suffix _4prism. (e.g. DATA_FILE_NAME_4prism.xlsx)
   5. Import DATA_FILE_NAME_4prism.xlsx from Cyton Solver

NB: YES, you may stop at step 2.1. and not bother to run Cohort Explorer, however, it is always a good practice to check your data
before getting into the modelling. Perhaps it will give you an insight on what to expect from the model or find outlier(s). step 2.2 is
also a good way of checking the data format as it returns guide for any errors it encounters.

3. Please refer to the manual for utilising the program. It should be located inside 'doc' folder

## Developer's guide
CytonSolver is written in Python v3.6.5. It is highly recommended to use virtual environment to isolate the project from your default global python settings & libraries.

Before you begin, set the project root to be one path ABOVE "/src".
(i.e. project folder that contains "/img", "/src" etc should be the root, and those folders should be at the same depth)

All the dependencies can be found in "requirements.txt", and use following command to install pre-defined versions of the packages:
```shell
pip install -r requirements.txt
```

You need to compile Cython scripts (src/workbench/cyton1/c1_model.pyx, cyton15/c15_model.pyx) to OS specific build. 
Use "CythonSetup.py" and following command,
```shell
python CythonSetup.py build_ext --inplace
```
This will create shared library objects, which can be accessed by usual pythonic way.

After completing above steps, you can directly invoke "src/gui/main_cs.py" to initiate the program,
```shell
python /src/gui/main_cs.py
```

### BUILDING THE APP
PyInstaller is responsible for bundling the program into single executible file (incl. python interpreter).
However, this requires slightly different approach for MAC and WINDOWS. Note that this process is very sensitive to the versions of packages
used in the program including python itself. So please be aware of tracking all the versions as listed in "requirements.txt".

In order to build MAC version of the program, run 
```shell
python -m PyInstaller --clean -y -w -F MAC-cyton-solver.spec
```

"MAC-cyton-solver.spec" is the specification file that I wrote to define and wrap external files (e.g. images).
It also provides the main entry point of the program, and analyses all the modules (incl. 3rd party libraries),
and grab them into single file.

In order to build WINDOWS version of the program, run
```shell
python -m PyInstaller --clean -y -w -F WIN-cyton-solver.spec
```
This will result in slightly different style than that of MAC version. It somehow fails to create clean single ouput, instead
it copies all libraries in a single folder along with the executible file, "CytonSolver.exe". You need those copied files to be in the same folder
in order to run the program. So it is adviced to create a shortcut to the desktop to minimise the mess.