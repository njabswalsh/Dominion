import cardUtils


# Dominion Feature Extractor
#deck, hand, drawPile, discardPile, phase, turn = state
def computeHandValue(hand):
    handValue = 0
    for cardID in hand:
        card = cardUtils.getCardFromID(cardID)
        if card.cardType == "treasure":
            handValue += card.treasureValue
    return handValue
    
def tdDominionFeatureExtractor(state):
    deck, hand, drawPile, discardPile, phase, turn = state
    features = []
    
    handValue = computeHandValue(hand)
    features.append(("handValue" + str(handValue), 1))
    
    vPoints = deck[3] + 3 * deck[4] + 6 * deck[5]
    features.append(("vPoints"+ str(vPoints), 1))
  
    for cardID in deck:
        features.append(("numOfCardsInDeckOfType" + str(cardID) + "=" + str(deck[cardID]), 1)) 
    return features
    
def qDominionFeatureExtractor(state, action):
    deck, hand, drawPile, discardPile, phase, turn = state
    features = []    
    return features
 