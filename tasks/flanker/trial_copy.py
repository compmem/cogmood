from smile.common import *
from smile.scale import scale as s
from smile.lsl import LSLPush
from flanker import Flanker
from list_gen import gen_fblocks
import config


@Subroutine
def GetResponse(self,
                keys,
                base_time=None,
                correct_resp=None,
                duration=None):
    self.pressed = None
    self.rt = None
    self.correct = None
    self.press_time = None
    with Parallel():
        kp = KeyPress(base_time=base_time,
                      keys=keys,
                      correct_resp=correct_resp,
                      duration=duration,
                      blocking=False)
        with Serial(blocking=False):
            with ButtonPress(correct_resp=correct_resp,
                             base_time=base_time,
                             duration=duration,
                             ) as bp:
                Button(width=self.exp.screen.width*.45,
                       height=self.exp.screen.height,
                       name=keys[0], text="",
                       left=0, bottom=0, background_color=(0, 0, 0, 0))
                Button(width=self.exp.screen.width*.45, height=self.exp.screen.height,
                       name=keys[-1], text="", right=self.exp.screen.width,
                       bottom=0, background_color=(0, 0, 0, 0))

    self.pressed = Ref.cond((bp.pressed == ''), kp.pressed, bp.pressed)
    self.rt = Ref.cond((bp.pressed == ''), kp.rt, bp.rt)
    self.correct = Ref.cond((bp.pressed == ''), kp.correct, bp.correct)
    self.press_time = Ref.cond((bp.pressed == ''), kp.press_time, bp.press_time)


@Subroutine
def Trial(self,
          config,
          direct,
          center_x,
          center_y,
          condition,
          correct_resp=None,
          color='white',
          pulse_server=None,
          background = True):

    self.eeg_pulse_time = None
    # present the dots
    fl = Flanker(config, center_x= center_x, center_y = center_y, direction = direct, condition = condition, layers = config.LAYERS,
                 background = background)

    with UntilDone():
        # Collect key response
        Wait(until=fl.stim_appear_time)
        if config.EEG:
            pulse_fn = LSLPush(server=pulse_server,
                               val=Ref.getitem(config.EEG_CODES, condition))
            Log(name="FLKR_PULSES",
                start_time=pulse_fn.push_time)
            self.eeg_pulse_time = pulse_fn.push_time
        gr = GetResponse(correct_resp=correct_resp,
                         base_time=fl.stim_appear_time["time"],
                         duration=config.RESPONSE_DURATION,
                         keys=config.RESP_KEYS)

    self.pressed = gr.pressed
    self.press_time = gr.press_time
    self.rt = gr.rt
    self.correct = gr.correct

    # save vars
    self.appear_time = fl.stim_appear_time
    self.disappear_time = fl.stim_disappear_time

# blocks = gen_fblocks(config)
# print(blocks)


# exp = Experiment()
# blocks = Func(gen_fblocks,config)
# res = blocks.result
# with Loop(res) as block:
#     with Loop(block.current) as trial:
#         Trial(config, direct = trial.current["dir"],
#                            center_x=exp.screen.center_x + trial.current['loc_x']*s(config.FROM_CENTER),
#                            center_y=exp.screen.center_y + trial.current['loc_y']*s(config.FROM_CENTER),
#                            correct_resp=trial.current['corr_resp'],
#                            condition=trial.current['condition'])
# exp.run()