import collections, util, math, random, copy


# Performs Q-learning.  Read util.RLAlgorithm for more information.
# actions: a function that takes a state and returns a list of actions.
# discount: a number between 0 and 1, which determines the discount factor
# featureExtractor: a function that takes a state and action and returns a list of (feature name, feature value) pairs.
# explorationProb: the epsilon value indicating how frequently the policy
# returns a random action.
class TDLearningAlgorithm():
    def __init__(self, mdp, discount, featureExtractor, explorationProb=0.2):
        self.mdp = mdp
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = collections.Counter()
        self.numIters = 0

    # Return the Q function associated with the weights and features
    def getV(self, state):
        score = 0
        for f, v in self.featureExtractor(state):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state, actions):
        self.numIters += 1
        #if no more actions it means it's the end of the game
        if actions == []:
            return None
        if random.random() < self.explorationProb:
            return random.choice(actions)
        else:
            bestAction = None
            bestActionScore = float('-inf')
            
            
            for action in actions:
                actionScore = 0
                #(newState, prob, reward)
                probAndRewards = self.mdp.succAndProbReward(state, action)
                for newState, prob, reward in probAndRewards:
                    actionScore += self.getV(newState) * prob
                if actionScore >= bestActionScore:
                    bestActionScore = actionScore
                    bestAction = action
                #print "action, actionScore: ", action, actionScore

            #return max((sum(getV(newState) * prob for newState, prob, reward in mdp.succAndProbRewards(state, action)), action) for action in actions)[1]
            return bestAction
            
            
            #max((self.getQ(state, action), action) for action in self.actions(state))[1]

    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 0.1

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        # BEGIN_YOUR_CODE (around 15 lines of code expected)
        residual = (reward + (self.discount * self.getV(newState))) - self.getV(state)
        print "Residual:",residual
        for feature, value in self.featureExtractor(state):
            self.weights[feature] += self.getStepSize() * residual * value
        # END_YOUR_CODE

