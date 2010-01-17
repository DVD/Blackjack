from UserList import UserList
from random import shuffle

RANK_VALUE_HASH = {
	'Two':		(2),
	'Three':		(3),
	'Four':		(4),
	'Five':		(5),
	'Six':		(6),
	'Seven':		(7),
	'Eight':		(8),
	'Nine':		(9),
	'Ten':		(10),
	'Jack':		(10),
	'Queen':		(10),
	'King':		(10),
	'Ace':		(11, 1)
}

SUITS = ('Spades', 'Heart' , 'Diamonds', 'Clubs')

RANKS = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')

class BlackjackCard(object):
	def __init__(self, rank, suit):
		self.suit = suit
		self.rank = rank
	
	@property
	def value(self):
		return RANK_VALUE_HASH[self.rank]

	def __repr__(self):
		return "%s of %s" % (self.rank,self.suit)

	__str__ = __repr__


class BlackjackDeck(UserList):
	def __init__(self, decks = 6):
		self.decks = decks
		self.reset()

	def shuffle(self):
		shuffle(self.data)
	
	def deal(self):
		if (len(self.data) == 0): self.reset()
		return self.data.pop(0)

	def reset(self):
		self.data = [BlackjackCard(suit, rank) for suit in SUITS for rank in RANKS for x in range(decks)]
		self.shuffle()


class BlackjackBet(object):
	def __init__(self):
		self._cards = []
		self.wager = 0
		self._sum = [0]

	def add_card(self, card):
		self._cards.append(card)
		tmp = self._sum
		self._sum = []
		for new_val in card.value:
			self._sum.extend(filter(lambda x: x <= 21, map(lambda x: x + new_val, tmp)))
	
	@property
	def sum(self):
		return self._sum.clone()

	@property
	def cards(self):
		return self._cards.clone()

	def double_down(self):
		# Application must check if the player is allowed to double-down
		# and if they have enough money for that
		self.wager*=2
	
	def split(self):
		# Application must check if the player is allowed to split
		# and if they have enough money for the new wager
		if(len(self._cards)!=2 or self._cards[0]!=self._cards[1]):
			raise 'ActionNotAllowedError'
		new_bet=Bet()
		new_bet.wager=self.wager
		self._sum=list(self._cards[0].value)
		new_bet.add_card(self._cards.pop(1))
		return new_bet


if __name__ == '__main__':
	deck = BlackjackDeck()
	for i in range(500):
		print repr(deck.deal())
