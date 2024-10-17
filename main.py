# General imports
import os
import sys
# Smile imports
from smile.common import Experiment, Log, Wait, Func, UntilDone, \
    Label, Loop, If, Elif, Else, KeyPress, Ref, \
    Parallel, Slider, Serial, UpdateWidget
from smile.clock import clock
from smile.scale import scale as s
from smile.startup import InputSubject
# from android.permissions import request_permissions, Permission
# request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
from kivy.resources import resource_add_path
# CogBatt general imports for running and organizing the experiment.
import config as CogBatt_config
from utils import read_app_worker_id, read_exe_worker_id, \
    get_blocks_to_run, upload_block
import version

# Various task imports
from tasks import FlankerExp, Flanker_config
from tasks import RDMExp, RDM_config
from tasks import AssBindExp, AssBind_config
from tasks import BartuvaExp, Bartuva_config


# Different configs getting set for the different subject names. If their ID
# ends in *b* then it is behavioral/eyetracking, if it ends in *e* it is
# EEG/eyetracking, and if it ends in *m* then it is fMRI.


RDM_config.TOUCH = CogBatt_config.TOUCH
AssBind_config.TOUCH = CogBatt_config.TOUCH
Flanker_config.TOUCH = CogBatt_config.TOUCH
Bartuva_config.TOUCH = CogBatt_config.TOUCH
BorE = False
EYES = False


# Change the resp keys and instruction texts of the different tasks depending
# on the subject ID.
CogBatt_config.INST_TEXT = CogBatt_config.INST_TEXT % (CogBatt_config.RESP_KEYS[0],
                                                       CogBatt_config.RESP_KEYS[-1])
RDM_config.RESP_KEYS = CogBatt_config.RESP_KEYS[:]
RDM_config.CONT_KEY = CogBatt_config.CONT_KEY

Flanker_config.RESP_KEYS = CogBatt_config.RESP_KEYS[:]
Flanker_config.CONT_KEY = CogBatt_config.CONT_KEY
AssBind_config.RESP_KY = CogBatt_config.RESP_KEYS[:]
AssBind_config.RESP_KEYS = {'old': 'F', "new": 'J'}
AssBind_config.CONT_KEY = CogBatt_config.CONT_KEY
Bartuva_config.RESP_KEYS = CogBatt_config.RESP_KEYS[:]
Bartuva_config.CONT_KEY = CogBatt_config.CONT_KEY


# If we have an eeg experiment, then we need to initialize the lsl outlet.

pulse_server = None

# ----------------WRK_DIR EDITS HERE----------------
# edited so the data_dir is the WRK_DIR if running from the packaged exe
# otherwise the data_dir is '.'
retrieved_worker_id = None
if CogBatt_config.RUNNING_FROM_EXECUTABLE:
    if CogBatt_config.CURRENT_OS == 'Windows':
        retrieved_worker_id = read_exe_worker_id()
    elif CogBatt_config.CURRENT_OS == 'Darwin':
        retrieved_worker_id = read_app_worker_id()

    WRK_DIR = sys._MEIPASS
    resource_add_path(os.path.join(sys._MEIPASS))
else:
    WRK_DIR = '.'

# Requests list of tasks from the server. All tasks must be presented before
# another is repeated, except BART which is repeated half as often. Also, no
# task can repeat directly following itself.
tasks_from_api: list[str] | dict[str, str] = get_blocks_to_run(
    CogBatt_config.API_BASE_URL, retrieved_worker_id)

# Formats tasks into [{'task_name': 'flkr', 'block_number': 0}] format
tasks: list[dict[str, str]] | None = None if 'error' in tasks_from_api else [
    {'task_name': task.split('_')[0], 'block_number': int(task.split('_')[1])} for task in tasks_from_api]

# Initialize the SMILE experiment.
exp = Experiment(name=CogBatt_config.EXP_NAME,
                 background_color=CogBatt_config.BACKGROUND_COLOR,
                 scale_down=True, scale_box=(1000, 1000), debug=False,
                 Touch=False, local_crashlog=True,
                 cmd_traceback=False, data_dir=WRK_DIR,
                 working_dir=WRK_DIR)

# TODO: Handle case where there are no more blocks to run
# TODO: Error screen for no failed GET request to retrieve blocks
# TODO: Error screen for no worker_id or default worker_id
exp.worker_id = retrieved_worker_id if retrieved_worker_id else "Not running from exe, no Subject ID provided."

Label(text="Worker ID: " + exp.worker_id + "\nPress any key to continue.",
      text_size=(s(700), None),
      font_size=s(CogBatt_config.INST_FONT),
      halign="center")

with UntilDone():
    KeyPress()

InputSubject(exp_title="Supreme")
with Parallel():
    with Serial(blocking=False):
        # Log all of the info about the subject and the CogBatt version
        Log(name="Supremeinfo",
            version=version.__version__,
            author=version.__author__,
            date_time=version.__date__,
            email=version.__email__)

        Wait(.5)

        # Give participants the option to record demographic information, but only on
        # their first visit, the behavioral visit.

        # Demographics(CogBatt_config)
        # Wait(1.0)

        # Present initial CogBatt instructions.
        Label(text=CogBatt_config.INST_TEXT,
              font_size=s(CogBatt_config.INST_FONT),
              text_size=(s(700), None))
        with UntilDone():
            KeyPress()

        Label(text=CogBatt_config.HAPPY_TEXT,
              text_size=(s(700), None),
              font_size=s(CogBatt_config.INST_FONT))
        with UntilDone():
            KeyPress()
        Wait(.3)
        with Parallel():
            Label(text="Taken all together, how happy are you with your life these days?\nPress F to move left, Press J to move right.",
                  font_size=s(CogBatt_config.HAPPY_FONT_SIZE),
                  halign='center',
                  center_y=exp.screen.center_y + s(300))
            sld = Slider(min=-10, max=10, value=0,
                         width=s(CogBatt_config.SLIDER_WIDTH))
            Label(text="unhappy", font_size=s(CogBatt_config.HAPPY_FONT_SIZE),
                  center_x=sld.left, center_y=sld.center_y - s(100))
            Label(text="happy", font_size=s(CogBatt_config.HAPPY_FONT_SIZE),
                  center_x=sld.right, center_y=sld.center_y - s(100))
            Label(text='Press Spacebar to lock-in your response.',
                  top=sld.bottom - s(250), font_size=s(CogBatt_config.HAPPY_FONT_SIZE))

        with UntilDone():
            exp.happy_start_time = Ref(clock.now)
            exp.last_check = exp.happy_start_time
            exp.happy_dur = 0.0
            exp.HAPPY_SPEED = CogBatt_config.HAPPY_INC_BASE
            exp.first_press_time = None
            with Loop():
                ans = KeyPress(keys=CogBatt_config.RESP_HAPPY)
                with If(exp.first_press_time == None):
                    exp.first_press_time = ans.press_time
                with If(ans.press_time['time'] - exp.last_check <
                        CogBatt_config.NON_PRESS_INT):
                    exp.HAPPY_SPEED = (CogBatt_config.HAPPY_INC_BASE * (Ref(clock.now) -
                                       exp.happy_start_time) * CogBatt_config.HAPPY_MOD) + CogBatt_config.HAPPY_INC_START

                with Else():
                    exp.HAPPY_SPEED = CogBatt_config.HAPPY_INC_START
                    exp.happy_start_time = Ref(clock.now)
                exp.last_check = Ref(clock.now)

                with If(ans.pressed == CogBatt_config.RESP_HAPPY[0]):
                    with If(sld.value - exp.HAPPY_SPEED <= (-1 * CogBatt_config.HAPPY_RANGE)):
                        UpdateWidget(
                            sld, value=(-1 * CogBatt_config.HAPPY_RANGE))
                    with Else():
                        UpdateWidget(sld, value=sld.value - exp.HAPPY_SPEED)
                with Elif(ans.pressed == CogBatt_config.RESP_HAPPY[1]):
                    with If(sld.value + exp.HAPPY_SPEED >= CogBatt_config.HAPPY_RANGE):
                        UpdateWidget(sld, value=CogBatt_config.HAPPY_RANGE)
                    with Else():
                        UpdateWidget(sld, value=sld.value + exp.HAPPY_SPEED)

                # Wait(.005)
            with UntilDone():
                submit = KeyPress(keys=['SPACEBAR'])
        Log(name="happy",
            task='main',
            slider_appear=sld.appear_time,
            first_press=exp.first_press_time,
            submit_time=submit.press_time,
            value=sld.value)

        exp.practice = True
        exp.BART_practice = True
        Wait(1.0)

        # Log the block order
        Log(name="BLOCK_ORDER",
            order=tasks)

        Label(text="You will now start the experiments. Press any key to continue.",
              text_size=(s(700), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
        with UntilDone():
            KeyPress()
        Wait(.3)
        # Main loop for the experiment
        exp.cal_counter = 0
        exp.file_counter = 1
        exp.still_loop = True

        with Loop(tasks) as task:
            exp.task_name = task.current['task_name']
            exp.block_number = task.current['block_number']
            with If(exp.task_name == "flkr"):
                Wait(.5)
                FlankerExp(Flanker_config,
                           run_num=exp.block_number,
                           lang='E',
                           happy_mid=False)
            with Elif(exp.task_name == "cab"):
                Wait(.5)

                if CogBatt_config.RUNNING_FROM_EXECUTABLE:
                    taskdir = os.path.join(os.path.join(
                        sys._MEIPASS), "tasks", "AssBind")
                else:
                    taskdir = os.path.join("tasks", "AssBind")
                AssBindExp(AssBind_config,
                           task_dir=taskdir,
                           sub_dir=Ref.object(exp)._subject_dir,
                           block=exp.block_number,
                           happy_mid=False)
            with Elif(exp.task_name == "rdm"):
                Wait(.5)
                RDMExp(RDM_config,
                       run_num=exp.block_number,
                       lang='E',
                       happy_mid=False)

            with Elif(exp.task_name == "bart"):
                Wait(.5)
                if CogBatt_config.RUNNING_FROM_EXECUTABLE:
                    task2dir = os.path.join(os.path.join(
                        sys._MEIPASS), "tasks", "BARTUVA")
                else:
                    task2dir = os.path.join("tasks", "BARTUVA")
                BartuvaExp(Bartuva_config,
                           run_num=exp.block_number,
                           sub_dir=Ref.object(exp)._session_dir,
                           practice=False,
                           task_dir=task2dir,
                           happy_mid=False)

            Wait(1.0)
            Label(text="You may take a short break!\n\nPress any key when you would like to continue to the next experiment. ",
                  text_size=(s(700), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
            with UntilDone():
                # TODO: Add error screen for failed upload
                task_data_upload_response = Func(upload_block,
                                                 worker_id=retrieved_worker_id,
                                                 block_name=exp.task_name + Ref(str, exp.block_number),
                                                 data_directory=Ref.object(
                                                     exp)._session_dir,
                                                 slog_file_name='log_'+exp.task_name+'_'+'0.slog')
                KeyPress()

    KeyPress(['ESCAPE'], blocking=False)
Wait(.25)
exp.run()
