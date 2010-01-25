#!/usr/bin/env python2.6
import card_utils
import random
from blackjack_messages import *
from pysage import Actor, ActorManager
from simpleui import *
from sys import argv

class GameTable(object):
    '''Represents the Blackjack table with the dealer and the players and the entire game'''

    def __init__(self, simple_ui = False, config_file='blackjack.conf'):
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
#        self.players = [ HumanPlayer(str(i), 100000000) for i in range(1) ]
#        self.players.append(BasicStrategyPlayer('1',200))
#        self.players.append(HiLoCountingPlayer('2',250))
        # register players and dealer as actors
        am = ActorManager.get_singleton()
        if (simple_ui):
            self.ui = SimpleUI()
            am.register_actor(self.ui, 'ui')
#        for player in self.players:
#            am.register_actor(player, player.player_id)
#        am.register_actor(self.dealer, 'dealer')

    def play_game(self):
        '''Play an Elimination Blackjack game'''
        self.__play_round()

    def train_player(self, player, dealer):
        total_won=0
        f=open("statistics","w")
        for iteration in range(100):
            won = 0
            lost = 0
            for game in range(100):
                ActorManager.get_singleton().trigger(NextRound(round_number = game))
                player.hands = [card_utils.BlackjackHand()]
                player.hands[0].wager = 1
                dealer.hand = card_utils.BlackjackHand()
                dealer.deal_cards([player])
                dealer.deal_with_player(player)
                dealer.play()
                hand = player.hands[0]
                if hand.is_busted():
                    player.result(0, -hand.wager)
                    lost += 1
                    print 'Dealer wins'
                elif hand.is_blackjack():
                    if dealer.hand.is_blackjack():
                        player.result(0, 0)
                        print 'Player and dealer are equal'
                    else:
                        player.result(0, hand.wager*3.0/2.0)
                        won += 1
                        print 'Player 0 wins'
                else:
                    dp = max(0, 0, *dealer.hand.sum)
                    pp = max(0, 0, *hand.sum)
                    if dp > pp:
                        lost += 1
                        player.result(0, -hand.wager)
                        print 'Dealer wins'
                    elif dp < pp:
                        won += 1
                        player.result(0, hand.wager)
                        print 'Player 0 wins'
                    else:
                        player.result(0, 0)
                        print 'Player and dealer are equal'
            total_won+=won            
            f.write("%d\n" % won)
        print("Total won: %s" % repr(total_won))
        f.close()
           

    def __play_round(self):
        '''Plays a single Elimination Blackjack round'''
        #TODO: reinitialize hands before actual play
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
    
    def __pay_off(self):
        for player_num, player in enumerate(self.players):
            if not is_eliminated[player_num]:
                for hand_number, hand in enumerate(player.hands):
                    if hand.is_busted():
                        player.result(hand_number, -hand.wager)
                    elif hand.is_blackjack():
                        player.result(hand_number, 0) if self.dealer.hand.is_blackjack() else player.result(hand_number, hand.money*3.0/2.0)
                    else:
                        dp = max(self.dealer.hand.sum)
                        pp = max(hand.sum)
                        if dp > pp:
                            player.result(hand_number, -hand.wager)
                        elif dp < pp:
                            player.result(hand_number, hand.wager)
                        else:
                            player.result(hand_number, 0)



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
            card = self.deck.deal()
        self.send_message(CardDeal(player_id = player_num, hand_number = hand_num, card = card))

    def deal_cards(self, players):
        for player in players:
            self.deal_card(player.player_id, 0)
        card = self.deck.deal()
        self.hand.add_card(card)
        self.deal_card('dealer', 0, card)
        for player in players:
            self.deal_card(player.player_id, 0)

    def deal_with_player(self, player):
        self.current_player = player.player_id
        for (hand_num, hand) in enumerate(player.hands):
            self.current_hand = hand_num
            self.send_message(PlayerHandTurn(player_id = player.player_id, hand_number = hand_num))
            while (hand.status == 'not played'):
                self.send_message(DecisionRequest(player_id = player.player_id, hand_number = hand_num))

    def handle_DecisionResponse(self, msg):
        if (msg.get_property('action') == 'hit'):
            self.send_message(
                    CardDeal(player_id = self.current_player, hand_number = self.current_hand, card = self.deck.deal()))

    def play(self):
        while len(self.hand.sum) > 0 and ( min(self.hand.sum) < 17 or ( min(self.hand.sum) == 17 and len(self.hand.sum) > 1) ):
            card = self.deck.deal()
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
        # reimplement this
        self.hands[0].wager = 100
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

    def result(self, hand_number, money):
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
    def __init__(self,player_id,money):
        Player.__init__(self,player_id,money)
        self.dealer_upcard=None

    def card_dealt_to_player(self, player, card):
        if player=='dealer':
            self.dealer_upcard=card

    def decide(self,hand_number):
        hand=self.hands[hand_number]
        if hand.is_hard():
            return BasicStrategyPlayer.hard_hand_decisions[hand.sum[0]-4][self.dealer_upcard.value[0]-2][-1] ##Change when added double down
        else:
            return BasicStrategyPlayer.soft_hand_decisions[max(hand.sum)-13][self.dealer_upcard.value[0]-2][-1] ##Change when added double down
    
    def card_dealt_to_self(self,card,hand_number):
        pass


class SARSAPlayer(Player):
    states = tuple( [x for x in range(4, 32)] )
    actions = ( 'hit', 'stand' )

    def __init__(self, player_id, money, epsilon = 0.01, alpha = 0.01, gamma = 0.9):
        Player.__init__(self, player_id, money)
        self.epsilon = epsilon
        self.gamma = gamma
        self.alpha = alpha
        self.q = dict( [ (state, dict( [(action, random.random()) for action in SARSAPlayer.actions] ))  for state in SARSAPlayer.states ] )
        self.reset()

    def reset(self):
        self.s = 0
        self.a = 'no action'

    def card_dealt_to_player(self, player, card):
        pass

    def card_dealt_to_self(self, card, hand_number):
        pass

    def _state(self,hand_number):
        hand=self.hands[hand_number]
        if hand.is_hard():
            return hand.sum[0]
        else:
            return max(hand.sum)+10

    def decide(self, hand_number):
        #TODO: implement hands when we are ready

        #epsilon-greedy choose
        choose_best = random.random()
        state = self._state(hand_number)
        if choose_best < self.epsilon:
            #so we have to pick a radom action
            action = 'hit' if random.randint(0,1) == 1 else 'stand'
        else:
            action = self.q[state].keys()[self.q[state].values().index(max(self.q[state].values()))]

#        print action, state

        if self.s > 0:
            self.q[self.s][self.a] += self.alpha * (self.r + self.gamma * self.q[state][action] - self.q[self.s][self.a])

        self.s, self.a = state, action
        self.r = 0
        return action

    def result(self, hand_number, money):
        if money > 0:
            self.r = 1
        elif money < 0:
            self.r = -1
        else:
            self.r = 0


class HiLoCountingPlayer(BasicStrategyPlayer):
    illustrious18=[[None for _ in range(2,12)] for __ in range(4,22)]
    illustrious18 [16-4] [10-2] = (('stand',)      ,0)
    illustrious18 [15-4] [10-2] = (('stand',)      ,4)
    illustrious18 [10-4] [10-2] = (('double','hit'),4)
    illustrious18 [12-4]  [3-2] = (('stand',)      ,2)
    illustrious18 [12-4]  [2-2] = (('stand',)      ,3)
    illustrious18 [11-4] [11-2] = (('double','hit'),1)
    illustrious18  [9-4]  [2-2] = (('double','hit'),1)
    illustrious18 [10-4] [11-2] = (('double','hit'),4)
    illustrious18  [9-4]  [7-2] = (('double','hit'),3)
    illustrious18 [16-4]  [9-2] = (('stand',)      ,5)
    illustrious18 [13-4]  [2-2] = (('hit',)       ,-1)
    illustrious18 [12-4]  [4-2] = (('hit',)        ,0)
    illustrious18 [12-4]  [5-2] = (('hit',)       ,-2)
    illustrious18 [12-4]  [6-2] = (('hit',)       ,-1)
    illustrious18 [13-4]  [3-2] = (('hit',)       ,-2)
    ##When we add splitting, 10+10 vs. 5/6 is 'split' with index 5/4

    def __init__(self,player_id,money):
        BasicStrategyPlayer.__init__(self,player_id,money)
        self.running_count=0
        self.unseen_cards=312

    @property
    def true_count(self):
        return self.running_count/(self.unseen_cards/52.0)

    def _count_card(self,card):
        self.unseen_cards-=1
        if self.unseen_cards<=0:
            self.unseen_cards+=312
        self.running_count+=self._count_value(card)

    def card_dealt_to_player(self ,player, card):
        BasicStrategyPlayer.card_dealt_to_player(self,player,card)
        self._count_card(card)

    def _count_value(self,card):
        if card.value[0]<=6:
            return 1
        elif card.value[0]>=10:
            return -1
        return 0
    
    def card_dealt_to_self(self,card,hand_number):
        self._count_card(card)

    def decide(self,hand_number):
        hand = self.hands[hand_number]
        illustrious18_record = HiLoCountingPlayer.illustrious18[max(hand.sum)-4][self.dealer_upcard.value[0]-2]
        if illustrious18_record==None or self.true_count<illustrious18_record[1]:
            return BasicStrategyPlayer.decide(self,hand_number)
        else:
            return illustrious18_record[0][-1] ## Change this when adding double down!!!

class ProbabilityCountingPlayer(Player):

    ace_next=[None,12,13,14,15,16,17,18,19,20,11,12,13,14,15,16,17,18,19,31,22,22,23,24,25,26,27,28,29,30,31]

    def __init__(self,player_id,money):
        Player.__init__(self,player_id,money)
        self._reset_counts()
    
    def _reset_counts(self):
        self.remaining=[24 for _ in range(12)] #remaining[i] - how many cards of value i are there left in the deck
        self.remaining[0]=None
        self.remaining[1]=None
        self.remaining[10]*=4
        self.unseen_cards=312

    def card_dealt_to_player(self, player, card):
        if self.unseen_cards==0:
            self._reset_counts()
        self.unseen_cards-=1
        self.remaining[card.value[0]]-=1
        if player=='dealer':
            self.dealer_upcard=card
    
    def card_dealt_to_self(self, card, hand_number):
        if self.unseen_cards==0:
            self._reset_counts()
        self.unseen_cards-=1
        self.remaining[card.value[0]]-=1
    
    def decide(self,hand_number):
        ##Just stand or hit fow now
        ##First probablilities for dealer's last state
        p=[0 for _ in range(33)]
        p[0]=None
        p[ProbabilityCountingPlayer._state_number(self.dealer_upcard)]=1
        for s in range(1,33):
            if ProbabilityCountingPlayer._dealer_draws(s):
                for i in range(2,12):
                    p[ProbabilityCountingPlayer._next(s,i)]+=p[s]*self._fraction(i)
                p[s]=0
        ##Then probabilities to win if we stand at a certain state
        st=[0 for _ in range(33)]
        st[0]=None
        for s in range(1,33):
            st[s]=sum([p[ds] for ds in ProbabilityCountingPlayer._win_to(s)]) + 0.5*sum([p[ds] for ds in ProbabilityCountingPlayer._push_to(s)])
        ##Then the probability to win if playing according to the st[s]
        b=[0 for _ in range(33)]
        for s in range(31,0,-1):
            w=0
            for i in range(2,12):
                w+=self._fraction(i)*b[ProbabilityCountingPlayer._next(s,i)]
            if w>st[s]:
                b[s]=w
            else:
                b[s]=st[s]
        ##And now - hit or stand
        state=ProbabilityCountingPlayer._state_number(self.hands[hand_number])
        if b[state]==st[state]:
            return 'stand'
        return 'hit'

    @staticmethod
    def _state_number(obj):
        if isinstance(obj,card_utils.BlackjackCard):
            return obj.value[0]-1
        elif isinstance(obj,card_utils.BlackjackHand):
            if obj.is_hard():
                return obj.sum[0]-1 if obj.sum[0]<11 else obj.sum[0]+10
            else:
                return 32 if len(obj.sum)==0 else obj.sum[0]-1
    
    @staticmethod
    def _dealer_draws(state):
        return not ( (state>=17 and state<=20) or state>=27)

    @staticmethod
    def _next(state,card_value):
        if state==32:
            return None
        if state==31:
            return 32
        if card_value==11:
            return ProbabilityCountingPlayer.ace_next[state]
        if state<=9:
            return state+card_value if state+card_value<=9 else state+card_value+11
        if state<=20:
            return state+card_value if state+card_value<=20 else state+card_value+1
        return min(state+card_value,32)

    @staticmethod
    def _total(state):
        return state+1 if state<=20 else state-10

    @staticmethod
    def _win_to(state):
        total=ProbabilityCountingPlayer._total(state)
        #return range(total,21)+range(max(total+10,20)+1,33)
        return filter(lambda x: x<=total,range(17,21))+filter(lambda x: x<=total+9,range(27,32))+[32]
    
    @staticmethod
    def _push_to(state):
        total=ProbabilityCountingPlayer._total(state)
        if total>21:
            return []
        if total<10:
            return [total-1,]
        return [total-1,total+10]
    
    def _fraction(self,card_value):
        if self.unseen_cards==0:
            self._reset_counts()
        return self.remaining[card_value]/float(self.unseen_cards)
        
if __name__ == '__main__':
#    game.play_game()
#    player = SARSAPlayer('3', 1000000000, 0.01, 0.01, 0.9)
    players = {
            'probability': ProbabilityCountingPlayer,
            'SARSA': SARSAPlayer,
            'HiLo': HiLoCountingPlayer,
            'basic': BasicStrategyPlayer,
            'human': HumanPlayer,
    }

    if len(argv) < 2 or not argv[1] in players.keys():
        print 'Wrong arguments!'
        exit(-1)

    if len(argv) == 2 and argv[1] != 'human':
        game = GameTable(False)
    else:
        game = GameTable(True)
    player = players[argv[1]]('0', 100000)
    dealer = Dealer();
    ActorManager.get_singleton().register_actor(player, player.player_id)
    ActorManager.get_singleton().register_actor(dealer, 'dealer')
    game.train_player(player, dealer);


