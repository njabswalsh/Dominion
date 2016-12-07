import collections, random, cardUtils, os


# Perform |numTrials| of the following:
# On each trial, take the MDP |mdp| (for example, DominionMDP) and 
# and simulates the game of Dominion according to the dynamics of
# the MDP.
# On each iteration/turn, it prints all possible actions and uses the 
# action entered by a human player.
# Each trial will run for at most |maxIterations|.
# Return the list of rewards that we get and total turns taken for each trial.
def humanSimulate(mdp, numTrials=1, maxIterations=200, verbose=False,
             sort=False):
    def getHumanAction(state):
        kingdom, deck, hand, drawPile, discardPile, phase, turn, buys, numActions, money, cardsPlayed = state
        print "State:", state
        actions = mdp.actions(state)
        print "Money:", money
        print "Buys:", buys
        print "Actions:", numActions
        print "Hand:",
        cardUtils.printHand(hand)
        print "Possible actions:"
        for i in range(len(actions)):
            action = actions[i]
            actionType, cardID = action
            print i, ":", actionType, cardUtils.getCardNameFromID(cardID),
            if actionType == "buy":
                print "(cost %d)" % cardUtils.getCardCostFromID(cardID),
                cardUtils.printCardEffects(cardID)
            else:
                cardUtils.printCardEffects(cardID)

        if len(actions) == 1:
            action = actions[0]
            actionType, cardID = action
            print "No choice to be made: ", actionType, cardUtils.getCardNameFromID(cardID)
            return action
        else:
            while True:
                try:
                    actionChoice = raw_input("Enter the number of your choice (q to quit): ")
                    if "q" in actionChoice:
                        exit()
                    action = actions[int(actionChoice)]
                    return action
                except IndexError:
                    print "That is not a valid action. Try again."
                except ValueError:
                    print "That is not a valid action. Try again."
    # Return i in [0, ..., len(probs)-1] with probability probs[i].
    def sample(probs):
        target = random.random()
        accum = 0
        for i, prob in enumerate(probs):
            accum += prob
            if accum >= target: return i
        raise Exception("Invalid probs: %s" % probs)

    totalRewards = []  # The rewards we get on each trial
    totalTurns = []
    for trial in range(numTrials):
        state = mdp.startState()
        sequence = [state]
        totalDiscount = 1
        totalReward = 0
        allStates = [] #keep track of all states so that we can backpropogate end reward

        for _ in range(maxIterations):
            allStates.append(state) 
            actions = mdp.actions(state)
            #if it's an end state, the only action will be idle.
            if actions == ["idle"]:
                break
            action = getHumanAction(state)
            transitions = mdp.succAndProbReward(state, action, otherPlayerStates = [])

            # Choose a random transition
            i = sample([prob for newState, prob, reward in transitions])
            newState, prob, reward = transitions[i]
            sequence.append(action)
            sequence.append(reward)
            sequence.append(newState)
            totalReward += totalDiscount * reward
            totalDiscount *= mdp.discount()
            state = newState
        if verbose:
            print "Trial %d (totalReward = %s): %s" % (trial, totalReward, sequence)
        totalRewards.append(totalReward)
        kingdom, deck, hand, drawPile, discardPile, phase, turn, buys, actions, money, cardsPlayed = state
        totalTurns.append(turn)
        print "End of game, your reward is:", totalReward, "after", turn, "turns"

    if verbose:
        print "Total Rewards:", totalRewards
        print "Total Turns:", totalTurns
    return (totalRewards, totalTurns)


