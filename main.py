# General imports
import os
from os.path import join
import sys
import requests
import json
import subprocess
import zipfile
import hashlib
# Smile imports
from smile.common import Experiment, Log, Wait, Func, UntilDone, ButtonPress, \
    Button, Label, Loop, If, Elif, Else, KeyPress, Ref, \
    Parallel, Slider, MouseCursor, Rectangle, Meanwhile, \
    Serial, Debug, Screenshot, Questionnaire, UpdateWidget
from smile.clock import clock
from smile.lsl import init_lsl_outlet, LSLPush
from smile.scale import scale as s
from smile.startup import InputSubject
# from android.permissions import request_permissions, Permission
# request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
from kivy.resources import resource_add_path
# CogBatt general imports for running and organizing the experiment.
import config as CogBatt_config
from executable_utils import read_app_subject_id, read_exe_subject_id
from list_gen import gen_order
import version

# pyperclip for copying to clipboard
import pyperclip

# Various task imports
from tasks import FlankerExp, Flanker_config
from tasks import RDMExp, RDM_config
from tasks import AssBindExp, AssBind_config
from tasks import BartuvaExp, Bartuva_config


def zip_directory(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, mode='w') as zipf:
        len_dir_path = len(folder_path)
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path[len_dir_path:])


def ToOut(message, exp, post_urlFULL):
    failed_post = False
    failed_copy = False
    print(exp._subject_dir)
    to_zip = "data.zip"
    print(to_zip)
    try:
        zip_directory(exp._session_dir, to_zip)
    except BaseException as err:
        print(f"Unexpected {err=}, Could not zip directory.{type(err)=}")
        raise err

    status_code = None
    try:
        with open(to_zip, 'rb') as f:
            data = f.read()
            print(post_urlFULL)
            r = requests.post(post_urlFULL,
                              data={'results': data},
                              verify=os.path.join(WRK_DIR, "cert.pem"),
                              allow_redirects=False,
                              timeout=120)
            print(r.status_code)
            status_code = r.status_code
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")
        failed_post = True
    if status_code != 200:
        failed_post = True
    m = 'e0000000000'
    if (not (message is None)) & (not failed_post):
        m = message['extra'][10:-5]
        with open('confirmation_code.txt', 'w') as f:
            f.write(message['extra'][10:-5])

        try:
            pyperclip.copy(message['extra'][10:-5])
        except BaseException as err:
            print(
                f"Unexpected {err=}, Could not copy to clipboard: {type(err)=}")
            failed_copy = True
    else:
        with open(to_zip, 'rb') as f:
            data = f.read()
            m = "e" + hashlib.md5(data).hexdigest()[:10]
        try:
            pyperclip.copy(m)
        except BaseException as err:
            print(
                f"Unexpected {err=}, Could not copy to clipboard: {type(err)=}")
            failed_copy = True

    return failed_post, failed_copy, m


# ----------------WRK_DIR EDITS HERE----------------
# edited so the data_dir is the WRK_DIR if running from the packaged exe
# otherwise the data_dir is '.'
retrieved_subject_id = None
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if CogBatt_config.CURRENT_OS == 'Windows':
        retrieved_subject_id = read_exe_subject_id()
    elif CogBatt_config.CURRENT_OS == 'Darwin':
        retrieved_subject_id = read_app_subject_id()
        
    WRK_DIR = sys._MEIPASS
    resource_add_path(os.path.join(sys._MEIPASS))
else:
    WRK_DIR = '.'


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

# Generates the block order for the tasks. All tasks must be presented before
# another is repeated, except BART which is repeated half as often. Also, no
# task can repeat directly following itself.
blocks = gen_order(CogBatt_config)
print(blocks)
# Do the get
# print('About to get')
# with open(os.path.join(WRK_DIR, 'serverinfo.txt'), 'r') as f:
#     serverinfo = f.readline().strip()
#     post_urlFULL = f.readline().strip()
#     print(serverinfo, post_urlFULL)

# try:
#     r = requests.get(serverinfo, verify=os.path.join(WRK_DIR, "cert.pem"),
#                      timeout=2)
#     print(r.text)
#     message = json.loads(r.text.replace("\'", "\""))
#     post_urlFULL = post_urlFULL.format(message['platformid'],
#                                        message['sqlid'])
#     connected = True
#     to_message = message['extra'][10:-5]
# except:
#     print("NO CONNECTION")
#     message = None
#     post_urlFULL = None
#     connected = False
#     to_message = "Yo"
# print("connected: ", connected)
# Initialize the SMILE experiment.
exp = Experiment(name=CogBatt_config.EXP_NAME,
                 background_color=CogBatt_config.BACKGROUND_COLOR,
                 scale_down=True, scale_box=(1000, 1000), debug=False,
                 Touch=False, local_crashlog=True,
                 cmd_traceback=False, data_dir=WRK_DIR,
                 working_dir=WRK_DIR)

exp.subject_id = retrieved_subject_id if retrieved_subject_id else "Not running from exe, no Subject ID provided."

Label(text="Subject ID: " + exp.subject_id + "\nPress any key to continue.",
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

        Wait(.3)
        with Parallel():
            Questionnaire(loq=CogBatt_config.CESD, font_size=s(25),
                          width=s(1100),
                          x=(exp.screen.width/2.) - s(1100)/2.)
            MouseCursor(blocking=False)

        exp.practice = True
        exp.BART_practice = True
        Wait(1.0)

        # Log the block order
        Log(name="BLOCK_ORDER",
            order=blocks)

        Label(text="You will now start the experiments. Press any key to continue.",
              text_size=(s(700), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
        with UntilDone():
            KeyPress()
        Wait(.3)
        # Main loop for the experiment
        exp.cal_counter = 0
        exp.file_counter = 1
        exp.still_loop = True

        with Loop(blocks) as BL:
            with Loop(BL.current) as TL:
                with If(TL.current[0] == "flkr"):
                    Wait(.5)
                    FlankerExp(Flanker_config,
                               run_num=BL.i,
                               lang='E',
                               happy_mid=TL.current[1])
                with Elif(TL.current[0] == "cab"):
                    Wait(.5)

                    if hasattr(sys, '_MEIPASS'):
                        taskdir = os.path.join(os.path.join(
                            sys._MEIPASS), "tasks", "AssBind")
                    else:
                        taskdir = os.path.join("tasks", "AssBind")
                    AssBindExp(AssBind_config,
                               task_dir=taskdir,
                               sub_dir=Ref.object(exp)._subject_dir,
                               block=BL.i,
                               happy_mid=TL.current[1])
                with Elif(TL.current[0] == "rdm"):
                    Wait(.5)
                    RDMExp(RDM_config,
                           run_num=BL.i,
                           lang='E',
                           happy_mid=TL.current[1])

                with Elif(TL.current[0] == "bart"):
                    Wait(.5)
                    if hasattr(sys, '_MEIPASS'):
                        task2dir = os.path.join(os.path.join(
                            sys._MEIPASS), "tasks", "BARTUVA")
                    else:
                        task2dir = os.path.join("tasks", "BARTUVA")
                    BartuvaExp(Bartuva_config,
                               run_num=BL.i,
                               sub_dir=Ref.object(exp)._session_dir,
                               practice=False,
                               task_dir=task2dir,
                               happy_mid=TL.current[1])

                Wait(1.0)
                Label(text="You may take a short break!\n\nPress any key when you would like to continue to the next experiment. ",
                      text_size=(s(700), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
                with UntilDone():
                    KeyPress()

    KeyPress(['ESCAPE'], blocking=False)
Wait(.25)
exp.run()
# with If(connected):
#     Label(text="Thank you! Your data is about to be sent to our servers.\nOn one of the next screens, you will see your confirmation code!\nPress any key to continue",
#           text_size=(s(900), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
#     with UntilDone():
#         KeyPress()
#     # Start the experiment, everything above runs before the experiment even starts
#     # since SMILE is a state machine. You must build it and then *.run()* it.

#     Wait(.25)
#     Label(text="Please wait, this could take several minutes...",
#           text_size=(s(900), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
#     with UntilDone():
#         Wait(.033)
#         to_server_resp = Func(ToOut, message, exp, post_urlFULL)
#     with If(to_server_resp.result[1]):

#         Label(text="Due to an error, we were unable to copy the code to your clipboard.\n\nPlease see confirmation_code.txt for your code and paste it into MTurk. In case you cannot find this file, the code again is:\n\n"+to_server_resp.result[2]+"\n\nPress any key to continue.",
#               text_size=(s(900), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
#         with UntilDone():
#             KeyPress()
#     with Else():
#         Label(text="Your confirmation code was sent to your clipboard and saved in confirmation_code.txt.\n\nPlease paste it into MTurk. The code is:\n\n"+ to_server_resp.result[2] + "\n\nPlease write it down, then press any key to continue.",
#               text_size=(s(900), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
#         with UntilDone():
#             KeyPress()
#     with If(to_server_resp.result[0]):
#         Label(text="Due to an error with the server, we ask that you send your data to: dylan.nielson@nih.gov\n\nYour data is in a file called data.zip located the same place as this experiment, cogmood.exe.\n\nPress any key to exit.",
#               text_size=(s(900), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
#         with UntilDone():
#             KeyPress()
# with Else():
#     ret2 = Func(ToOut, message, exp, post_urlFULL)

#     Label(text="Thank you!\n\nDue to an error with the server, we ask that you send your data to: dylan.nielson@nih.gov\n\nYour data is in a file called data.zip located the same place as this experiment, cogmood.exe.\n\nYour confirmation code for the experiment is\n\n" +ret2.result[2]+".\n\nPress any key to continue.",
#           text_size=(s(900), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
#     with UntilDone():
#         KeyPress()
