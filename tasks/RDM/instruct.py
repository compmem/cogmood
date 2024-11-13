# -*- coding: utf-8 -*-

from smile.common import *
from smile.scale import scale as s

from .trial import Trial, GetResponse
from .list_gen import gen_practice_trials


# Text for instructions
top_text = {'E':'You are an astronaut and your goal is to determine the direction that\n' +
                '[i]MOST[/i] of the satellites are moving through the sky.\n' +
                'Please respond quickly and accurately.',
            'S':'Su objetivo es determinar la dirección que la\n' +
                '[b]MAYORÍA[/b] de los puntos se están moviendo.\n' +
                'Por favor responda con rapidez y precisión.',
            'P':'Seu objetivo é determinar a direção em que' +
                '[b]A MAIOR PARTE[/b] dos pontos está se movendo.' +
                'Por favor responda rápida e diretamente.'}

def bottom_text(config, left=True, lang="E"):
    if config.TOUCH:
        if not left:
            if lang == "E":
                value_str = 'Press the [b]RIGHT SIDE OF THE SCREEN[/b] if ' + \
                            'the [b]DIRECTION OF THE DOTS[/b] is ' + \
                            '[b]TO THE RIGHT[/b]'
            elif lang == "S":
                value_str = 'Presione el [b]LADO DERECHO DE LA PANTALLA[/b] ' + \
                            ' si la [b]DIRECCIÓN DE LOS PUNTOS[/b] está ' + \
                            'a [b]LA DERECHA[/b].'
            elif lang == "P":
                value_str = 'Pressione [b]O LADO DIREITO DA TELA[/b] se a ' + \
                            '[b]DIREÇÃO DOS PONTOS[/b] for a ' + \
                            '[b]DA DIREITA[/b].'


        else:
            if lang == "E":
                value_str = 'Press the [b]LEFT SIDE OF THE SCREEN[/b] if ' + \
                            'the [b]DIRECTION OF THE DOTS[/b] is ' + \
                            '[b]TO THE LEFT[/b]'
            elif lang == "S":
                value_str = 'Presione el [b]LADO IZQUIERDO DE LA PANTALLA[/b] ' + \
                            'si la [b]DIRECCIÓN DE LOS PUNTOS[/b] está ' + \
                            'a [b]LA IZQUIERDA[/b].'
            elif lang == "P":
                value_str = 'Pressione o LADO ESQUERDO DA TELA se a ' + \
                            '[b]DIREÇÃO DOS PONTOS[/b] for a ' + \
                            '[b]DA ESQUERDA[/b].'

    else:
        if not left:
            if lang == "E":
                value_str = 'Press the [b]{0}[/b]'.format(config.RESP_KEYS[-1]) + \
                            ' if the [b]DIRECTION OF THE DOTS[/b] is ' + \
                            '[b]TO THE RIGHT[/b]'
            elif lang == "S":
                value_str = 'Press the [b]{0}[/b]'.format(config.RESP_KEYS[-1]) + \
                            ' if the [b]DIRECTION OF THE DOTS[/b] is ' + \
                            '[b]TO THE RIGHT[/b]'
            elif lang == "P":
                value_str = 'Press the [b]{0}[/b]'.format(config.RESP_KEYS[-1]) + \
                            ' if the [b]DIRECTION OF THE DOTS[/b] is ' + \
                            '[b]TO THE RIGHT[/b]'

        else:
            if lang == "E":
                value_str = 'Press the [b]{0}[/b] '.format(config.RESP_KEYS[0]) + \
                            'if the [b]DIRECTION OF THE DOTS[/b] is ' + \
                            '[b]TO THE LEFT[/b]'
            if lang == "S":
                value_str = 'Press the [b]{0}[/b] '.format(config.RESP_KEYS[0]) + \
                            'if the [b]DIRECTION OF THE DOTS[/b] is ' + \
                            '[b]TO THE LEFT[/b]'
            if lang == "P":
                value_str = 'Press the [b]{0}[/b] '.format(config.RESP_KEYS[0]) + \
                            'if the [b]DIRECTION OF THE DOTS[/b] is ' + \
                            '[b]TO THE LEFT[/b]'

    # eval and return the str
    return value_str


@Subroutine
def Instruct(self, config, lang="E", practice=False):
    if len(config.CONT_KEY) > 1:
        cont_key_str = str(config.CONT_KEY[0]) + " or " + str(config.CONT_KEY[-1])
    else:
        cont_key_str = str(config.CONT_KEY[0])
    print(cont_key_str)
    with If(lang=="E"):
        self.top_text = Ref.object(top_text)['E']
        self.tap_text_M = 'Tap [b]the screen[/b] when you ' + 'are ready to begin the block.'
        self.tap_text_C = 'Press [b]%s[/b] when you are ready to begin the block.'%(cont_key_str)
    with Elif(lang=="S"):
        self.top_text = Ref.object(top_text)['S']
        self.tap_text_M = 'Toque [b]la pantalla[/b] cuando usted esté listo para comenzar el bloque.'
        self.tap_text_C = 'Press [b]%s[/b] when you are ready to begin the block.'%(cont_key_str)
    with Elif(lang=="P"):
        self.top_text = Ref.object(top_text)['P']
        self.tap_text_M = 'Pressione a tela quando você estiver pronto para começar este bloco.'
        self.tap_text_C = 'Press [b]%s[/b] when you are ready to begin the block.'%(cont_key_str)

    # handle the reverse mapping
    with Parallel():
        Label(text=self.top_text,
              markup=True, halign='center', text_size=(s(config.TEST_WIDTH), None),
              bottom=self.exp.screen.center_y + s(config.INST_RADIUS) + s(60),
              font_size=s(config.INST_FONT_SIZE))
        md_l = MovingDots(color='white', scale=s(config.INST_SCALE),
                          num_dots=config.NUM_DOTS, radius=s(config.INST_RADIUS),
                          coherence=config.COHERENCES[2],
                          direction=180, lifespan=config.INST_LIFESPAN,
                          center_y=self.exp.screen.center_y + s(45),
                          lifespan_variance=config.INST_LIFESPAN_VAR, speed=s(config.INST_SPEED),
                          right=self.exp.screen.center_x - s(10))
        md_r = MovingDots(color='white', scale=s(config.INST_SCALE),
                          num_dots=config.NUM_DOTS, radius=s(config.INST_RADIUS),
                          coherence=config.COHERENCES[2],
                          direction=0, lifespan=config.INST_LIFESPAN,
                          center_y=self.exp.screen.center_y + s(45),
                          lifespan_variance=config.INST_LIFESPAN_VAR, speed=s(config.INST_SPEED),
                          left=self.exp.screen.center_x + s(10))
        lt = Label(text=Ref(bottom_text, config, True, lang),
              markup=True, halign='left',
              text_size=(s(config.INST_RADIUS)*1.9, None),
              left_top=(self.exp.screen.center_x - (2*s(config.INST_RADIUS)) - s(10),
                          self.exp.screen.center_y - (s(config.INST_RADIUS))),
              font_size=s(config.INST_FONT_SIZE))
        Label(text=Ref(bottom_text, config, False, lang),
              markup=True, halign='right',
              text_size=(s(config.INST_RADIUS)*1.9, None),
              right_top=(self.exp.screen.center_x + 2*s(config.INST_RADIUS) + s(10),
                          self.exp.screen.center_y - s(config.INST_RADIUS)),
              font_size=s(config.INST_FONT_SIZE))
        if config.TOUCH:
            Label(text=self.tap_text_M,
                  font_size=s(config.INST_FONT_SIZE),
                  top=lt.bottom - s(10),
                  markup=True, halign='center')
        else:
            Label(text=self.tap_text_C,
                  font_size=s(config.INST_FONT_SIZE),
                  top=lt.bottom - s(10),
                  markup=True, halign='center')

    with UntilDone():
        GetResponse(keys=config.CONT_KEY)
    # practice block
    with Parallel():
        MouseCursor(blocking=False)
        with Serial(blocking=False):
            with If(practice):
                Label(text="You will now have a short practice set of trials.\n" +
                           " Press %s to continue." % ("the screen"),
                      halign='center',
                      font_size=s(config.INST_FONT_SIZE))
                with UntilDone():
                    Wait(0.5)
                    GetResponse(keys=config.CONT_KEY)

                Wait(1.0)
                res = Func(gen_practice_trials, config)
                self.md_blocks = res.result

                # do the practice block
                with Loop(self.md_blocks) as block:
                    with Parallel():
                    # put up the fixation cross
                        Background = Image(source = config.BACKGROUND_IMAGE, size = (self.exp.screen.size[0]*1.1, self.exp.screen.size[1]*1.1), allow_stretch = True, keep_ratio = False, blocking=False)
                        Border= Ellipse(size = (s((config.RADIUS)*1.2*2),(s((config.RADIUS)*1.2*2))), color = (.55,.55,.55,1))
                        Telescope = Ellipse(size = (s((config.RADIUS)*1.1*2),(s((config.RADIUS)*1.1*2))), color = (.35, .35, .35, 1.0))
                        cross = Label(text='+', color=config.CROSS_COLOR,
                                  font_size=s(config.CROSS_FONTSIZE))
                    with UntilDone():
                        # loop over trials
                        with Loop(block.current) as trial:
                            # Wait the ISI
                            Wait(config.ISI, jitter=config.JITTER)

                            # do the trial
                            mdt = Trial(cross,
                                        config,
                                        correct_resp=trial.current['correct_resp'],
                                        incorrect_resp=trial.current['incorrect_resp'],
                                        num_dots=config.NUM_DOTS,
                                        right_coherence=trial.current['right_coherence'],
                                        left_coherence=trial.current['left_coherence'])

                Label(text='You have completed the practice.\n' +
                           'Press %s to continue.' % (cont_key_str),
                      halign='center',
                      font_size=s(config.INST_FONT_SIZE))
                with UntilDone():
                    Wait(1.0)
                    GetResponse(keys=config.CONT_KEY)
        with Serial(blocking=False):
            with ButtonPress():
                Button(text="Skip Practice", width=s(config.SKIP_SIZE[0]),
                       bottom=0, right=self.exp.screen.width,
                       height=s(config.SKIP_SIZE[1]),
                       font_size=s(config.SKIP_FONT_SIZE))
    Label(text='You will now begin the task.\n' +
               'Press %s to continue.' % (config.CONT_KEY[0]),
          halign='center',
          font_size=s(config.INST_FONT_SIZE))
    with UntilDone():
        Wait(1.0)
        GetResponse(keys=config.CONT_KEY)
