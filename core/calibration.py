import numpy as np
import pygame
import sys
import time

WIDTH, HEIGHT = (1200, 800)
SAMPLING_FREQUENCY = 9600
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
ORANGE = (255,165,0)

def draw_text_in_the_middle(text: str, 
                            color: pygame.Color | tuple[int,int,int],
                            screen: pygame.Surface, 
                            font: pygame.font.Font) -> None:
    """Text with newlines will be separated by lines(by default pygame ignores \\n)"""
    text_lines = text.split('\n')
    WIDTH, HEIGHT = screen.get_size()
    for i, line in enumerate(text_lines):
        line_size = font.size(line)
        screen.blit(
            font.render(line, True, WHITE),
            ((WIDTH - line_size[0])//2, (HEIGHT + line_size[1] * i * 2)//2)
            ) 
def get_signal(sampling_frequency, size ,*args, **kwargs):
    print("Imitating of receiving signal...")
    time.sleep(size)
    return np.random.uniform(0, 100, (int(sampling_frequency * size),))

pygame.init()
pygame.font.init()

###### Greeting ######
screen = pygame.display.set_mode((WIDTH,HEIGHT))
screen.fill(BLACK)  
font: pygame.font.Font = pygame.font.SysFont(pygame.font.get_default_font(), WIDTH*HEIGHT//20000)
GREETING_TEXT = "Для начала пройдите калибровку.\nСледуйте указаниям. Чтобы продолжить, нажмите любую клавишу!"
draw_text_in_the_middle(GREETING_TEXT, WHITE, screen, font)
pygame.display.flip()

greeting = True
while greeting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            greeting = False

###### Getting noise value ######


###### Getting thresholds ######
PROMPTING_DOT_BLINK_TEXT = "Моргните слабо для обозначения точки"
PROMPTING_DASH_BLINK_TEXT = "Моргните сильно для обозначения тире"
USER_ACCURACY = ("Ваша погрешность моргания для точки: dot_blink_error.\n"
                "Для тире: dash_blink_error\n"
                "Чтобы продолжить, нажмите Пробел.\n"
                "Чтобы завершить, нажмите Escape.")
USER_HIGH_ACCURACY_REPORT = ("Погрешность моргания достаточно низкая!\n"
                             "Вы можете завершить калибровку")
USER_LOW_ACCURACY_REPORT = ("Погрешность моргания пока высокая."
                            "Продолжайте калибровку.")

OPTIMAL_CONVERGENCE = 30 # optimal difference between two epochs. low convergence shows that user is blinking with persistently same values
OPTIMAL_ITERATIONS = 5 # user will likely start giving persistent blinks within this iteration amount
ITERATION_SIZE = 10 # amount of prompted dash or dots within an iteration

dot_threshold = 0
dash_threshold = 0

iteration = 1
dot_threshold_peaks = []
dash_threshold_peaks = []

dot_blink_error = 1000
dash_blink_error = 1000

calibrating = True
while calibrating:
    for epoch in range(ITERATION_SIZE):
        mode = np.random.random() < 0.5 # prompting dot or dash
        text = PROMPTING_DOT_BLINK_TEXT if mode == 0 else PROMPTING_DASH_BLINK_TEXT
        screen.fill(ORANGE)
        draw_text_in_the_middle(text, BLACK, screen, font)
        #make a line that appears and dissapears instantly for user to react
        pygame.display.flip()
        interval = np.random.randint(5,20) / 10 # for user to get persistent in different intervals between blinks.

        #get signal smh
        epoch_data = get_signal(SAMPLING_FREQUENCY, interval)# get data for *interval* of time
        (dot_threshold_peaks if mode == 0 else dash_threshold_peaks).append(np.max(epoch_data)) 

        screen.fill(ORANGE) # for message to dissapear. it will make user react on next message better
        pygame.display.flip()

    screen.fill(BLUE)

    last_dot_blink_error = dot_blink_error
    last_dash_blink_error = dash_blink_error
    dot_blink_error = np.round(np.std(dot_threshold_peaks),2)
    dash_blink_error = np.round(np.std(dash_threshold_peaks),2)
    dot_convergence = np.abs(last_dot_blink_error - dot_blink_error)
    dash_convergence = np.abs(last_dash_blink_error - dash_blink_error)

    accuracy_report = (USER_HIGH_ACCURACY_REPORT 
                       if dot_convergence < OPTIMAL_CONVERGENCE and dash_convergence < OPTIMAL_CONVERGENCE
                  else USER_LOW_ACCURACY_REPORT)

    dot_threshold = np.mean(dot_threshold_peaks)
    dash_threshold = np.mean(dash_threshold_peaks)

    #persistence of user blink strength
    #NOTE: accuracy is counted on all calibration epochs, not current one
    draw_text_in_the_middle(
        USER_ACCURACY.replace("dot_blink_error", str(dot_convergence)).replace("dash_blink_error", str(dash_convergence)) + '\n' + accuracy_report,
        WHITE,
        screen,
        font
        ) 
    pygame.display.flip()

    waiting_to_proceed = True
    while waiting_to_proceed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE:
                        waiting_to_proceed = False
                        calibrating = False
                    case pygame.K_SPACE:
                        waiting_to_proceed = False
                         

    iteration += 1

pygame.quit()