import wx
import Image
import pysage
import string

BACKGROUND_COLOR = '#1ac500'
INACTIVE_PLAYER_COLOR = 'ffffff'

NUMBER_OF_PLAYERS = 7

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1240
PANEL_WIDTH = 170
PANEL_HEIGHT = 300
LABEL_OFFSET = 15
CARD_OFFSET_SIDE = 15
CARD_OFFSET_DOWN = 30
CARD_HEIGHT = 123
CARD_WIDTH = 79
COLUMNS_OFFSET = 5
ROWS_OFFSET = 50


class BlackjackGUI(wx.Frame, pysage.Actor):
        '''The Class representing the main GUI: the table and the players' cards and actions.'''
 	def __init__(self, parent, id, title, player_labels):
		wx.Frame.__init__(self, parent, id, title, size=(SCREEN_WIDTH, SCREEN_HEIGHT))

                # players_card_numbers - the number of the cards each player has in each of their piles
                # player_labels - labels of the players
                # player_panels - panel instances for each of the players
		self.player_labels = player_labels
		self.players_card_numbers = []
                for counter in range(NUMBER_OF_PLAYERS):
                        self.players_card_numbers.append([0, 0, 0, 0])
                self.player_panels = []                
               
		global_panel = wx.Panel(self, -1)
		global_panel.SetBackgroundColour(BACKGROUND_COLOR)
  
		global_grid = wx.GridSizer(2, 7, 10, 30)
                #inserting empty spaces (what are we livin' for)
		for i in range(3):
			global_grid.Add((PANEL_WIDTH, PANEL_HEIGHT), 0)

                #adding the Dealer
		global_grid.Add(PlayerPanel(global_panel, (SCREEN_WIDTH / 2, 0), (PANEL_WIDTH, PANEL_HEIGHT), "Dealer"), 1, wx.TOP, 50)

                #inserting empty spaces (what are we livin' for)
		for i in range(3):
                        global_grid.Add((PANEL_WIDTH, PANEL_HEIGHT), 0)
		for player in player_labels: 
                        player_panel = PlayerPanel(global_panel, (0, 0), (PANEL_WIDTH, PANEL_HEIGHT), player)
			global_grid.Add(player_panel)
                        self.player_panels.append(player_panel)

		global_panel.SetSizer(global_grid)

		self.Centre()
		self.Show(True)
		#self.Bind(wx.EVT_PAINT, self.refresh_scene)	

	def refresh_scene(self, event):
		pass


	def add_card_to_position (self, image_file_name, x, y, id):
		try:
			image = wx.Image(image_file_name, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			wx.StaticBitmap(self, id, image, (x, y), (image.GetWidth(), image.GetHeight()))
		except IOError:
			print "Image file %s not found" % image_file_name
			raise SystemExit

class PlayerPanel(wx.Panel):
	def __init__(self, parent, position, size, player_label):
		super(wx.Panel, self).__init__(parent, -1, position, size)
		self.SetBackgroundColour('RED')
                self.player_label = wx.StaticText(self, -1, "PLAYER: "player_label, (0, 0))
                self.wager_label = wx.StaticText(self, -1, "WAGER: ", (0, LABEL_OFFSET))
                self.action_label = wx.StaticText(self, -1, "ACTION: ", (0, 2 * LABEL_OFFSET))

		#self.add_card_to_position('../images/queenofdiamonds.png', 0, LABEL_OFFSET * 2, 0)
		#self.add_card_to_position('../images/queenofclubs.png', CARD_WIDTH + COLUMNS_OFFSET, LABEL_OFFSET * 2, 1)
		#self.add_card_to_position('../images/queenofhearts.png', 0, CARD_HEIGHT + ROWS_OFFSET, 2)
		#self.add_card_to_position('../images/queenofspades.png', CARD_WIDTH + COLUMNS_OFFSET, CARD_HEIGHT + ROWS_OFFSET, 3)

		self.Bind(wx.EVT_PAINT, self.paint)

	def paint(self, event):
		pass

        def add_card_to player_in_pile(cardsuit, cardrank, )
        def add_card_to_position (self, image_file_name, x, y, id):
                try:
                        image = wx.Image(image_file_name, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                        wx.StaticBitmap(self, id, image, (x, y), (image.GetWidth(), image.GetHeight()))
                except IOError:
                        print "Image file %s not found" % image_file_name
 
app = wx.App()
BlackjackGUI(None, -1, 'Blackjack',[ "player_0", "player_1", "player_2", "player_3", "player_4", "player_5", "player_6"])
app.MainLoop()


