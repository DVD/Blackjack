import wx
import Image

BACKGROUND_COLOR = '#1ac500'
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1240
CARD_OFFSET_SIDE = 15
CARD_OFFSET_DOWN = 30
CARD_HEIGHT = 123
CARD_WIDTH = 79
COLUMNS_OFFSET = 5
ROWS_OFFSET = 50


class BlackjackGUI(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title, size=(SCREEN_WIDTH, SCREEN_HEIGHT))
		self.SetBackgroundColour(BACKGROUND_COLOR)
		#self.Bind(wx.EVT_PAINT, self.refresh_scene)		
		global_panel = wx.Panel(self, -1)
		global_panel.SetBackgroundColour(BACKGROUND_COLOR)
		global_grid = wx.GridSizer(2, 7)
		i = 0
		for i in range(14): 
			global_grid.Add	(PlayerPanel(global_panel, (0, 200), (400, 300), "player"))
			#global_grid.Add(wx.StaticText(global_panel, -1, 'Find: ', (5, 5)), 0,  wx.ALIGN_CENTER_VERTICAL)
		global_panel.SetSizer(global_grid)
		#global_hbox = wx.BoxSizer(wx.HORIZONTAL)
		#global_vbox = wx.BoxSizer(wx.VERTICAL)
		#panel = PlayerPanel(global_panel, (0, 200), (400, 300), "player1")

                #global_vbox.Add(panel, 1, wx.LEFT, 100)
                #global_hbox.Add(panel, 1, wx.TOP, 50)

		#global_panel.SetSizer(global_hbox)
		#global_panel.SetSizer(global_vbox)

		self.Centre()
		self.Show(True)

	def refresh_scene(self, event):
		self.add_card_to_position('images/queenofdiamonds.png' , 100, 100, 0)
		self.add_card_to_position('images/queenofspades.png' , 100 + CARD_OFFSET_SIDE, 100 + CARD_OFFSET_DOWN, 1)


	def add_card_to_position (self, image_file_name, x, y, id):
		try:
			image = wx.Image(image_file_name, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
			wx.StaticBitmap(self, id, image, (x, y), (image.GetWidth(), image.GetHeight()))
		except IOError:
			print "Image file %s not found" % image_file_name
			raise SystemExit

class PlayerPanel(wx.Panel):
	def __init__(self, parent, position, size, player_name):
		super(wx.Panel, self).__init__(parent, -1, position, size)
		self.SetBackgroundColour('RED')
		
		#sizer = wx.GridBagSizer(0, 0)

		#text1 = wx.StaticText(self, -1, player_name)
                #sizer.Add(text1, (0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=15)	
		self.add_card_to_position('images/queenofdiamonds.png', 0, 0, 0)
		self.add_card_to_position('images/queenofclubs.png', CARD_WIDTH + COLUMNS_OFFSET, 0, 1)
		self.add_card_to_position('images/queenofhearts.png', 0, CARD_HEIGHT + ROWS_OFFSET, 2)
		self.add_card_to_position('images/queenofspades.png', CARD_WIDTH + COLUMNS_OFFSET, CARD_HEIGHT + ROWS_OFFSET, 3)

		#sizer.Fit(self)
		#self.SetSizer(sizer)
		self.Bind(wx.EVT_PAINT, self.paint)

	def paint(self, event):
		pass

        def add_card_to_position (self, image_file_name, x, y, id):
                try:
                        image = wx.Image(image_file_name, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                        wx.StaticBitmap(self, id, image, (x, y), (image.GetWidth(), image.GetHeight()))
                except IOError:
                        print "Image file %s not found" % image_file_name
                        raise SystemExit

app = wx.App()
BlackjackGUI(None, -1, 'Blackjack')
app.MainLoop()


