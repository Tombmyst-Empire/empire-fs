@echo off
rem pip install -r requirements.txt
rem pip install -r requirements_dev.txt
echo "Compiling Cython"
python setup.py build_ext --inplace
echo "Formatting using black"
black -t py310 src
echo "Formating using isort"
isort src
echo "################################### PYLINT ########################"
pylint src
echo "################################### PYTEST ########################"
pytest
cd docs
make html
cd..