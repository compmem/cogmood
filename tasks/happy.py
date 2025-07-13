import random
from smile.common import *
from smile.scale import scale as s
from smile.clock import clock
from . import happy_config as default_happy_config

def make_trials(config):
    temp_moods = [mm for mm in config.MOODS]
    random.shuffle(temp_moods)
    trials = []
    for mm in temp_moods:
        trial = dict(
            inst=f"How {mm['mood']} are you at this moment?\nPress F to move left, Press J to move right.",
            mood=mm['mood'].title(),
            notmood=mm['notmood'].title()
        )
        trials.append(trial)
    return trials

@Subroutine
def HappyQuest(self, task, block_num, trial_num, config=default_happy_config):
    # gen = Func(
    #     make_trials,
    #     config
    # )
    # trials = gen.result

    trials = make_trials(config)

    with UntilDone():

        with Loop(trials) as trial:
            Wait(0.3)
            with Parallel():
                Label(text=trial.current['inst'],
                      font_size=s(config.HAPPY_FONT_SIZE),
                      halign='center',
                      center_y=self.exp.screen.center_y + s(300))
                sld = Slider(min=-10, max=10, value=0, width=s(config.SLIDER_WIDTH))
                Label(text=trial.current['notmood'], font_size=s(config.HAPPY_FONT_SIZE),
                      center_x=sld.left, center_y=sld.center_y - s(100))
                Label(text=trial.current['mood'], font_size=s(config.HAPPY_FONT_SIZE),
                      center_x=sld.right, center_y=sld.center_y - s(100))
                Label(text='Press Spacebar to lock-in your response.',
                      top=sld.bottom - s(250), font_size=s(config.HAPPY_FONT_SIZE))

            with UntilDone():
                self.happy_start_time = Ref(clock.now)
                self.last_check = self.happy_start_time
                self.happy_dur = 0.0
                self.happy_speed = config.HAPPY_INC_BASE
                self.first_press_time = None
                with Loop():
                    ans = KeyPress(keys=config.RESP_HAPPY)
                    with If(self.first_press_time == None):
                        self.first_press_time = ans.press_time
                    with If(ans.press_time['time'] - self.last_check <
                            config.NON_PRESS_INT):
                        self.happy_speed = (config.HAPPY_INC_BASE * (Ref(clock.now) -
                                            self.happy_start_time) * config.HAPPY_MOD) + config.HAPPY_INC_START
                    with Else():
                        self.happy_speed = config.HAPPY_INC_START
                        self.happy_start_time = Ref(clock.now)
                    self.last_check = Ref(clock.now)
                    with If(ans.pressed == config.RESP_HAPPY[0]):
                        with If(sld.value - self.happy_speed <= (-1*config.HAPPY_RANGE)):
                            UpdateWidget(sld, value=(-1*config.HAPPY_RANGE))
                        with Else():
                            UpdateWidget(sld, value=sld.value - self.happy_speed)
                    with Elif(ans.pressed == config.RESP_HAPPY[1]):
                        with If(sld.value + self.happy_speed >= config.HAPPY_RANGE):
                            UpdateWidget(sld, value=config.HAPPY_RANGE)
                        with Else():
                            UpdateWidget(sld, value=sld.value + self.happy_speed)
                with UntilDone():
                    submit = KeyPress(keys=['SPACEBAR'])
            Log(name="happy",
                task=task,
                mood=trial.current['mood'],
                block_num=block_num,
                trial_num=trial_num,
                slider_appear=sld.appear_time,
                first_press=self.first_press_time,
                submit_time=submit.press_time,
                value=sld.value)


if __name__ == "__main__":
    import config

    exp = Experiment()

    HappyQuest(task='test', block_num=0, trial_num=0)
    HappyQuest(task='test', block_num=0, trial_num=1)

    exp.run()
