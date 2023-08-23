# root-dash

This is a template repository for creating a simple exploratory data-science dashboard for a userbase with widely-varying technical backgrounds.
Data is explored using [Streamlit](https://streamlit.io/).
Preprocessing is wrapped into the Streamlit dashboard for lightweight datasets,
while for ones requiring more processing there is data pipeline functionality,
including automating the use of [Python notebooks](https://jupyter.org/).
This template repository uses a blend of real and fake data---any analysis contained within is for demonstration purposes only.

This repository was originally built for the [Center for Interdisciplinary Exploration and Research in Astrophysics (CIERA)](https://ciera.northwestern.edu/) at Northwestern University,
according to the design specifications listed below.

<details>
<summary> <b>Internally maintained</b> </summary>

CIERA should be able to maintain existing dashboards without external expertise.
CIERA is home to a deep pool of technical expertise, both due to its nature as an astrophysics research center and due to years of work by its leadership and community.
If the right tools are selected when building the dashboard, the necessary expertise to maintain it should be on hand.

Accordingly, the dashboard is built on
Python and shell scripting.
Streamlit was selected as the dashboard framework because Streamlit is compatible with matplotlib,
and a Streamlit dashboard script differs from a traditional plot-generation script by only a few lines of Python.

We evaluated the Cognos Analytics Business Intelligence System as an alternative dashboard platform.
Cognos is widely used by the Northwestern data community, and is the platform through which most of the official data is accessed.
However, creating a Cognos dashboard depends on utilizing a graphical UI which no one at CIERA is familiar with,
rather than techniques used day-in and day-out.
</details>

<details>
<summary><b>Accessible</b></summary>
CIERA staff, who do not necessarily have a coding background, should be able to use existing dashboards with as little effort as possible. In particular, CIERA staff should be able to perform extensive plot tuning, explore the data, upload new data, and modify the config.

For most dashboards built via this template the dashboard is accessible online, and all of those features are possible to complete in the web browser with only a few clicks.
This avoids many users ever needing to use git or navigate their computer with command line.

Another reason we did not select Cognos is because of accessibility---gaining access to data and a Cognos dashboard can require working through several layers of permission.
</details>

<details>
<summary><b>Functions offline</b></summary>
There should be a way to create and share private dashboards, including on closed-networks.

Fortunately, streamlit is compatible with this: it can be run locally even more-easily than it can be hosted online.
This does require additional steps for the user, compared to viewing the dashboard on the web, but those steps are well-defined and brief.
</details>

<details>
<summary><b>Easily shared</b></summary>

Streamlit provides a [free service for hosting streamlit apps](https://streamlit.io/cloud), and if that is retired there are other options to host the application.
</details>

<details>
<summary><b>Clarity is prioritized</b></summary>
If there is a choice between two comparable solutions, one of which is more robust and the other of which is easier to understand, the more-understandable option is preferred.
This goes hand-in-hand with maintenance.

This is possible because there is an emphasis on being a template, not a library.
While the template comes with a solid library, users are encouraged to modify the code for their own purposes,
and the code is simple enough to not require a class-centric approach.
</details>

<details>
<summary><b>Widely applicable</b></summary>
Much of the data employed by CIERA staff follow a common format:
categorized time-series data.
Examples include news articles over time, grants and proposals per year, and outreach activities over time.
The default dashboard library comes with tools to visualize such data straightforwardly.
As such, the dashboard template is widely applicable to the common scenario of communicating a business or institution's growth over time.
</details>

<details>
<summary><b>Robust dependencies</b></summary>
The dashboard exclusively uses libraries that are supported by a broad community.
</details>

---

Steps to adapt the template as your own:
1. **Fork** the repository.
2. **Verify** functionality and understanding of the repository as is by going through the existing template readme below, including running tests.
3. **Rename** `./root_dash_lib` to an appropriate name, e.g. `./revolutionary_dash_lib`.
4. **Update** `./setup.py` with the new library name and both `./setup.py` and `./requirements.txt` with any new packages that your dashboard requires.
5. **Modify** the modules in the directory formerly known as `root_dash_lib` for your use case. It is very likely you need to edit the renamed `root_dash_lib/user_utils`, but you may not need to update the other modules.
6. **Update the README** (found below) and remove everything above the double lines (including this sentence).

---
---

# <**Title**>

[![Installation and Tests](https://github.com/zhafen/root-dash/actions/workflows/installation_and_tests.yml/badge.svg)](https://github.com/zhafen/root-dash/actions/workflows/installation_and_tests.yml)

<**root-dash**: The above button tracks the status of code tests for the repository. You need to replace the URLs in the markdown with your own URLs.>

This <**data-science dashboard**> provides a way for interested individuals to explore data regarding <**your data source**>.
This dashboard setup is primarily for exploratory or explanatory data analysis common in academia,
whereas preditive data analysis is more common outside academia.
Predictive data science dashboards may differ in usage and structure.

Instructions are provided below for various levels of usage.
Even if you have never edited code before, the goal of the instructions in [Level 1](#level-1-changing-the-configuration-and-data) is for you to update the data and settings of a pre-existing dashboard running online.
On the other end of things, if you are comfortable with routine use of git, code testing, etc., [Level 4](#level-4-significant-customization-and-editing) provides an overview of how the dashboard works and what you might want to edit.
It is still recommended you briefly skim through the previous sections, even if you are comfortable with a higher level, as they describe general use.

## Table of Contents

- [Level 0: Using the Dashboard Online](#level-0-using-the-dashboard-online)
- [Level 1: Changing the Configuration and Data](#level-1-changing-the-configuration-and-data)
- [Level 2: Using the Dashboard on your Computer](#level-2-using-the-dashboard-on-your-computer)
- [Level 3: Making Some Edits to the Code](#level-3-making-some-edits-to-the-code)
- [Level 4: Significant Customization and Editing](#level-4-significant-customization-and-editing)
- [Level 5: Additional Features](#level-5-additional-features)

## Level 0: Using the Dashboard Online

The dashboard has a plethora of features that can be interacted with via a web interface.
If the dashboard is currently live at [<**streamlit app**>](https://root-dash.streamlit.app), you can use the dashboard without any additional effort.
One of the main features is the application of filters and the ability to download the edited data and images.
While the interface should be relatively intuitive, a helpful tip is that you can reset your choices by refreshing the page.

## Level 1: Updating the Configuration and Data

When the dashboard is hosted on the web in some cases you can edit the configuration and data without ever needing to download anything and view the updated dashboard without ever needing to download anything.
This is possible for dashboards where the computations are sufficiently light to be wrapped into the interactive dashboard.

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
Note that macs typically have a pre-existing Python installation, but this installation is not set up to install new packages easily, and the below instructions may not work.
Therefore it is still recommended that you install via miniconda even if your system has Python pre-installed.

Open the directory containing the code (the root directory) in your terminal or command prompt.
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
git clone git@github.com:zhafen/root-dash.git
```

### If you edit anything, edit `<short name>_dash_lib/user_utils.py`

This file contains two functions essential to working with arbitrary data:

1. `load_data`, which the user must edit to ensure it loads the data into a DataFrame.
2. `preprocess_data`, which will make alterations to the loaded data.

Just by changing these two functions and the config you can adapt the pipeline to a wide variety of purposes.

### Editing the Pipeline

If you want to change the more intensive data-processing, edit `src/transform.ipynb`.
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

The basic streamlit dashboard that starts up is a general-purpose dashboard,
for which the majority of the code exists in `<short name>_dash_lib/pages/blank_page.py`
The file `src/dashboard.py`calls the main function in `blank_page.py` by default,
but can be edited to call the main function of a different file by default instead.
Much of the Streamlit functionality is also encapsulated in utility functions inside the `<short name>_dash_lib/` directory.

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
├── README.md                   # Documentation for the project
├── __init__.py
├── src                         # Source code directory
│   ├── __init__.py
|   ├── config.yml              # Configuration file for the dashboard
│   ├── dashboard.py            # Script for interactive dashboard
│   ├── pipeline.sh             # Shell script for running data pipeline
│   └── transform.ipynb         # Jupyter notebook for data transformation
├── root_dash_lib               # Custom library directory
│   ├── __init__.py
│   ├── user_utils.py           # Utilities specific to the dashboard. Must be edited.
│   ├── dash_utils.py           # Utilities for creating widgets and accepting input.
│   ├── data_utils.py           # Utilities for general-purpose data handling
│   ├── plot_utils.py           # Utilities for plotting data.
│   ├── time_series_utils.py    # Utilities for working with time series.
│   └── pages                   # Dashboard page templates.
│       ├── __init__.py
│       ├── blank_page.py       # The default dashboard setup. High flexibility.
│       └── panels_page.py      # A multi-panel dashboard example.
├── setup.py                    # Script for packaging the project
├── requirements.txt            # List of project dependencies
├── data                        # Data storage directory
│   ├── raw_data                # Raw data directory
│   |   ├── <your raw data>.csv 
│   |   └── <more raw data>.xlsx
│   └── processed_data          # Processed data directory
│       ├── <your processed data>.csv
│       └── <more processed data>.csv
├── test                        # Test directory
│   ├── __init__.py
|   ├── config.yml              # Configuration file for the tests.
│   ├── test_pipeline.py        # Unit tests for data pipeline
│   ├── test_streamlit.py       # Unit tests for the dashboard
│   └── lib_for_tests           # Used to load the default test dataset,
│       ├── __init__.py         # enabling users to change the code and check
│       └── press_data_utils.py     # if their changes broke any functionality.
├── conftest.py                 # Configuration for test suite
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

**Note:** you cannot deploy a streamlit app where the source is a repository owned by the organization, unless you can log into that organization's github account.
This is true even if you have full read/write access to the organization's repositories.
Instead you must create a fork of the repository you want to deploy, and point streamlit.io to that fork.

## Level 5: Additional Features

### Using and Editing Multiple Dashboards

It is recommended that your repositories that use this dashboard template are a fork of the template.
Unfortunately you cannot have multiple official forks of a single repository, nor can you have a private fork, which is necessary for dashboards with sensitive data.
However, you can create a "manual" fork in both cases, as described below.

1. **Create a New Repository**: In your GitHub/Atlassian account, create a new repository. The repository can be set to "Private" if you wish.

2. **Clone the Original Repository**: Clone the public repository to your local machine and navigate to the cloned repository directory.

   ```bash
   git clone https://github.com/zhafen/root-dash.git
   cd your-public-repo
   ```

3. **Change the setup for the remote repositories**: Designate the repository you cloned from as `upstream`, and create a new origin with the url of your private repository.

   ```bash
   git remote rename origin upstream
   git remote add origin https://github.com/<your-username>/<your-private-repo>.git
   ```

4. **Check the result**: If done correctly, the output of `git remote -v` should be

    ```bash
    git remote -v
    ```

    > ```
    > origin  git@github.com:<your-username>.git (fetch)
    > origin  git@github.com:<your-username>.git (push)
    > upstream        git@github.com:zhafen/root-dash.git (fetch)
    > upstream        git@github.com:zhafen/root-dash.git (push)
    > ```

4. **Push to the Private Repository**: Push all branches and tags to your new private repository:

   ```bash
   git push origin --all
   git push origin --tags
   ```

### Continuous Integration

Continuous integration (automated testing) is an excellent way to check if your dashboard is likely to function for other users.
You can enable continuous integration [via GitHub Actions](https://docs.github.com/en/actions/automating-builds-and-tests/about-continuous-integration) (also available in a tab at the top of your github repo), including adding a badge showing the status of your tests
(shown at the top of this page).
Some tests don't work on continuous integration,
and are disabled until the underlying issues are addressed.
Continuous integration can be tested locally using [act](https://github.com/nektos/act),
which may be helpful if the issues that occur during continuous integration are system specific.

### Deploying a Private App
Streamlit has the option to deploy your code without sharing it publicly.
More information can be found [in this section of the Streamlit Sharing documentation](https://docs.streamlit.io/streamlit-community-cloud/share-your-app#make-your-app-public-or-private).


---

ChatGPT was used in the construction of this document.
