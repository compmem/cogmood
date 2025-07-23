from smile.common import Subroutine, BoxLayout, Label, scale
from config import SSI_FONT_SIZE

@Subroutine
def error_screen(self, error, message):
    with BoxLayout(orientation='vertical', spacing=20, pos=[self.exp.screen.width/2, self.exp.screen.height/4]):
        Label(name="error_details",
              text=error,
              text_size=(scale(700), None), font_size=scale(SSI_FONT_SIZE),
              size_hint=(1, None),
              valign='middle',
              halign='center')
        Label(name="error_message",
              text=message,
              text_size=(scale(700), None), font_size=scale(SSI_FONT_SIZE),
              size_hint=(1, None),
              valign='middle',
              halign='center')
        Label(name="error_exit_instructions",
              text="Press escape to exit.",
              text_size=(scale(700), None), font_size=scale(SSI_FONT_SIZE),
              size_hint=(1, None),
              valign='middle',
              halign='center')
