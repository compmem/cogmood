from pathlib import Path

# Define the base directory as the directory containing the current file
BASE_DIR = Path(__file__).resolve().parent

# Use BASE_DIR / "stim" / "fish_" to define the STIM_DIRECTORY path
STIM_DIRECTORY = str(BASE_DIR / "stim" / "fish_")

# Background image path
BACKGROUND_IMAGE = str(BASE_DIR / "ocean_background.png")

# FLANKER VARIABLES
NUM_TRIALS = 1 # (len(evidence_conditions)-1) * 4 + 2 * num_trials
NUM_BLOCKS = 1
MOUSE = False


RESP_KEYS = ['1', '4']
CONT_KEY = ['1', '4']

NUM_FLANKS = 2
LAYERS = [{"condition": "=", "dir":"right", "layers":["right","left"]},{"condition":"~","dir":"right","layers":["left","right"]},{"condition": "=", "dir":"left", "layers":["left","right"]},{"condition":"~","dir":"left","layers":["right","left"]},{"condition": "+", "dir":"right", "layers":["right","right"]},{"condition":"+","dir":"left","layers":["left","left"]}]


CONDITIONS = [
              # Mixed Easy R
              {"condition": "=",
               "dir": "right"},
              # Mixed Hard R
              { "condition": "~",
               "dir": "right"},
              # Mixed Hard L
              {"condition": "~",
               "dir": "left"},
              # Mixed Easy L
              {"condition": "=",
               "dir": "left"},
              # Congruent R
              {"condition": "+",
               "dir": "right"},
              # Congruent L
              {"condition": "+",
               "dir": "left"},

              ]

#EVIDENCE_CONDITIONS = [0., 45.]
NUM_LOCS = 8
DEF_SAT = [255.,255.,255.]
CONFIG_BOX = 45.
CONFIG_AROUND = 45.*(15./40.)
LW = 2.
NUM_REPS = 1
RESPONSE_DURATION = 3.
FROM_CENTER = 300
FEEDBACK_TIME = 0.5

STIM_SIZE = 35
PADDING = 3

SKIP_SIZE = [200, 50]
SKIP_FONT_SIZE = 25

FINAL_FONT_SIZE = 35
INST_FONT_SIZE = 35
ORIENT_FONT_SIZE = 80
SCORE_FONT_SIZE = 60
CROSS_FONTSIZE = 90

# Around 2.3 seconds each
ORIENT_DUR = .4
WAIT_DUR = .5
WAIT_JITTER = .5
ITI = .75
ITI_JITTER = .5
FEEDBACK_DUR = 1.0

POS_FEEDBACK_COLOR = [0./255., 171./255., 56./255., 255./255.]
NEG_FEEDBACK_COLOR = "red"
FEEDBACK_FONT_SIZE = 120
WIDTH_SCORE_RECT = 1200
HEIGHT_SCORE_RECT = 900

FAST_TIME = 0.5
SLOW_TIME = 3.0
CROSS_COLOR = (1.0, 1.0, 1.0, 1.0)
INNER_CIRCLE_COLOR = (.35, .35, .35, 1.0)
NUM_LOCS = 8

TIME_BETWEEN_HAPPY = 15
TIME_JITTER_HAPPY = 10

TOUCH = False

FMRI = False
FMRI_TR = ["T"]
FMRI_TECH_KEYS = ['ENTER']
FMRI_TR_DUR = .8
INIT_TR_WAIT = 6.0
POST_TR_WAIT = 16.0
POST_CHECK_TR_DUR = 3.0*FMRI_TR_DUR

EEG = False
EEG_CODES = {"=":11, "+":12,
             "~":13, "--":14, "|":15}
