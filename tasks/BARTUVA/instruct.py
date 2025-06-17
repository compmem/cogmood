# -*- coding: utf-8 -*-
from smile.common import *
from smile.scale import scale as s
from .inst.computer import computer_list
from .inst.mobile import mobile_list

from .list_gen import add_air
from .trial import BARTSub, GetResponse

import os

def get_is_first(run_num):
    return run_num == 0

def get_practice_inst(config, run_num):
    if len(config.CONT_KEY) > 1:
        cont_key_str = str(config.CONT_KEY[0]) + " or " + str(config.CONT_KEY[-1])
    else:
        cont_key_str = str(config.CONT_KEY[0])
    practice_inst = "You will now have a short practice bag of balloons.\n " \
                    "Please note how the money in the bank drops until you" \
                    " make a decision.\nPress %s to continue." % (cont_key_str)
    if run_num > 0:
        practice_inst += "\n You may press the button in the lower right " \
                         f"corner to skip the practice."

    return practice_inst
@Subroutine
def Instruct(self, config, run_num, sub_dir, task_dir=None,
             full_instructions=True, practice=True, lang="E", flip_resp=False):
    is_first = Func(get_is_first, run_num).result

    if len(config.CONT_KEY) > 1:
        cont_key_str = str(config.CONT_KEY[0]) + " or " + str(config.CONT_KEY[-1])
    else:
        cont_key_str = str(config.CONT_KEY[0])

    if flip_resp:
        pos = -1
        resp_keys = [config.RESP_KEYS[1], config.RESP_KEYS[0]]
        key_text = resp_keys
        inst_img_path = config.FLIPPED_INST2_IMG_PATH
    else:
        pos = 1
        key_text = config.KEY_TEXT
        resp_keys = config.RESP_KEYS
        inst_img_path = config.INST2_IMG_PATH

    practice_inst = Func(get_practice_inst, config, run_num).result
    if config.TOUCH:
        with Loop(computer_list) as instruction:
            txt = instruction.current
            with Parallel():
                with If((instruction.i==3)):
                    Label(text=txt%(config.TOUCH_INST[0],
                                    config.TOUCH_INST[-1]),
                          halign='left',
                          font_size=s(config.LABEL_FONT_SIZE))
                with Elif((instruction.i==7)):
                    Label(text=txt%(config.NUM_BALLOONS),
                          halign='left',
                          font_size=s(config.LABEL_FONT_SIZE))
                with Elif((instruction.i==8)):
                    Label(text=txt%(config.NUM_BAGS,
                                    config.BALLOONS_PER_BAG),
                          halign='left',
                          font_size=s(config.LABEL_FONT_SIZE))
                with Else():
                    Label(text=txt,
                          halign='left',
                          font_size=s(config.LABEL_FONT_SIZE))
                Label(text='Press %s to continue'%(config.CONT_KEY_STR),
                      halign='left',
                      bottom=(self.exp.screen.center_x,0),
                      font_size=s(config.LABEL_FONT_SIZE))
            with UntilDone():
                Wait(.5)
                GetResponse(keys=config.CONT_KEY)

    else:
        with If(is_first):
            with Parallel():
                MouseCursor(blocking=False)
                with Serial(blocking=True):
                    with If(full_instructions):
                        with Loop(computer_list) as instruction:
                            txt = instruction.current
                            with Parallel():
                                with If((instruction.i==2)):
                                    with Parallel():
                                        img2 = Image(source=inst_img_path,
                                                     bottom=(self.exp.screen.height/2.) + s(50),
                                                     keep_ratio=True, allow_stretch=True,
                                                     height=s(400))
                                        lbl2 = Label(text=txt%(key_text[0],
                                                               key_text[-1]),
                                                     halign='left', top=img2.bottom-s(10),
                                                     font_size=s(config.LABEL_FONT_SIZE))
                                        Label(text='Press %s to continue'%(config.CONT_KEY_STR),
                                              halign='left',
                                              top=lbl2.bottom,
                                              font_size=s(config.LABEL_FONT_SIZE))
                                with Else():
                                    with Parallel():
                                        lbl1 = Label(text=txt,
                                                     halign='left',
                                                     font_size=s(config.LABEL_FONT_SIZE))
                                        Label(text='Press %s to continue'%(config.CONT_KEY_STR),
                                              halign='left',
                                              top=lbl1.bottom - s(75),
                                              font_size=s(config.LABEL_FONT_SIZE))
                            with UntilDone():
                                Wait(.5)
                                GetResponse(keys=config.CONT_KEY)

                    with If(practice):

                        Label(text=practice_inst,
                              halign='center',
                              font_size=s(config.LABEL_FONT_SIZE))
                        with UntilDone():
                            Wait(.5)
                            GetResponse(keys=config.CONT_KEY)

                        number_of_sets = 1
                        self.set_number = 0
                        self.grand_total = config.GRAND_TOTAL
                        self.balloon_number_session = 0
                        self.trkp_press_time = None

                        Wait(1.)
                        # Loop over practice blocks
                        with Loop(number_of_sets):
                            Wait(.5, jitter=.5)

                            # Calling listgen as 'bags'
                            bg = Func(add_air,
                                      total_number_of_balloons=len(config.PRACTICE_SETUP) * 2,
                                      num_ranges=len(config.PRACTICE_SETUP),
                                      balloon_setup=config.PRACTICE_SETUP,
                                      randomize=config.RANDOMIZE_BALLOON_NUM,
                                      reward_low=config.REWARD_LOW,
                                      reward_high=config.REWARD_HIGH,
                                      subject_directory=sub_dir,
                                      practice=True,
                                      shuffle_bags=config.SHUFFLE_BAGS)
                            bags = bg.result
                            self.block_tic = 0

                            # with Loop(bag.current) as balloon:
                            with Loop(bags) as balloon:
                                Balloon = BARTSub(config,
                                                  log_name='bart_practice',
                                                  balloon=balloon.current,
                                                  block=self.block_tic,
                                                  set_number=self.set_number,
                                                  grand_total=self.grand_total,
                                                  balloon_number_session=self.balloon_number_session,
                                                  subject=self._exp.subject,
                                                  run_num=run_num,
                                                  trkp_press_time=self.trkp_press_time,
                                                  flip_resp=flip_resp)
                                self.balloon_number_session += 1
                                self.grand_total = Balloon.grand_total
                            self.block_tic += 1

                            self.set_number += 1

                        Wait(.5)
                        Label(text='You have completed the practice.\n' +
                                   'Press %s to continue.' % (cont_key_str),
                              halign='center',
                              font_size=s(config.LABEL_FONT_SIZE))
                        with UntilDone():
                            Wait(0.5)
                            GetResponse(keys=config.CONT_KEY)

        with Else():
            with Parallel():
                MouseCursor(blocking=False)
                with Serial(blocking=False):
                    with If(full_instructions):
                        with Loop(computer_list) as instruction:
                            txt = instruction.current
                            with Parallel():
                                with If((instruction.i == 2)):
                                    with Parallel():
                                        img2 = Image(source=inst_img_path,
                                                     bottom=(self.exp.screen.height / 2.) + s(50),
                                                     keep_ratio=True, allow_stretch=True,
                                                     height=s(400))
                                        lbl2 = Label(text=txt % (key_text[0],
                                                                 key_text[-1]),
                                                     halign='left', top=img2.bottom - s(10),
                                                     font_size=s(config.LABEL_FONT_SIZE))
                                        Label(text='Press %s to continue' % (config.CONT_KEY_STR),
                                              halign='left',
                                              top=lbl2.bottom,
                                              font_size=s(config.LABEL_FONT_SIZE))
                                with Else():
                                    with Parallel():
                                        lbl1 = Label(text=txt,
                                                     halign='left',
                                                     font_size=s(config.LABEL_FONT_SIZE))
                                        Label(text='Press %s to continue' % (config.CONT_KEY_STR),
                                              halign='left',
                                              top=lbl1.bottom - s(75),
                                              font_size=s(config.LABEL_FONT_SIZE))
                            with UntilDone():
                                Wait(.5)
                                GetResponse(keys=config.CONT_KEY)

                    with If(practice):
                        Label(text=practice_inst,
                              halign='center',
                              font_size=s(config.LABEL_FONT_SIZE))
                        with UntilDone():
                            Wait(.5)
                            GetResponse(keys=config.CONT_KEY)

                        number_of_sets = 1
                        self.set_number = 0
                        self.grand_total = config.GRAND_TOTAL
                        self.balloon_number_session = 0
                        self.trkp_press_time = None

                        Wait(1.)
                        # Loop over practice blocks
                        with Loop(number_of_sets):
                            Wait(.5, jitter=.5)

                            # Calling listgen as 'bags'
                            bg = Func(add_air,
                                      total_number_of_balloons=len(config.PRACTICE_SETUP) * 2,
                                      num_ranges=len(config.PRACTICE_SETUP),
                                      balloon_setup=config.PRACTICE_SETUP,
                                      randomize=config.RANDOMIZE_BALLOON_NUM,
                                      reward_low=config.REWARD_LOW,
                                      reward_high=config.REWARD_HIGH,
                                      subject_directory=sub_dir,
                                      practice=True,
                                      shuffle_bags=config.SHUFFLE_BAGS)
                            bags = bg.result
                            self.block_tic = 0

                            # with Loop(bag.current) as balloon:
                            with Loop(bags) as balloon:
                                Balloon = BARTSub(config,
                                                  log_name='bart_practice',
                                                  balloon=balloon.current,
                                                  block=self.block_tic,
                                                  set_number=self.set_number,
                                                  grand_total=self.grand_total,
                                                  balloon_number_session=self.balloon_number_session,
                                                  subject=self._exp.subject,
                                                  run_num=run_num,
                                                  trkp_press_time=self.trkp_press_time,
                                                  flip_resp=flip_resp)
                                self.balloon_number_session += 1
                                self.grand_total = Balloon.grand_total
                            self.block_tic += 1

                            self.set_number += 1

                        Wait(.5)
                        Label(text='You have completed the practice.\n' +
                                   'Press %s to continue.' % (cont_key_str),
                              halign='center',
                              font_size=s(config.LABEL_FONT_SIZE))
                        with UntilDone():
                            Wait(0.5)
                            GetResponse(keys=config.CONT_KEY)
                with Serial(blocking=False):
                    with ButtonPress():
                        Button(text="Skip Practice", width=s(config.SKIP_SIZE[0]),
                               bottom=0, right=self.exp.screen.width,
                               height=s(config.SKIP_SIZE[1]),
                               font_size=s(config.SKIP_FONT_SIZE))
