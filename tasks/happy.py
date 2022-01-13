from smile.common import *
from smile.scale import scale as s


@Subroutine
def HappyQuest(self, config):
    with Parallel():
        Label(text="How happy are you at this moment?\nPress F to move left, Press J to move right.",
              font_size=s(config.INST_FONT_SIZE),
              halign='center',
              center_y=exp.screen.center_y + s(300))
        sld = Slider(min=-10, max=10, value=0, width=s(config.SLIDER_WIDTH))
        Label(text="unhappy", font_size=s(config.INST_FONT_SIZE),
              center_x=sld.left, center_y=sld.center_y - s(100))
        Label(text="happy", font_size=s(config.INST_FONT_SIZE),
              center_x=sld.right, center_y=sld.center_y - s(100))
        Label(text='Press Spacebar to lock-in your response.',
              top=sld.bottom - s(250), font_size=s(config.INST_FONT_SIZE))

    with UntilDone():
        with Loop():
            ans = KeyPress(keys=config.RESP_KEYS)
            with If(ans.pressed == config.RESP_KEYS[0]):
                with If(sld.value - config.HAPPY_SPEED <= -10):
                    UpdateWidget(sld, value=-10)
                with Else():
                    UpdateWidget(sld, value=sld.value - config.HAPPY_SPEED)
            with Elif(ans.pressed == config.RESP_KEYS[1]):
                with If(sld.value + config.HAPPY_SPEED >= 10):
                    UpdateWidget(sld, value=10)
                with Else():
                    UpdateWidget(sld, value=sld.value + config.HAPPY_SPEED)
            Wait(.05)
        with UntilDone():
            KeyPress(keys=['SPACEBAR'])
    Log(name="happy",
        value=sld.value)



if __name__ == "__main__":
    import config

    exp = Experiment()

    HappyQuest(config)

    exp.run()
