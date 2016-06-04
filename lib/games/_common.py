class SimpleGridGame(object):

	""" 
	Generic grid-based game superclass. No constructor. Assumes you have the following properties:
	  * board: a 2D array
	  * players: an array of userids
	  * currplayer: int representing which player's turn it is
	  * numplayers: int representing the number of players

	This is the "simple" variant, meaning that 
	  * the the pieces on the board move as one (no seeding) and
	  * players are not eliminated.
	"""

	def get_piece_at(self, xy):
		return self.board[xy[1]][xy[0]]

	def place_piece_at(self, piece, xy):
		self.board[xy[1]][xy[0]] = piece
		return self

	def move_piece(self, fromxy, toxy):
		piece = self.get_piece_at(fromxy)
		self.place_piece_at(None, fromxy)
		self.place_piece_at(piece, toxy)
		return self

	def next_player(self):
		self.currplayer = (self.currplayer+1) % self.numplayers
		return self

	def curr_player_id(self):
		return self.players[self.currplayer]

	def player_from_id(self, userid):
		if userid not in self.players:
			return None
		for i in range(len(self.players)):
			if userid == self.players[i]:
				return i

