import wx
import Image
import pysage
import string

BACKGROUND_COLOR = '#1ac500'
ACTIVE_PLAYER_COLOR = 'PURPLE'
INACTIVE_PLAYER_COLOR = 'GRAY'
PLAYER_LABEL_COLOR = 'WHITE'

NUMBER_OF_PLAYERS = 7

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1320
PANEL_WIDTH = 170
PANEL_HEIGHT = 500
LABEL_OFFSET = 15
CARD_OFFSET_SIDE = 15
CARD_OFFSET_DOWN = 30
CARD_HEIGHT = 123
CARD_WIDTH = 79
COLUMNS_OFFSET = 5
ROWS_OFFSET = 50


class BlackjackTable(wx.Frame, pysage.Actor):
    '''The Class representing the main GUI: the table and the players' cards and actions.'''
    def __init__(self, parent, id, title, player_labels, app, active_player=0):
        '''Constructor for BlackjackTable, main class for the game's GUI'''
        wx.Frame.__init__(self, parent, id, title, size=(SCREEN_WIDTH, SCREEN_HEIGHT))

        # players_card_numbers - the number of the cards each player has in each of their piles
        # player_labels - labels of the players
        # player_panels - panel instances for each of the players
        self.player_labels = player_labels


        menubar = wx.MenuBar()
        file = wx.Menu()
        file.Append(-1, 'Quit', 'Quit application')
        menubar.Append(file, '&File')
        self.SetMenuBar(menubar)

        self.player_panels = []
        self.app = app
        self.active_player = active_player

        global_panel = wx.Panel(self, -1)
        global_panel.SetBackgroundColour(BACKGROUND_COLOR)

        vbox = wx.BoxSizer(wx.VERTICAL)
        global_grid1 = wx.GridSizer(1, 7, 5, 0)
        global_grid2 = wx.GridSizer(1, 7, 5, 0)

        DEALER_PANEL_HEIGHT = CARD_HEIGHT + 2 * LABEL_OFFSET + 50

        # inserting empty spaces (what are we livin' for)
        for i in range(3):
            global_grid1.Add((PANEL_WIDTH, DEALER_PANEL_HEIGHT), 0)

        # adding the Dealer
        global_grid1.Add(DealerPanel(global_panel, -1, (0, 0), (PANEL_WIDTH * 2, DEALER_PANEL_HEIGHT)), 1, wx.TOP, 50)

        # inserting empty spaces (what are we livin' for)
        global_grid1.Add((PANEL_WIDTH, DEALER_PANEL_HEIGHT), 0)

        # adding the HumanPlayerRulesMunu as a legend
        global_grid1.Add(HumanPlayerRulesPanel(global_panel, (PANEL_WIDTH, DEALER_PANEL_HEIGHT), "Rules"))

        # inserting empty spaces (what are we livin' for)
        global_grid1.Add((PANEL_WIDTH, DEALER_PANEL_HEIGHT), 0)

        for player in player_labels:
            player_panel = PlayerPanel(global_panel, (PANEL_WIDTH, PANEL_HEIGHT), player)
            global_grid2.Add(player_panel)
            self.player_panels.append(player_panel)

        vbox.Add(global_grid1, 0, wx.TOP, 9)
        vbox.Add(global_grid2, 0, wx.BOTTOM, 9)
        global_panel.SetSizer(vbox)
        global_panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        global_panel.SetFocus()

        self.Centre()
        self.Show(True)
        #self.Bind(wx.EVT_PAINT, self.refresh_scene)

    def on_key_down(self, event):
        '''Event handler for a keypad button pressed'''
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.app.ExitMainLoop()
            print "MainLoopExited"
            if self.player_panels[self.active_player].active_wager > 3:
                self.set_active_player(self.active_player + 1)
            else:
                self.player_panels[self.active_player].set_wager_active(self.player_panels[self.active_player].active_wager + 1)

            self.app.MainLoop()
            self.app.ExitMainLoop()
        event.Skip()

    def set_active_player(self, player_no):
        '''Colors the active player in the ACTIVE_PLAYER_COLOR to emphasize who is he.'''
        self.player_panels[self.active_player].SetBackgroundColour(INACTIVE_PLAYER_COLOR)
        self.active_player = player_no
        self.player_panels[self.active_player].SetBackgroundColour(ACTIVE_PLAYER_COLOR)



    def reset_scene(self, event):
        pass



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
        player_label = wx.StaticText(label_panel, -1, "PLAYER: " + player_name, (0, 0))
        strategy_label = wx.StaticText(label_panel, -1, "STRATEGY: " + strategy_name, (0, LABEL_OFFSET))

        wagers_panel = wx.Panel(self, -1, (0, LABEL_OFFSET), (PANEL_WIDTH, PANEL_HEIGHT - LABEL_OFFSET * 2))
        wagers_panel.SetBackgroundColour(BACKGROUND_COLOR)

        wagers_grid = wx.GridSizer(2, 2, 20, 20)

        #Here we create a WagerPanel for each of the four possible wagers of a player
        for i in range(4):
            if i < 2:
                wager_panel = WagerPanel(wagers_panel, i, (i * (PANEL_WIDTH / 2), 0), (PANEL_WIDTH / 2, PANEL_HEIGHT / 2))
            else:
                wager_panel = WagerPanel(wagers_panel, i, ((i % 2) * (PANEL_WIDTH / 2), PANEL_HEIGHT / 2), (PANEL_WIDTH / 2, PANEL_HEIGHT / 2))
            wagers_grid.Add(wager_panel)

            self.wager_panels.append(wager_panel)
        wagers_panel.SetSizer(wagers_grid)

        vbox.Add(strategy_label, 0, wx.BOTTOM, 9)
        vbox.Add(player_label, 0, wx.BOTTOM, 9)
        vbox.Add(wagers_panel, 0, wx.BOTTOM, 9)
        self.SetSizer(vbox)

        self.Bind(wx.EVT_PAINT, self.paint)
        self.add_card_to_player_in_pile('Ace of Spades', 3)



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
        file_name = card_name.replace(" ", "").lower()
        return "../images/" + file_name + ".png"

    def set_action(self, action=""):
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
        self.action_label = wx.StaticText(self, -1, "ACTION: ", (0, LABEL_OFFSET))

        self.add_card_to_position('../images/queenofdiamonds.png', 0, LABEL_OFFSET * 2, 0)


        def reset(self):
            CardPanel.reset(self)

        def extract_file_name(self, card_name):
            '''Extracts an image file name from card_name'''
            return CardPanel.extract_file_name(self, card_name)

        def set_action(self, action=""):
            CardPanel.set_action(self, ction)


        def add_card_to_position (self, image_file_name, x, y, id):
            '''Adds a card(specified by its filename) to the specified,
              local for this PlayerPanel,  coordinates'''
            CardPanel.add_card_to_position(self, image_file_name, x, y, id)

        def add_card_to_next_position(self, card_name):
            '''This methods adds the card, whose name by convention is card_name,
              to the pile of the dealer'''
            card_image_file_name = self.extract_file_name(card_name)
            self.add_card_to_position(card_image_file_name, LABEL_OFFSET * 2, self.number_of_cards * CARD_OFFSET_SIDE, self.number_of_cards)
            self.number_of_cards += 1



class WagerPanel(CardPanel):
    def __init__(self, parent, id, position, size):

        super(CardPanel, self).__init__(parent, id, position, size)
        self.SetBackgroundColour(INACTIVE_PLAYER_COLOR)

        self.number_of_cards = 0
        self.wager_label = wx.StaticText(self, -1, "WAGER: ", (0, 0))
        self.action_label = wx.StaticText(self, -1, "ACTION: ", (0, LABEL_OFFSET))

        self.add_card_to_position('../images/queenofdiamonds.png', 0, LABEL_OFFSET * 2, 0)


    def reset(self):
        CardPanel.reset(self)

    def extract_file_name(self, card_name):
        '''Extracts an image file name from card_name'''
        return CardPanel.extract_file_name(self, card_name)

    def set_action(self, action=""):
        CardPanel.set_action(self, ction)

    def set_wager(self, wager=0):
        wager_string = "WAGER" + str(wager)
        self.wager_label = wx.StaticText(self, -1, "WAGER: ", (0, 0))

    def add_card_to_position (self, image_file_name, x, y, id):
        '''Adds a card(specified by its filename) to the specified,
        local for this PlayerPanel,  coordinates'''
        CardPanel.add_card_to_position(self, image_file_name, x, y, id)

    def add_card_to_next_position(self, card_name):
        '''This methods adds the card, whose name by convention is card_name,
            to the pile of that particular wager'''
        card_image_file_name = self.extract_file_name(card_name)
        self.add_card_to_position(card_image_file_name, 0, -1 * self.number_of_cards * CARD_OFFSET_DOWN, self.number_of_cards)
        self.number_of_cards += 1

    def set_active(self, active=True):
        self.SetBackgroundColour(ACTIVE_PLAYER_COLOR) if active else self.SetBackgroundColour(INACTIVE_PLAYER_COLOR)



class HumanPlayerRulesPanel(wx.Panel):
    def __init__(self, parent, size, player_label):
        super(wx.Panel, self).__init__(parent, -1, (0, 0), size)
        self.SetBackgroundColour(BACKGROUND_COLOR)
        wx.StaticText(self, -1, "HUMAN PLAYER:", (0, 0))
        wx.StaticText(self, -1, "Keyboard Actions:", (0, LABEL_OFFSET))
        wx.StaticText(self, -1, "", (0, LABEL_OFFSET * 2))
        wx.StaticText(self, -1, "H - Hit", (0, LABEL_OFFSET * 3))
        wx.StaticText(self, -1, "D - Deal", (0, LABEL_OFFSET * 4))
        wx.StaticText(self, -1, "S - Split", (0, LABEL_OFFSET * 5))
        wx.StaticText(self, -1, "W - Double Down", (0, LABEL_OFFSET * 6))

app = wx.App()
BlackjackTable(None, -1, 'Blackjack',[ "player 0", "player 1", "player 2", "player 3", "player 4", "player 5", "player 6"], app)
app.MainLoop()
