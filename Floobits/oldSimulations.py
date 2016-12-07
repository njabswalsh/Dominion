if (False):
    vi = ValueIteration()
    vi.solve(dominion)
    for state, action in vi.pi.iteritems():
        if action != "idle": 
            if action[0] == 'buy':
                buy, buyCardID = action
                if buyCardID == -1:
                    cardName = "None"
                else:
                    cardName = cardUtils.getCardFromID(buyCardID).cardName
                print "State: ", state, "Action:", buy, cardName

if (False):
    tdFeatureExtractor = tdDominionFeatureExtractor
    discount = 1
    td = TDLearningAlgorithm(dominion, discount, tdFeatureExtractor)
    rewards = tdSimulate(dominion, td, 500)
    print "TD Average reward: ", sum(rewards) / (0.0 + len(rewards))
    print "TDweights:", td.weights
    
    td.explorationProb = 0
    rewards = tdSimulate(dominion, td, 500)
    print "TD Average reward no exploring: ", sum(rewards) / (0.0 + len(rewards))
    print "TDweights no exploring:", td.weights

if (False):
    qFeatureExtractor = qDominionFeatureExtractor
    discount = 1
    qLearn = QLearningAlgorithm(dominion.actions, discount, qFeatureExtractor)
    qRewards = qSimulate(dominion, qLearn, 100)
    print "Q Average reward:", sum(qRewards) / (0.0 + len(qRewards))
    print "Qweights:", qLearn.weights

#for run in range(20):
if usingBackpropagate:
#    print "Run:", run
    trainingExplorationProb = 0
    playingExplorationProb = 0
    
    backpropagatePlayer.explorationProb = trainingExplorationProb
    #NOTE: SEE cacheStringKeyS FILE FOR CACHES
    backpropagatePlayer.usingCachedWeights = True
    backpropagatePlayer.cachingWeights = True
    backpropagatePlayer.cacheStringKey = "testingkeystringname"
    #backpropagatePlayer.cacheStringKey = "backprop4prov"
    cacheReductionFactor = 1
    players = []
    players.append(backpropagatePlayer)

    print "TRAINING PHASE"
    for playerID in range(len(players)):
        print "Player ", playerID, ":", players[playerID].getPlayerName()
        if (players[playerID].usingCachedWeights):
            cacheStringKey = players[playerID].cacheStringKey
            print "Using Cached Weights from", cacheStringKey
            #Retrieve weights from cache so that it builds on already cached weights.
            cachedWeights = Counter()
            cacheWeightsBackpropagate.bpsetWeightsFromCache(dominion.startKingdom, cachedWeights, cacheStringKey, cacheReductionFactor)
            players[playerID].weights = cachedWeights
            print "Starting weights from cache:", players[playerID].weights
        else:
            print "Not Using Cached Weights"

    results = simulateDominion(dominion, players, numGames=50, maxTurns=100, verbose=False)
    allGameRewards, allGameTurns = results
    
    print "Backpropagate Player Learned Weights: ", backpropagatePlayer.weights

    for playerID in range(len(players)):
        if (players[playerID].cachingWeights): 
            cacheWeightsBackpropagate.bpcacheWeights(dominion.startKingdom, backpropagatePlayer.weights, backpropagatePlayer.cacheStringKey)
        
    print
    print
    print "PLAYING PHASE"  
 
    players.append(bigMoneyPlayer)
    #players.append(bigMoneyPlayer2)
    backpropagatePlayer.explorationProb = playingExplorationProb
    #backpropagatePlayer.verbose = True
    results = simulateDominion(dominion, players, numGames=10, maxTurns=100, verbose=False)
    allGameRewards, allGameTurns = results
    
    for playerID in range(len(players)):
        numGames = len(allGameRewards[playerID])
        numWins = 0
        numTies = 0
        numLosses = 0
        for reward in allGameRewards[playerID]:
            if reward > 0:
                numWins += 1
            elif reward < 0:
                numLosses += 1
            else:
                numTies += 1
        print "_______________________________"
        print "Player:", playerID, ":", players[playerID].getPlayerName()
        print "Number of Games Played: ", numGames
        print "NumWins:", numWins, "Win Percentage: ", numWins / (0.0 + numGames)
        print "NumLosses:", numLosses, "Loss Percentage: ", numLosses / (0.0 + numGames)
        print "NumTies:", numTies, "Tie Percentage: ", numTies / (0.0 + numGames)