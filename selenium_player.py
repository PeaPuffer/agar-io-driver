from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import json
import random
import time


class AgarIODriver(object):

	CANVAS_ID = 'canvas'
	PLAY_BUTTON_CLASS = "btn-play-guest"
	CONTINUE_BUTTON_ID = "statsContinue"

	WINDOW_SIZE_X = 200
	WINDOW_SIZE_Y = 300

	PROXY = '127.0.0.1:8080'

	GET_CANVAS_PIXELS_JAVASCRIPT = """
		var canvas = document.getElementById('canvas');
		var canvasWidth = canvas.width;
		var canvasHeight = canvas.height;
		var ctx = canvas.getContext('2d');
		var imageData = ctx.getImageData(0, 0, canvasWidth, canvasHeight);
		return '[' + String(Array.prototype.slice.call(imageData.data)) + ']';
		"""

	GET_SCORE_JAVASCRIPT = "return document.getElementById('score').innerHTML"

	IS_GAME_OVER_JAVASRIPT = """
	    var continueBttn = document.getElementById("statsContinue");
		var bttnIsVisible = (continueBttn.offsetParent != null);
		return bttnIsVisible;
		"""

	START_NEW_GAME_JAVASCRIPT = "setNick('');"

	def __init__(self):
		self.driver = self._get_chrome_webdriver()
		self.driver.set_window_size(self.WINDOW_SIZE_X, self.WINDOW_SIZE_Y)
		self.driver.get('http://agar.io')
		self.canvas_element = self.driver.find_element(By.ID, self.CANVAS_ID)
		self.canvas_width = self.canvas_element.size['width']
		self.canvas_height = self.canvas_element.size['height']

		self.play_button = self.driver.find_element_by_class_name(self.PLAY_BUTTON_CLASS)
		self.continue_button = self.driver.find_element_by_id(self.CONTINUE_BUTTON_ID)

		print "%s x %s" % (self.canvas_width, self.canvas_height)

	def get_score(self):
		return self.driver.execute_script(self.GET_SCORE_JAVASCRIPT)

	def is_game_over(self):
		return self.driver.execute_script(self.IS_GAME_OVER_JAVASRIPT)

	def get_canvas_pixels(self):
		return self.driver.execute_script(self.GET_CANVAS_PIXELS_JAVASCRIPT)

	def start_new_game(self):
		self.driver.execute_script(self.START_NEW_GAME_JAVASCRIPT)

	def play_game(self):
		self.start_new_game()
		while True:
			loop_start = time.time()

			pixelJson = self.get_canvas_pixels()
			#pixels = json.loads(pixelJson)
			score = self.get_score()
			game_over = self.is_game_over()
			print "Score %s, Game over: %s" % (score, game_over)

			if game_over:
				ActionChains(self.driver).click(self.continue_button).perform()
				return

			x_offset = random.choice([0, self.canvas_width-1])
			y_offset = random.choice([0, self.canvas_height-1])
			ActionChains(self.driver).move_to_element_with_offset(self.canvas_element, x_offset,
											y_offset).perform()
			
			loop_duration = time.time() - loop_start
			print loop_duration

	@classmethod
	def _get_chrome_webdriver(cls):
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--proxy-server=%s' % cls.PROXY)
		return webdriver.Chrome(chrome_options=chrome_options)

	@classmethod
	def _get_firefox_webdriver(cls):
		proxy = webdriver.Proxy(raw={
			"httpProxy":cls.PROXY,
		    "ftpProxy":cls.PROXY,
		    "sslProxy":cls.PROXY,
		    "noProxy":None,
		    "proxyType":"MANUAL",
		    "class":"org.openqa.selenium.Proxy",
		    "autodetect":False
		})
		return webdriver.Firefox(proxy=proxy)

agar = AgarIODriver()
while True:
	agar.play_game()