# -*- coding: utf-8 -*-

# load all the states
from smile.common import *
from smile.scale import scale as s
from smile.lsl import LSLPush
import smile.ref as ref
from smile.clock import clock
from ..happy import HappyQuest


from list_gen import gen_moving_dot_trials
from math import log
from trial import Trial, GetResponse
from instruct import Instruct
# from . import version


def _get_score(config, corr_trials, num_trials, rt_trials):
    min_rt = log(config.FAST_TIME+1.0)
    max_rt = log(config.SLOW_TIME+1.0)

    acc_tf = (corr_trials/num_trials - .5)/.5
    rt_list = []
    for x in rt_trials:
        rt_list.append((max_rt - log(x + 1.0))/(max_rt - min_rt))

    # transform rts
    rts_tf = sum(rt_list)/len(rt_list)
    # calculate performance measures
    perf = acc_tf * rts_tf

    if perf < 0:
        perf = 0.

    return int(perf * 100)


@Subroutine
def RDMExp(self, config, run_num=0, lang="E", pulse_server=None, practice=False,
           happy_mid=False):

    if len(config.CONT_KEY) > 1:
        cont_key_str = str(config.CONT_KEY[0]) + " or " + \
                       str(config.CONT_KEY[-1])
    else:
        cont_key_str = str(config.CONT_KEY[0])

    res = Func(gen_moving_dot_trials, config)

    Log(name="RDMinfo")
        # version=version.__version__,
        # author=version.__author__,
        # date_time=version.__date__,
        # email=version.__email__)

    self.md_blocks = res.result

    Instruct(config, lang, practice)
    Wait(1.0)

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
            Log(name="RDM_TR",
                press_time=trkp.press_time)
            self.trkp_press_time = trkp.press_time
        Wait(duration=config.INIT_TR_WAIT)

    # HAPPY TIMING
    self.start_happy = Func(clock.now).result
    self.end_happy = self.start_happy + ref.jitter(config.TIME_BETWEEN_HAPPY,
                                                   config.TIME_JITTER_HAPPY)

    # loop over blocks
    with Loop(self.md_blocks) as block:
        with Parallel():
        # put up the fixation cross
            Background = Image(source = "./NIGHT_SKY.png", size = (self.exp.screen.size[0]*1.1, self.exp.screen.size[1]*1.1), allow_stretch = True, keep_ratio = False, blocking=False)
            Border= Ellipse(size = (s((config.RADIUS)*1.2*2),(s((config.RADIUS)*1.2*2))), color = (.55,.55,.55,1))
            Telescope = Ellipse(size = (s((config.RADIUS)*1.1*2),(s((config.RADIUS)*1.1*2))), color = (.35, .35, .35, 1.0))
            cross = Label(text='+', color=config.CROSS_COLOR,
                                  font_size=s(config.CROSS_FONTSIZE))
        with UntilDone():
            # loop over trials
            with Loop(block.current) as trial:
                with If((Func(clock.now).result >= self.end_happy) & (happy_mid)):
                    UpdateWidget(cross, text='')
                    Wait(.3)
                    with Parallel():
                        Rectangle(blocking=False, color=(.35, .35, .35, 1.0),
                                  size=self.exp.screen.size)
                        HappyQuest(task='RDM', block_num=run_num, trial_num=trial.i)
                    self.start_happy = Func(clock.now).result
                    self.end_happy = self.start_happy + ref.jitter(config.TIME_BETWEEN_HAPPY,
                                                                   config.TIME_JITTER_HAPPY)
                    UpdateWidget(cross, text='+')
                # Wait the ISI
                Wait(config.ISI, jitter=config.JITTER)
                # do the trial
                mdt = Trial(cross,
                            config,
                            correct_resp=trial.current['correct_resp'],
                            incorrect_resp=trial.current['incorrect_resp'],
                            num_dots=config.NUM_DOTS,
                            right_coherence=trial.current['right_coherence'],
                            left_coherence=trial.current['left_coherence'],
                            pulse_server=pulse_server)

                self.cor = [trial.current['left_coherence'],
                            trial.current['right_coherence']]
                self.trials_num = self.trials_num + 1.

                with If(self.cor[0] != self.cor[1]):
                    with If(mdt.correct):
                        # If they got it right, add 1 to
                        # the final total correct
                        self.trials_corr = self.trials_corr + 1.
                with Else():
                    # Add .5 for chance performance on all equal coherence
                    # trials
                    self.trials_corr = self.trials_corr + .5

                with If(mdt.rt == None):
                    self.trials_rt = self.trials_rt + [config.SLOW_TIME]
                with Else():
                    self.trials_rt = self.trials_rt + [mdt.rt]

                # log what we need
                Log(trial.current,
                    name='rdm',
                    run_num=run_num,
                    appear_time=mdt.appear_time,
                    disappear_time=mdt.disappear_time,
                    pressed=mdt.pressed,
                    press_time=mdt.press_time,
                    rt=mdt.rt,
                    block=block.i,
                    trial_id=trial.i,
                    correct=mdt.correct,
                    refresh_rate=mdt.refresh_rate,
                    fmri_tr_time=self.trkp_press_time,
                    eeg_pulse_time=mdt.eeg_pulse_time)
    Wait(.5)
    HappyQuest(task='RDM', block_num=run_num, trial_num=trial.i)
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

    """self.block_score = Func(_get_score, config, self.trials_corr,
                            self.trials_num, self.trials_rt)
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
            Label(text="Press %s to continue." % (cont_key_str),
                  font_size=s(config.FINAL_FONT_SIZE),
                  top=pbfbC.bottom - s(10.))

    with UntilDone():
        Wait(1.5)
        GetResponse(keys=config.CONT_KEY)

    Log(name="moving_dots_block_score",
        block_score=self.block_score)
    Wait(.5)"""


if __name__ == "__main__":
    import config
    from smile.startup import InputSubject
    from smile.common import Experiment
    from smile.lsl import init_lsl_outlet

    config.FMRI = False
    config.EEG = True
    if config.EEG:
        pulse_server = init_lsl_outlet(server_name='MarkerStream',
                                       server_type='Markers',
                                       nchans=1,
                                       suggested_freq=500,
                                       channel_format='int32',
                                       unique_id='COGBATT_LSL_OUT')
    else:
        pulse_server = None

    exp = Experiment(background_color=(.35, .35, .35, 1.0),
                     name="RDMExp", scale_down=True, scale_box=(1200, 900))

    RDMExp(config, run_num=0, lang="E",
           pulse_server=pulse_server, practice=True)

    exp.run()
