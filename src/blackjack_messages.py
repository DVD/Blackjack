from pysage import Message

class Decision(Message):
	'''Class used for messages telling the player's decision for the current hand.
	Action can be "hit", "stand", "double down", "split"'''
	# sent by a player to the dealer
	properties = ['action']
	packet_type = 101

class PlayerTurn(Message):
	'''Class used for telling whose turn it is'''
	# sent by the dealer
	# used mainly by the GUI
	properties = ['player_id', 'hand_number']
	packet_type = 102

class PlayerHandTurn(Message):
	'''Class used for telling which hand on the table is on turn'''
	# sent by the dealer
	# used mainly by the GUI
	properties = ['player_id', 'hand_number']
	packet_type = 112

class NextRound(Message):
	'''Class used to announce next round in the game (on the table)'''
	# sent by the dealer
	# used mainly by the GUI
	properties = ['round_number', 'active_players']
	packet_type = 113
	# needs more thinking

class WagerRequest(Message):
	'''Class used for sending a request to each player to
	place their wager'''
	# sent by the dealer to the player
	# sent by the human player to the GUI
	# when sent by the human player to the GUI
	# 'player_id'='GUI'
	properties = ['player_id']
	packet_type = 103

class WagerResponse(Message):
	'''Class used for announcing the player's wager'''
	# sent by the player to the dealer
	# sent by the GUI to the human player
	properties = ['hand_number','hand_wager']
	packet_type = 104

class BlackjackAnnouncement(Message):
	'''Class used for announcing player's or the dealer's blackjack'''
	properties=['hand_number']
	packet_type=105
	# sent by the player to the dealer

class BustAnnouncement(Message):
	'''Class used for announcing that a player or the dealer busts'''
	properties=['hand_number']
	packet_type=106
	# sent by the player to the dealer

class InsuranceOffer(Message):
	'''Class used for asking the player if they want
	to make an insurance bet'''
	# sent by the dealer to the player
	# sent by the human player to the GUI
	# when sent by the human player to the GUI
	# 'player_id'='GUI'
	properties = ['player_id']
	packet_type=107

class InsuranceResponse(Message):
	'''Class used for answering to insurance offer'''
	properties = ['answer']
	packet_type=108
	# sent by the player to the dealer
	# the insurance bet is half of the initial bet
	# accepting or rejecting to make an asurance does not affect the dealer

class CardDeal(Message):
	'''Class used for sending a card to the player'''
	properties = ['player_id', 'hand_number', 'card']
	packet_type=109
	# sent by the dealer to the player
	# always a single card

class HumanDecision(Message):
	'''Class used for passing the human player's decision by the GUI'''
	properties=['player_id','action']
	packet_type=110
	# sent bythe GUI to the human player

class HumanInsuranceResponse(Message):
	'''Class used for answering to insurance offer by a human player'''
	properties = ['player_id','answer']
	packet_type=111
	# sent by the GUI to the human player
	# the insurance bet is half of the initial bet
	# accepting or rejecting to make an asurance does not affect the dealer
