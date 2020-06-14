# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 11:41:16 2020

@author: Felix
"""

import pygame as pg
from dataclasses import dataclass
import random as rnd

# resolution of the game window
resolution = 1000
# number of cells 
game_array_size = 9
# space per cell
space_per_cell = resolution // game_array_size

pg.init()
# game window
screen = pg.display.set_mode([resolution, resolution])
# sprites from spriters-resource.com
cell_default = pg.transform.scale(pg.image.load('sprites/cell_default.png'),
                                  (space_per_cell, space_per_cell))
cell_flagged = pg.transform.scale(pg.image.load('sprites/cell_flagged.png'),
                                  (space_per_cell, space_per_cell))
cell_mine = pg.transform.scale(pg.image.load('sprites/cell_mine.png'),
                                  (space_per_cell, space_per_cell))
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

game_array = []
neighbouring_mines_array = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

class Cell:
   def __init__(self, column, row):
      self.column = column
      self.row = row
      self.mine = False
      self.selected = False
      self.flagged = False
      self.neighbouring_mines = 0
   
   def draw(self):
      pos = (self.column*space_per_cell, self.row*space_per_cell)
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



for i in range(game_array_size*game_array_size):
   game_array.append(Cell(i//game_array_size, i%game_array_size))
   
while number_of_mines > 0:
   buffer = rnd.randrange(game_array_size*game_array_size)
   if not game_array[buffer].mine:
      game_array[buffer].mine = True
      number_of_mines -= 1
      
for cell_obj in game_array:
   cell_obj.get_neighbouring_mines()

running = True
while running:
   for event in pg.event.get():
      if event.type == pg.QUIT:
         running = False
      if event.type == pg.MOUSEBUTTONDOWN:
         mouseX, mouseY = pg.mouse.get_pos()
         column = mouseX // space_per_cell
         row = mouseY // space_per_cell
         index = column*game_array_size + row
         active_cell = game_array[index]
         if pg.mouse.get_pressed()[2]:
            active_cell.flagged = not active_cell.flagged
         if pg.mouse.get_pressed()[0]:
            active_cell.selected = True
            if active_cell.neighbouring_mines == 0 and not active_cell.mine:
               floodfill(row, column)
         
   for cell_obj in game_array:
      # cell_obj.selected = True
      cell_obj.draw()
   pg.display.flip()
   
pg.quit()