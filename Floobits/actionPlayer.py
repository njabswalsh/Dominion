import collections, util, math, random, copy
import cardUtils
from DominionPlayer import DominionPlayer


#An attempt to use the same weighted average reward strategy to play actions.  
#Abandoned this approach when we saw such good results with expectimax
class actionPlayer(DominionPlayer):
    
    def __init__(self, mdp, discount, explorationProb=0.2, verbose=False, usingCachedWeights=False, cachingWeights=False, cacheStringKey=""):
        self.verbose = verbose
        self.mdp = mdp
        self.discount = discount
        self.explorationProb = explorationProb
        self.weights = {} #weights is a dict of feature to (timesVisited, weight), where weight is the average reward
        self.numIters = 0
        self.usingCachedWeights = usingCachedWeights
        self.cachingWeights = cachingWeights
        self.cacheStringKey = cacheStringKey

    def featureExtractor(self, state, action):
        kingdom, deck, hand, drawPile, discardPile, phase, turn, buys, actions, money, cardsPlayed = state
        actionType, cardID = action
        actionCardEffects = cardUtils.getCardEffectsFromCardID(cardID)
        features = []
        possibleActions = self.mdp.actions(state)
        features.append(("possibleActions:" + str(possibleActions) + "numActions" + str(actions) + "action:" + str(action), 1))
        return features
    
    def getV(self, state, action):
        score = 0
        if state != None:
            features = self.featureExtractor(state, action)
            for feature, v in features:
                if feature in self.weights:
                    timesVisited, weight = self.weights[feature]
                    score += (1.0 / len(features)) * weight * v
        return score

    def backpropagateReward(self, reward, allStates, allStatesAndActions):
        for state, action in allStatesAndActions:
            for feature, value in self.featureExtractor(state, action):
                if feature in self.weights:
                    timesVisited, weight = self.weights[feature]
                    newWeight = ((timesVisited + 0.0) / (timesVisited + 1)) * weight + ((1 + 0.0) / (timesVisited + 1)) * reward
                    self.weights[feature] = (timesVisited + 1, newWeight)
                else:
                    self.weights[feature] = (1, reward)
    
    def endOfGame(self, reward):
        self.backpropagateReward(reward, allStates, allStatesAndActions)
        pass
    
    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        if state == None:
            print "GET Q CALLED ON NONE STATE - does this happen?"
        if state != None:
            for f, v in self.featureExtractor(state, action):
                score += self.weights[f] * v
                
        return score
        
    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        #return 1.0 / math.sqrt(self.numIters)
        return .1

    def incorporateFeedback(self, state, action, reward, newState):
        return
        #reward = money + buys * (money / 4.0 )
        residual = 0
        if newState != None:
            residual += (reward + (self.discount * max(self.getQ(newState, nextAction) for nextAction in self.mdp.actions(newState)))) - self.getQ(state, action)
        else:
            residual += reward - self.getQ(state, action)
            
        #else the newState == None, meaning it's the end of the game, 
        # so the residual is just reward - getQ(state, action)

        for feature, value in self.featureExtractor(state, action):
            self.weights[feature] += self.getStepSize() * residual * value


    def getAction(self, state, actions, otherPlayerStates=[]):
        self.numIters += 1
        #if no more actions it means it's the end of the game
        if actions == ["idle"]:
            if self.verbose:
                "Returning idle"
            return "idle" #don't compute succAndProbReward
        if random.random() < self.explorationProb:
            if self.verbose:
                "Returning random action due to exploration"
            return random.choice(actions)
        else:
            bestAction = None
            bestActionScore = float('-inf')
            for action in actions:
                actionScore = 0
                actionScore += self.getV(state, action)
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
            
    def getPlayerName(self):
        return "Action Player"
