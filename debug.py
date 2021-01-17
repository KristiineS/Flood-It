
import pygame
import random
import numpy as np
import copy
from statistics import mode 
import time
from math import inf


class Square:
    def __init__(self, x, y, color, size, neighbors):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.neighbors = neighbors
        self.active = False
        
    def display(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size)) # left, top, width, height


# Calculate all the neighbors of a square
def getNeighbors(i,j,m,n):
    # central area
    if i > 0 and j > 0 and i < m and j < n:
        return np.asarray([[(i-1), j], [i, (j-1)], [(i+1), j], [i, (j+1)]])
    # sides, apart from the corners
    elif i <= 0 and j > 0 and i < m and j < n:
        return np.asarray([[i, (j-1)], [(i+1), j], [i, (j+1)]])
    elif i > 0 and j <= 0 and i < m and j < n:
        return np.asarray([[(i-1), j], [(i+1), j], [i, (j+1)]])
    elif i > 0 and j > 0 and i >= m and j < n:
        return np.asarray([[(i-1), j], [i, (j-1)], [i, (j+1)]])
    elif i > 0 and j > 0 and i < m and j >= n:
        return np.asarray([[(i-1), j], [i, (j-1)], [(i+1), j]])
    # corners
    elif i <= 0 and j <= 0 and i < m and j < n:
        return np.asarray([[(i+1), j], [i, (j+1)]])    
    elif i <= 0 and j > 0 and i < m and j >= n:
        return np.asarray([[i, (j-1)], [(i+1), j]])
    elif i > 0 and j <= 0 and i >= m and j < n:
        return np.asarray([[(i-1), j], [i, (j+1)]])
    else:
        return np.asarray([[(i-1), j], [i, (j-1)]])


# Select a square via a mouse click
def clickSquare(all_squares, x, y):
    for i in range(all_squares.shape[0]):
        for j in range(all_squares.shape[1]):
            # checking if the position of the mouse is inside the selected square
            if (all_squares[i][j].x < x and all_squares[i][j].y < y 
                    and (all_squares[i][j].x + all_squares[i][j].size) > x 
                            and (all_squares[i][j].y + all_squares[i][j].size) > y):
                return all_squares[i][j]
    return None


# change the color of the active square
def isValidNeighbor(all_squares, selected_square, active_color):
    if selected_square.active == False:
        working_array = [] # array to check if the square clicked is further away but directly connected to the working area
        for el1,el2 in selected_square.neighbors:
            # check if the square clicked is next to the working area
            if all_squares[el1][el2].active == True:
                selected_square.active = True
                return selected_square.color, True
            # check if the neighboring square is the same color as the one clicked
            elif all_squares[el1][el2].color == selected_square.color:
                working_array.extend(all_squares[el1][el2].neighbors)
        # checking all the connected squares of the same color for connection to the working area
        while working_array:
            el = working_array.pop(0)
            if all_squares[el[0]][el[1]].color == selected_square.color:
                working_array.extend(all_squares[el[0]][el[1]].neighbors)
            elif all_squares[el[0]][el[1]].active == True:
                selected_square.active = True
                return selected_square.color, True
    return active_color, False


# Change the status of the adjoining squares into active
def activateSquares(square_rows, square_columns, all_squares, active_color):
    for i in range(square_rows): 
        for j in range(square_columns): 
            if all_squares[i][j].active == True:
                for el1,el2 in all_squares[i][j].neighbors:
                    if all_squares[el1][el2].color == active_color:
                        all_squares[el1][el2].active = True


# Recolor all the active squares
# def recolor(square_rows, square_columns, all_squares, active_color, screen): 
def recolor(square_rows, square_columns, all_squares, active_color):                               
    for i in range(square_rows): 
        for j in range(square_columns): 
            if all_squares[i][j].active == True:
                all_squares[i][j].color = active_color
                # all_squares[i][j].display(screen)


def updateScreen(square_rows, square_columns, all_squares, screen):
    for i in range(square_rows): 
        for j in range(square_columns): 
                all_squares[i][j].display(screen)




def main():
    pygame.init()
    
    pygame.display.set_caption('Flood it')
    # (width, height) = (1100, 600)
    (width, height) = (100, 100)
    screen = pygame.display.set_mode((width, height))
    square_size = 25 
    
    white = (255, 255, 255) 
    red = (255, 0, 0)
    green = (50, 197, 62)
    blue = (51, 51, 155)
    yellow = (255, 255, 51)
    #misty_rose = (232, 44, 49)
    some_color = (200, 200, 200)
    ahh = (100,100,100)
    
    colors = [red, green, blue, yellow, some_color, ahh]
    screen.fill(white)
    
    # Number of squares on the table
    (square_rows, square_columns) = int(width/square_size), int(height/square_size)
    all_squares = np.empty((square_rows, square_columns), dtype=object)
    
    for i in range(square_rows): # creating and coloring every row
        for j in range(square_columns): # creating and coloring every column
            all_squares[i][j] = Square(i*square_size, j*square_size, random.choice(colors), 
                                       square_size, getNeighbors(i, j, square_rows-1, square_columns-1))
            all_squares[i][j].display(screen)
                                   
    # Changes need to be made before the flip() function is called.
    pygame.display.flip()    
    
    # Make the upper left square active (and the adjoining ones of the same color)
    all_squares[0][0].active = True
    active_color = all_squares[0][0].color
    # print(f"0,0: {active_color} 0,1: {all_squares[0][1].color} 1, 0: {all_squares[1][0].color}")
    activateSquares(square_rows, square_columns, all_squares, active_color)
    
    start_greedy = time.time()
    minimal_steps = greedyApproach(square_rows, square_columns, copy.deepcopy(all_squares))
    end_greedy = time.time()
    print(f"With greedy solvable in: {minimal_steps} steps; Elapsed time: {end_greedy-start_greedy}s")

    start_rec = time.time()
    rec_sols = [inf]
    for color in colors:
        min_steps = min(rec_sols)
        rec_sols.append(recursiveSolution(square_rows, square_columns, copy.deepcopy(all_squares), colors, color, 0, min_steps))
    minimal_steps_rec = min(rec_sols)
    end_rec = time.time()
    print(f"With recursive solvable in: {minimal_steps_rec} steps; Elapsed time: {end_rec-start_rec}s")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                (mouseX, mouseY) = pygame.mouse.get_pos()
                selected_square = clickSquare(all_squares, mouseX, mouseY)
                
                if selected_square is not None:
                    active_color, valid_move = isValidNeighbor(all_squares, selected_square, active_color)
                    
                if valid_move == True:
                    # recolor(square_rows, square_columns, all_squares, active_color, screen)
                    recolor(square_rows, square_columns, all_squares, active_color)
                    updateScreen(square_rows, square_columns, all_squares, screen)            
                    activateSquares(square_rows, square_columns, all_squares, active_color)
                                        
                pygame.display.flip()    
    
    pygame.quit()


def checkFinished(square_rows, square_columns, all_squares):
    # checks if all squares are of the same color
    color = all_squares[0][0].color
    for i in range(square_rows):
        for j in range (square_columns):
            if all_squares[i][j].color != color:
                return False
    return True


def greedyApproach(square_rows, square_columns, all_squares):
    # determines minimal number of moves using greedy approach
    steps = 0
    while(not checkFinished(square_rows, square_columns, all_squares)):
        next_step = getMostImportantNeighbor(square_rows, square_columns, all_squares)       
        recolor(square_rows, square_columns, all_squares, next_step)            
        activateSquares(square_rows, square_columns, all_squares, next_step)
        steps +=1
    return steps


def getMostImportantNeighbor(square_rows, square_columns, all_squares):
    # get most often occuring color of neighboring squares from active area
    all_colours = list()
    for i in range(square_rows): 
        for j in range(square_columns): 
            current_square = all_squares[i][j]
            if current_square.active == True:
                for neighbor_i, neighbor_j in current_square.neighbors:
                    if all_squares[neighbor_i][neighbor_j].color != current_square.color:
                        all_colours.append(((neighbor_i, neighbor_j),all_squares[neighbor_i][neighbor_j].color))
    # print(all_colours)
    # print(mode([x[1] for x in list(set(all_colours))]))
    
    return mode([x[1] for x in list(set(all_colours))])

def recursiveSolution(square_rows, square_columns, all_squares, colors, color, steps, min_steps):
    if (checkFinished(square_rows, square_columns, all_squares)):
        return steps
    else:
        if(steps >= min_steps):
            return inf
        steps +=1     
        if  isValidColor(square_rows, square_columns, all_squares, color):
            recolor(square_rows, square_columns, all_squares, color)            
            activateSquares(square_rows, square_columns, all_squares, color)
            ls = list()
            for color in colors:
                ls.append(recursiveSolution(square_rows, square_columns, copy.deepcopy(all_squares), colors, color, steps, min_steps))
            return min(ls)
        else:
            return inf

def isValidColor(square_rows, square_columns, all_squares, color):
    for i in range(square_rows): 
        for j in range(square_columns): 
            current_square = all_squares[i][j]
            if current_square.active == True:
                if (color == current_square.color):
                    return False
                for neighbor_i, neighbor_j in current_square.neighbors:
                    if all_squares[neighbor_i][neighbor_j].color == color:
                        return True
    return False


if __name__=="__main__":
    main()



