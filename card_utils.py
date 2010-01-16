from UserList import UserList
from random import shuffle

RANK_VALUE_HASH = {
	2:	[2],
	3:	[3],
	4:	[4],
	5:	[5],
	6:	[6],
	7:	[7],
	8:	[8],
	9:	[9],
	10:	[10],
	'Jack':	[10],
	'Queen':	[10],
	'King':	[10],
	'Ace':	[11, 1]
}

SUITS = ['Spades', 'Heart' , 'Diamonds', 'Clubs']

RANKS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King', 'Ace']

class BlackjackCard(object):
	def __init__(self, suit, rank):
		self.suit = suit
		self.rank = rank
	
	def value(self):
		return RANK_VALUE_HASH[self.rank]

	def __repr__(self):
		return "%s of %s" % (self.rank,self.suit)

	__str__ = __repr__


class BlackjackDeck(UserList):
	def __init__(self, ndecks = 6):
		self.ndecks = ndecks
		self.data = [BlackjackCard(suit, rank) for suit in SUITS for rank in RANKS for x in range(ndecks)]
		self.shuffle()

	def shuffle(self):
		shuffle(self.data)
	
	def deal(self):
		if (len(self.data) == 0): self.reset()
		return self.data.pop(0)

	def reset(self):
		self.__init__(self.ndecks)

	
if __name__ == '__main__':
	deck = BlackjackDeck()
	for i in range(500):
		print repr(deck.deal())
