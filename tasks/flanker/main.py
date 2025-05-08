# -*- coding: utf-8 -*-

# load all the states
from smile.common import *
from smile.clock import clock
import smile.ref as ref

from smile.scale import scale as s
from smile.lsl import LSLPush
from happy import HappyQuest
import smile.ref as ref
from list_gen import gen_fblocks
from math import log
from trial_copy import Trial, GetResponse
from instruct_copy import Instruct
#from . import version


def _get_score(corr_trials, num_trials, rt_trials):
    avec = (((corr_trials/num_trials) - .5)/.5)
    rvec = (sum([(log(3. + 1.) - log(r + 1.))/((log(3. + 1.) - log(.5 + 1.)))
                 for r in rt_trials]) / num_trials)
    g = avec * rvec

    return int(g*100)


@Subroutine
def FlankerExp(self, config, run_num=0, lang="E", pulse_server=None,
               happy_mid=False):

    if len(config.CONT_KEY) > 1:
        cont_key_str = str(config.CONT_KEY[0]) + " or " + \
                       str(config.CONT_KEY[-1])
    else:
        cont_key_str = str(config.CONT_KEY[0])

    res = Func(gen_fblocks, config)
    self.f_blocks = res.result

    Log(name="flankerinfo")
        #version=version.__version__,
        #author=version.__author__,
        #date_time=version.__date__,
        #email=version.__email__)

    Instruct(config, lang=lang)
    Wait(2.0)

    self.trials_corr = 0.
    self.trials_num = 0.
    self.trials_rt = []
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
            Log(name="FLANKER_TR",
                press_time=trkp.press_time)
            self.trkp_press_time = trkp.press_time
        Wait(duration=config.INIT_TR_WAIT)
    self.start_happy = Func(clock.now).result
    self.end_happy = self.start_happy + ref.jitter(config.TIME_BETWEEN_HAPPY,
                                                   config.TIME_JITTER_HAPPY)
    # loop over blocks
    with Loop(self.f_blocks) as block:

        # put up the fixation cross
        with Parallel():
            Background = Image(source = "ocean_background.png", size = (self.exp.screen.size[0] * 1.1, 
                                                                    self.exp.screen.size[1] * 1.1),
                        allow_stretch = True, keep_ratio = False)
            fix = Label(text='+', color=config.CROSS_COLOR,
              font_size=s(config.CROSS_FONTSIZE))
        with UntilDone():

            # loop over trials
            with Loop(block.current) as trial:

                with If((Func(clock.now).result >= self.end_happy)&(happy_mid)):
                    UpdateWidget(fix, text='')
                    Wait(.3)
                    with Parallel():
                        Rectangle(blocking=False, color=(.35, .35, .35, 1.0),
                                  size=self.exp.screen.size)
                        HappyQuest(config, task='FLANKER', block_num=run_num, trial_num=trial.i)
                    self.start_happy = Func(clock.now).result
                    self.end_happy = self.start_happy + ref.jitter(config.TIME_BETWEEN_HAPPY,
                                                                   config.TIME_JITTER_HAPPY)
                    UpdateWidget(fix, text='+')

                Wait(config.ITI, jitter=.25)

                # do the trial
                ft = Trial(config, direct = trial.current["dir"],
                           center_x=self.exp.screen.center_x + trial.current['loc_x']*s(config.FROM_CENTER),
                           center_y=self.exp.screen.center_y + trial.current['loc_y']*s(config.FROM_CENTER),
                           correct_resp=trial.current['corr_resp'],
                           condition=trial.current['condition'],
                           pulse_server=pulse_server)

                self.trials_num = self.trials_num + 1.
                with If(ft.correct):
                    self.trials_corr = self.trials_corr + 1.
                with If(ft.rt == None):
                    self.trials_rt = self.trials_rt + [config.SLOW_TIME]
                with Else():
                    self.trials_rt = self.trials_rt + [ft.rt]



                # log what we need
                Log(trial.current,
                    name='FL',
                    run_num=run_num,
                    appear_time=ft.appear_time,
                    disappear_time=ft.disappear_time,
                    pressed=ft.pressed,
                    press_time=ft.press_time,
                    rt=ft.rt,
                    block=block.i,
                    trial_id=trial.i,
                    correct=ft.correct,
                    fmri_tr_time=self.trkp_press_time,
                    eeg_pulse_time=ft.eeg_pulse_time)

    Wait(1)
    HappyQuest(config, task='FLANKER', block_num=run_num, trial_num=trial.i)

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

    """self.block_score = Func(_get_score, self.trials_corr, self.trials_num,
                            self.trials_rt)
    with Parallel():
        Rectangle(width=s(config.WIDTH_SCORE_RECT),
                  height=s(config.HEIGHT_SCORE_RECT),
                  color=[144./255., 175./255., 197./255.])
        pbfbC = Label(text=Ref(str, self.block_score.result)+" Points!",
                      font_size=s(config.FINAL_FONT_SIZE))
        Label(text="Your score for this block:",
              font_size=s(config.FINAL_FONT_SIZE), bottom=pbfbC.top + s(10.))
        if config.TOUCH:
            Label(text="Press the screen to continue.",
                  font_size=s(config.FINAL_FONT_SIZE),
                  top=pbfbC.bottom - s(10.))
        else:
            Label(text="Press %s to continue." % cont_key_str,
                  font_size=s(config.FINAL_FONT_SIZE),
                  top=pbfbC.bottom - s(10.))

    with UntilDone():
        Wait(1.5)
        GetResponse(keys=config.CONT_KEY)

    Log(name="flanker_block_score",
        block_score=self.block_score)"""
    Wait(.5)


if __name__ == "__main__":
    from smile.common import Experiment
    from smile.startup import InputSubject
    from smile.lsl import init_lsl_outlet
    import config

    config.TOUCH = False
    config.EEG = False
    config.FMRI = False

    if config.EEG:
        pulse_server = init_lsl_outlet(server_name='MarkerStream',
                                       server_type='Markers',
                                       nchans=1,
                                       suggested_freq=500,
                                       channel_format='int32',
                                       unique_id='COGBATT_LSL_OUT')
    else:
        pulse_server = None
    exp = Experiment(name="FLANKERONLY",
                     background_color=((.35, .35, .35, 1.0)),
                     scale_down=True, scale_box=(1200, 900))
    # InputSubject(exp_title="Flanker")
    Wait(1.0)
    FlankerExp(config, run_num=0, lang="E",
               pulse_server=pulse_server)

    exp.run()
