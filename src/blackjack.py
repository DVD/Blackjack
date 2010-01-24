import card_utils
import random
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
        self.players.append(BasicStrategyPlayer('2',200))
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
        player=msg.get_property('player_id')
        if player != self.player_id:
            self.card_dealt_to_player(player,card)
            return

        self.hands[hand_number].add_card(card)
        self.card_dealt_to_self(card, hand_number)

        if self.hands[hand_number].is_blackjack():
            self.send_message(BlackjackAnnouncement(hand_number = hand_number))
        if self.hands[hand_number].is_busted():
            self.send_message(BustAnnouncement(hand_number = hand_number))

    def handle_DecisionRequest(self, msg):
        if msg.get_property('player_id') != self.player_id:
            return
        hand_number = msg.get_property('hand_number')
        action = self.decide(hand_number)
        if action == 'stand':
            self.hands[hand_number].status = 'stand'
        self.send_message(DecisionResponse(action = action, hand_number = hand_number))

    def card_dealt_to_player(self, player, card):
        raise NotImplementedError()

    def card_dealt_to_self(self, card, hand_number):
        raise NotImplementedError()

    def decide(self, hand_number):
        raise NotImplementedError()

    def result(self, money):
        pass


class HumanPlayer(Player):
    def __init__(self, player_id, money):
        Player.__init__(self, player_id, money)
        self.subscriptions.extend(['HumanDecisionResponse'])

    def card_dealt_to_player(self, player, card):
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
    soft_hand_decisions = [
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

    hard_hand_decisions = [
    [('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)        ,('hit',)        ],
    [('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)        ,('hit',)        ],
    [('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)        ,('hit',)        ],
    [('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)        ,('hit',)        ],
    [('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)        ,('hit',)        ],
    [('hit',)         ,('double','hit'),('double','hit'),('double','hit'),('double','hit'),('hit',)         ,('hit',)         ,('hit',)         ,('hit',)        ,('hit',)        ],
    [('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('hit',)        ,('hit',)        ],
    [('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit'),('double','hit')],
    [('hit',)         ,('hit',)         ,('stand',)       ,('stand',)       ,('stand',)       ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)        ,('hit',)        ],
    [('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)        ,('hit',)        ],
    [('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)        ,('hit',)        ],
    [('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)        ,('hit',)        ],
    [('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('hit',)         ,('hit',)         ,('hit',)         ,('hit',)        ,('hit',)        ],
    [('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)      ,('stand',)      ],
    [('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)      ,('stand',)      ],
    [('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)      ,('stand',)      ],
    [('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)      ,('stand',)      ],
    [('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)       ,('stand',)      ,('stand',)      ],
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

    def card_dealt_to_player(self, player, card):
        if player=='dealer':
            self.dealer_upcard=card

    def decide(self,hand_number):
        hand=self.hands[hand_number]
        if hand.is_hard:
            return BasicStrategyPlayer.hard_hand_decisions[hand.sum[0]-4][self.dealer_upcard.value[0]-2][-1]
        else:
            return BasicStrategyPlayer.soft_hand_decisions[max(hand.sum)-13][self.dealer_upcard.value[0]-2][-1]
        return
    
    def card_dealt_to_self(self,card,hand_number):
        pass


class SARSAPlayer(Player):
    states = tuple( [x for x in range(4, 32)] )
    actions = ( 'hit', 'stand' )

    def __init__(self, player_id, money, epsilon, alpha, gamma):
        Player.__init__(self, player_id, money)
        self.epsilon = epsilon
        self.gamma = gamma
        self.q = dict( [ (state, dict( [(action, random.random()) for action in SARSAPlayer.actions] ))  for state in SARSAPlayer.states ] )
        self.reset()

    def reset(self):
        self.s = 0
        self.a = 'no action'

    def card_dealt_to_player(self, player, card):
        pass

    def card_dealt_to_self(self, card):
        pass

    def decide(hand_number):
        #TODO: implement hands when we are ready

        #epsilon-greedy choose
        choose_best = random.random()
        if choose_best < eps:
            #so we have to pick a radom action
            action = 'hit' if random.randint() == 1 else 'stand'
            state = random.choice(self.hand[hand_number].sum)
        else:
            (action, state) = reduce(lambda x, y: (x[0][0],x[1]) if x[0][1] > y[0][1] else (y[0][0], y[1]), [(pair, st) for pair in self.q[st] for st in self.hand[hand_number].sum])

        if self.s > 0:
            self.q[self.s][self.a] += self.alpha * (self.r + self.gamma * self.q[state][action] - self.q[self.s][self.a])

        self.s, self.a = state, action
        self.r = 0

    def result(money):
        if result > 0:
            self.r = 1
        elif result < 0:
            self.r = -1
        else:
            self.r = 0



if __name__ == '__main__':
    game = GameTable()
    game.play_game()

