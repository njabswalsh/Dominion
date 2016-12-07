import cardUtils, util, copy
from collections import Counter


kingdom = Counter({0:100, 1:100, 2:100, 3:8, 4:8, 5:1})

#startDeck = Counter({0:7,3:3})
#startDeck = Counter({0:7})
#hand = (0,0,0,3,3)
newDrawPile = Counter({0:8})
drawIndex = 0
handSize = 0
hand = []
numCardsToDraw = 5
numHands = util.nchoosek(sum(newDrawPile.values()), numCardsToDraw)
print "numHands:", numHands
handsAndProbs = []
def computeHandsAndProbs(kingdom, hand, numHands, results, drawPile, drawIndex, handSize):
    if drawIndex >= len(kingdom):
        return
    if len(hand) == handSize:
        prob = computeHandProbability(hand, drawPile, numHands)
        results.append((list(hand), prob))
        return
    if drawPile[drawIndex] > 0:
        hand.append(drawIndex)
        drawPile[drawIndex] -= 1
        computeHandsAndProbs(kingdom, hand, numHands, results, drawPile, drawIndex, handSize)
        drawPile[drawIndex] += 1
        hand.pop()
    computeHandsAndProbs(kingdom, hand, numHands, results, drawPile, drawIndex + 1, handSize)

def computeHandProbability(hand, drawPile, numHands):
    prob = 1
    handCounter = util.HashableDict(Counter(hand))
    for cardID in handCounter.keys():
        prob *= util.nchoosek(drawPile[cardID] + handCounter[cardID], handCounter[cardID])
    prob /= (0.0 + numHands)
    return prob
    
print computeHandsAndProbs(kingdom, hand, numHands, handsAndProbs, Counter(newDrawPile), drawIndex, numCardsToDraw)


