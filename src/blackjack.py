import card_utils
from blackjack_messages import *
from pysage import Actor, ActorManager

class GameTable(object):
    '''Represents the Blackjack table with the dealer and the players and the entire game'''

    def __init__(self,config_file='blackjack.conf'):
        '''Parse the configuration file, create the dealer and the players and register them as actors, initialize the GUI'''
        # fields:
        # dealer - an instance of the Dealer class
        # players - a list of instances of the Player class
        # round_number - the number of the current hand, 0 after this method, modified by __next_hand
        # ranking - a queue, containing pairs (player_number,balance) - after each player is eliminated, an entry for them is pushed on top of the queue
        # is_eliminated - a list, containing boolean values, telling if the corresponding player is eliminated or not
        # table_min and table_max
        self.dealer = Dealer()
        self.round_number = 0
        self.ranking = []
        self.is_eliminated = [ True ] * 7
        # this initialization must change
        self.players = [ Player(_, 100) for _ in range(2) ]
        # register players and dealer as actors
        am = ActorManager.get_singleton()
        for player in self.players:
            am.register_actor(player, player.player_id)
        am.register_actor(self.dealer, 'dealer')

    def play_game(self):
        '''Play an Elimination Blackjack game'''
        self.__play_round()

    def __play_round(self):
        '''Plays a single Elimination Blackjack round'''
        ActorManager.get_singleton().trigger(NextRound(round_number = self.round_number))
        players = [player for player_num, player in enumerate(self.players) if not self.is_eliminated[player_num]]
        self.dealer.deal_cards(players)
        for player in players:
            dealer.deal_with_player(player)

    def __update_database(self):
        '''Update the database with current game ranking'''
        #called at the end of a game??
        raise 'Unimplemented error!'


class Dealer(Actor):
    '''Represents the dealer in the game'''

    def __init__(self):
        '''Create a dealer with a deck and subscribe to the needed message types'''
        Actor.__init__(self)
        self.deck = card_utils.BlackjackDeck()
        self.subscriptions = [ 'DecisionResponse' ]
        self.cards = card_utils.BlackjackHand()

    def __ignore_handler(self):
        '''An empty handler used to skip some messages'''
        pass

    def send_message(self, msg):
        msg.sender='dealer'
        ActorManager.get_singleton().trigger(msg)

    def ask_player_for_insurance(self, player):
        self.send_message(InsuranceOffer(player_id = player))

    def deal_card(self, player_num, hand_num):

        self.send_message(CardDeal(player_id = player_num, hand_number = hand_num, card=self.deck.pop(0)))

    def deal_cards(self, players):
        for player in players:
            self.deal_card(players[player].player_id, 0)
        self.deal_card('dealer', 0)
        for player in players:
            self.deal_card(players[player].player_id, 0)

    def deal_with_player(self, player):
        for (hand_num, hand) in enumerate(player.hands):
            self.send_message(PlayerHandTurn(player_id = player.player_id, hand_number = 0))
            while (hand.status == 'not played'):
                self.send_message(DecisionRequest(player_id = player.player_id, hand_number = hand_num))

    def handle_DecisionResponse(self, msg):
        if (msg.get_property('action') == 'hit'):
            send_message(CardDeal(player_id = player, hand_number = msg.get_property('hand_number')))


class Player(Actor):
    '''A class that every player in the game must extend'''

    def __init__(self, player_id, money):
        '''Create a simple player and subscribe to the message types sufficient to play the game.'''
        #fields : player_id, hands, money, insurance
        Actor.__init__(self)
        self.player_id = player_id
        self.money = money
        self.hands = [ card_utils.BlackjackHand() ]
        self.insurance = 0
        self.subscriptions = [ 'WagerRequest', 'InsuranceOffer', 'CardDeal' , 'DecisionRequest']

    def send_message(self, msg):
        msg.sender=self.player_id
        ActorManager.get_singleton().trigger(msg)

    def handle_CardDeal(self, msg):
        '''A method that is called whenever the player is given a card. This is an internal method and
        shall never be overridden.'''
        hand_number = msg.get_property('hand_number')
        card = msg.get_property('card')

        if msg.get_property('player_id') != self.player_id:
            self.card_dealt_to_player(card)
            return

        self.hands[hand_number].add_card(card)
        self.card_dealt_to_self(card, hand_number)

    def handle_DecisionRequest(self, msg):
        action = self.decide()
        if action == 'stand':
            self.hands[msg.get_property('hand_number')].status = 'stand'

        send_message(DecisionResponse(action = self.decide(), hand_number = msg.get_property('hand_number')))

    def card_dealt_to_player(self, card):
        raise NotImplementedError()

    def card_dealt_to_self(self, card):
        raise NotImplementedError()

    def decide(self):
        raise NotImplementedError()


if __name__ == '__main__':
    game = GameTable()
    game.play_game()

