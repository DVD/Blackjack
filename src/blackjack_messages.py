from pysage import Message

class DecisionResponse(Message):
    '''Class used for messages telling the player's decision for the current hand.
    Action can be "hit", "stand", "double down", "split"'''
    # sent by a player to the dealer
    properties = ['action']
    packet_type = 101

class WagerResponse(Message):
    '''Class used for announcing the player's wager'''
    # sent by the player to the dealer
    properties = ['wager_amount']
    packet_type = 102

class InsuranceResponse(Message):
    '''Class used for answering to insurance offer'''
    properties = ['answer']
    packet_type = 103
    # sent by the player to the dealer
    # the insurance bet is half of the initial bet
    # accepting or rejecting to make an asurance does not affect the dealer

class BlackjackAnnouncement(Message):
    '''Class used for announcing player's or the dealer's blackjack'''
    properties=['hand_number']
    packet_type = 104
    # sent by the player or the dealer

class BustAnnouncement(Message):
    '''Class used for announcing that a player or the dealer busts'''
    properties=['hand_number']
    packet_type = 105
    # sent by the player or the dealer

class CardDeal(Message):
    '''Class used for sending a card to the player'''
    properties = ['player_id', 'hand_number', 'card']
    packet_type = 106
    # sent by the dealer to the player
    # always a single card

class PlayerHandTurn(Message):
    '''Class used for telling which hand on the table is on turn'''
    # sent by the dealer
    properties = ['player_id', 'hand_number']
    packet_type = 107

class NextRound(Message):
    '''Class used for telling the gui a new round is starting'''
    properties = ['round_number']
    packet_type = 108
    # sent by the dealer
    # used by the UI

class DecisionRequest(Message):
    '''Class used for asking the player for their decision'''
    # sent by the dealer to the player
    properties=['player_id','hand_number']
    packet_type = 109

class WagerRequest(Message):
    '''Class used for sending a request to each player to
    place their wager'''
    # sent by the dealer to the player
    properties = ['player_id']
    packet_type = 110

class InsuranceOffer(Message):
    '''Class used for asking the player if they want
    to make an insurance bet'''
    # sent by the dealer to the player
    properties = ['player_id']
    packet_type = 111

class HumanInsuranceResponse(Message):
    '''Class used for answering to insurance offer by a human player'''
    properties = ['player_id','answer']
    packet_type = 112
    # sent by the UI to the HumanPlayer class
    # the insurance bet is half of the initial bet
    # accepting or rejecting to make an asurance does not affect the dealer

class HumanDecisionResponse(Message):
    '''Class used for passing the human player's decision by the UI'''
    properties=['player_id','action']
    packet_type = 113
    # sent by the UI to the HumanPlayer class

class HumanWagerRequest(Message):
    '''Class used for asking the UI to 
    ask the human player for a wager'''
    properties=[]
    packet_type = 114
    # sent by the HumanPlayer class to the UI

class HumanInsuranceOffer(Message):
    '''Class used for asking the UI to ask 
    the human player if they want
    to make an insurance bet'''
    properties=[]
    packet_type = 115
    # sent by the HumanPlayer class to the UI

class HumanDecisionRequest(Message):
    '''Class used for asking the UI to ask the
    human player for an action to be taken'''
    properties=['allowed_actions']
    packet_type = 116
    # sent by the HumanPlayer class to the UI

class HumanWagerResponse(Message):
    '''Class used for passing the human player's wager by the UI'''
    properties=['player_id','wager_amount']
    packet_type = 117
    # sent by the UI to the HumanPlayer class

