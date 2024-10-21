from smile.common import Subroutine, StackLayout, Label, \
    UntilDone, KeyPress


@Subroutine
def error_screen(self, error, message):
    with StackLayout(blocking=True):
        Label(name="error_details",
              text=error)
        Label(name="error_message",
              text=message)
        Label(name="error_exit_instructions",
              text="Press escape to exit.")
    with UntilDone():
        KeyPress(keys=['ESCAPE'])
