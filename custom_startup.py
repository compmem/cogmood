from smile.common import Experiment, Log, Wait, Func, UntilDone, \
    Label, Loop, If, Elif, Else, KeyPress, Ref, \
    Parallel, Slider, Serial, UpdateWidget, Debug, Meanwhile, While, Subroutine
from smile.video import Rectangle, TextInput, Button, ButtonPress
from smile.mouse import MouseCursor
from smile.startup import (
    INFO_WIDTH,
    INFO_HEIGHT,
    INFO_OUTLINE_COLOR,
    INFO_COLOR,
    INFO_FONT_SIZE,
    INFO_BUTTON_HEIGHT,
    INFO_BUTTON_WIDTH,
    TEXT_INPUT_WIDTH,
    TEXT_INPUT_HEIGHT
)
from smile.scale import scale as s
from hashlib import blake2b

import config as CogBatt_config

def _validate_code(exp):
    worker_id = exp._subject
    code = exp.get_var('_code')
    expected_code = blake2b(worker_id.encode(), digest_size=4, salt=CogBatt_config.API_SALT.encode()).hexdigest()[:4]
    exp.set_var('code_invalid', code != expected_code)

@Subroutine
def InputSubject(self):
    with Serial():
        # Present initial CogBatt instructions.
        Label(text="Welcome to the Mood and Cognition Tasks!"
                   "\n\nYou may press 'Shift' + 'Esc' to exit at any time. "
                   "Though your progress will only be saved at the end of each task."
                   "\n\nPress any button to continue.",
              font_size=s(CogBatt_config.INST_FONT),
              text_size=(s(700), None))
        with UntilDone():
            KeyPress()
        with Parallel():
            with Parallel(blocking=False):
                MouseCursor()
                recOut = Rectangle(width=s(INFO_WIDTH) + s(20),
                                   height=s(INFO_HEIGHT) + s(20),
                                   color=INFO_OUTLINE_COLOR)
                recin = Rectangle(width=s(INFO_WIDTH),
                                  height=s(INFO_HEIGHT),
                                  color=INFO_COLOR)
                lbl = Label(text="Mood and Cognition Tasks", center_x=recin.center_x,
                            top=recin.top - s(10),
                            font_size=s(INFO_FONT_SIZE))
                idIn = TextInput(width=s(TEXT_INPUT_WIDTH),
                                 height=s(TEXT_INPUT_HEIGHT),
                                 font_size=s(INFO_FONT_SIZE),
                                 center_x=recin.center_x,
                                 top=lbl.bottom - s(20),
                                 multiline=False,
                                 text="",
                                 disabled=False,
                                 hint_text="Prolific Worker ID",
                                 write_tab=False)
                codeIn = TextInput(width=s(TEXT_INPUT_WIDTH),
                                   height=s(TEXT_INPUT_HEIGHT),
                                   font_size=s(INFO_FONT_SIZE),
                                   center_x=recin.center_x,
                                   top=lbl.bottom - s(80),
                                   multiline=False,
                                   text="",
                                   disabled=False,
                                   hint_text="4 digit task code",
                                   write_tab=False)
                bc = Button(text="Continue", font_size=s(INFO_FONT_SIZE),
                            height=s(INFO_BUTTON_HEIGHT),
                            width=s(INFO_BUTTON_WIDTH),
                            right=recin.right - s(20),
                            bottom=recin.bottom + s(20),
                            name="C",
                            background_normal="",
                            background_color=INFO_OUTLINE_COLOR,
                            disabled=True)
                esc_lbl = Label(text="Press shift + escape if you need to exit this screen.", center_x=recin.center_x,
                            top=recin.bootom - s(10),
                            font_size=s(INFO_FONT_SIZE))
            with Serial():
                with While(
                        (Ref.object(codeIn.text).__len__() < 4)
                        or (Ref(str, idIn.text) == '')
                ):
                    Wait(0.1)
                bc.disabled = False

                bp = ButtonPress(buttons=[bc])
                with If(
                        (bp.pressed == "C")
                ):
                    Func(self.exp._change_smile_subj, Ref.object(idIn.text).lower().strip())
                    Func(self.exp.set_var, '_code', Ref.object(codeIn.text).lower().strip())
                    Func(_validate_code, Ref.object(self.exp))
