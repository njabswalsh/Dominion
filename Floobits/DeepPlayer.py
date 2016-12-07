import collections, util, math, random, copy
from DominionPlayer import DominionPlayer
import cardUtils
from ExpectimaxActionPhasePlayer import ExpectimaxActionPhasePlayer
from keras.models import Sequential
from keras.layers import Dense, Activation
from random import shuffle
import numpy as np
import featureExtractor as fe

# actions: a function that takes a state and returns a list of actions.
# featureExtractor: a function that takes a state and action and returns a list of (feature name, feature value) pairs.
# explorationProb: the epsilon value indicating how frequently the policy
# returns a random action.
class DeepPlayer(DominionPlayer):
    def setupModel(self):
        self.gameModel = Sequential()
        self.gameModel.add(Dense(output_dim=64, input_dim=self.networkInputSize))
        self.gameModel.add(Activation("relu"))
        self.gameModel.add(Dense(output_dim=1))
        self.gameModel.add(Activation("softmax"))

    def __init__(self, mdp, featureExtractor, explorationProb=0.2, actionPlayer=None, learning=False):
        self.verbose = False
        self.mdp = mdp
        self.explorationProb = explorationProb
        self.numIters = 0
        self.actionPlayer = actionPlayer
        self.learning = learning
        self.allStates = []
        self.featureExtractor = featureExtractor
        self.networkInputSize = fe.computeDeepFeatureLength(12, mdp.startKingdom)
        print self.networkInputSize
        self.setupModel()
        self.discount = 0.9

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state, actions, otherPlayerStates=[]):
        kingdom, deck, hand, drawPile, discardPile, phase, turn, buys, numActions, money, cardsPlayed = state
        self.numIters += 1
        #if no more actions it means it's the end of the game
        if actions == ["idle"]:
            print state
            raise Exception("ERROR: SHOULD NEVER GET HERE!")
        if phase == "action":
            if self.actionPlayer != None:
                action = self.actionPlayer.getAction(state, actions, otherPlayerStates=[])
                return action
        if random.random() < self.explorationProb:
            if self.verbose:
                "Returning random action due to exploration"
            return random.choice(actions)
        else:
            bestAction = None
            bestActionScore = float('-inf')
            for action in actions:
                actionScore = 0
                statesAndProbs = self.mdp.succAndProbs(state, action, otherPlayerStates)
                for newState, prob in statesAndProbs:
                    if self.mdp.endOfGame(newState):
                        actionScore += self.mdp.computeReward(newState, otherPlayerStates) * prob
                    else:
                        feature_vector = self.featureExtractor(state, otherPlayerStates)
                        actionScore += self.gameModel.predict(feature_vector) * prob
                if self.verbose:
                    print "Action: ",action, "Score:",actionScore
                    
                if actionScore >= bestActionScore:
                    bestActionScore = actionScore
                    bestAction = action
            if bestAction == None:
                print state
                print actions
                print "ERROR"
            if self.verbose:
                print "Best action: ", bestAction
            return bestAction


    # Doesn't update the weights until the end of the game, when endOfGame is called
    def incorporateFeedback(self, state, action, reward, newState, otherPlayerStates=[]):
        self.allStates.append((state, otherPlayerStates))
        return

    def backpropagateReward(self, reward, allStates):
        last_turn = allStates[-1][6]
        goals = []
        feature_vectors = []
        for i in shuffle(range(len(allStates))):
            state, otherPlayerStates = allStates[i]
            goals.append(reward * (self.discount ** (last_turn - state[6]))) 
            feature_vector = self.featureExtractor(state, otherPlayerStates)
            feature_vectors.append(feature_vector)
        model.train_on_batch(feature_vectors, goals)

    def endOfGame(self, reward):
        if self.learning:
            self.backpropagateReward(reward, self.allStates)
        self.allStates = []
        
    def getPlayerName(self):
        return "Deep Player"
            

