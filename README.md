# root-dash

This is a template repository for creating a simple data-science dashboard for a userbase with widely-varying technical backgrounds.
Data is processed using [Python notebooks](https://jupyter.org/) and then explored using [Streamlit](https://streamlit.io/).
This template repository uses a blend of real and fake data---any analysis contained within is for demonstration purposes only.

Steps to adapt the template as your own:
1. **Fork** the repository.
2. **Verify** functionality and understanding of the repository as is by going through the existing template readme below, including running tests.
3. **Rename** `./root_dash_lib` to an appropriate name, e.g. `./revolutionary_dash_lib`.
4. **Update** `./setup.py` with the new library name, author name, repository location, etc.
5. **Modify** the modules in the directory formerly known as `root_dash_lib` for your use case. It is very likely you need to edit the renamed `root_dash_lib/user_utils`, but you may not need to update the other modules.
6. **Update the README** (found below) and remove everything above the double lines (including this sentence).

---
---

# <**Title**>

[![Installation and Tests](https://github.com/zhafen/root-dash/actions/workflows/installation_and_tests.yml/badge.svg)](https://github.com/zhafen/root-dash/actions/workflows/installation_and_tests.yml)

<**root-dash**: The above button tracks the status of code tests for the repository. You need to replace the URLs in the markdown with your own URLs.>

This <**data-science dashboard**> provides a way for interested individuals to explore data regarding <**your data source**>.

Instructions are provided below for various levels of usage.
Even if you have never edited code before, the goal of the instructions in [Level 1](#level-1-using-the-dashboard-on-your-computer) is for you to run the dashboard on your computer.
On the other end of things, if you are comfortable with routine use of git, code testing, etc., then jump to [Level 4](#level-4-significant-customization-and-editing) to get an overview of how the dashboard works and what you might want to edit.

## Table of Contents

- [Level 0: Using the Dashboard Online](#level-0-using-the-dashboard-online)
- [Level 1: Changing the Configuration and Data](#level-2-changing-the-configuration-and-data)
- [Level 2: Using the Dashboard on your Computer](#level-1-using-the-dashboard-on-your-computer)
- [Level 3: Making Some Edits to the Code](#level-3-making-some-edits-to-the-code)
- [Level 4: Significant Customization and Editing](#level-4-significant-customization-and-editing)
- [Level 5: Additional Features](#level-5-additional-features)

## Level 0: Using the Dashboard Online

The dashboard has a plethora of features that can be interacted with via a web interface.
If the dashboard is currently live at [<**streamlit app**>](https://root-dash.streamlit.app), you can use the dashboard without any additional effort.
One of the main features is the application of filters and the ability to download the edited data and images.

## Level 1: Updating the Configuration and Data

For many applications the data is light-weight enough that you can do the pre-processing as part of running the dashboard.
If the dashboard is also hosted on the web you can edit the configuration and data without ever needing to download anything.

### Editing the Config

Some options are only available in the `config.yml` file found in the `src` directory (`./src/config.yml` if you are in the root directory, i.e. [here](https://github.com/zhafen/root-dash/blob/main/src/config.yml)).
You can edit this on github by clicking on the edit button in the upper right, provided you are logged in with an account that has the necessary permissions.
Locally this can be edited with TextEdit (mac), Notepad (Windows), or your favorite code editor.

### Updating the Data

The raw data lives in [the `data/raw_data` folder](https://github.com/zhafen/root-dash/tree/main/data/raw_data).
To update the data used, add and/or replace the data in this folder.
You can do this on github by clicking the "Add file" button in the upper right hand corner.
The pipeline will automatically select the most recent data.

## Level 2: Using the Dashboard on your Computer

If you need a private dashboard or you need to run more-intensive data processing you'll need to run the dashboard on your computer.

### Downloading the Code

The code lives in a git repository, but you don't have to know git to retrieve and use it.
The process for downloading the code is as follows:

1. Click on the green "Code" button on [the GitHub repository](https://github.com/zhafen/root-dash), near the top of the page.
2. Select "Download ZIP."
3. Extract the downloaded ZIP file.
4. Optional: Move the extracted folder (`<repository-name>`; referred to as the code's "root directory") to a more-permanent location.

### Installing the Dashboard

Running the dashboard requires Python.
If you do not have Python on your computer it is recommended you download and install [Miniconda](https://docs.conda.io/en/main/miniconda.html).

With Python installed, 
open the directory containing the code (the root directory) in your terminal or command prompt.
If youre a mac user and you've never used a terminal or command prompt before
you can do this by right clicking the extracted folder and selecting "New Terminal at Folder" ([more info](https://support.apple.com/guide/terminal/open-new-terminal-windows-and-tabs-trmlb20c7888/mac); [Windows Terminal is the windows equivalent](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)).

Once inside the root directory and in a terminal, you can install the code by executing the command
```
pip install -e .
```

### Running the Dashboard Locally

Inside the root directory and in a terminal window, enter
```
streamlit run src/dashboard.py
```
This will open the dashboard in a tab in your default browser.
This does not require internet access.

### Running the Data Pipeline

<**Some analyses require additional data processing. This template comes with a built-in template for your own data pipeline.**>
To run the data-processing pipeline, while in the root directory run the following command in your terminal:
```
./src/pipeline.sh ./src/config.yml
```

### Viewing the Logs

Usage logs are automatically output to the `logs` directory.
You can open the notebooks as you would a normal Python notebook, if you are familiar with those.

## Level 3: Making Some Edits to the Code

### Downloading the Code (with git)

A basic familiarity with git is highly recommended if you intend to edit the code yourself.
There are many good tutorials available (e.g.
[GitHub's "Git Handbook"](https://guides.github.com/introduction/git-handbook/),
[Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials),
[Git - The Simple Guide](http://rogerdudler.github.io/git-guide/),
[Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)).
For convenience, the main command you need to download the code with git is
```
git clone git@github.com:zhafen/root-dash.git`
```

### Editing the Pipeline

If you want to change how the data is processed, edit `src/transform.ipynb`.
The data-processing pipeline runs this notebook when you execute the bash script `./src/pipeline.sh`,
and saves the output in the logs.
It is recommended to use the config whenever possible for any new variables introduced.

### Adding to the Pipeline

You can add additional notebooks to the data-processing pipeline.
Just make the notebook, place it in the `src` dir, and add its name to the array at the top of `src/pipeline.sh`.

### Editing the Streamlit Script

The interactive dashboard is powered by [Streamlit](https://streamlit.io/), a Python library that enables easy interactive access.
Streamlit is built on a very simple idea---to make something interactive, just rerun the script every time the user makes a change.
This enables editing the streamlit script to be almost exactly like an ordinary Python script.
If you know how to make plots in Python, then you know how to make interactive plots with Streamlit.

If you want to change the Streamlit dashboard, edit `src/dashboard.py`.
Much of the Streamlit functionality is also encapsulated in utility functions inside the `<short name>_dash_lib/` directory, particularly in `<short name>_dash_lib/streamlit_utils.py`.
Streamlit speeds up calculations by caching calls to functions.
If a particular combination of arguments has been passed to the function
(and the function is wrapped in the decorator `st.cache_data` or `st.cache_resource`)
then the results are stored in memory for easy access if the same arguments are passed again.

## Level 4: Significant Customization and Editing

Before making significant edits it is recommended you make your own fork of the dashboard repository,
and make your own edits as a branch.
This will enable you to share your edits as a pull request.

### Repository Structure
The repository is structured as follows:
```
<root-directory>/
│
├── README.md                  # Documentation for the project
├── __init__.py
├── src                        # Source code directory
│   ├── __init__.py
|   ├── config.yml              # Configuration file for the dashboard
│   ├── dashboard.py            # Script for interactive dashboard
│   ├── pipeline.sh             # Shell script for running data pipeline
│   └── transform.ipynb         # Jupyter notebook for data transformation
├── root_dash_lib              # Custom library directory
│   ├── __init__.py
│   └── streamlit_utils.py      # Utility functions for the dashboard
├── setup.py                   # Script for packaging the project
├── requirements.txt           # List of project dependencies
├── data                       # Data storage directory
│   ├── raw_data                # Raw data directory
│   |   ├── <your raw data>.csv 
│   |   └── <your additional raw data>.xlsx
│   └── processed_data          # Processed data directory
│       ├── <your processed data>.csv
│       └── <your additional processed data>.csv
├── test                       # Test directory
│   ├── __init__.py
│   ├── test_pipeline.py        # Unit tests for data pipeline
│   └── test_streamlit.py       # Unit tests for the dashboard
├── conftest.py                # Configuration for test suite
└── test_data                   # Test datasets
```

### The Test Suite

The dashboard comes with a suite of code tests that help ensure base functionality.
It is recommended you run these tests both before and after editing the code.
To run the tests, simply navigate to the code's root directory and enter
```
pytest
```

### Updating the Usage and Installation Instructions

If your edits include new packages, you need to add them to both `requirements.txt` and `setup.py`.
You may also consider changing the metadata in `setup.py`.

### Deploying on the Web
You can deploy your app on the web using Streamlit sharing.
Visit [Streamlit Sharing](https://streamlit.io/sharing) for more information.

## Level 5: Additional Features

### Continuous Integration

Continuous integration (automated testing) is an excellent way to check if your dashboard is likely to function for other users.
You can enable continuous integration [via GitHub Actions](https://docs.github.com/en/actions/automating-builds-and-tests/about-continuous-integration), including adding a badge showing the status of your tests.
Continuous integration can be tested locally using [act](https://github.com/nektos/act).
Some tests don't work on continuous integration,
and are disabled until the underlying issues are addressed.

### Deploying a Private App
Streamlit has the option to deploy your code without sharing it publicly.
More information can be found [in this section of the Streamlit Sharing documentation](https://docs.streamlit.io/streamlit-community-cloud/share-your-app#make-your-app-public-or-private).


ChatGPT was used in the construction of this document.
