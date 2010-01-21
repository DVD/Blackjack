from pysage import Actor, ActorManager, Messages
from blackjack_messages import *

class SimpleUI(Actor):
    subscriptions=[
            'DecisionRequest', 'DecisionResponse', 'PlayerTurn',
            'PlayerHandTurn', 'NextRound', 'WagerRequest', 
            'WagerResponse', 'BlackjackAnnouncement', 'BustAnnouncement',
            'InsuranceOffer', 'InsuranceResponse', 'CardDeal'
            'HumanDecisionResponse', 'HumanInsuranceResponse', 
            ]
    def send_message(self,msg):
        msg.sender='ui'
        ActionManager.get_singleton().trigger(msg)

    def handle_NextRound(self,msg):
        print('*'*50)
        print("\nRound number %s\n" % msg.get_property('round_number'))

    def handle_PlayerHandTurn(self,msg):
        print("Next to play: Player %s, hand %s" % (msg.get_property('player_id'),msg.get_property('hand_number')))

    def handle_CardDeal(self,msg):
        print("Dealer gives player %s a %s (hand %s)" % (msg.get_property('player_id'),msg.get_property('card'),msg.get_property('hand_number')))

    def handle_DecisionRequest(self,msg):
        if msg.get_sender()=='dealer':
            print("Dealer asks %s for decision on hand %s" % (msg.get_property('player_id'), msg.get_property('hand_number')))

    def handle_DecisionResponse(self,msg):
        print("Player %s decides to %s" % (msg.get_sender(), msg.get_property('action')))

    def handle_HumanDecisionRequest(self,msg):
        answer=None
        while not answer in msg.get_property('allowed_actions'):
            answer=raw_input("How do you play? %s :" % msg.get_property('allowed_actions'))
        send_message(HumanDecisionResponse(player_id=msg.get_sender(),action=answer))

    def handle_WagerRequest(self,msg):
        if msg.get_sender()=='dealer':
            print("Dealer asks %s to place their wager" % msg.get_property('player_id'))

    def handle_WagerResponse(self,msg):
        print("Player %s bets %s" % (msg.get_sender(),msg.get_property('wager_amount')))

    def handle_HumanWagerRequest(self,msg):
        wager=int(raw_input("Place your wager:"))
        send_message(HumanWagerResponse(player_id=msg.get_sender(),wager_amount=wager))

    def handle_InsuranceOffer(self,msg):
        print("Dealer offers player %s to make an insurance bet" % msg.get_property('player_id'))

    def handle_InsuranceResponse(self,msg):
        print("Player %s says: %s" % (msg.get_sender(),msg.get_property('answer')))

    def handle_HumanInsuranceOffer(self,msg):
        response=None
        while not response in ('yes','no'):
            response=raw_input("Do you wish to make an insurance bet? (yes,no): ")
        send_message(HumanInsuranceResponse(player_id=msg.get_sender(),answer=response))

    def handle_BlackjackAnnouncement(self,msg):
        if msg.get_sender()=='dealer':
            print("Dealer has a blackjack!!!")
        else:
            print("Player %s has a blackjack!!!" % msg.get_sender())

    def handle_BustAnnouncement(self,msg):
        if msg.get_sender()=='dealer':
            print("Dealer busts!")
        else:
            print("Player %s busts!" % msg.get_sender())

