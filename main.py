import cardUtils, util, copy
from collections import Counter
from simulate import simulate
from featureExtractor import tdDominionFeatureExtractor
from featureExtractor import qDominionFeatureExtractor
from tdlearning import TDLearningAlgorithm
from qLearning import QLearningAlgorithm

class ValueIteration(util.MDPAlgorithm):

    # Implement value iteration.  First, compute V_opt using the methods 
    # discussed in class.  Once you have computed V_opt, compute the optimal 
    # policy pi.  Note that ValueIteration is an instance of util.MDPAlgrotithm, 
    # which means you will need to set pi and V (see util.py).cou
    def solve(self, mdp, epsilon=0.001):
        mdp.computeStates()
        # BEGIN_YOUR_CODE (around 15 lines of code expected)
        def computeActionValue(state, action, vPrevious):
            total = 0.0
            for newState, prob, reward in mdp.succAndProbReward(state, action):
                total += prob * (reward + (mdp.discount() * vPrevious[newState]))
            return total
        def maxDiff(v, vPrevious):
            m = max(abs(v[state] - vPrevious[state]) for state in mdp.states)
            return m
        #TODO: make this not use dicts (non-hashable states)
        pi = {}
        v = {state:0.0 for state in mdp.states}
        while True:
            vPrevious = copy.copy(v)
            for state in mdp.states:
                if mdp.actions(state) == []:
                    pi[state] = None
                else:
                   actionValues = {action:computeActionValue(state, action, vPrevious) for action in mdp.actions(state)}
                   optAction, optValue = max(actionValues.iteritems(), key=lambda pair: pair[1])
                   v[state] = optValue
                   pi[state] = optAction
                   if mdp.succAndProbReward(state, optAction) == []:
                       pi[state] = None
            if maxDiff(v, vPrevious) <= epsilon:
                break
        self.V = v
        self.pi = pi
        # END_YOUR_CODE

class DominionMDP:
    def __init__(self):
        # BEGIN_YOUR_CODE (around 5 lines of code expected)
        #kingdom: possible cards in stock to buy (by ID)
        self.kingdom = [0, 1, 2, 3, 4, 5] # TODO save this better/read this better
        self.handSize = 5
        self.maxTurns = 4
        return
        # END_YOUR_CODE

    def startState(self):
        # BEGIN_YOUR_CODE (around 5 lines of code expected)
        #starting deck by ID, number of cards in that ID
        deck = util.Hashabledict(Counter({0:7, 3:3})) # TODO Make this better: read from human readable input/sparse vector?
        hand = (0,0,0,0,0) # TODO randomize?
        drawPile = copy.copy(deck)
        for cardID in hand:
        	drawPile[cardID] -= 1
        discardPile = util.Hashabledict(Counter())
        phase = "buy"
        turn = 0
        return (deck, hand, drawPile, discardPile, phase, turn)
        # END_YOUR_CODE

    # Return set of actions possible from |state|. Actions is a list of ("buy cardName") strings.
    def actions(self, state):
        def computeHandValue(hand):
            handValue = 0
            for cardID in hand:
                card = cardUtils.getCardFromID(cardID)
                if card.cardType == "treasure":
                    handValue += card.treasureValue
            return handValue
        # BEGIN_YOUR_CODE (around 5 lines of code expected)
        results = []
        results.append(("buy", -1))
        deck, hand, drawPile, discardPile, phase, turn = state
        if turn == self.maxTurns:
            return []
        if phase == "buy":
            handValue = computeHandValue(hand)
            for cardID in self.kingdom:
                buyCard = cardUtils.getCardFromID(cardID)
                if buyCard.cardCost <= handValue:
                    results.append(("buy", buyCard.cardID))
        #print handValue
        return results
        # END_YOUR_CODE

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.
    def succAndProbReward(self, state, action):
        # BEGIN_YOUR_CODE (around 5 lines of code expected)
        #do we need to have handValue in the state...?
        deck, hand, drawPile, discardPile, phase, turn = state
        actionType, buyCardID = action
        nextDeck = util.Hashabledict(Counter(deck))
        nextDiscardPile = util.Hashabledict(Counter(discardPile))
        if actionType == "buy":
            if buyCardID != -1:
                #Buy the card
                nextDeck[buyCardID] += 1
                nextDiscardPile[buyCardID] += 1
        #Discard your hand
        for cardID in hand:
            nextDiscardPile[cardID] += 1
        #Compute new hands and probabilities
        newHand = []
        handSize = self.handSize
        if sum(drawPile.values()) < self.handSize:
            #Reshuffle. 
            #TODO: fix.
            for cardID in drawPile.keys():
                for i in range(drawPile[cardID]):
                    newHand.append(cardID)
                    drawPile[cardID] -= 1
                    handSize -= 1
            drawPile = nextDiscardPile
            nextDiscardPile = util.Hashabledict(Counter())
        

        def computeHandProbability(hand, drawPile, numHands):
            prob = 1
            handCounter = util.Hashabledict(Counter(hand))
            for cardID in handCounter.keys():
                prob *= util.nchoosek(drawPile[cardID] + handCounter[cardID], handCounter[cardID])
            prob /= (0.0 + numHands)
            return prob

        def computeHandsAndProbs(hand, numHands, results, drawPile, drawIndex, handSize):
            if drawIndex >= len(self.kingdom):
                return
            if len(hand) == handSize:
                prob = computeHandProbability(hand, drawPile, numHands)
                results.append((list(hand), prob))
                #print "appended"
                #print results
                return
            #print "drawPile: ",drawPile,"drawIndex: ",drawIndex   
            if drawPile[drawIndex] > 0:
                hand.append(drawIndex)
                drawPile[drawIndex] -= 1
                computeHandsAndProbs(hand, numHands, results, drawPile, drawIndex, handSize)
                drawPile[drawIndex] += 1
                hand.pop()
            computeHandsAndProbs(hand, numHands, results, drawPile, drawIndex + 1, handSize)

        numHands = util.nchoosek(sum(drawPile.values()), handSize)
        handsAndProbs = []
        computeHandsAndProbs([], numHands, handsAndProbs, drawPile, 0, handSize)
        #print "handsAndProbs: ",handsAndProbs

        reward = 0
        if turn == self.maxTurns - 1:
            reward = nextDeck[3] + 3 * nextDeck[4] + 6 * nextDeck[5] #TODO: make readable. extract into method (sum victory points).
        

        #deck, hand, drawPile, discardPile, phase, turn = state
        #(newState, prob, reward)

        results = []
        for handAddition, prob in handsAndProbs:
            nextHand = newHand + handAddition
            nextDrawPile = util.Hashabledict(Counter(drawPile))
            for cardID in handAddition:
                nextDrawPile[cardID] -= 1
            newState = (nextDeck, tuple(nextHand), nextDrawPile, nextDiscardPile, phase, turn + 1)
            results.append((newState, prob, reward))

        #print "Results:",results
        return results
        # END_YOUR_CODE

    def discount(self):
        # BEGIN_YOUR_CODE (around 5 lines of code expected)
        return 1
        # END_YOUR_CODE

    def computeStates(self):
        self.states = []
        queue = []
        self.states.append(self.startState())
        queue.append(self.startState())
        while len(queue) > 0:
            state = queue.pop()
            for action in self.actions(state):
                #print action
                for newState, prob, reward in self.succAndProbReward(state, action):    
                    self.states.append(newState)
                    queue.append(newState)

cardUtils.initializeCardList("cards.txt")

def printActions(actions):
    for action in actions:
        actionType, cardID = action
        print actionType, cardUtils.getCardFromID(cardID).cardName, ",",
    print
dominion = DominionMDP()
'''vi = ValueIteration()
vi.solve(dominion)
for state, action in vi.pi.iteritems():
    if action != None: 
        if action[0] == 'buy':
            buy, buyCardID = action
            if buyCardID == -1:
                cardName = "None"
            else:
                cardName = cardUtils.getCardFromID(buyCardID).cardName
            #print "State: ", state, "Action:", buy, cardName'''
#print "Policy: ", vi.pi
#actions = dominion.actions(dominion.startState())
#printActions(dominion.actions(dominion.startState()))
#dominion.succAndProbReward(dominion.startState(), actions[0])
#dominion.succAndProbReward(dominion.startState(), actions[1])

tdFeatureExtractor = tdDominionFeatureExtractor
qFeatureExtractor = qDominionFeatureExtractor
discount = 1
td = TDLearningAlgorithm(dominion, discount, tdFeatureExtractor)
qLearn = QLearningAlgorithm(dominion.actions, discount, qFeatureExtractor)
rewards = simulate(dominion, td, 100)
print "Average reward: ", sum(rewards) / (0.0 + len(rewards))


