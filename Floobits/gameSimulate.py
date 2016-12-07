import collections, random, util, cardUtils

# Params: players - a list of players
#kingdom, deck, hand, drawPile, discardPile, phase, turn, buys, actions, money, cardsPlayed = state
def simulateDominion(mdp, players, numGames=1, maxTurns=200, verbose=False,
             sort=False):
    # Return i in [0, ..., len(probs)-1] with probability probs[i].
    def sample(probs):
        target = random.random()
        accum = 0
        for i, prob in enumerate(probs):
            accum += prob
            if accum >= target: return i
        raise Exception("Invalid probs: %s" % probs)
    
    #totalRewards = []  # The rewards we get on each trial
    for game in xrange(numGames):
        state = mdp.startState()
        sequence = [state]
        totalDiscount = 1
        playerStates = [state] * len(players)
        playerHistory = [[] for _ in range(len(players))]
        for _ in range(maxTurns):
            for playerID in xrange(len(players)):

                otherPlayerStates = []
                for otherPlayerID in xrange(len(players)):
                    if playerID != otherPlayerID:
                        otherPlayerStates.append(playerStates[otherPlayerID])

                state = playerStates[playerID]
                if mdp.endOfGame(state):
                    #print "end of game"
                    playerStates[playerID] = state
                    player.incorporateFeedback(state, action, 0, None)
                    break
                player = players[playerID]
                actions = mdp.actions(state)
                action = player.getAction(state, actions)
                transitions = mdp.succAndProbs(state, action, otherPlayerStates)
                if sort: transitions = sorted(transitions)
    
                # Choose a random transition
                i = sample([prob for newState, prob, reward in transitions])
                newState, prob, reward = transitions[i]
                playerHistory[playerID].append(action)
                playerHistory[playerID].append(reward)
                playerHistory[playerID].append(newState)

                player.incorporateFeedback(state, action, reward, newState)
                totalDiscount *= mdp.discount()
                playerStates[playerID] = newState
                #Update player states with new kingdom
                newKingdom = newState[0]
                for otherPlayerID in xrange(len(players)):
                    if playerID != otherPlayerID:
                        kingdom, deck, hand, drawPile, discardPile, phase, turn = playerStates[otherPlayerID]
                        playerStates[otherPlayerID] = (util.HashableDict(newKingdom), deck, hand, drawPile, discardPile, phase, turn)
        if verbose:
            for playerID in xrange(len(players)):
                print "###############################################" 
                print "###############################################" 
                print "###############################################" 
                print "Player", playerID, "Game ", game, ":"
                printGameHistory(playerHistory[playerID], mdp, allPlayerStates=playerStates, playerID=playerID)

def printGameHistory(gameHistory, mdp, allPlayerStates=[], playerID=None):
    #TODO: readability: /3 , * 3 ???
    print "player states: ", allPlayerStates
    for i in range(len(gameHistory) / 3):
        state = gameHistory[i * 3 + 2]
        kingdom, deck, hand, drawPile, discardPile, phase, turn, buys, actions, money, cardsPlayed = state
        print "Turn:", turn,
        if phase == "buy":
            print "Money:", money, 
        action = gameHistory[i * 3]
        if action[0] == 'buy':
                buy, buyCardID = action
                if buyCardID == -1:
                    cardName = "None"
                else:
                    cardName = cardUtils.getCardFromID(buyCardID).cardName
                print "Action:", buy, cardName
        else:
            print action
        print "Deck after:",
        cardUtils.printDeck(deck)
        print "Drew hand: ", hand
        print "###############################################" 
        if mdp.endOfGame(state):
            print "end of game"
            for ID in range(len(allPlayerStates)):
                kingdom1, deck1, hand1, drawPile1, discardPile1, phase1, turn1, buys1, actions1, money1, cardsPlayed1 = allPlayerStates[ID]

                otherPlayerStates = list(allPlayerStates)
                otherPlayerStates.remove(allPlayerStates[ID])
                print "Player ", str(ID), "Game Reward: ", str(mdp.computeReward(allPlayerStates[ID], otherPlayerStates))
                print "Number of Victory Points:", str(cardUtils.computeVictoryPoints(deck1))
            print "Number of Turns:", turn

