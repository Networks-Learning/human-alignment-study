# Human-Alignment Study Data

## Overview
This dataset contains the study data collected to analyze to what extend the degree of alignment between
the AI confidence and the decision
maker’s confidence on their own
predictions modulates the utility of
AI-assisted decision making. 

Participants of the study play an simple card game — participants guess the color of a
randomly picked card from a pile of red and black cards that is partially observed
assisted by an AI model.
The group condition assigned to each participant steers the degree of alignment of the AI model. 
As group conditions, we have

- Group <img src="../symbols/symbolA.png" alt="small icon" height="15"> (denoted by A in files)
- Group <img src="../symbols/symbolB.png" alt="small icon" height="15"> (denoted by B in files)
- Group <img src="../symbols/symbolC.png" alt="small icon" height="15"> (denoted by C in files)
- Group <img src="../symbols/symbolBP.png" alt="small icon" height="15"> (denoted by BP in files)

where the symbols indicate the induced perception bias as described in the paper.

## Dataset Description

### Basic Information
- **Format**: CSV
- **Size**: 8 files, 4.1 MB
- **Number of Participants**: 703
- **Number of Game Trial Records**: 18.981
- **Last Updated**: January 15, 2025
- **License**: Open Data Commons Attribution License (ODC-BY)

## Directory Structure
```
study_data/
├── readme.md          # Data description file
├── group_A.csv        # Game data from group condition A
├── group_B.csv        # Game data from group condition B
├── group_C.csv        # Game data from group condition C
├── group_BP.csv       # Game data from group condition BP
├── group_B_calibration.csv    # Game data from group condition B used for multicalibration
├── end_of_game_survey.csv     # Survey data from end of game survey
├── end_of_study_survey.csv    # Survey data from end of study survey
└── demo_survey.csv            # Survey data from demographic survey
```

## Data Quality
We separated game data and survey data into different files. Game data is saved by group condition of participants. Survey data is saved by survey type. Game data includes games designed as attention tests marked by a negative ```game_id```. Each participant completed 24 games and 3 attention tests. The attention tests can be used to filter out participants. There is no missing data as the only data saved was from participants that completed the study. 

## Intended Uses
This study was conducted to better understand AI-assisted decision making using a gamified setting. This study does not contain sensitive data.

## Technical Requirements
The dataset is relatively small so there are no minimum hardware requirements.

## Loading the Data
```python
# Example code for loading the dataset
import pandas as pd

df = pd.read_csv('study_data/group_A.csv')
```

### Features - Game Data
| Feature Name | Type | Description | Values/Range (if applicable) |
|--------------|------|-------------|---------------------|
| participant_id | string | Unique identifier for participants | N/A |
| level_name| string | Group condition | {level_A, level_B, level_C, level_BP, level_B_cal}  |
| game_batch | integer | Game batch id the participant played (unique per group condition) | 1 to 60 |
| game_id | integer | Game id the participant played (unique per group condition) | -4 to 1918 |
| trial_id | integer | Trial round the game was played during the study | 0 to 26 |
| AI_conf | integer | AI confidence for the game pile displayed to participants | 0 to 100 |
| human_conf | integer | Participant's stated confidence that the card picked is red **before** seeing the AI confidence | 0 to 100 |
| human_AI_conf | integer | Participant's stated confidence that the card picked is red **after** seeing the AI confidence | 0 to 100 |
| Ai_calibrated_conf| integer | AI confidence after recalibration (if applicable to group condition) | 0 to 100 |
| true_prob | float | Probability of picking a red card from the game pile | [0,100] |
| nr_reds_shown | integer | Number of red cards displayed to participant | 0 to 21 |
| initial_decision | categorical | Color of initial guess | {Red, Black} |
| final_decision | categorical | Color of final guess | {Red, Black} |
| outcome | categorical | Color of card picked | {Red, Black} |
| win | integer | Points won/lost in this round | {-1, 1} |
| points | integer | Points won until this trial round | -27 to 27 |

### Features - Survey Data

| Feature Name | Type | Description | Values/Range (if applicable) |
|--------------|------|-------------|---------------------|
| participant_id | string | Unique identifier for participants | N/A |
| level_name| string | Group condition | {level_A, level_B, level_C, level_BP, level_B_cal}  |
| game_id | integer | Game id the participant played (unique per group condition) | -4 to 1918 |
| trial_id | integer | Trial round the game was played during the study | 0 to 26 |
| recap | string | Statement selected by participant to best apply to their experience in this round | N/A |
| accuracy | integer | Value chosen on likert scale for accuracy question | 0 to 4 |
| final_recap | string | Statement selected by participant to best apply to their overall game experience  | N/A |
| changed_confidence | integer | Value chosen on likert scale for question if confidence was affected by the AI| 0 to 4 |
| trust | integer | Value chosen on likert scale for trust question | 0 to 4 |
| accuracy | integer | Value chosen on likert scale for accuracy question | 0 to 4 |
| age | integer | self-declared age of participant | N/A |
| age group | categorical | Description of target variable | 0 to 26 |
| gender| categorical | self-declared gender of participant  | N/A |
| degree | categorical | self-declared highest obtained degree of participant  | N/A |
| subjects | categorical | self-declared study area of degree  | N/A |



<!-- ## Citation
If you use this dataset, please cite:
```
[Citation information in preferred format]
``` -->

## Contact Information
- Nina Corvelo Benz
- ninacobe@mpi-sws.org
- Max Planck Institute for Software Systems

## Version History
- v1.0.0 (2025-01-21): Initial release

