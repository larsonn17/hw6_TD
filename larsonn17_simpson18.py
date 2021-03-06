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
        self.tunnelCoords = (6,1)
        self.anthillCoords = (2,2)

        #loads utility file if it is present, leaves list empty otherwise
        self.utilityList = []
        self.stateList = []
        if os.path.exists('larsonn17_simpson18_utilities.pk1'):
            print " Files exist, loading"
            self.utilityList = self.readUtility()
            self.stateList = self.readState()
        else:
            print " No previous state/utility files"

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
            return[self.anthillCoords, self.tunnelCoords, (0,3), (0,2), (0,1), (0,0), (1,3),(1,2), (1,1), (1,0), (9,3)];    #grass placement
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

        #randomly select a random move to allow for learning
        chance = random.randint(1,10)
        if chance > 8 and len(moveList) > 2:
            move = moveList[random.randint(0,len(moveList) - 1)]
            nextState = getNextState(currentState, move)
            currStateUtility = self.updateUtility(currentState, nextState)
            return move

        myInv = getCurrPlayerInventory(currentState)
        #only allow AI to construct additional units in certain situations,
        #training for this is outside scope of our implementation
        ##build a ranged soldier (max 1)
        if(getAntAt(currentState, self.anthillCoords) == None and myInv.foodCount >= 4
        and (len(getAntList(currentState, currentState.whoseTurn, (R_SOLDIER,))) < 1)):
                moveList.append(Move(BUILD, [self.anthillCoords], R_SOLDIER))
        ##build a worker if our original is lost
        if(getAntAt(currentState, self.anthillCoords) == None and myInv.foodCount >= 1
        and (len(getAntList(currentState, currentState.whoseTurn, (WORKER,))) < 1)):
            moveList.append(Move(BUILD, [self.anthillCoords], WORKER))

        for move in moveList:
            #get what the next state will look like if current move is performed
            nextState = getNextState(currentState, move)
            currStateUtility = self.updateUtility(currentState, nextState)
            #find the state with the best outcome
            if currStateUtility > bestUtility:
               bestUtility = currStateUtility
               bestMove = move
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
        #write to the utility and state
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
        all_food_coords = []
        isCarrying = 0
        workerCoords = (0,0)
        rsoldierCoord = None
        playerQueen = None
        enemyQueen = None

        for inv in currentState.inventories:
            if inv.player == currentState.whoseTurn:
                playerInv = inv
            else:
                enemyInv = inv
                numEnemy = len(enemyInv.ants)
                for ant in enemyInv.ants:
                    if ant.type == QUEEN:
                        enemyQueen = ant
        #all food locations
        for food in getConstrList(currentState, None, (FOOD,)):
            all_food_coords.append(food.coords)

        foodNum = playerInv.foodCount
        #get information about our ants
        for ant in playerInv.ants:
            if ant.type == QUEEN:
                playerQueen = ant
            if ant.type == R_SOLDIER:
                rsoldierCoord = ant.coords
            if ant.type == WORKER:
                workerCoords = ant.coords
                for coords in all_food_coords:
                    if workerCoords == coords:
                        isCarrying = 1
                if ant.carrying == True:
                    isCarrying = 1
                if isCarrying and (ant.coords == self.tunnelCoords or ant.coords == self.anthillCoords):
                    isCarrying = 0
                    foodNum += 1

        #checks to see if anyone has won/lost
        if enemyQueen is None or playerInv.foodCount >= 12 or (len(enemyInv.ants) == 1 and enemyInv.foodCount == 0):
            win = 1
        elif playerQueen is None or enemyInv.foodCount >= 12 or (len(playerInv.ants) == 1 and playerInv.foodCount == 0):
            win = 0
        else:
            win = 0.5

        tempList = [win, foodNum, workerCoords, isCarrying, rsoldierCoord, numEnemy]
        return tempList

    #
    #updateUtility
    #
    #Description: takes a the current state and determines if it
    #has been visited before
    #
    #Parameters:
    #   currentState - current state of the game
    #   potentialState - the potential state if the move was made
    #
    #Returns: Utility of state
    def  updateUtility(self, currentState, potentialState):

        #get the compressed current state
        currState = self.compressState(currentState)

        #get the compressed next state
        nextState = self.compressState(potentialState)

        #append the state and utility if the current state is new
        if currState not in self.stateList:
            self.stateList.append(currState)
            indexCurr = self.stateList.index(currState)
            self.utilityList.append(0)

        #get the index of the current state in list
        indexCurr = self.stateList.index(currState)

        #append the state and utility if the next state is new
        if nextState not in self.stateList:
            self.stateList.append(nextState)
            self.utilityList.append(0)
        else: #else update the utility of the current state using TD learning algorithm
            indexNext = self.stateList.index(nextState)
            self.utilityList[indexCurr] += self.alpha*(self.reward(currState) + self.lambdA*self.utilityList[indexNext] - self.utilityList[indexCurr])
            print self.utilityList[indexCurr]

        #return the utility of the current state
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
        if compressStated[0] == 1:
            return 1 #won game
        elif compressStated[0] == 0:
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
    #   stateList - a list of state values
    #
    #Reference: https://docs.python.org/2/library/pickle.html
    #
    def writeStateAndUtil(self, utilityList, stateList):
        utilityFile = open("AI/" + 'larsonn17_simpson18_utilities.pk1', 'wb')
        pickle.dump(utilityList, utilityFile)
        utilityFile.close()

        stateFile = open("AI/" + 'larsonn17_simpson18_states.pk1', 'wb')
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
