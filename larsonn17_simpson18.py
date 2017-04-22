# -*- coding: latin-1 -*-
import random
import pickle
import sys
import os
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

        #Constants
        self.alpha = .2
        self.lambdA= .8

        #loads utility file if it is present, leaves list empty otherwise
        self.utilityList = []
        self.stateList = []
        #testList = [True, 4, -5, False, True] #test list to use
        #self.writeStateAndUtil(testList, testList)
        self.utilityExists = False
        if os.path.exists('larsonn17_simpson18_utilities.pk1'):
            print " File exists!"
            self.utilityList = self.readUtility()
            self.stateList = self.readState()
            self.utilityExists = True
            #print " Utility File: " + str(self.utilityFile)
        else:
            print " File DNE"

        self.loadedFiles = 1


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
            return[(0,0), (6,1), (0,3), (1,3), (2,3), (3,3), (4,3),( 6,3), (7,3), (8,3), (9,3)];    #grass placement
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
        #look at all moves, ignoring build moves
        moveList = listAllMovementMoves(currentState)
        bestMove = None
        bestUtility = -100

        for move in moveList:
            #get what the next state will look like if current move is performed
            nextState = getNextState(currentState, move)
            currStateUtility = self.addUtility(currentState, nextState)
            if currStateUtility > bestUtility:
               bestUtility = currStateUtility
               bestMove = move

        #add in random chance for move
        numStates =  len(self.utilityList)
        chance = (1/numStates)*(random.randint(1,1000))
        if chance > 10:
            bestMove =  moveList[random.randint(0,len(moves) - 1)]
        if bestMove != None:
            return bestMove
        else:#If we are out of moves, end our turn
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
        self.writeStateAndUtil(self.utilityList, self.stateList)
        print "Number of States: " + str(len(self.stateList))
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
        my_food_coords = []
        all_food_coords = []
        tunnelDist = 100
        food_1_dist = 100
        food_2_dist = 100
        workerCoords = (0,0)
        isCarrying = 0

        for inv in currentState.inventories:
            if inv.player == currentState.whoseTurn:
                playerInv = inv
            else:
                enemyInv = inv
                for ant in enemyInv.ants:
                    if ant.type == QUEEN:
                        enemyQueen = ant

        for food in getConstrList(currentState, None, (FOOD,)):
            if food.coords[1] < 5:
                my_food_coords.append(food.coords)
            all_food_coords.append(food.coords)

        foodNum = playerInv.foodCount
        tunnel = getConstrList(currentState, currentState.whoseTurn, (TUNNEL,))
        anthill = getConstrList(currentState, currentState.whoseTurn, (ANTHILL,))
        anthillCoords = anthill[0].coords

        for ant in playerInv.ants:
            if ant.type == QUEEN:
                playerQueen = ant
            if ant.type == WORKER:
                workerCoords = ant.coords
                for coords in all_food_coords:
                    if workerCoords == coords:
                        isCarrying = 1
                if ant.carrying == True:
                    isCarrying = 1
                food_1_dist = approxDist(workerCoords, my_food_coords[0])
                food_2_dist = approxDist(workerCoords, my_food_coords[1])
                if tunnel != None:
                    tunnelCoords = tunnel[0].coords
                    tunnelDist = approxDist(workerCoords, tunnelCoords)
                    if isCarrying and (ant.coords == tunnelCoords or ant.coords == anthillCoords):
                        isCarrying = 0
                        foodNum += 1

        #checks to see if anyone has won/lost
        if enemyQueen is None or playerInv.foodCount >= 12 or (len(enemyInv.ants) == 1 and enemyInv.foodCount == 0):
            win = 1
        elif playerQueen is None or enemyInv.foodCount >= 12 or (len(playerInv.ants) == 1 and playerInv.foodCount == 0):
            win = 0
        else:
            win = 0.5

        tempList = [foodNum, workerCoords, isCarrying, food_1_dist, food_2_dist, tunnelDist, win]
        return tempList

    #
    #addUtility
    #
    #Description: takes a the current state and determines if it
    #has been visited before
    #
    #Parameters:
    #   currentState - current state of the game
    #   potentialState - the potential state if the move was made
    #
    #Returns: Utility of state
    def addUtility (self, currentState, potentialState):
        currState = self.compressState(currentState)
        nextState = self.compressState(potentialState)

        #edge cases
        if self.loadedFiles:
            self.stateList.append(currState)
            self.utilityList.append(0)
            self.loadedFiles = 0

        inv = getCurrPlayerInventory(currentState)
        if len(inv.ants) < 2:
            self.stateList.append(currState)
            self.utilityList.append(0)


        indexCurr = self.stateList.index(currState)

        if currState not in self.stateList:
            self.utilityList[indexCurr] = 0

        if nextState not in self.stateList:
            self.stateList.append(nextState)
            self.utilityList.append(0)
        else:
            indexNext = self.stateList.index(nextState)
            self.utilityList[indexCurr] += self.alpha*(self.reward(currState) + self.lambdA*self.utilityList[indexNext] - self.utilityList[indexCurr])

        return self.utilityList[indexCurr]


    #
    #reward
    #
    #Description: takes a list, and returns a value to the AI
    #
    #Parameters:
    #   compressStated - a compressState (list)
    #
    #Returns: A value between 1 & -1
    def reward(self, compressStated):
        if compressStated[6] == 1:
            return 1 #won game
        elif compressStated[6] == 0:
            return -1.0 #lost game
        else:
            return -0.1
    #
    #writeList
    #
    #Description: Takes a list of state utilities, prints it out to a file
    #
    #Parameters
    #   utilityList - a list of utility values
    #
    #Reference: https://docs.python.org/2/library/pickle.html
    #
    def writeStateAndUtil(self, utilityList, stateList):
        utilityFile = open('larsonn17_simpson18_utilities.pk1', 'wb')
        pickle.dump(utilityList, utilityFile)
        utilityFile.close()

        stateFile = open('larsonn17_simpson18_states.pk1', 'wb')
        pickle.dump(stateList, stateFile)
        stateFile.close()


    #
    #readUtility
    #
    #Description: Reads a list of utility values from a file
    #
    #Returns: A list of state utilities
    #
    #Reference: https://docs.python.org/2/library/pickle.html
    #
    def readUtility(self):
        readList = []
        utilityFile = open('larsonn17_simpson18_utilities.pk1', 'rb')
        readList = pickle.load(utilityFile)
        utilityFile.close()
        return readList

    #
    #readState
    #
    #Description: Reads a list of utility values from a file
    #
    #Returns: A list of state utilities
    #
    #Reference: https://docs.python.org/2/library/pickle.html
    #
    def readState(self):
        readList = []
        stateFile = open('larsonn17_simpson18_states.pk1', 'rb')
        readList = pickle.load(stateFile)
        stateFile.close()
        return readList
