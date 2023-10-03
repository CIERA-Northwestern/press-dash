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
    name="press_dash_lib",
    version="0.1",
    author="CIERA (Zach Hafen-Saavedra)",
    author_email="ciera@northwestern.edu",
    description="Dashboard for exploring and presenting press data related to CIERA.",
    long_description_content_type="text/markdown",
    url="https://github.com/CIERA-Northwestern/press-dash",
    packages=setuptools.find_packages(),
    install_requires = [
        'numpy',
        'pandas',
        'openpyxl',
        'matplotlib',
        'seaborn',
        'nbconvert',
        'nbformat',
        'PyYAML',
        'streamlit',
        'pytest',
        'jupyterlab',
	'root-dash',
   ],
)
