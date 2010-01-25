import wx
import Image
from pysage import Actor, ActorManager, Message 
from simpleui import SimpleUI
import blackjack_messages

BACKGROUND_COLOR = '#1ac500'
ACTIVE_PLAYER_COLOR = 'PURPLE'
INACTIVE_PLAYER_COLOR = 'GRAY'
ELIMINATED_PLAYER_COLOR = '#000000'
PLAYER_LABEL_COLOR = 'WHITE'

NUMBER_OF_PLAYERS = 7

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1320
PANEL_WIDTH = 174
PANEL_HEIGHT = 500
LABEL_OFFSET = 15
CARD_OFFSET_SIDE = 15
CARD_OFFSET_DOWN = 20
CARD_HEIGHT = 123
CARD_WIDTH = 79
COLUMNS_OFFSET = 5
ROWS_OFFSET = 50

class BlackjackTable(wx.Frame, SimpleUI):
    '''The Class representing the main GUI: the table and the players' cards and actions.'''
    def __init__(self, parent, id, title, player_labels, app, active_player=0):
        '''Constructor for BlackjackTable, main class for the game's GUI'''

        wx.Frame.__init__(self, parent, id, title, size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # players_card_numbers - the number of the cards each player has in each of their piles
        # player_labels - labels of the players
        # player_panels - panel instances for each of the players
        # app - a ref to the current application
        self.player_labels = player_labels
        self.player_panels = []
        self.app = app
        self.active_player = active_player

        # Defining the control menu 
        menubar = wx.MenuBar()
        setup = wx.Menu()
        setup.Append(0, '&Setup Game Players and Strategies', 'Setup Game\'players and options')
        setup.Append(1, '&Train a Player', 'Trains a player via neural network')
        setup.Append(2, 'Start &Game', 'Starts a game with the current configuaration')
        setup.Append(3, '&Quit', 'Get away from here')      

        self.Bind(wx.EVT_MENU, self.onSetup, id=0)
        self.Bind(wx.EVT_MENU, self.onTrain, id=1)
        self.Bind(wx.EVT_MENU, self.onStart, id=2)
        self.Bind(wx.EVT_MENU, self.onQuit, id=3)

        menubar.Append(setup,'&Game')
        self.SetMenuBar(menubar)

        DEALER_PANEL_HEIGHT = CARD_HEIGHT + 2 * LABEL_OFFSET + 50

        # Layout panels and sht
        global_panel = wx.Panel(self, -1)
        global_panel.SetBackgroundColour(BACKGROUND_COLOR)

        self.dealer = DealerPanel(global_panel, -1, (0, 0), (PANEL_WIDTH, DEALER_PANEL_HEIGHT))

        vbox = wx.BoxSizer(wx.VERTICAL)
        global_grid1 = wx.GridSizer(1, 7, 5, 0)
        global_grid2 = wx.GridSizer(1, 7, 5, 0)

        #Simple rules panel
        global_grid1.Add(HumanPlayerRulesPanel(global_panel, (PANEL_WIDTH, DEALER_PANEL_HEIGHT), "Rules"))

        # inserting empty spaces (what are we livin' for)
        for i in range(2):
            global_grid1.Add((PANEL_WIDTH, DEALER_PANEL_HEIGHT), 0)

        # adding the Dealer
        global_grid1.Add(self.dealer, 0, wx.TOP, 9)
       
        # inserting empty spaces (what are we livin' for)
        for i in range(3):
            global_grid1.Add((PANEL_WIDTH, DEALER_PANEL_HEIGHT), 0)

        for player in player_labels:
            player_panel = PlayerPanel(global_panel, (PANEL_WIDTH, PANEL_HEIGHT), player)
            global_grid2.Add(player_panel)
            self.player_panels.append(player_panel)

        vbox.Add(global_grid1, 0, wx.BOTTOM, 9)
        vbox.Add(global_grid2, 0, wx.BOTTOM, 9)
        global_panel.SetSizer(vbox)
        global_panel.Bind(wx.EVT_CHAR, self.on_key_down)
        global_panel.SetFocus()

        self.Centre()
        self.Show(True)
        
        #self.app.ExitMainLoop()
        # And here come the Actor's genes
        subscriptions=['DecisionRequest', 'DecisionResponse',\
                      'PlayerHandTurn', 'NextRound', 'WagerRequest',\
                      'WagerResponse', 'BlackjackAnnouncement', 'BustAnnouncement',\
                      'InsuranceOffer', 'InsuranceResponse', 'CardDeal',\
                      'HumanDecisionRequest', 'HumanInsuranceResponse']
        
        print "Blackjack table"

    def restart_gui(self):
        self.app.MainLoop()
        self.app.ExitMainLoop()

    def send_message(self,msg):
        print "GUI sent message"
        msg.sender='gui'
        ActorManager.get_singleton().trigger(msg)

    def handle_NextRound(self,msg):
        # TODO reset all wager fields
        print('*'*50)
        print("\nRound number %s\n" % msg.get_property('round_number')) 
    

    def handle_PlayerHandTurn(self,msg):
        print "PlayerHandTurn message"
        self.set_active_player(int(msg.get_property('player_id')))
        self.player_panels[int(msg.get_property('player_id'))].set_wager_active(int(msg.get_property('hand_number')))
        self.restart_gui()

    def handle_CardDeal(self,msg):
        print "CardDeal"
        player = msg.get_property('player_id')
        card_name = msg.get_property('card')
        if player == 'dealer':
            self.dealer.add_card_to_next_position(card_name)
        else:
            player_no = int(player)
            wager_no = int(msg.get_property('hand_number'))
            self.player_panels[player_no].wager_panels[wager_no].add_card_to_next_position(card_name)
        

    def handle_DecisionRequest(self,msg):
        if msg.get_sender()=='dealer':
            self.dealer.set_action(str(self.player_labels[int(msg.get_property('player_id'))]).append(" play, please"))            
        self.app.MainLoop()
            
    def handle_DecisionResponse(self,msg):
        player = int(msg.get_sender())
        action = msg.get_property('action')
        sel.player_panels[player].wager_panels[0].set_action(action)
        self.restart_gui()
        
    def handle_HumanDecisionRequest(self,msg):
        self.dealer.set_action("HumanPLayer, play, please")        
        self.app.MainLoop()

    def handle_WagerRequest(self,msg):
        if msg.get_sender()=='dealer':
            self.dealer.set_action("Wager request to" + self.player_labels[int(msg.get_property('player_id'))])

        self.restart_gui()
    
    def handle_WagerResponse(self,msg):
        print("Player %s bets %s" % (msg.get_sender(),msg.get_property('wager_amount')))
    
    def handle_HumanWagerRequest(self,msg):
        pass        

    def handle_BlackjackAnnouncement(self,msg):
        player_id = msg.get_sender()
        wager_no = int(msg.get_property('hand_number'))
        if player_id == 'dealer':
            self.dealer.set_action("Blackjack!")
        else:
            self.player_panels[int(player_id)].wager_panels[wager_no].set_action("Blackjack!")

        self.restart_gui()

    def handle_BustAnnouncement(self, msg):
        player_id = msg.get_sender()
        wager_no = int(msg.get_property('hand_number'))
        if player_id == 'dealer':
            self.dealer.set_action("Bust!")
        else:
            self.player_panels[int(player_id)].wager_panels[wager_no].set_action("Bust!")

        self.restart_gui()


    def handle_InsuranceOffer(self, msg):
        self.app.MainLoop()
        self.offer_insurance()
        self.app.ExitMainLoop()

  
    #These functions are called when some option from the game menu is chosen        
    def onQuit(self, event):
        self.Close()

    def onStart(self, event):
        self.offer_insurance()
        event.Skip()

    def onTrain(self, event):
        pass

    def onSetup(self, event):
        GameSetupDialog(None, self.app, -1, "Players and Strategies Options")


    # Dealer asks the HumanPlayer for insurance
    def offer_insurance(self):
        ''' Dealer asks the HumanPlayer for insurance. Answer is processed'''
        insurance = wx.MessageDialog(None, 'Would you like insurance?', 'Insurance', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        reply = insurance.ShowModal()
        if reply == wx.ID_YES:
            #Process the event; HumanPlayer send an action message
            print "YES!"
        else:
            print "NO!"
    

    def on_key_down(self, event):
        '''Event handler for a keypad button pressed'''
        keycode = event.GetKeyCode()

        if keycode == wx.WXK_ESCAPE:
            self.app.ExitMainLoop()
            if self.player_panels[self.active_player].active_wager > 2:
                self.set_active_player(self.active_player + 1)
            else:
                self.player_panels[self.active_player].set_wager_active(self.player_panels[self.active_player].active_wager + 1)

            self.app.MainLoop()
            self.app.ExitMainLoop()

        # H - hit
        elif keycode == 72:
            print "HumanPlayer: hit!"                
            self.app.ExitMainLoop()
            self.send_message(HumanDecisionResponse(player_id=msg.get_sender(),action='hit'))

        # S -stand
        elif keycode == 83:
            print "HumanPlayer: stand!"
            self.app.ExitMainLoop()
            self.send_message(HumanDecisionResponse(player_id=msg.get_sender(),action='stand'))
            

        # D - double down
        elif keycode == 68:
            print "D"

        # M - split
        elif keycode == 77:
            print "M"


    def set_active_player(self, player_no):
        '''Colors the active player in the ACTIVE_PLAYER_COLOR to emphasize who is he.'''
        self.player_panels[self.active_player].SetBackgroundColour(INACTIVE_PLAYER_COLOR)
        for wager_panel in self.player_panels[self.active_player].wager_panels:
            wager_panel.set_active(False)
        self.active_player = player_no
        self.player_panels[self.active_player].SetBackgroundColour(ACTIVE_PLAYER_COLOR)


    def set_eliminated_player(self, player_no):
        self.player_panels[player_no].SetBackgroundColour(ELIMINATED_PLAYER_COLOR)       
        self.player_panels[player_no].wager_panels[0].set_action('Eliminated.')

    def reset_scene(self, event):
        pass


class GameSetupDialog(wx.Dialog):
    '''A class defining the dialog box for choosing players and strategies'''
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, app, id, title, size=(500, 300))
        
        
        panel = wx.Panel(self, -1, (10, 10), (480, 290))        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(panel, -1, 'Please choose player types and player strategies:', (0, 0)))

        self.app = app
        self.players = ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5", "Player 6", "Player 7"]
        self.player_types = ["DrunkPlayer", "BasicStrategyPlayer", "HiLoCountingPlayer", "ProbabilityCountingPlayer", "SARSALearningPlayer", "HumanPlayer"]
        self.strategies = ["Random Bet", "Count Bet", "Kelly", "Half Kelly", "Paroli", "Labouchere", "Martingale"]
        self.players_strategies = {\
            "No Player": [],\
            "DrunkPlayer": ["Random Bet", "Paroli", "Labouchere", "Martingale"],\
            "BasicStrategyPlayer": ["Random Bet", "Paroli", "Labouchere", "Martingale"],\
            "HiLoCountingPlayer": ["Random Bet", "Count Bet", "Paroli", "Labouchere", "Martingale"],\
            "ProbabilityCountingPlayer": ["Random Bet", "Kelly", "Half Kelly", "Paroli", "Labouchere", "Martingale"],\
            "SARSALearningPlayer": ["Random Bet", "Paroli", "Labouchere", "Martingale"],\
            "HumanPlayer": [] }

        self.players_num = 7
        
        self.first_combo_boxes = []
        self.second_combo_boxes = [wx.ComboBox(panel, -1, pos=(300, (i + 1) * 20), size=(150, -1), choices=[], style=wx.CB_READONLY) for i in range(self.players_num)]
        
        count = 0
        for combo in self.second_combo_boxes:
            combo.index = self.players_num + count
            combo.SetValue("None")
            count += 1

        grid = wx.GridSizer(7, 3, 20, 3)
        row_count = 0
        for player_choice in self.players:
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            text = wx.StaticText(panel, -1, "Type of " + player_choice, (0, (row_count + 1) * 20))
            combo = wx.ComboBox(panel, row_count, pos=(100, (row_count + 1) * 20), size=(150, -1), choices=self.player_types, style=wx.CB_READONLY)
            combo.SetValue("None")
            self.first_combo_boxes.append(combo)
            combo.index = row_count
            grid.Add(text)
            grid.Add(combo)
            grid.Add(self.second_combo_boxes[row_count])
            row_count += 1

        vbox.Add(grid)
        
        button = wx.Button(panel, 123, 'Done')
        self.Bind(wx.EVT_BUTTON, self.confDone)
        vbox.Add(button)
        panel.SetSizer(vbox)

        self.Bind(wx.EVT_COMBOBOX, self.OnSelect)

        self.Centre()
        self.ShowModal()
        self.Destroy()
    
    
    def OnClose(self, event):
        self.Close()

    def OnSelect(self, event):
        combo = event.GetEventObject()
        if combo.index < self.players_num:
            #self.second_combo_boxes[combo.index].choices = self.players_strategies[self.player_types[combo.index]]
            #self.app.ExitMainLoop()
            self.second_combo_boxes[combo.index] = wx.ComboBox(self.panel, row_count, pos=(100, (row_count + 1) * 20), size=(150, -1), choices=self.players_strategies[self.player_types[combo.index]])
            print self.players_strategies[self.player_types[combo.index]]
            #self.app.MainLoop()
        else:
            pass
        print combo.index
            

    def confDone(self, event):
        for chosen_player in self.first_combo_boxes:
            if chosen_player.GetValue() != "None":
                print chosen_player.GetValue()
        #parse current configuration
        self.Close()


class PlayerPanel(wx.Panel):
    '''This class holds all the wager panels of a player'''
    def __init__(self, parent, size, player_name, strategy_name="some"):
        super(wx.Panel, self).__init__(parent, -1, (0, 0), size)
        self.SetBackgroundColour(BACKGROUND_COLOR)

        self.active_wager = 0

        self.wager_panels = []

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        label_panel = wx.Panel(self, -1, (0, 0), (PANEL_WIDTH, LABEL_OFFSET * 2))
        label_panel.SetBackgroundColour(PLAYER_LABEL_COLOR)
        player_label = wx.StaticText(label_panel, -1, "PLAYER: " + str(player_name), (0, 0))
        strategy_label = wx.StaticText(label_panel, -1, "STRATEGY: " + strategy_name, (0, LABEL_OFFSET))

        wagers_panel = wx.Panel(self, -1, (0, LABEL_OFFSET*2), (PANEL_WIDTH, PANEL_HEIGHT - LABEL_OFFSET))
        wagers_panel.SetBackgroundColour(BACKGROUND_COLOR)

        wagers_grid = wx.GridSizer(2, 2, 20, 20)

        #Here we create a WagerPanel for each of the four possible wagers of a player
        for i in range(4):
            if i < 2:
                wager_panel = WagerPanel(wagers_panel, i, (i * (PANEL_WIDTH / 2), 0), (PANEL_WIDTH / 2, PANEL_HEIGHT / 2 - LABEL_OFFSET))
            else:
                wager_panel = WagerPanel(wagers_panel, i, ((i % 2) * (PANEL_WIDTH / 2), PANEL_HEIGHT / 2 - LABEL_OFFSET), (PANEL_WIDTH / 2, PANEL_HEIGHT / 2 - LABEL_OFFSET))
            self.wager_panels.append(wager_panel)

        vbox.Add(strategy_label, 0, wx.BOTTOM, 9)
        vbox.Add(player_label, 0, wx.BOTTOM, 9)
        vbox.Add(wagers_panel, 0, wx.BOTTOM, 9)
        self.SetSizer(vbox)

        self.Bind(wx.EVT_PAINT, self.paint)
#        self.add_card_to_player_in_pile('Ace of Spades', 3)



    def paint(self, event):
        pass


    def add_card_to_player_in_pile(self, card_name, wager_no):
        '''Adds a card, denoted by its conventional name(as in card_utils.py) \n
           to the wager, denoted by wager_no.'''
        if wager_no > 3 or wager_no < 0:
            pass
        else:
            if self.active_wager != wager_no:
                self.set_wager_active(wager_no)
            self.wager_panels[wager_no].add_card_to_next_position(card_name)

    def set_wager_active(self, wager_no):
        '''The next wager that the player will play with is set to active\n
            (by changing its panel's background color to ACTIVE_COLOR)\n
            the current active wager panel becomes the wager_no-th one.'''
        self.wager_panels[self.active_wager].set_active(False)
        self.active_wager = wager_no
        self.wager_panels[self.active_wager].set_active(True)

    def reset(self):
        '''The current PlayerPanel is reset as for a new game.'''
        for wager_panel in self.wager_panels:
            wager_panel.reset()



class CardPanel(wx.Panel):
    '''A parent class for DealerPanel and WagerPanel, containing the common classes.'''
    def __init__(self, parent, id, position, size):
        '''Constructor for the class \n setting parent, to which this CardPanel is a child,
        id - God knows why wxPython need that param, \n
        position - the relative position to the parent's coordinates, \n
        size - the panel's size expressed in a tuple, (width, height)'''
        super(wx.Panel, self).__init__(parent, id, position, size)
        self.action_label = wx.StaticText(self, -1, "ACTION: ", (0, LABEL_OFFSET))

    def extract_file_name(self, card_name):
        '''Extracts an image file name from card_name'''
        file_name = str(card_name).replace(" ", "").lower()
        return "../images/" + file_name + ".png"

    def set_action(self, action=""):
        '''Setter for the aaction label(the action param denotes the action performed.'''
        action_string = "ACTION " + action
        self.action_label = wx.StaticText(self, -1, action_string, (0, LABEL_OFFSET))

    def add_card_to_position (self, image_file_name, x, y, id):
        '''Adds a card(specified by its filename) to the specified,
        local for this PlayerPanel,  coordinates'''
        try:
            image = wx.Image(image_file_name, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            wx.StaticBitmap(self, id, image, (x, y), (CARD_WIDTH, CARD_HEIGHT))
        except IOError:
            print "Image file %s not found" % image_file_name

    def reset(self):
        pass



class DealerPanel(CardPanel):
    '''Inherits CardPanel. Special panel for the Dealer. Cards here are situated horizontally instead of vertically.'''
    def __init__(self, parent, id, position, size):
        '''Constructor. Takes parent, id, position and size for the parent constructor.'''
        super(CardPanel, self).__init__(parent, id, position, size)
        self.SetBackgroundColour(INACTIVE_PLAYER_COLOR)

        wx.StaticText(self, -1, "DEALER" , (0, 0))

        self.number_of_cards = 0
        self.action_label = wx.StaticText(self, -1, "ACTION: ", (0, LABEL_OFFSET), (200, 20))

        # keeps the name of the first card that stays hidden
        self.initial_card = ""
        
#        self.add_card_to_next_position("Ten of Spades")
 #       self.add_card_to_next_position("Ace of Hearts") 
     #   self.add_card_to_next_position("Ace of Hearts") 
      #  self.unhide_initial_card()

    def reset(self):
        CardPanel.reset(self)

    def extract_file_name(self, card_name):
        '''Extracts an image file name from card_name'''
        return CardPanel.extract_file_name(self, card_name)

    def set_action(self, action=""):
        '''Setter for the aaction label(the action param denotes the action performed.'''
        CardPanel.set_action(self, action)

    def add_card_to_position (self, image_file_name, x, y, id):
        '''Adds a card(specified by its filename) to the specified,
        local for this PlayerPanel,  coordinates'''
        CardPanel.add_card_to_position(self, image_file_name, x, y, id)

    def add_card_to_next_position(self, card_name):
        '''This methods adds the card, whose name by convention is card_name,
        to the pile of the dealer'''
        if self.number_of_cards == 0:
            self.initial_card = card_name
            self.add_card_to_position("../images/back.png", 0, LABEL_OFFSET * 2, self.number_of_cards)
        else:
            card_image_file_name = self.extract_file_name(card_name)
            self.add_card_to_position(card_image_file_name, CARD_WIDTH + self.number_of_cards * CARD_OFFSET_SIDE, LABEL_OFFSET * 2, self.number_of_cards)
        self.number_of_cards += 1

    def unhide_initial_card(self):
        card_image_file_name = self.extract_file_name(self.initial_card)
        self.add_card_to_position(card_image_file_name, 0, LABEL_OFFSET * 2, 0)



class WagerPanel(CardPanel):
    def __init__(self, parent, id, position, size):

        super(CardPanel, self).__init__(parent, id, position, size)
        self.SetBackgroundColour(INACTIVE_PLAYER_COLOR)

        self.number_of_cards = 0
        self.wager_label = wx.StaticText(self, -1, "WAGER: ", (0, 0))
        self.action_label = wx.StaticText(self, -1, "ACTION: ", (0, LABEL_OFFSET))

#        self.add_card_to_next_position("King of Hearts")

    def reset(self):
        CardPanel.reset(self)

    def extract_file_name(self, card_name):
        '''Extracts an image file name from card_name'''
        return CardPanel.extract_file_name(self, card_name)

    def set_action(self, action=""):    
        '''Setter for the action label(the action param denotes the action performed).'''
        CardPanel.set_action(self, ction)

    def set_wager(self, wager=0):
        '''Setter for the wager label(the wager param denotes the wager performed).'''
        wager_string = "WAGER" + str(wager)
        self.wager_label = wx.StaticText(self, -1, "WAGER: ", (0, 0))

    def add_card_to_position (self, image_file_name, x, y, id):
        '''Adds a card(specified by its filename) to the specified,
        local for this PlayerPanel,  coordinates'''
        CardPanel.add_card_to_position(self, image_file_name, x, y, id)

    def add_card_to_next_position(self, card_name):
        '''This methods adds the card, whose name by convention is card_name,
            to the pile of that wager'''
        card_image_file_name = self.extract_file_name(card_name)
        self.add_card_to_position(card_image_file_name, 0, self.number_of_cards * CARD_OFFSET_DOWN + LABEL_OFFSET * 2, self.number_of_cards)
        self.number_of_cards += 1

    def set_active(self, active=True):
        '''Setter for if the Panel is active; color the active panel.'''
        self.SetBackgroundColour(ACTIVE_PLAYER_COLOR) if active else self.SetBackgroundColour(INACTIVE_PLAYER_COLOR)



class HumanPlayerRulesPanel(wx.Panel):
    '''Simple class with only labels to denote rules for the HumanPlayer'''
    def __init__(self, parent, size, player_label):
        super(wx.Panel, self).__init__(parent, -1, (0, 0), size)
        self.SetBackgroundColour(BACKGROUND_COLOR)
        wx.StaticText(self, -1, "HUMAN PLAYER:", (0, 0))
        wx.StaticText(self, -1, "Keyboard Actions:", (0, LABEL_OFFSET))
        wx.StaticText(self, -1, "", (0, LABEL_OFFSET * 2))
        wx.StaticText(self, -1, "Shift + H - Hit", (0, LABEL_OFFSET * 3))
        wx.StaticText(self, -1, "Shift + S - Stand", (0, LABEL_OFFSET * 4))
        wx.StaticText(self, -1, "Shift + M - Split", (0, LABEL_OFFSET * 5))
        wx.StaticText(self, -1, "Shift + D - Double Down", (0, LABEL_OFFSET * 6))

#app = wx.App()
#BlackjackTable(None, -1, 'Blackjack',[ "player 0", "player 1", "player 2", "player 3", "player 4", "player 5", "player 6"], app)
#app.MainLoop()
