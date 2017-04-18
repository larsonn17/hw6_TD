  # -*- coding: latin-1 -*-
import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):
    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "TED")


    #getPlacement
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a placement from the player.(GameState)
    #
    #Return: If setup phase 1: list of eleven 2-tuples of ints -> [(x1,y1), (x2,y2),…,(x10,y10)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    #Creates a defensive wall of grass, while putting the tunnel and the anthill in the middle
    ##
    def getPlacement(self, currentState):

        if currentState.phase == SETUP_PHASE_1:
            return[(2,1), (7,1), (0,3), (1,3), (2,3), (3,3), (4,3),( 6,3), (7,3), (8,3), (9,3)];    #grass placement
        #Randomly places enemy food, *stolen from Dr. Nuxoll's Simple Food Gatherer AI*
        elif currentState.phase == SETUP_PHASE_2:
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return None  #should never happen

    ##
    #getMove
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a move from the player.(GameState)
    #
    #Return: Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int]
    ##
    def getMove(self, currentState):
        #If we are out of moves, end our turn
        return Move(END, None, None)
    ####### END OF GET MOVE #######

    ##
    #getAttack
    #Parameters:
    #   currentState - The current state of the game at the time the Game is requesting
    #       a move from the player. (GameState)
    #   attackingAnt - A clone of the ant currently making the attack. (Ant)
    #   enemyLocation - A list of coordinate locations for valid attacks (i.e.
    #       enemies within range) ([list of 2-tuples of ints])
    #
    #Return: A coordinate that matches one of the entries of enemyLocations. ((int,int))
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]

    ##
    #registerWin
    #Description: The last method, registerWin, is called when the game ends and simply
    #indicates to the AI whether it has won or lost the game. This is to help with
    #learning algorithms to develop more successful strategies.
    #
    #Parameters:
    #   hasWon - True if the player has won the game, False if the player lost. (Boolean)
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass

    #
    #compressState
    #Description: Takes a state, and reduces the amount of information stored
    #
    #Parameters:
    #   currentState - the state to be reduced
    #
    #Returns: A list containing the reduced state list
    #
    def compressState(self, currentState):
        tempList = []
        myInventory = getCurrPlayerInventory(currentState)
        for food in foods:
            if food.coords[1] < 5:
                my_food_coords.append(food.coords)
        foodNum = myInventory.foodCount
        #numAnts = len(myInventory.ants)
        for ant in myInventory.ants:
            if ant.type == WORKER:
                workerCoords = ant.coords
                if ant.carrying == True:
                    isCarrying = True
                else:
                    isCarrying = False
        food_1_dist = approxDist(workerCoords, my_food_coords[0])
        food_2_dist = approxDist(workerCoords, my_food_coords[1])
        if tunnel[0] != []:
            tunnelDist = tunnel[0].coords
        else:
            tunnelDist = 100 #really big value

        tempList = [foodNum, workerCoords, isCarrying, food_1_dist, food_2_dist, tunnelDist]
        return tempList
