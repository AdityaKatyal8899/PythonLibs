import pygame
from pygame.locals import *
from collections import deque
import random

# Define colors for each face
colors = {
    'W': (255, 255, 255),
    'Y': (255, 255, 0),
    'R': (255, 0, 0),
    'O': (255, 165, 0),
    'G': (0, 255, 0),
    'B': (0, 0, 255)
}

# Initialize cube with 6 faces
faces = {
    'U': [['W'] * 3 for _ in range(3)],
    'D': [['Y'] * 3 for _ in range(3)],
    'F': [['G'] * 3 for _ in range(3)],
    'B': [['B'] * 3 for _ in range(3)],
    'L': [['O'] * 3 for _ in range(3)],
    'R': [['R'] * 3 for _ in range(3)],
}

pygame.init()
# try:
#     pygame.mixer.init()
#     flipping = pygame.mixer.Sound("New.wav")
# except Exception as e:
#     print("Audio error:", e)
flipping = None

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Rubik's Cube with Scramble")
font = pygame.font.SysFont(None, 28)

def draw_face(face, x, y):
    for i in range(3):
        for j in range(3):
            color = colors[face[i][j]]
            rect = pygame.Rect(x + j * 40, y + i * 40, 40, 40)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)

def draw_button():
    button_rect = pygame.Rect(600, 100, 140, 50)
    pygame.draw.rect(screen, (70, 130, 180), button_rect)
    text = font.render("Scramble", True, (255, 255, 255))
    screen.blit(text, (button_rect.x + 25, button_rect.y + 12))
    return button_rect

def draw_cube():
    screen.fill((30, 30, 30))
    draw_face(faces['U'], 280, 80)
    draw_face(faces['L'], 160, 200)
    draw_face(faces['F'], 280, 200)
    draw_face(faces['R'], 400, 200)
    draw_face(faces['B'], 520, 200)
    draw_face(faces['D'], 280, 320)

# Rotation helpers
def rotate_face_clockwise(face):
    return [list(row)[::-1] for row in zip(*face)]

def rotate_face_counter_clockwise(face):
    return [list(row) for row in zip(*face[::-1])]

def play_and_rotate(rotation_func):
    if flipping:
        flipping.stop()
        flipping.play()
    rotation_func()

# Front face
def rotate_front_clockwise():
    faces['F'][:] = rotate_face_clockwise(faces['F'])
    top = faces['U'][2]
    right = [faces['R'][i][0] for i in range(3)]
    bottom = faces['D'][0][::-1]
    left = [faces['L'][i][2] for i in reversed(range(3))]
    q = deque([top, right, bottom, left])
    q.rotate(-1)
    faces['U'][2] = q[0]
    for i in range(3): faces['R'][i][0] = q[1][i]
    faces['D'][0] = q[2][::-1]
    for i in range(3): faces['L'][2 - i][2] = q[3][i]

def rotate_front_counter_clockwise():
    faces['F'][:] = rotate_face_counter_clockwise(faces['F'])
    top = faces['U'][2]
    right = [faces['R'][i][0] for i in range(3)]
    bottom = faces['D'][0][::-1]
    left = [faces['L'][i][2] for i in reversed(range(3))]
    q = deque([top, right, bottom, left])
    q.rotate(1)
    faces['U'][2] = q[0]
    for i in range(3): faces['R'][i][0] = q[1][i]
    faces['D'][0] = q[2][::-1]
    for i in range(3): faces['L'][2 - i][2] = q[3][i]

# Back face
def rotate_back_clockwise():
    faces['B'][:] = rotate_face_clockwise(faces['B'])
    top = faces['U'][0]
    left = [faces['L'][i][0] for i in reversed(range(3))]
    bottom = faces['D'][2][::-1]
    right = [faces['R'][i][2] for i in range(3)]
    q = deque([top, right, bottom, left])
    q.rotate(-1)
    faces['U'][0] = q[0]
    for i in range(3): faces['R'][i][2] = q[1][i]
    faces['D'][2] = q[2][::-1]
    for i in range(3): faces['L'][2 - i][0] = q[3][i]

def rotate_back_counter_clockwise():
    faces['B'][:] = rotate_face_counter_clockwise(faces['B'])
    top = faces['U'][0]
    left = [faces['L'][i][0] for i in reversed(range(3))]
    bottom = faces['D'][2][::-1]
    right = [faces['R'][i][2] for i in range(3)]
    q = deque([top, right, bottom, left])
    q.rotate(1)
    faces['U'][0] = q[0]
    for i in range(3): faces['R'][i][2] = q[1][i]
    faces['D'][2] = q[2][::-1]
    for i in range(3): faces['L'][2 - i][0] = q[3][i]

# Left face
def rotate_left_clockwise():
    faces['L'][:] = rotate_face_clockwise(faces['L'])
    top = [faces['U'][i][0] for i in range(3)]
    front = [faces['F'][i][0] for i in range(3)]
    bottom = [faces['D'][i][0] for i in range(3)]
    back = [faces['B'][2 - i][2] for i in range(3)]
    for i in range(3):
        faces['U'][i][0] = back[i]
        faces['F'][i][0] = top[i]
        faces['D'][i][0] = front[i]
        faces['B'][2 - i][2] = bottom[i]

def rotate_left_counter_clockwise():
    faces['L'][:] = rotate_face_counter_clockwise(faces['L'])
    top = [faces['U'][i][0] for i in range(3)]
    front = [faces['F'][i][0] for i in range(3)]
    bottom = [faces['D'][i][0] for i in range(3)]
    back = [faces['B'][2 - i][2] for i in range(3)]
    for i in range(3):
        faces['U'][i][0] = front[i]
        faces['F'][i][0] = bottom[i]
        faces['D'][i][0] = back[i]
        faces['B'][2 - i][2] = top[i]

# Right face
def rotate_right_clockwise():
    faces['R'][:] = rotate_face_clockwise(faces['R'])
    top = [faces['U'][i][2] for i in range(3)]
    front = [faces['F'][i][2] for i in range(3)]
    bottom = [faces['D'][i][2] for i in range(3)]
    back = [faces['B'][2 - i][0] for i in range(3)]
    for i in range(3):
        faces['U'][i][2] = front[i]
        faces['F'][i][2] = bottom[i]
        faces['D'][i][2] = back[i]
        faces['B'][2 - i][0] = top[i]

def rotate_right_counter_clockwise():
    faces['R'][:] = rotate_face_counter_clockwise(faces['R'])
    top = [faces['U'][i][2] for i in range(3)]
    front = [faces['F'][i][2] for i in range(3)]
    bottom = [faces['D'][i][2] for i in range(3)]
    back = [faces['B'][2 - i][0] for i in range(3)]
    for i in range(3):
        faces['U'][i][2] = back[i]
        faces['F'][i][2] = top[i]
        faces['D'][i][2] = front[i]
        faces['B'][2 - i][0] = bottom[i]

# Up face
def rotate_up_clockwise():
    faces['U'][:] = rotate_face_clockwise(faces['U'])
    front = faces['F'][0]
    right = faces['R'][0]
    back = faces['B'][0]
    left = faces['L'][0]
    faces['F'][0], faces['R'][0], faces['B'][0], faces['L'][0] = left, front, right, back

def rotate_up_counter_clockwise():
    faces['U'][:] = rotate_face_counter_clockwise(faces['U'])
    front = faces['F'][0]
    right = faces['R'][0]
    back = faces['B'][0]
    left = faces['L'][0]
    faces['F'][0], faces['R'][0], faces['B'][0], faces['L'][0] = right, back, left, front

# Down face
def rotate_down_clockwise():
    faces['D'][:] = rotate_face_clockwise(faces['D'])
    front = faces['F'][2]
    right = faces['R'][2]
    back = faces['B'][2]
    left = faces['L'][2]
    faces['F'][2], faces['R'][2], faces['B'][2], faces['L'][2] = right, back, left, front

def rotate_down_counter_clockwise():
    faces['D'][:] = rotate_face_counter_clockwise(faces['D'])
    front = faces['F'][2]
    right = faces['R'][2]
    back = faces['B'][2]
    left = faces['L'][2]
    faces['F'][2], faces['R'][2], faces['B'][2], faces['L'][2] = left, front, right, back

# Handle mouse click on front face (optional)
def handle_click(pos, button):
    x, y = pos
    if 280 <= x <= 400 and 200 <= y <= 320:  # Front face only
        if button == 1:
            play_and_rotate(rotate_front_clockwise)
        elif button == 3:
            play_and_rotate(rotate_front_counter_clockwise)

# Scramble logic using all face rotations
def scramble_cube(moves=20):
    for _ in range(moves):
        play_and_rotate(random.choice(all_rotations))

all_rotations = [
    rotate_front_clockwise,
    rotate_front_counter_clockwise,
    rotate_back_clockwise,
    rotate_back_counter_clockwise,
    rotate_left_clockwise,
    rotate_left_counter_clockwise,
    rotate_right_clockwise,
    rotate_right_counter_clockwise,
    rotate_up_clockwise,
    rotate_up_counter_clockwise,
    rotate_down_clockwise,
    rotate_down_counter_clockwise
]

# Main loop
def main():
    running = True
    while running:
        draw_cube()
        button_rect = draw_button()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    scramble_cube()
                else:
                    handle_click(event.pos, event.button)
            elif event.type == KEYDOWN:
                if event.key == K_f:
                    play_and_rotate(rotate_front_clockwise)
                elif event.key == K_g:
                    play_and_rotate(rotate_front_counter_clockwise)
                elif event.key == K_b:
                    play_and_rotate(rotate_back_clockwise)
                elif event.key == K_n:
                    play_and_rotate(rotate_back_counter_clockwise)
                elif event.key == K_l:
                    play_and_rotate(rotate_left_clockwise)
                elif event.key == K_k:
                    play_and_rotate(rotate_left_counter_clockwise)
                elif event.key == K_r:
                    play_and_rotate(rotate_right_clockwise)
                elif event.key == K_t:
                    play_and_rotate(rotate_right_counter_clockwise)
                elif event.key == K_u:
                    play_and_rotate(rotate_up_clockwise)
                elif event.key == K_y:
                    play_and_rotate(rotate_up_counter_clockwise)
                elif event.key == K_d:
                    play_and_rotate(rotate_down_clockwise)
                elif event.key == K_e:
                    play_and_rotate(rotate_down_counter_clockwise)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
