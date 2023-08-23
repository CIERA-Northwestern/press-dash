'''This is the install script used by pip to install the package,
i.e. enable your Python version to find and import the package.
Setup can accept a wide variety of options, but for the purpose
of installing via "pip install -e .", the only required options
are the name of the package and the packages to be included (`install_requires`).

**If you plan on running your dashboard on streamlit.io/cloud,
you must also include the necessary packages in the `requirements.txt` file.**
'''
import setuptools

setuptools.setup(
    name="root_dash_lib",
    packages=setuptools.find_packages(),
    install_requires = [
        'numpy',
        'pandas',
        'openpyxl',
        'matplotlib',
        'seaborn',
        'sympy',
        'nbconvert',
        'nbformat',
        'PyYAML',
        'streamlit',
        'pytest',
        'ipython',
        'jupyter',
        'jupyterlab',
        'jupyter_contrib_nbextensions',
    ],
)
