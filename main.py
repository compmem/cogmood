# General imports
import os
import sys
# Smile imports
from smile.common import Experiment, Log, Wait, Func, UntilDone, \
    Label, Loop, If, Elif, Else, KeyPress, Ref, \
    Parallel, Slider, Serial, UpdateWidget, Debug, Meanwhile, While
from smile.scale import scale as s
from custom_startup import InputSubject
# from android.permissions import request_permissions, Permission
# request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
from kivy.resources import resource_add_path
# CogBatt general imports for running and organizing the experiment.
import config as CogBatt_config
from utils import retrieve_worker_id, \
    get_blocks_to_run, upload_block
import version

# Various task imports
from tasks import FlankerExp, Flanker_config
from tasks import RDMExp, RDM_config
from tasks import AssBindExp, AssBind_config
from tasks import BartuvaExp, Bartuva_config
from tasks import HappyQuest

from error_screen import error_screen


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


# Define default WRK_DIR as current directory
WRK_DIR = '.'

# Check if running from an executable
if CogBatt_config.RUNNING_FROM_EXECUTABLE:
    # Update WRK_DIR to the location of the executable
    WRK_DIR = sys._MEIPASS
    resource_add_path(WRK_DIR)


# Initialize the SMILE experiment.
exp = Experiment(name=CogBatt_config.EXP_NAME,
                 background_color=CogBatt_config.BACKGROUND_COLOR,
                 scale_down=True, scale_box=(1000, 1000), debug=True,
                 Touch=False, local_crashlog=True,
                 cmd_traceback=False, data_dir=WRK_DIR,
                 working_dir=WRK_DIR)
exp._code = ''
if CogBatt_config.WORKER_ID_SOURCE == 'EXECUTABLE':
    retrieved_worker_id = retrieve_worker_id()
    tasks_from_api = get_blocks_to_run(retrieved_worker_id['content'])
    number_of_tasks = 0 if tasks_from_api['status'] == 'error' else len(tasks_from_api['content'])

    exp.tasks_from_api = tasks_from_api
    exp.worker_id_dict = retrieved_worker_id
elif CogBatt_config.WORKER_ID_SOURCE == 'USER':
    InputSubject()
    tasks_from_api = Func(get_blocks_to_run, Ref.object(exp)._subject, Ref.object(exp).get_var('_code')).result
    with If(tasks_from_api['status'] == 'error'):
        number_of_tasks = 0
    with Else():
        number_of_tasks = tasks_from_api['content'].__len__()
    exp.tasks_from_api = tasks_from_api
    exp.worker_id_dict = {"status": "success", "content": Ref.object(exp)._subject}
else:
    raise NotImplementedError



with Parallel():
    with Serial(blocking=False):
        # Log all of the info about the subject and the CogBatt version
        Log(name="Supremeinfo",
            version=version.__version__,
            author=version.__author__,
            date_time=version.__date__,
            email=version.__email__)
        Wait(.5)
        with If(Ref.object(exp).get_var('code_invalid')):
            error_screen(error='Invalid task code: ' + Ref(str, exp._code),
                         message='You entered an incorrect task code, please double check the code '
                                 'listed on the website and try again. If it still does not work '
                                 'please contact Dylan Nielson at Dylan.Nielson@nih.gov.'
                         )

        with If(CogBatt_config.RUNNING_FROM_EXECUTABLE):
            # Handles case where retrieval of worker id fails
            with If(exp.worker_id_dict['status'] == 'error'):
                error_screen(error='Failed to Retrieve Identifier: ' + exp.worker_id_dict['content'],
                            message='Contact Dylan Nielson')
            # Handles case where retrieval of worker id is default placeholder
            with Elif((exp.worker_id_dict['content'] == CogBatt_config.WORKER_ID_PLACEHOLDER_VALUE)
                       and (CogBatt_config.API_BASE_URL != 'NOSERVER')):
                error_screen(error='Non-Unique Identifier',
                            message='Contact Dylan Nielson')
        # Error screen for failed GET request to retrieve blocks
        with If(exp.tasks_from_api['status'] == 'error'):
            error_screen(error='Failed to retrieve tasks.',
                            message=exp.tasks_from_api['content'])
        # Handles case where there are no more blocks to run
        with Elif(number_of_tasks == 0):
            error_screen(error='No tasks to run.',
                            message='Press next in the browser or return to the website via the link from prolific if that window is no longer open.')

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
        
        HappyQuest(task='main', block_num=-1, trial_num=-1)

        exp.practice = True
        exp.BART_practice = True
        Wait(1.0)

        # Log the block order
        Log(name="BLOCK_ORDER",
            order=exp.tasks_from_api['content'])

        Label(text="You will now start the experiments. Press any key to continue.",
              text_size=(s(700), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
        with UntilDone():
            KeyPress()
        Wait(.3)
        
        # Main loop for the experiment
        with Loop(exp.tasks_from_api['content']) as task:
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
            
            Wait(.5)

            Label(text="Uploading data...",
                      text_size=(s(700), None), font_size=s(CogBatt_config.SSI_FONT_SIZE))
            with UntilDone():
                with Parallel():
                    exp.task_data_upload = Func(upload_block,
                                                worker_id=exp.worker_id_dict['content'],
                                                block_name=exp.task_name + '_' + Ref(str, exp.block_number),
                                                data_directory=Ref.object(
                                                    exp)._session_dir,
                                                slog_file_name='log_'+exp.task_name+'_'+'0.slog',
                                                code=Ref.object(exp).get_var('_code'))
                    Wait(3)

            # Error screen for failed upload
            with If(exp.task_data_upload.result['status'] == 'error'):
                error_screen(error='Error During Upload',
                             message=exp.task_data_upload.result['content'])

    KeyPress(['ESCAPE'], blocking=False)
Wait(.25)
exp.run()
