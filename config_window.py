from smile.common import *
from smile.scale import scale as s


@Subroutine
def FrameTest(self,
              config,
              num_flips=500,
              to_skip=5,
              ):

    self.tot_flips = num_flips + to_skip
    self.diff_sum = 0.0
    self.last_flip = 0

    with Parallel():
        # BlockingFlips()
        config_window = Rectangle(height=s(config.INFO_HEIGHT) + s(20),
                                  width=s(config.INFO_WIDTH) + s(20),
                                  color=config.INFO_OUTLINE_COLOR)
        recin = Rectangle(height=s(config.INFO_HEIGHT),
                          width=s(config.INFO_WIDTH),
                          color=[144./255.,175./255.,197./255.],
                          center_y=config_window.center_y)
        pb = ProgressBar(max=self.tot_flips, width=config_window.width*2/3,
                         height=s(50),
                         center_y=recin.center_y, center_x=recin.center_x)
        lbl = Label(text='???', top=pb.bottom, font_size=s(config.INFO_FONT_SIZE),
                    center_x=recin.center_x)
    with UntilDone():
        with Loop(self.tot_flips) as loop:
            # skip the first 5
            with Parallel():
                uw = UpdateWidget(pb, value=loop.i+1)
                with If(self.diff_sum > 0.0):
                    UpdateWidget(lbl,
                                 text=Ref('{:5.2f}'.format,
                                          (loop.i-to_skip)/self.diff_sum))
            with If(loop.i >= to_skip):
                self.diff_sum = self.diff_sum + \
                                (uw.appear_time['time'] - self.last_flip)
            self.last_flip = uw.appear_time['time']
            ResetClock(self.last_flip)
    self.framerate = lbl.text


@Subroutine
def ConfigWindow(self, config, params):
    self.params = params
    self.canceled = True
    self.keep_looping = True
    self.lock_state = Ref.cond(self.params["locked"], "down", "normal")
    self.frameText = Ref(str, self.params['frame_rate'])

    with Loop(conditional=self.keep_looping):
        with Parallel():
            with If(self._exp._platform != "android"):
                MouseCursor()
            config_window = Rectangle(height=s(config.INFO_HEIGHT) + s(20),
                                      width=s(config.INFO_WIDTH) + s(20),
                                      color=config.INFO_OUTLINE_COLOR)
            recin = Rectangle(height=s(config.INFO_HEIGHT),
                              width=s(config.INFO_WIDTH),
                              color=config.INFO_COLOR,
                              center_y=config_window.center_y)
            title = Label(text="SMILE Settings",
                          font_size=s(config.INFO_FONT_SIZE),
                          top=config_window.top - s(50))

            # SUBJECT ID LOCK

            lRec = Rectangle(color="GRAY",
                             left=recin.left + s(20),
                             top=title.bottom - s(40),
                             height=s(config.CHECK_HEIGHT),
                             width=s(config.CHECK_WIDTH))
            cb_l = CheckBox(name="tog_lock", state=self.lock_state,
                            center_y=lRec.center_y,
                            center_x=lRec.center_x,
                            height=s(config.CHECK_HEIGHT),
                            width=s(config.CHECK_WIDTH),
                            allow_stretch=True, keep_ratio=False)
            lbl_lock = Label(text="Lock the Subject ID",
                             center_y=lRec.center_y,
                             left=lRec.right + s(50),
                             font_size=s(config.INFO_FONT_SIZE))

            timeInput = TextInput(text=self.frameText,
                                  font_size=s(config.INFO_FONT_SIZE),
                                  width=s(config.TEXT_INPUT_WIDTH)/3.,
                                  height=s(config.TEXT_INPUT_HEIGHT),
                                  left=recin.left + s(20),
                                  top=lRec.bottom - s(40),
                                  multiline=False)
            timeLabel = Label(text="Framerate",
                              center_y=timeInput.center_y,
                              left=timeInput.right + s(10),
                              font_size=s(config.INFO_FONT_SIZE))
            timing_button = Button(name="timing", text="Test",
                                   font_size=s(config.INFO_FONT_SIZE),
                                   height=s(config.INFO_BUTTON_HEIGHT),
                                   width=s(config.INFO_BUTTON_WIDTH),
                                   background_color=config.INFO_OUTLINE_COLOR,
                                   background_normal="",
                                   center_y=timeLabel.center_y,
                                   left=timeLabel.right + s(20))

            # CONTINUE BUTTONS
            cancel_button = Button(text="Cancel", name="cancel",
                                   bottom=recin.bottom + s(20),
                                   left=recin.left + s(20),
                                   height=s(config.INFO_BUTTON_HEIGHT),
                                   width=s(config.INFO_BUTTON_WIDTH),
                                   font_size=s(config.INFO_FONT_SIZE),
                                   background_color=config.INFO_OUTLINE_COLOR,
                                   background_normal="")
            app_button = Button(text="Apply", name="apply",
                                bottom=recin.bottom + s(20),
                                right=recin.right - s(20),
                                font_size=s(config.INFO_FONT_SIZE),
                                height=s(config.INFO_BUTTON_HEIGHT),
                                width=s(config.INFO_BUTTON_WIDTH),
                                background_color=config.INFO_OUTLINE_COLOR,
                                background_normal="")

        with UntilDone():
            bp = ButtonPress(buttons=[cancel_button,
                                      app_button,
                                      timing_button])

        with If(bp.pressed == "apply"):
            self.locked = Ref.cond(cb_l.state == "down", 1, 0)
            self._exp.flip_interval = 1./Ref(float, timeInput.text)
            self.framerate = Ref(float, timeInput.text)
            self.canceled = False
            self.keep_looping = False
        with Elif(bp.pressed == "timing"):
            ft = FrameTest(config)
            self.frameText = ft.framerate
        with Else():
            self.keep_looping = False
