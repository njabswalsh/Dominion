from card import Card

cardList = []
def initializeCardList(filename):
	cardsFile = open(filename, 'r')
	for line in cardsFile:
		if line == "" or line[0] == "#":
			pass
		else: 
			words = line.split()
			cardID = int(words[0])
			cardName = words[1]
			cardType = words[2]
			cardCost = int(words[3])
			treasureValue = int(words[4])
			victoryPoints = words[5]
			effects = words[6]
			cardList.append(Card(cardID, cardName, cardType, cardCost, treasureValue, victoryPoints, effects))
	for card1 in cardList:
		print card1
	return cardList

def getCardFromID(id):
	return cardList[id]



