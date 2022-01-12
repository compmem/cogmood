from smile.video import WidgetState

from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, StringProperty
from kivy.graphics import Point, Color, Line
from math import cos, sin, sqrt, pi
import random


@WidgetState.wrap
class Flanker(Widget):
    """Display a Flanker stimulus anywhere, any color, any shape, any contents!

    Parameters
    ----------
    stim : string
        A string that makes up the matrix that is the desplayed flanker stimulus.
        The stimulus has to be a rectangle, where every row is puncuated by an
        end line character *\\n*. SAMPLE : \"<___>\\n_<_>_\\n<<_>>\\n_<_>_\\n<___>\\n\"
    sep : integer
        Seperation between each flanker arrow
    df : integer
        Difference between the center of a flanker arrow and the middle of the
        top line of the arrow/bottom line of the arrow. The length of each line
        is calculated by sqrt(8)*df.
    line_width : integer
        Width of each line.
    color : tuple or string
        Color of the stimulus


    """
    color = ListProperty([1, 1, 1, 1])
    stim = StringProperty("<<><<")
    box = NumericProperty(50)
    around = NumericProperty(10)
    #df = NumericProperty(2)
    line_width = NumericProperty(2)

    def __init__(self, **kwargs):
        super(type(self), self).__init__(**kwargs)

        self._color = self.color
        self._stim = self.stim
        self._box = self.box

        self._around = self.around
        self._line_width = self.line_width

        self.bind(color=self._update_color,
                  stim=self._update_stim,
                  around=self._update_around,
                  line_width=self._update_line_width,
                  box=self._update_box)
        self._update_stim()


    def _update_color(self, *pargs):
        self._color.rgba = self.color

    def _update_box(self, *pargs):
        self._box = self.box
        self._update_stim()

    def _update_around(self, *pargs):
        self._around = self.around
        self._update_stim()

    def _update_line_width(self, *pargs):
        self._line_width = self.line_width

    def _update_stim(self, *pargs):
        self._stim = self.stim

        self._ncols = self._stim.find("\n")
        self._nrows = len(self._stim.split("\n")) - 1
        self._X0 = self.center_x
        self._Y0 = self.center_y

        self._IH = self._box - self._around
        self._IW = self._box - self._around
        self._height = (self._nrows - 1)*self._box
        self._width = (self._ncols - 1)*self._box
        self._top_row = self._Y0 + self._height/2.
        self._left_col = self._X0 - self._width/2.

        self._update()


    def _update(self, *pargs):
        # draw the flanks
        row_num = 0.
        col_num = 0.
        self.canvas.clear()
        with self.canvas:
            # set the color
            self._color = Color(*self.color)
            for i in self._stim:
                # Blank area of the stimulus
                if i == "_":
                    col_num += 1.
                # Go to the next row of the stimulus, start at first column
                elif i == "\n":
                    row_num += 1.
                    col_num = 0.
                # Left or right arrow of the stimulus
                elif (i == "<") or (i == ">"):
                    Xi = self._left_col + col_num*self._box
                    Yi = self._top_row - row_num*self._box
                    if i == "<":
                        Line(points=[Xi + .5*self._IW,
                                     Yi - .5*self._IH,
                                     Xi - .5*self._IW,
                                     Yi,
                                     Xi + .5*self._IW,
                                     Yi + .5*self._IH],
                                     cap="square", width=self._line_width)

                    else:
                        Line(points=[Xi - .5*self._IW,
                                     Yi + .5*self._IH,
                                     Xi + .5*self._IW,
                                     Yi,
                                     Xi - .5*self._IW,
                                     Yi - .5*self._IH],
                                     cap="square", width=self._line_width)

                    # Go to next column
                    col_num += 1.
