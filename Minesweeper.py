# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 11:41:16 2020

@author: Felix
"""

import pygame as pg
import random as rnd
from ctypes import c_int, WINFUNCTYPE, windll
from ctypes.wintypes import HWND, LPCSTR, UINT
def MessageBox(title, text, style):
    return windll.user32.MessageBoxW(0, text, title, style)



# resolution of the game window
# more in y direction to put the settings
resolutionY = 900
resolutionX = 800
# number of cells 
game_array_size = 20
# space per cell
space_per_cell = (resolutionX) // game_array_size

# colors
white = (255,255,255)
black = (0,0,0)

pg.init()
# game window
screen = pg.display.set_mode([resolutionX, resolutionY])
pg.display.set_caption('Minesweeper')
screen.fill((255,255,255))
# sprites from spriters-resource.com
cell_default = pg.transform.scale(pg.image.load('sprites/cell_default.png'),
                                  (space_per_cell, space_per_cell))
cell_flagged = pg.transform.scale(pg.image.load('sprites/cell_flagged.png'),
                                  (space_per_cell, space_per_cell))
cell_mine = pg.transform.scale(pg.image.load('sprites/cell_mine.png'),
                                  (space_per_cell, space_per_cell))
smiles_default = pg.transform.scale(pg.image.load('sprites/smiles_default.png'),
                                  (space_per_cell, space_per_cell))
smiles_win = pg.transform.scale(pg.image.load('sprites/smiles_win.png'),
                                  (space_per_cell, space_per_cell))
smiles_lose = pg.transform.scale(pg.image.load('sprites/smiles_lose.png'),
                                  (space_per_cell, space_per_cell))
pg.display.set_icon(cell_mine)
# coordinates of the smiley
smiles_pos = (resolutionX/2-space_per_cell/2, 50-space_per_cell/2)
smiles_coord = (smiles_pos[0]/space_per_cell, smiles_pos[1]/space_per_cell)
# sprites for empty and number cells
cell_selected = []
for i in range(9):
   buffer = pg.transform.scale(pg.image.load(f'sprites/cell_{i}.png'),
                                (space_per_cell, space_per_cell))
   cell_selected.append(buffer)

# draw the cell_default sprite at 100, 100
# screen.blit(cell_default,(100,100))
# while True:
#    pg.display.flip()
   
   
# number of mines in the game
number_of_mines = 10
number_of_mines_static = number_of_mines
# creating the array where the cells are stored
game_array = []
# array to handle the neighbouring cells
neighbouring_mines_array = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

# message when game is lost
def lose():
   MessageBox('You lost!', 'You lost!', 0)
# message when the game is won
def win():
   MessageBox('You win!', 'You win!', 0)
   


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
            
   def get_neighbouring_mines(self):
      for pos in neighbouring_mines_array:
         new_row = self.row + pos[0]
         new_column = self.column + pos[1]
         if new_row >= 0 and new_row < game_array_size and new_column >= 0 and new_column < game_array_size:
            if game_array[new_column*game_array_size + new_row].mine:
               self.neighbouring_mines += 1
               
# implement the standard minesweeper behaviour, where if you click on an
# empty cell, all neighbouring cells are getting selected as well
def floodfill(row, column):
   for pos in neighbouring_mines_array:
      new_row = row + pos[0]
      new_column = column + pos[1]
      if new_row >= 0 and new_row < game_array_size and new_column >= 0 and new_column < game_array_size:
         active_cell = game_array[new_column*game_array_size + new_row]
         if active_cell.neighbouring_mines == 0 and not active_cell.selected:
            active_cell.selected = True
            floodfill(new_row, new_column)
         else:
            active_cell.selected = True
            
# reset function to start the game over
def reset():
   screen.blit(smiles_default, smiles_pos)
   global game_array
   game_array = []
   for i in range(game_array_size*game_array_size):
      game_array.append(Cell(i//game_array_size, i%game_array_size))
   number_of_mines = number_of_mines_static
   while number_of_mines > 0:
      buffer = rnd.randrange(game_array_size*game_array_size)
      if not game_array[buffer].mine:
         game_array[buffer].mine = True
         number_of_mines -= 1
      
   for cell_obj in game_array:
      cell_obj.get_neighbouring_mines()

# filling the game array with cells 
for i in range(game_array_size*game_array_size):
   game_array.append(Cell(i//game_array_size, i%game_array_size))

# putting mines at random positions
while number_of_mines > 0:
   buffer = rnd.randrange(game_array_size*game_array_size)
   if not game_array[buffer].mine:
      game_array[buffer].mine = True
      number_of_mines -= 1
      
# calculate the number of neighbouring mines for every cell
for cell_obj in game_array:
   cell_obj.get_neighbouring_mines()

# game loop
def game_loop():
    screen.fill(white)
    running = True
    smiles_button_size = (space_per_cell,space_per_cell)
    smiles_button_pos = (smiles_pos)
    smiles_button = pg.Rect(smiles_button_pos[0], smiles_button_pos[1], smiles_button_size[0], smiles_button_size[1])
    screen.blit(smiles_default, smiles_pos)
    while running:
       for event in pg.event.get():
          # check for the quit event
          if event.type == pg.QUIT:
             running = False
          if event.type == pg.KEYDOWN:
             if event.key == pg.K_ESCAPE:
                 running = False
          if event.type == pg.MOUSEBUTTONDOWN:
             mouseX, mouseY = pg.mouse.get_pos()
             column = mouseX // space_per_cell
             row = (mouseY-100) // space_per_cell
             # check if the smiley is pressed and reset the game
             if smiles_button.collidepoint(mouseX, mouseY):
                reset()
                pg.display.update()
             index = column*game_array_size + row
             active_cell = game_array[index]
             # check if the right mousebutton is pressed and flag the cell
             if pg.mouse.get_pressed()[2] and row >= 0:
                active_cell.flagged = not active_cell.flagged
             # check if the right mouse button is pressed and evaluate the rules
             # of the game
             if pg.mouse.get_pressed()[0] and row >= 0:
                active_cell.selected = True
                if active_cell.neighbouring_mines == 0 and not active_cell.mine:
                   floodfill(row, column)
                if active_cell.mine == 1:
                   for cell_obj in game_array:
                      if cell_obj.mine == 1:
                         cell_obj.selected = True
                   screen.blit(smiles_lose, smiles_pos)
                   for cell_obj in game_array:
                   # cell_obj.selected = True
                      cell_obj.draw()
                   pg.display.flip()
       # check whether every mine is flagged --> game won 
       win_cond = 0
       non_win_cond = True
       for cell_obj in game_array:
          if cell_obj.flagged:
             if cell_obj.mine:
                win_cond += 1
             else:
                non_win_cond = False
       if win_cond == number_of_mines_static and non_win_cond:
          for cell_obj in game_array:
             cell_obj.selected = True
          screen.blit(smiles_win, smiles_pos)
          pg.display.update()
          for cell_obj in game_array:
             # cell_obj.selected = True
             cell_obj.draw()
          pg.display.flip()
       # draw the game window
       for cell_obj in game_array:
          # cell_obj.selected = True
          cell_obj.draw()
       pg.display.flip()
       
# menu
def game_menu():
    screen.fill(white)
    menu = True
    start_button_size = (350,100)
    quit_button_size = (350,100)
    start_button_pos = (resolutionX/2, 300)
    quit_button_pos = (resolutionX/2, 500)
    start_button_pos_corr = (start_button_pos[0]-start_button_size[0]/2, start_button_pos[1]-start_button_size[1]/2)
    quit_button_pos_corr = (quit_button_pos[0]-quit_button_size[0]/2, quit_button_pos[1]-quit_button_size[1]/2)
    # button_size = (300,100)
    fontLarge = pg.font.SysFont('arial', 115)
    fontSmall = pg.font.SysFont('arial', 80)
    start_buttonText = fontSmall.render('Start Game', True, black)
    start_buttonTextRect = start_buttonText.get_rect()
    start_buttonTextRect.center = (start_button_pos)
    quit_buttonText = fontSmall.render('Quit Game', True, black)
    quit_buttonTextRect = start_buttonText.get_rect()
    quit_buttonTextRect.center = (quit_button_pos)
    largeText = fontLarge.render('Minesweeper', True, black)
    largeTextRect = largeText.get_rect()
    largeTextRect.center = (resolutionX/2, 100)
    start_button = pg.Rect(start_button_pos_corr[0], start_button_pos_corr[1], start_button_size[0], start_button_size[1])
    quit_button = pg.Rect(quit_button_pos_corr[0], quit_button_pos_corr[1], quit_button_size[0], quit_button_size[1])
    while menu:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                menu = False
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    game_loop()
                    screen.fill(white)
                if quit_button.collidepoint(mouse_pos):
                    menu = False
        pg.draw.rect(screen, [255,0,0], start_button)
        pg.draw.rect(screen, [255,0,0], quit_button)
        screen.blit(largeText, largeTextRect)
        screen.blit(start_buttonText, start_buttonTextRect)
        screen.blit(quit_buttonText, quit_buttonTextRect)
        pg.display.flip()
        

    

game_menu()
pg.quit()