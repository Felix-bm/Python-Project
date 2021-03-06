# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 11:41:16 2020

@author: Felix
"""

import pygame as pg
import random as rnd
import numpy as np


# resolution of the game window
resolutionY = 900
resolutionX = 800
# number of cells = game_array_size**2
game_array_size = 20
# pixels per cell
space_per_cell = (resolutionX) // game_array_size

# colors
white = (255,255,255)
grey = (150,150,150)
dark_grey = (100,100,100)
black = (0,0,0)
red = (180,20,20)

# loading the sprites and resize them
# sprites from spriters_resource.com
cell_default = pg.transform.scale(pg.image.load('sprites/cell_default.png'),
                                  (space_per_cell, space_per_cell))
cell_flagged = pg.transform.scale(pg.image.load('sprites/cell_flagged.png'),
                                  (space_per_cell, space_per_cell))
cell_mine = pg.transform.scale(pg.image.load('sprites/cell_mine.png'),
                                  (space_per_cell, space_per_cell))
cell_xplode = pg.transform.scale(pg.image.load('sprites/cell_xplode.png'),
                                  (space_per_cell, space_per_cell))
smiles_default = pg.transform.scale(pg.image.load(
                                  'sprites/smiles_default.png'),
                                  (space_per_cell, space_per_cell))
smiles_win = pg.transform.scale(pg.image.load('sprites/smiles_win.png'),
                                  (space_per_cell, space_per_cell))
smiles_lose = pg.transform.scale(pg.image.load('sprites/smiles_lose.png'),
                                  (space_per_cell, space_per_cell))
cell_selected = []
for i in range(9):
   buffer = pg.transform.scale(pg.image.load(f'sprites/cell_{i}.png'),
                                (space_per_cell, space_per_cell))
   cell_selected.append(buffer)
# initializing the pygame window
pg.init()
# clock used as waiting time after each loop
# useful for defining time
clock = pg.time.Clock()
# setting up the display
screen = pg.display.set_mode([resolutionX, resolutionY])
pg.display.set_caption('Minesweeper')
pg.display.set_icon(cell_mine)
# coordinates of the status/reset smiley
smiles_pos = (resolutionX/2-space_per_cell/2, 50-space_per_cell/2)
smiles_coord = (smiles_pos[0]/space_per_cell, smiles_pos[1]/space_per_cell)
# array to handle the evaluation of neighbouring cells
neighbouring_mines_array = [(-1,-1),(-1,0),(-1,1),(0,-1),
                            (0,1),(1,-1),(1,0),(1,1)]

class Cell:
   """
   Definition of a cell with methods to draw the cell and to check for
   the number of neighbouring cells
   """
   def __init__(self, column, row):
      self.column = column
      self.row = row
      self.mine = False
      self.selected = False
      self.flagged = False
      self.neighbouring_mines = 0
   
   # draws the sprite depending on the state of the cell
   def draw(self):
      pos = (self.column*space_per_cell, self.row*space_per_cell+100)
      if self.selected:
         if self.mine:
            screen.blit(cell_mine, pos)
         else:
            screen.blit(cell_selected[self.neighbouring_mines], pos)
      else:
         if self.flagged:
            screen.blit(cell_flagged, pos)
         else:
            screen.blit(cell_default, pos)
   
   # gets the number of neighbouring mines
   def get_neighbouring_mines(self, game_array):
      for pos in neighbouring_mines_array:
         new_row = self.row + pos[0]
         new_column = self.column + pos[1]
         if (new_row >= 0 and new_row < game_array_size 
             and new_column >= 0 and new_column < game_array_size):
            if game_array[new_column*game_array_size + new_row].mine:
               self.neighbouring_mines += 1


class TextButton(pg.Rect):
    """
    class for creating the text buttons using the pre-existing class Rect from
    pygame
    """
    def __init__(self, screen, pos, size, text, color, color_button=white,
                 font='arial', fontsize=0):
        self.screen = screen
        self.pos = pos
        self.size = size
        self.text = text
        self.font = font
        self.color = color
        self.color_button = color_button
        font_array = (115,80,50)
        self.fontUsed = pg.font.SysFont(font, font_array[fontsize])
        pos_corr = (pos[0]-size[0]/2, pos[1]-size[1]/2)
        self.buttonText = self.fontUsed.render(self.text, True, self.color)
        self.buttonTextRect = self.buttonText.get_rect()
        self.buttonTextRect.center = (self.pos)
        super().__init__(pos_corr[0], pos_corr[1], size[0], size[1])
    
    # updates the button text
    def update_text(self, text):
        self.buttonText = self.fontUsed.render(text, True, self.color)
        self.buttonTextRect = self.buttonText.get_rect()
        self.buttonTextRect.center = (self.pos)
   
    # updates the color of the text
    def update_color(self, color):
        self.buttonText = self.fontUsed.render(self.text, True, color)
        self.buttonTextRect = self.buttonText.get_rect()
        self.buttonTextRect.center = (self.pos)
    
    # draws just the text on the screen
    def draw_text(self):
        self.screen.blit(self.buttonText, self.buttonTextRect)
        
    # draws the text and creates the button on the screen
    def draw_all(self):
        pg.draw.rect(self.screen, self.color_button, self)
        self.draw_text()
    
    # checks if the mouse hovers over the button and changes the text color
    def mouse_hover(self, color):
       if self.collidepoint(pg.mouse.get_pos()):
          self.update_color(color)
       else:
          self.update_color(self.color)
        
        
# implement the standard minesweeper behaviour, where if you click on an
# empty cell, all neighbouring cells are getting selected as well
def floodfill(row, column, game_array):
   for pos in neighbouring_mines_array:
      new_row = row + pos[0]
      new_column = column + pos[1]
      # checks if the neighbouring cells have no neighbouring cells as well
      # if yes, then it selects these cells and calls floodfill on these cells
      # aswell
      # if no, then it only selects the cells
      if (new_row >= 0 and new_row < game_array_size and new_column >= 0 
          and new_column < game_array_size):
         active_cell = game_array[new_column*game_array_size + new_row]
         if active_cell.neighbouring_mines == 0 and not active_cell.selected:
            active_cell.selected = True
            floodfill(new_row, new_column, game_array)
         else:
            active_cell.selected = True

# function takes difficulty as input and outputs the number of mines
def difficulty(var, num=10):
   if var == 'hard':
      number_of_mines = 50
      diff_number = 2
   if var == 'medium':
      number_of_mines = 25
      diff_number = 1
   if var == 'easy':
      number_of_mines = 10
      diff_number = 0
   if var == 'custom':
      number_of_mines = num
   return number_of_mines, diff_number

# function that resets the game state
def reset(number_of_mines):
   screen.blit(smiles_default, smiles_pos)
   reset_var = 1
   win = False
   lose = False
   game_array = []
   game_array = fill_cells(game_array_size)
   put_mines(number_of_mines, game_array)
   for cell_obj in game_array:
      cell_obj.get_neighbouring_mines(game_array)
   return reset_var, win, lose, game_array
      
# function that takes the game_array_size as input and outputs an array filled
# with objects of the class Cell
def fill_cells(game_array_size):
   game_array = []
   for i in range(game_array_size*game_array_size):
      game_array.append(Cell(i//game_array_size, i%game_array_size))
   return game_array

# function that takes the number of mines and the game_array given by 
# fill cells and puts the given number of mines at random on the game array
def put_mines(number_of_mines, game_array):
   while number_of_mines > 0:
      buffer = rnd.randrange(game_array_size*game_array_size)
      if not game_array[buffer].mine:
         game_array[buffer].mine = True
         number_of_mines -= 1

# function that resets the highscore.txt to all zeros
def reset_highscore():
   score = np.array([0,0,0])
   outputstr = 'easy \t medium \t hard'
   np.savetxt('./highscore.txt', score, delimiter="\t", header=outputstr)

# function that reads in the highscore.txt and returns the contents as a
# np.array
def check_highscore():
   highscore_data = np.loadtxt('./highscore.txt')
   return highscore_data

# takes the played time and the difficulty as input and checks if the 
# highscore time was beaten
# if yes, it updates the highscore.txt and returns True
# if no, return False
def highscore(final_time, diff):
   highscore_data = np.loadtxt('./highscore.txt')
   outputstr = 'easy \t medium \t hard'
   if final_time < highscore_data[diff] or highscore_data[diff] == 0:
      highscore_data[diff] = final_time
      np.savetxt('./highscore.txt', highscore_data,
                 delimiter="\t", header=outputstr)
      return True
   else:
      return False
      
# function that creates the game window and does the game loop
# takes the number_of_mines and the difficulty as input
def game_loop(number_of_mines, diff_number):
    screen.fill(grey)
    running = True
    # variables that track if winning or losing condition is met
    win = False 
    lose = False
    # filling the game array with cells and putting the mines
    game_array = fill_cells(game_array_size)
    put_mines(number_of_mines, game_array)
    # calculate the number of neighbouring mines for every cell
    for cell_obj in game_array:
       cell_obj.get_neighbouring_mines(game_array)
    # drawing the smiley sprite on a button that calls the reset function 
    # if pressed
    smiles_button_size = (space_per_cell,space_per_cell)
    smiles_button_pos = (smiles_pos)
    smiles_button = pg.Rect(smiles_button_pos[0], smiles_button_pos[1],
                            smiles_button_size[0], smiles_button_size[1])
    # highscore text, that is drawn if a new highscore has been achieved
    highscoreText = TextButton(screen, (resolutionX*1/4, 50), (500,100),
                               'New Highscore!', red, fontsize=2)
    # initializing the text Button that will be showing the game time
    timeText = TextButton(screen, (resolutionX*3/4, 50), (500,100),
                          'buffer', black, fontsize=2)
    # tick variable counts the number of times the game has been looped 
    tick = 0
    reset_var = 0
    update = 0
    while running:
       screen.fill(grey)
       screen.blit(smiles_default, smiles_pos)
       for event in pg.event.get():
          # check for the quit event
          if event.type == pg.QUIT:
             running = False
          # check if the escape button has been pressed then quit the loop
          if event.type == pg.KEYDOWN:
             if event.key == pg.K_ESCAPE:
                 running = False
          if event.type == pg.MOUSEBUTTONDOWN:
             mouseX, mouseY = pg.mouse.get_pos()
             column = mouseX // space_per_cell
             row = (mouseY-100) // space_per_cell
             # check if the smiley is pressed and reset the game
             if smiles_button.collidepoint(mouseX, mouseY):
                reset_var, win, lose, game_array = reset(number_of_mines)
                pg.display.update()
             index = column*game_array_size + row
             active_cell = game_array[index]
             # check if the right mousebutton is pressed and flag the cell
             if pg.mouse.get_pressed()[2] and row >= 0:
                if active_cell.selected == False:
                   active_cell.flagged = not active_cell.flagged
             # check if the right mouse button is pressed and evaluate the 
             # rules of the game
             if pg.mouse.get_pressed()[0] and row >= 0:
                active_cell.selected = True
                if (active_cell.neighbouring_mines == 0 
                    and not active_cell.mine):
                   floodfill(row, column, game_array)
                if active_cell.mine == 1:
                   for cell_obj in game_array:
                      if cell_obj.mine == 1:
                         cell_obj.selected = True
                   screen.blit(smiles_lose, smiles_pos)
                   for cell_obj in game_array:
                   # cell_obj.selected = True
                      cell_obj.draw()
                   lose = True
                   pg.display.flip()
       # if the lose condition has been met, change the smiley sprite
       if lose:
          screen.blit(smiles_lose, smiles_pos)
       # check whether every mine is flagged --> game won 
       win_cond = 0
       non_win_cond = True
       for cell_obj in game_array:
          if cell_obj.flagged:
             if cell_obj.mine:
                win_cond += 1
             else:
                non_win_cond = False
       # check if the win condition has been met, and change the smiley sprite
       # also sets the win variable to True
       if win_cond == number_of_mines and non_win_cond:
          for cell_obj in game_array:
             cell_obj.selected = True
          screen.blit(smiles_win, smiles_pos)
          win = True
          for cell_obj in game_array:
             # cell_obj.selected = True
             cell_obj.draw()
       # draw the game window
       for cell_obj in game_array:
          # cell_obj.selected = True
          cell_obj.draw()
       # resets the tick variable, if the game has been reset
       if reset_var == 1:
          tick = 0
       # updates the timeText, to show the time in second to the first decimal
       if tick % 6 == 0 and win == False:
          time_in_s = tick / 60
          timeText.update_text(f'{time_in_s}')
       # if win condition has been met, call the highscore function
       if win == True:
          time_in_s_final = tick/60
          if highscore(time_in_s_final, diff_number):
             update = 60
          if update:
             highscoreText.draw_text()
             update -= 1
       timeText.draw_text()
       pg.display.flip()
       reset_var = 0
       # waits 1/60 of a second before new iteration so that the game runs
       # on 60 frames per second
       clock.tick(60)
       tick += 1

# menu that shows the current highscores
def highscore_menu():
    screen.fill(grey)
    menu = True
    checked_highscore = check_highscore()
    # show the highscore to the third decimal
    checked_highscore = np.round(checked_highscore, 3)
    easy_txt = f'Easy:    {checked_highscore[0]}s'
    medium_txt = f'Medium:    {checked_highscore[1]}s'
    hard_txt = f'Hard:    {checked_highscore[2]}s'
    easy_button = TextButton(screen, (resolutionX/2,300), (500,100),
                             easy_txt, black, fontsize=1)
    medium_button = TextButton(screen, (resolutionX/2,420), (500,100),
                               medium_txt, black, fontsize=1)
    hard_button = TextButton(screen, (resolutionX/2,540), (500,100),
                             hard_txt, black, fontsize=1)
    largeText = TextButton(screen, (resolutionX/2,100), (500,100),
                           'Highscore', black, fontsize=0)
    # button to reset the highscores
    reset_button = TextButton(screen, (resolutionX/2,660), (500,100),
                              'Reset Highscore', black, color_button=red, 
                              fontsize=1)
    while menu:
       reset_button.mouse_hover(white)
       for event in pg.event.get():
          if event.type == pg.QUIT:
             menu = False
          if event.type == pg.KEYDOWN:
             if event.key == pg.K_ESCAPE:
                 menu = False
          if event.type == pg.MOUSEBUTTONDOWN:
             mouse_pos = event.pos
             if reset_button.collidepoint(mouse_pos):
                reset_highscore()
                highscore_menu()
                menu = False
       easy_button.draw_text()
       medium_button.draw_text()
       hard_button.draw_text()
       reset_button.draw_all()
       largeText.draw_text()
       pg.display.flip()
       clock.tick(60)

# menu to change the difficulty
# needs to take the number of mines and the difficulty as input, in case
# the user quits out of the menu without choosing a new difficulty
def sel_diff(number_of_mines, diff_number):
    screen.fill(grey)
    selDiff = True
    largeText = TextButton(screen, (resolutionX/2,100), (500,100),
                           'Set Difficulty', black, fontsize=0)
    # shows a difficulty set text for 1 second after a difficulty has been 
    # selected
    updateText = TextButton(screen, (resolutionX/2, 700), (350,100),
                            'Difficulty Set!', black, fontsize=1)
    easy_button = TextButton(screen, (resolutionX/2, 300), (350,100),
                             'Easy', black, color_button=dark_grey,
                             fontsize=1)
    medium_button = TextButton(screen, (resolutionX/2, 420), (350,100),
                               'Medium', black, color_button=dark_grey,
                               fontsize=1)
    hard_button = TextButton(screen, (resolutionX/2, 540), (350,100), 
                             'Hard', black, color_button=dark_grey,
                             fontsize=1)
    update = 0
    while selDiff:
       easy_button.mouse_hover(white)
       medium_button.mouse_hover(white)
       hard_button.mouse_hover(white)
       for event in pg.event.get():
          if event.type == pg.QUIT:
             selDiff = False
          if event.type == pg.KEYDOWN:
             if event.key == pg.K_ESCAPE:
                 selDiff = False
          if event.type == pg.MOUSEBUTTONDOWN:
             mouse_pos = event.pos
             if easy_button.collidepoint(mouse_pos):
                number_of_mines, diff_number = difficulty('easy')
                update = 60
             if medium_button.collidepoint(mouse_pos):
                number_of_mines, diff_number = difficulty('medium')
                update = 60
             if hard_button.collidepoint(mouse_pos):
                number_of_mines, diff_number = difficulty('hard')
                update = 60
       screen.fill(grey)
       if update:
          updateText.draw_text()
          update -= 1
       easy_button.draw_all()
       medium_button.draw_all()
       hard_button.draw_all()
       largeText.draw_text()
       pg.display.flip()
       clock.tick(60)
    return number_of_mines, diff_number    

# main menu, from where all other menus can be accessed
def game_menu():
    screen.fill(grey)
    menu = True
    number_of_mines, diff_number = difficulty('easy')
    largeText = TextButton(screen, (resolutionX/2, 100), (350,100), 
                           'Minesweeper', black, fontsize=0)
    start_button = TextButton(screen, (resolutionX/2, 300), (350,100), 
                              'Start Game', black, color_button=dark_grey,
                              fontsize=1)
    diff_button = TextButton(screen, (resolutionX/2, 420), (350,100),
                             'Difficulty', black, color_button=dark_grey,
                             fontsize=1)
    highscore_button = TextButton(screen, (resolutionX/2, 540), (350,100),
                                  'Highscore', black, color_button=dark_grey,
                                  fontsize=1)
    quit_button = TextButton(screen, (resolutionX/2, 660), (350,100),
                             'Quit Game', black, color_button=dark_grey,
                             fontsize=1)
    while menu:
        start_button.mouse_hover(white)
        diff_button.mouse_hover(white)
        highscore_button.mouse_hover(white)
        quit_button.mouse_hover(white)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                menu = False
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    game_loop(number_of_mines, diff_number)
                    screen.fill(grey)
                if diff_button.collidepoint(mouse_pos):
                    number_of_mines, diff_number = sel_diff(number_of_mines,
                                                            diff_number)
                    screen.fill(grey)
                if highscore_button.collidepoint(mouse_pos):
                    highscore_menu()
                    screen.fill(grey)
                if quit_button.collidepoint(mouse_pos):
                    menu = False
        largeText.draw_text()
        start_button.draw_all()
        diff_button.draw_all()
        highscore_button.draw_all()
        quit_button.draw_all()
        pg.display.flip()
        clock.tick(60)
        

if __name__ == '__main__':
    game_menu()
    pg.quit()