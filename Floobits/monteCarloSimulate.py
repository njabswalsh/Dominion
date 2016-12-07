import collections, random

# Perform |numTrials| of the following:
# On each trial, takes in a start state an plays randomly for a game.
# After all trial, returns all rewards.
def tdMonteCarloSimulate(mdp, startState, numTrials=1, maxIterations=1, verbose=False,
             sort=False):
    # Return i in [0, ..., len(probs)-1] with probability probs[i].
    def sample(probs):
        target = random.random()
        accum = 0
        for i, prob in enumerate(probs):
            accum += prob
            if accum >= target: return i
        raise Exception("Invalid probs: %s" % probs)

    def getAction(state, actions):
        return random.choice(actions)

    totalRewards = []  # The rewards we get on each trial
    for trial in range(numTrials):
        state = startState
        sequence = [state]
        totalDiscount = 1
        totalReward = 0
        for _ in range(maxIterations):
            actions = mdp.actions(state)
            #if it's an end state, the only action will be idle.
            if actions == ["idle"]:
                break
            action = getAction(state, mdp.actions(state))
            transitions = mdp.succAndProbReward(state, action)
            if sort: transitions = sorted(transitions)
            
            # IN MONTE CARLO SIMULATIONS, JUST RUN TRIALS, DON'T INCORPORATE FEEDBACK
            if len(transitions) == 0:
                break

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
    #print "Total monte carlo reward:", totalRewards
    return totalRewards