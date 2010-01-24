import card_utils
from blackjack_messages import *
from pysage import Actor, ActorManager
from simpleui import *

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
        self.is_eliminated = [ False ] * 7
        # this initialization must change
        self.players = [ HumanPlayer(str(i), 100) for i in range(1) ]
        self.ui = SimpleUI()
        # register players and dealer as actors
        am = ActorManager.get_singleton()
        am.register_actor(self.ui, 'ui')
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
            self.dealer.deal_with_player(player)
        self.dealer.play()
        self.round_number+=1

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
        self.hand = card_utils.BlackjackHand()

    def __ignore_handler(self):
        '''An empty handler used to skip some messages'''
        pass

    def send_message(self, msg):
        msg.sender='dealer'
        return ActorManager.get_singleton().trigger(msg)

    def ask_player_for_insurance(self, player):
        self.send_message(InsuranceOffer(player_id = player))

    def deal_card(self, player_num, hand_num, card = None):
        if not card:
            card = self.deck.pop(0)
        self.send_message(CardDeal(player_id = player_num, hand_number = hand_num, card = card))

    def deal_cards(self, players):
        for player in players:
            self.deal_card(player.player_id, 0)
        card = self.deck.pop(0)
        self.hand.add_card(card)
        self.deal_card('dealer', 0, card)
        for player in players:
            self.deal_card(player.player_id, 0)

    def deal_with_player(self, player):
        self.cuurent_player = player.player_id
        for (hand_num, hand) in enumerate(player.hands):
            self.current_hand = hand_num
            self.send_message(PlayerHandTurn(player_id = player.player_id, hand_number = hand_num))
            while (hand.status == 'not played'):
                self.send_message(DecisionRequest(player_id = player.player_id, hand_number = hand_num))

    def handle_DecisionResponse(self, msg):
        if (msg.get_property('action') == 'hit'):
            self.send_message(
                    CardDeal(player_id = self.cuurent_player, hand_number = self.current_hand, card = self.deck.deal()))

    def play(self):
        while len(self.hand.sum) > 0 and ( min(self.hand.sum) < 17 or ( min(self.hand.sum) == 17 and len(self.hand.sum) > 1) ):
            card = self.deck.pop(0)
            self.hand.add_card(card)
            self.deal_card('dealer', 0, card)

        if self.hand.is_blackjack():
            self.send_message(BlackjackAnnouncement(hand_number = 0))
        if self.hand.is_busted():
            self.send_message(BustAnnouncement(hand_number = 0))


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

        if self.hands[hand_number].is_blackjack():
            self.send_message(BlackjackAnnouncement(hand_number = hand_number))
        if self.hands[hand_number].is_busted():
            self.send_message(BustAnnouncement(hand_number = hand_number))

    def handle_DecisionRequest(self, msg):
        hand_number = msg.get_property('hand_number')
        action = self.decide(hand_number)
        if action == 'stand':
            self.hands[hand_number].status = 'stand'
        self.send_message(DecisionResponse(action = action, hand_number = hand_number))

    def card_dealt_to_player(self, card):
        raise NotImplementedError()

    def card_dealt_to_self(self, card, hand_number):
        raise NotImplementedError()

    def decide(self, hand_number):
        raise NotImplementedError()


class HumanPlayer(Player):
    def __init__(self, player_id, money):
        Player.__init__(self, player_id, money)
        self.subscriptions.extend(['HumanDecisionResponse'])

    def card_dealt_to_player(self, card):
        pass

    def card_dealt_to_self(self, card, hand_number):
        pass

    def decide(self, hand_number):
        self.send_message(HumanDecisionRequest(allowed_actions = [ 'hit', 'stand']))
        return self.action

    def handle_HumanDecisionResponse(self, msg):
        if (msg.get_property('player_id') == self.player_id):
            self.action = msg.get_property('action')

class BasicStrategyPlayer(Player):
    soft_hands_decisions = [
        [('hit',)          ,('hit',)          ,('hit',)          ,('double','hit')  ,('double','hit')  ,('hit',)  ,('hit',)  ,('hit',)  ,('hit',)  ,('hit',)  ],
        [('hit',)          ,('hit',)          ,('hit',)          ,('double','hit')  ,('double','hit')  ,('hit',)  ,('hit',)  ,('hit',)  ,('hit',)  ,('hit',)  ],
        [('hit',)          ,('hit',)          ,('double','hit')  ,('double','hit')  ,('double','hit')  ,('hit',)  ,('hit',)  ,('hit',)  ,('hit',)  ,('hit',)  ],
        [('hit',)          ,('hit',)          ,('double','hit')  ,('double','hit')  ,('double','hit')  ,('hit',)  ,('hit',)  ,('hit',)  ,('hit',)  ,('hit',)  ],
        [('hit',)          ,('double','hit')  ,('double','hit')  ,('double','hit')  ,('double','hit')  ,('hit',)  ,('hit',)  ,('hit',)  ,('hit',)  ,('hit',)  ],
        [('double','stand'),('double','stand'),('double','stand'),('double','stand'),('double','stand'),('stand',),('stand',),('hit',)  ,('hit',)  ,('hit',)  ],
        [('stand',)        ,('stand',)        ,('stand',)        ,('stand',)        ,('double','stand'),('stand',),('stand',),('stand',),('stand',),('stand',)],
        [('stand',)        ,('stand',)        ,('stand',)        ,('stand',)        ,('stand',)        ,('stand',),('stand',),('stand',),('stand',),('stand',)],
        [('stand',)        ,('stand',)        ,('stand',)        ,('stand',)        ,('stand',)        ,('stand',),('stand',),('stand',),('stand',),('stand',)],
    ]

    hard_hands_decisions = [
    [('hit')         ,('hit')         ,('hit')         ,('hit')         ,('hit')         ,('hit')         ,('hit')         ,('hit')         ,('hit',)        ,('hit',)        ],
    [('hit')         ,('double','hit'),('double','hit'),('double','hit'),('double','hit'),('hit')         ,('hit')         ,('hit')         ,('hit',)        ,('hit',)        ],
    [('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('hit',)        ,('hit',)        ],
    [('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit')],
    [('hit')         ,('hit')         ,('stand')       ,('stand')       ,('stand')       ,('hit')         ,('hit')         ,('hit')         ,('hit',)        ,('hit',)        ],
    [('stand')       ,('stand')       ,('stand')       ,('stand')       ,('stand')       ,('hit')         ,('hit')         ,('hit')         ,('hit',)        ,('hit',)        ],
    [('stand')       ,('stand')       ,('stand')       ,('stand')       ,('stand')       ,('stand')       ,('stand')       ,('stand')       ,('stand',)      ,('stand',)      ],
            ]
    split_pair_decisions = [
            [True , True , True , True , True , True , False, False, False, False],
            [True , True , True , True , True , True , False, False, False, False],
            [False, False, False, True , True , False, False, False, False, False],
            [False, False, False, False, False, False, False, False, False, False],
            [True , True , True , True , True , False, False, False, False, False],
            [True , True , True , True , True , True , False, False, False, False],
            [True , True , True , True , True , True , True , True , True , True ],
            [True , True , True , True , False, True , True , True , False, False],
            [False, False, False, False, False, False, False, False, False, False],
            [True , True , True , True , True , True , True , True , True , True ],
            ]

if __name__ == '__main__':
    game = GameTable()
    game.play_game()

