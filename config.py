# -*- coding: utf-8 -*-

import os
import sys
import platform

CURRENT_OS: str = platform.system()
if os
API_BASE_URL: str = 'NOSERVER'
VERIFY: bool = False
RUNNING_FROM_EXECUTABLE: bool = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
# WORKER_ID_PLACEHOLDER_VALUE is the placeholder value assigned to the WorkerID field
# in the executables when we build them. It should be replaced by actual ID when
# the executable is prepared for distribution.
WORKER_ID_PLACEHOLDER_VALUE = '"------------------------------------------------".---------------------------'
EXP_NAME = "SUPREMEMOOD"

BACKGROUND_COLOR = (.35, .35, .35, 1.0)

DEBRIEF_FONT_SIZE = 21
SSI_FONT_SIZE = 40
SLIDER_WIDTH = 1000

TOUCH = False
FMRI = False
EEG = False

RECOUTWIDTH = 1000
RECOUTHEIGHT = 800
DISPLAY_FONT = 45
BUTTON_WH = 200

NUM_REPS = 1
FMRI_TASKS = [['cab', 'flkr', 'rdm', 'bart'],
              ['cab', 'flkr', 'rdm'],
              ['cab', 'flkr', 'rdm']]
FMRI_REPS = 1
SHUFFLE_TASKS = True
RESP_KEYS = ['F', 'J']
CONT_KEY = ['SPACEBAR']
FMRI_TR = ['T']
BART_STRING = "F or J"
ASS_BIND_DICT = {'old': 'F', 'new': 'J'}

RESTING_STATE_SYNC_VAL = 99
RESTING_STATE_DUR = 180

# Stuff for Demographics
FONT_SIZE = 25

CRUB = os.path.join("assets", "buttons", "unpressedFILEbutton.png")
CRDB = os.path.join("assets", "buttons", "pressedFILEbutton.png")
FUB = os.path.join("assets", "buttons", "unpressedFLANKERbutton.png")
FDB = os.path.join("assets", "buttons", "pressedFLANKERbutton.png")
MDUB = os.path.join("assets", "buttons", "unpressedMOVINGDOTSbutton.png")
MDDB = os.path.join("assets", "buttons", "pressedMOVINGDOTSbutton.png")
BARTUB = os.path.join("assets", "buttons", "unpressedBALOONbutton.png")
BARTDB = os.path.join("assets", "buttons", "pressedBALOONbutton.png")
MMIUB = os.path.join("assets", "buttons", "unpressed_STW.png")
MMIDB = os.path.join("assets", "buttons", "pressed_STW.png")

TIME_BETWEEN_HAPPY = 15
TIME_JITTER_HAPPY = 10

INST_FONT = 25
INST_TEXT = "You will perform 4 tasks in this experiment, and some of the tasks more than once. Instructions will be displayed prior to each task. Please read the instructions for each task very carefully.\n\nFor each task, you will make responses by pressing the %s button with one hand, and the %s button with your other hand.\n\nSet aside 40 minutes to an hour. You are able to take short breaks between each task.\n\nOnce the experiment fully begins, you may end the experiment by pressing the escape key. The window will close, and your data up till that point will be sent to us and your payment will be forfeit. Press any key to proceed."
HAPPY_TEXT = "Periodically during this experiment, you will be asked about your mood. You will use the same keys as mentioned before. Please rate how you feel about your life these days.\n\nMove the slider with these keys and press SPACE BAR button to lock in your response.\n\nPlease respond as quickly and as accurately as possible.\n\nPress any key to continue."

CONSENT_FONT = 25
consent1 = """
[b]Informed Consent Agreement[/b]


[b]Please read this consent agreement carefully before you decide to participate in the study.[/b]

[b]Purpose of the research study:[/b] The purpose of the study is to learn more about different aspects of human memory. In other words, we are interested in how patterns of behavioral and neural activity affect changes in context between encoding and retrieval, lag recency effects in episodic and semantic memory, serial position effects, and the effects of stimulus characteristics such as word frequency and semantic relatedness.
[b]What you will do in the study:[/b] In this study, we hope to better understand how people remember recently experienced events by examining behavior and neural activity as participants encode information into memory and retrieve information from memory.

In this study you will:
1. Complete the consent forms and ensure you fully understand the study procedure
2. Study lists of words presented by a computer
3. Complete a series of arithmetic or reasoning problems or questionnaires

[b]Time required:[/b] The study will require about 1 hour of your time.
[b]Risks:[/b] There are no known risks. You will be able to speak to investigators at any time during the procedures if you have any concerns or difficulties.
[b]Benefits:[/b] There are no direct benefits to you from participation in this study. This study may help us understand the processes involved in making decisions and retrieving memories.
[b]Confidentiality:[/b] The information that you give in the study will be handled confidentially. Your data will be anonymous, which means that your name will not be collected or linked to the data. Your data will be reported in a way that will not identify you.

____

Press the 1 or 4 key when you are ready to continue to the next page of the informed consent agreement.
"""


consent2 = """
[b]Informed Consent Agreement[/b]


[b]Voluntary participation:[/b] Your participation is completely voluntary. You may refuse to participate in this study without penalty or loss of benefits to which you are otherwise entitled. If you are a student or employee at the University of Virginia, your decision will not affect your grades or employment status. If you choose to participate in the study, you may discontinue at any time without penalty or loss of benefits. By indicating your willingness to participate, you do not give up any personal legal rights you may have as a participant in this study. If you wish to withdraw from the study, simply tell the experimenter and leave the room. There is no penalty for withdrawing. You will still receive full credit for the study.

[b]Right to withdraw from the study:[/b] You have the right to withdraw from the study at any time without penalty.
[b]How to withdraw from the study:[/b] If you wish to withdraw from the study, you may simply let the experimenter know, and you are free to leave the room.
[b]Payment:[/b] You will receive no payment for participating in the study. You will receive class participation credit for enrolling in this study.

[b]If you have questions about the study, contact:[/b]

Per B. Sederberg, Ph.D.
B011 Gilmer Hall, 485 McCormick Road
University of Virginia, Charlottesville, VA 22903
434 924-5725, pbs5u@virginia.edu.

[b]If you have questions about your rights in the study, contact:[/b]

Tonya R. Moon, Ph.D.
Chair, Institutional Review Board for the Social and Behavioral Sciences
One Morton Dr. Suite 500
University of Virginia, P.O. Box 800392
Charlottesville, VA 22908-0392
434 924-5999, irbsbshelp@virginia.edu, Website: www.virginia.edu/vpr/irb/sbs.
____

If you give your consent to participate in this study, press 1 or 4.
If you do not give your consent, please speak with an experimenter."""


debrief = """
Debriefing

As we go about our daily lives, we form memories by binding information to the context (i.e. a particular place and time)
in which we experience it. To recall details of a specific event, we must mentally time travel back to the context of the
event in order to cue our memory system. In our research, we aim to determine what parts of context are important for
forming and retrieving memory. We investigate this by manipulating different aspects of information and how it is
presented, and then observing changes in memory behavior.

In this study, you were asked to look at information, such as words and/or pictures, and then recall or recognize the items
that you studied.  In some cases, the items you look at may have been related to one another and in some cases not.
We are particularly interested in the effect inter-item relatedness has on how the brain represents the context of an
event, and how it affects memory storage and retrieval.

In order to maintain the integrity of this study, we ask that you please do not discuss your experiences in the experiment with
other students who could potentially be participants. If others know all details of the study before participating, it could
affect the results in unexpected ways.

If you have any questions about this study, please do not hesitate to ask your experimenter now. You may also contact
Dr. Per B. Sederberg, pbs5u@virginia.edu.

If you are interested in learning more about the PI’s previous work on the effects of context on memory, the articles
listed below are a great place to start!

Sederberg, P. B., Howard, M. W., & Kahana, M. J. (2008). A context-based theory of recency
and contiguity in free recall. Psychological review, 115(4), 893.

Sederberg, P. B., Miller, J. F., Howard, M. W., & Kahana, M. J. (2010). The temporal contiguity
effect predicts episodic memory performance. Memory & cognition, 38(6), 689-699.

Sederberg, P. B., Gershman, S. J., Polyn, S. M., & Norman, K. A. (2011). Human memory
reconsolidation can be explained using the temporal context model. Psychonomic bulletin
& review, 18(3), 455-468.

Thank you for your participation! Press anything to continue."""





CESD = [{'type':'TITLE',
         'question':"General Questionnaire",
         },
        {'type':'MC',
         'question':"1. Sex assigned at birth:",
         'ans':['Male',
                'Female',
                'Perfer not to answer'],
         'group_id':"1"},
         {'type':'TI',
          'question':"2. Your Age: ",
          'multiline':2},
        {'type':'LI',
         'question':"3. I was bothered by things that usually don't bother me.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"3"},
        {'type':'LI',
         'question':"4. I did not feel like eating; my appetite was poor.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"4"},
        {'type':'LI',
         'question':"5. I felt that I could not shake off the blues even with help from my family or friends.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"5"},
        {'type':'LI',
         'question':"6. I felt I was just as good as other people.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"6"},
        {'type':'LI',
         'question':"7. I had trouble keeping my mind on what I was doing.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"7"},
        {'type':'LI',
         'question':"8. I felt depressed.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"8"},
        {'type':'LI',
         'question':"9. I felt that everything I did was an effort.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"9"},
        {'type':'LI',
         'question':"10. I felt hopeful about the future.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"10"},
        {'type':'LI',
         'question':"11. I thought my life had been a failure.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"11"},
        {'type':'LI',
         'question':"12. I felt fearful.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"12"},
        {'type':'LI',
         'question':"13. My sleep was restless",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"13"},
        {'type':'LI',
         'question':"14. I was happy.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"14"},
        {'type':'LI',
         'question':"15. I talked less than usual.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"15"},
        {'type':'LI',
         'question':"16. I felt lonely.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"16"},
        {'type':'LI',
         'question':"17. People were unfriendly.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"17"},
        {'type':'LI',
         'question':"18. I enjoyed life.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"18"},
        {'type':'LI',
         'question':"19. I had crying spells.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"19"},
        {'type':'LI',
         'question':"20. I felt sad.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"20"},
        {'type':'LI',
         'question':"21. I felt that people dislike me.",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"21"},
        {'type':'LI',
         'question':"22. I could not get \"going.\"",
         'ans':['Rarely or none\nof the time\n(less than 1 day)',
                'Some or a little of\nthe time (1-2 days)',
                'Occasionally or a\nmoderate amount of time\n(3-4 days)',
                'Most or all of the time\n(5-7 days)'],
         'group_id':"22"}
         ]
