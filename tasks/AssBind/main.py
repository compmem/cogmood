"""
This script presents stimuli for the associative binding task.

The task presents pairs of objects to participants, who must decide whether
each pair is "new" (i.e. not presented previously), or "old."

Each pair is presented 3 times (an initial presentation plus 2 repetitions), and
recombined with other pairs once.

The order in which these events occur differs by "strength" condition.

"Weak" condition trials: new, recombined, old 1, old 2
"Medium" condition trials: new, old 1, recombined, old 2
"Strong" condition trials: new, old 1, old 2, recombined

"""

# import needed libraries
from smile.common import Log, Label, Wait, Ref, Rectangle, Func, Debug, Loop, \
    UntilDone, If, Else, Parallel, Subroutine, KeyPress, \
    Image, Meanwhile
from smile.scale import scale as s
from smile.lsl import LSLPush
from smile.clock import clock
import smile.ref as ref

from ..happy import HappyQuest

from math import log
import os
from .list_gen import make_trials
from .instruct import Instruct
from .GetResponse import GetResponse


@Subroutine
def AssBindExp(self, config, sub_dir, task_dir=None, block=0,
               reminder_only=False, pulse_server=None, shuffle=False,
               conditions=None, happy_mid=False):
    TRIAL_REMIND_TEXT_L = "%s <-- %s" % (config.RESP_KY[0], list(config.RESP_KEYS.keys())[
                                         list(config.RESP_KEYS.values()).index(config.RESP_KY[0])])
    TRIAL_REMIND_TEXT_R = "%s --> %s" % (list(config.RESP_KEYS.keys())[list(
        config.RESP_KEYS.values()).index(config.RESP_KY[1])], config.RESP_KY[1])
    if task_dir is not None:
        config.TASK_DIR = task_dir

    if len(config.CONT_KEY) > 1:
        cont_key_str = str(config.CONT_KEY[0]) + " or " + \
            str(config.CONT_KEY[-1])
    else:
        cont_key_str = str(config.CONT_KEY[0])

    Log(name="AssBindinfo")

    # get needed variables from config file
    num_attempts = config.NUM_ATTEMPTS
    lag_constraint = config.LAG_CONSTRAINT
    num_pairs_cond = config.NUM_PAIRS_COND

    # generate trial dictionaries from listgen
    gen = Func(make_trials,
               config,
               num_attempts,
               lag_constraint,
               num_pairs_cond,
               sub_dir)
    trials = gen.result

    # present instructions / examples / reminder

    text_names = ['main', 'ex1', 'ex2', 'ex3', 'ex4', 'remind']
    rem_names = ['remind']
    with If(reminder_only):
        Instruct(config=config, text_names=rem_names)
    with Else():
        Instruct(config=config, text_names=text_names)

    Wait(1.0)

    self.eeg_pulse_time = None
    self.trkp_press_time = None
    # FMRI STUFF
    if config.FMRI:
        Label(text="Waiting for Experimenter...",
              font_size=s(config.INST_FONT_SIZE))
        with UntilDone():
            KeyPress(keys=config.FMRI_TECH_KEYS)

        Label(text="+", font_size=s(config.CROSS_FONTSIZE))
        with UntilDone():
            trkp = KeyPress(keys=config.FMRI_TR)
            Log(name="AssBind_TR",
                press_time=trkp.press_time)
            self.trkp_press_time = trkp.press_time
        Wait(duration=config.INIT_TR_WAIT)

    self.start_happy = Func(clock.now).result
    self.end_happy = self.start_happy + ref.jitter(config.TIME_BETWEEN_HAPPY,
                                                   config.TIME_JITTER_HAPPY)

    # initialize lists of accuracies and RTs
    # (to calculate a metric score at the end)
    self.accs = []
    self.rts = []
    with Parallel():
        # background_rect = Rectangle(color = "white",size=(self.exp.screen.width * 1.1,
        #                          self.exp.screen.height * 1.1))
        background = Image(source=Ref(os.path.join, config.TASK_DIR, 'card_table.png'),
                           size=(self.exp.screen.width,
                                 self.exp.screen.height),
                           allow_stretch=True,
                           keep_ratio=False)
        new_rem = Label(text=TRIAL_REMIND_TEXT_L,  # 'F = New',
                        font_size=s(config.INST_TITLE_FONT_SIZE),
                        bottom=self.exp.screen.bottom + s(300),
                        center_x=self.exp.screen.center_x - s(50),
                        color="black")
        old_rem = Label(text=TRIAL_REMIND_TEXT_R,  # 'H = Old',
                        font_size=s(config.INST_TITLE_FONT_SIZE),
                        top=new_rem.bottom,
                        center_x=self.exp.screen.center_x + s(50),
                        color="black")
    with UntilDone():
        # allows people time to orient
        Wait(1)
        # loop through trials
        with Loop(trials) as trial:
            # with If((Func(clock.now).result >= self.end_happy) & (happy_mid)):
            #     Wait(.3)
            #     with Parallel():
            #         Rectangle(blocking=False, color=(.35, .35, .35, 1.0), size=self.exp.screen.size)
            #         HappyQuest(task='CAB', block_num=block, trial_num=trial.i)
            #     self.start_happy = Func(clock.now).result
            #     self.end_happy = self.start_happy + ref.jitter(config.TIME_BETWEEN_HAPPY,
            #                                                    config.TIME_JITTER_HAPPY)
            # delay until next trial based on a base time plus a jitter
            Wait(config.ISI_BASE, jitter=config.ISI_JIT)

            with Parallel():
                # adding in a border around the image to make them look like cards (more gamelike)
                left_border = Image(source=Ref(os.path.join, config.TASK_DIR, "playing_card.png"),
                                    width=(s(config.IMG_WIDTH) + s(50)),
                                    height=(s(config.IMG_HEIGHT) + s(50)),
                                    blocking=False,
                                    allow_stretch=True,
                                    right=self.exp.screen.center_x - s(5),
                                    keep_ratio=False)
                right_border = Image(source=Ref(os.path.join, config.TASK_DIR, "playing_card.png"),
                                     width=(s(config.IMG_WIDTH) + s(50)),
                                     height=(s(config.IMG_HEIGHT) + s(50)),
                                     blocking=False,
                                     allow_stretch=True,
                                     left=left_border.right + s(10),
                                     keep_ratio=False)
                # initialize a frame around the images
                # (which is invisible until response)
                self.width = right_border.right - left_border.left
                self.height = right_border.top - right_border.bottom
                resp_rect = Rectangle(width = self.width, center_x = self.exp.screen.center_x - s(25/2),
                                      top = left_border.top, height = self.height,
                                      color=(.35, .35, .35, 0.0),
                                      duration=config.STIM_PRES_TIME)

                # present pair of images
                # left_image = Image(source=trial.current['img_L'],
                Debug(L=Ref(os.path.join, config.TASK_DIR, 'stim', trial.current['img_L']),
                      R=Ref(os.path.join, config.TASK_DIR, 'stim', trial.current['img_R']))
                left_image = Image(source=Ref(os.path.join, config.TASK_DIR, 'stim', trial.current['img_L']),
                                   duration=config.STIM_PRES_TIME,
                                   center=left_border.center,
                                   width=s(config.IMG_WIDTH),
                                   height=s(config.IMG_HEIGHT),
                                   allow_stretch=True, keep_ratio=False)
                # right_image = Image(source=trial.current['img_R'],
                right_image = Image(source=Ref(os.path.join, config.TASK_DIR, 'stim', trial.current['img_R']),
                                    duration=config.STIM_PRES_TIME,
                                    center=right_border.center,
                                    width=s(config.IMG_WIDTH),
                                    height=s(config.IMG_HEIGHT),
                                    allow_stretch=True, keep_ratio=False)
            # get new/old judgment
            with Meanwhile():
                Wait(until=left_image.appear_time)
                if config.EEG:
                    pulse_fn = LSLPush(server=pulse_server,
                                       val=Ref.getitem(config.EEG_CODES,
                                                       trial.current['cond_trial']))
                    Log(name="CAB_PULSES",
                        start_time=pulse_fn.push_time)
                    self.eeg_pulse_time = pulse_fn.push_time

                Wait(0.2)
                response = GetResponse(keys=config.RESP_KY,
                                       base_time=left_image.appear_time['time'],
                                       correct_resp=Ref.getitem(config.RESP_KEYS,
                                                                trial.current['resp_correct']))

                # present frame around images to indicate response
                with If(response.pressed != None):
                    with Parallel():
                        resp_rect.update(color=config.COLOR_RECT)
                        # add accuracy and RT to lists
                        # (to later calculate performance score)
                        self.accs += [response.correct]
                        self.rts += [response.rt]
                with Else():
                    self.accs += [False]
                    self.rts += [config.MAX_RT]

            # log data
            Log(trial.current,
                name="cab",
                appearL=left_image.appear_time,
                appearR=right_image.appear_time,
                disappearL=left_image.disappear_time,
                disappearR=right_image.disappear_time,
                resp_acc=response.correct,
                resp_rt=response.rt,
                press=response.press_time,
                pressed=response.pressed,
                block=block,
                trial_id=trial.i,
                fmri_tr_time=self.trkp_press_time,
                eeg_pulse_time=self.eeg_pulse_time)
    Wait(.5)
    HappyQuest(task='CAB', block_num=block, trial_num=trial.i)

    # Press 6 to say we are done recording then show them their score.
    if config.FMRI:
        self.keep_tr_checking = True
        Wait(config.POST_TR_WAIT)
        Label(text="Waiting for Experimenter...",
              font_size=s(config.INST_FONT_SIZE))
        with UntilDone():
            with Loop(conditional=self.keep_tr_checking):
                post_trkp = KeyPress(keys=config.FMRI_TR,
                                     duration=config.POST_CHECK_TR_DUR)
                with If(post_trkp.pressed == ''):
                    self.keep_tr_checking = False
            KeyPress(keys=config.FMRI_TECH_KEYS)

        Wait(1.0)


if __name__ == "__main__":
    from smile.common import Experiment
    from smile.startup import InputSubject
    from smile.lsl import init_lsl_outlet
    import config

    import os

    config.RESP_KY = ['1', '4']
    config.RESP_KEYS = {'old': '1', 'new': '4'}
    config.CONT_KEY = ['1', '4']
    config.EEG = True

    if config.EEG:
        # Initialize the outlet
        pulse_server = init_lsl_outlet(server_name='MarkerStream',
                                       server_type='Markers',
                                       nchans=1,
                                       suggested_freq=500,
                                       channel_format='int32',
                                       unique_id='COGBATT_LSL_OUT')
    else:
        pulse_server = None

    exp = Experiment(background_color=(.35, .35, .35, 1.0),
                     name="CAB", scale_down=True, scale_box=(1200, 900))

    # InputSubject(exp_title="Associative Binding")
    with Loop(3) as lp:
        exp.rem_only = (lp.i != 0)
        AssBindExp(config,
                   task_dir=os.path.join("."),
                   sub_dir=Ref.object(exp)._subject_dir,
                   block=lp.i+.1,
                   reminder_only=exp.rem_only,
                   pulse_server=pulse_server)
        Wait(1.0)
    exp.run()
