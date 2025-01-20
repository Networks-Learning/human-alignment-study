# Human-Alignment Influences the Utility of AI-assisted Decision Making – Study Data, Analysis Code and Website Documentation

## Overview
This repository contains the study data, analysis code and website code for "Human-Alignment Influences the Utility of AI-assisted Decision Making".
 <!-- published in PNAS ([DOI link]).  -->
The repository is organized into two main components:
1. Study data collected during the study
2. Analysis pipeline for processing and analyzing experimental data
3. Study website code used to gather data


### Prerequisites
- R version 4.4.1
- Python version 3.13.1
- Required R packages:
  ```r
  install.packages(c(
    "brms",
    "tidyverse",
    "stats",
    "tidybayes",
    "broom",
    "broom.mixed",
    "ggplot2",
    "rstanarm",
    "bayesplot",
    "reshape2",
    "latex2exp",
    "tikzDevice"
  ))
  ```
- Required Python packages:
  ```bash
  pip install -r requirements.txt
  ```

## Study Data

### Overview
This datatset contains study data collected to analyse to what extend the degree of alignment between
the AI confidence and the decision
maker’s confidence on their own
predictions modulates the utility of
AI-assisted decision making. 

Participants of the study play an simple card game — participants guess the color of a
randomly picked card from a pile of red and black cards that is partially observed
assisted by an AI model.
The group condition assigned to each participant steers the degree of alignment of the AI model. 

For more details on the dataset structure see the ```readme.md``` file in the study data directory.

### Basic Information
- **Format**: CSV
- **Size**: 8 files, 4.1 MB
- **Number of Participants**: 703
- **Number of Game Trial Records**: 18.981
- **Last Updated**: January 15, 2025
- **License**: Open Data Commons Attribution License (ODC-BY)

### Directory Structure
```
study_data/
├── readme.md          # Game data from group condition A
├── group_A.csv        # Game data from group condition A
├── group_B.csv        # Game data from group condition B
├── group_C.csv        # Game data from group condition C
├── group_BP.csv       # Game data from group condition BP
├── group_B_calibration.csv    # Game data from group condition B used for multicalibration
├── end_of_game_survey.csv     # Survey data from end of game survey
├── end_of_study_survey.csv    # Survey data from end of study survey
└── demo_survey.csv            # Survey data from demographic survey
```

## Analysis Code

### Directory Structure
```
analysis/                      # Analysis code
├── data/                      # processed data generated during analysis
├── figures/                   # Figures generated during analysis as pdf and tex files
├── outputs/                   # Analysis text output files
├── models/                    # Bayes fitted models
├── evaluation.ipynb           # Analysis notebook for game data
├── evaluation_survey.ipynb    # Analysis notebook for survey data
└── bayes_tests.R              # R code for Bayesian analysis
```

### Running the Analysis
1. Clone this repository
2. Install prerequisites
3. Run ```evaluation.ipynb``` notebook
3. Run ```evaluation_survey.ipynb``` notebook
3. Run ```bayes_tests.R``` script


## Study Website

### Directory Structure
```
study_code/                     # Study website code
├── calibration_algorithm/      # Base calibration algorithm
├── img/                        # Images used in the study website
├── jspsych/                    # Jspsych library files
├── materials/                  # Json files for the study
│   ├── games_level_A/          # Game batches for group condition A
│   ├── games_level_B/          # Game batches for group condition B
│   ├── games_level_C/          # Game batches for group condition C
│   ├── games_level_BP/         # Game batches for group condition BP
│   ├── games_level_B_cal/      # Game batches for group condition B used for multicalibration
│   ├── attention_tests.json    # Games for attention checks
│   ├── cards.json              # List of all card images used for pre-loading
│   ├── instructions.json       # File containing game instructions
│   └── alignment_alg.json      # Fitted multicalibration model
├── alignment.ipynb/            # Notebook to run multicalibration algorithm on the calibration data and save the model
├── experiment.js               # Main javascript file 
├── game_generator.py           # Code to generate and save all game batches for the study
├── index.html                  # Html Code
├── styles.css                  # Style files
├── survey.css                  # Style files
├── tailwind.min.css            # Style files
├── write_data.php              # Connects and sends data to database
└── database_config.php         # Empty template for database information
```

### Game Generation

To regenerate the games in the study and save under ```materials/``` run:

```python
from game_generator import GameGenerator 

# Example code for generating the game batches
gen = GameGenerator(nr_game_batches=20, nr_game_batches_calibration=60)
gen.create_all_games()

```

### Calibration Algorithm

The base calibration algorithm in ```calibration_algorithm/``` is a  binary histogram binning algorithm. We use the implementation provided by  https://github.com/aigen/df-posthoc-calibration .

## License
GNU General Public License (GPLv3)

<!-- ## Citation
If you use this code or data, please cite:
```
[Authors]. (Year). [Title]. PNAS. DOI: [DOI]
``` -->

## Contact
- Nina Corvelo Benz - ninacobe@mpi-sws.org
- Max Planck Institute for Software Systems
