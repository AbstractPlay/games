import cherrypy
import json
import jsonschema
import hashlib

import re
re_move = re.compile(r'([a-d][1-4])-([a-d][1-4])')

from ..grids.square import Face, SquareFixed
from ._common import SimpleGridGame

class IthakaGame(SimpleGridGame):

	def __init__(self, players):
		self.board = [
			['B', 'B', 'G', 'G'],
			['B', None, None, 'G'],
			['Y', None, None, 'R'],
			['Y', 'Y', 'R', 'R'],
		]
		self.board.reverse()
		currstate = self.board2str()
		self.states = {
			self.board2str(): 1
		}
		self.lastmoved = None
		self.currplayer = 0
		self.numplayers = 2
		self.players = players

	def from_dict(d):
		self = IthakaGame(d['players'])
		self.board = d['board']
		self.states = d['states']
		self.lastmoved = d['lastmoved']
		self.currplayer = d['currplayer']
		self.numplayers = 2
		return self

	def board2str(self):
		rep = ""
		for row in self.board:
			for cell in row:
				if cell is None:
					rep += '-'
				else:
					rep += cell
		return rep

	def save_state(self):
		state = self.board2str()
		if state in self.states:
			self.states[state] += 1
		else:
			self.states[state] = 1
		return self.states[state]

	def to_state(self):
		return {
			"players": self.players,
			"board": self.board,
			"states": self.states,
			"lastmoved": self.lastmoved,
			"currplayer": self.currplayer
		}

	def render(self):
		return {
			"spriteset": "generic",
			"legend": {
				"R": "piece-red",
				"B": "piece-blue",
				"G": "piece-green",
				"Y": "piece-yellow",
			},
			"position": self.board2str(),
			"boardwidth": 4,
			"board": "checkered"
		}

class Ithaka(object):
	exposed = True

	def __init__(self):
		self.version = 1
		self.description = '''# Ithaka

A player can move any piece on the board. The winner is the player at the end of whose turn a row of three pieces of the same colour exists (either orthogonal or diagonal).'''
		self.maxplayers = 2
		self.changelog = ""

	@property
	def state(self):
		m = hashlib.sha256()
		m.update(str(self.version).encode('utf-8'))
		m.update(str(self.maxplayers).encode('utf-8'))
		m.update(self.description.encode('utf-8'))
		m.update(self.changelog.encode('utf-8'))
		return m.hexdigest()
	
	@cherrypy.tools.accept(media="application/json")
	@cherrypy.tools.json_out()
	def POST(self, **kwargs):
		if 'mode' not in kwargs:
			raise cherrypy.HTTPError(400, "Missing 'mode' parameter.")

		mode = kwargs['mode']
		if mode == 'ping':
			return {"state": self.state}
		elif mode == 'metadata':
			return {
				"state": self.state,
				"version": self.version,
				"maxplayers": self.maxplayers,
				"description": self.description,
				"changelog": self.changelog
			}
		elif mode == 'init':
			if 'players' not in kwargs:
				raise cherrypy.HTTPError(400, "No 'players' parameter provided.")
			players = kwargs['players']
			if ( (not isinstance(players, list)) or (len(players) != 2) ):
				raise cherrypy.HTTPError(400, "The 'players' parameter must be a list of two userids.")
			players[0] = int(players[0])
			players[1] = int(players[1])
			game = IthakaGame(players)
			# game = self.newgame(players)
			return {
				"state": json.dumps(game.to_state()),
				"whoseturn": [game.currplayer],
				"renderrep": game.render()
			}
		elif mode == 'move':
			if 'userid' not in kwargs:
				raise cherrypy.HTTPError(400, "No 'userid' parameter provided.")
			if 'move' not in kwargs:
				raise cherrypy.HTTPError(400, "No 'move' parameter provided.")
			if 'state' not in kwargs:
				raise cherrypy.HTTPError(400, "No 'state' parameter provided.")

			game = Game.from_dict(json.loads(kwargs['state']))
			if game.curr_player_id() != int(kwargs['userid']):
				raise cherrypy.HTTPError(400, "It's not the given player's turn! This should never happen!")
			move = kwargs['move'].lower()
			m = re_move.match(move)
			if m is None:
				raise cherrypy.HTTPError(400, "The move you submitted is malformed.")
			cell_from = m.group(1)
			face_from = Face.from_cell(cell_from)
			cell_to = m.group(2)
			face_to = Face.from_cell(cell_to)
			game.lastmoved = cell_to

			#make sure there's a piece at FROM
			if (game.get_piece_at(face_from.to_tuple()) is None):
				raise cherrypy.HTTPError(400, "You're trying to move a nonexistent piece.")

			#make sure there's no piece at TO
			if (game.get_piece_at(face_to.to_tuple()) is not None):
				raise cherrypy.HTTPError(400, "The space you're trying to move to is already occupied.")

			#make sure that piece is allowed to move
			if ( (game.lastmoved is not None) and (game.lastmoved == cell_from) ):
				raise cherrypy.HTTPError(400, "You can't move the piece that was just moved.")

			#make sure there's a clear line from FROM to TO
			if ( (not face_from.orth_to(face_to)) and (not face_from.diag_to(face_to)) ):
				raise cherrypy.HTTPError(400, "The 'from' and 'to' cells are neither orthogonally nor diagonally aligned.")
			for f in face_from.between(face_to):
				if game['board'][f.y][f.x] is not None:
					raise cherrypy.HTTPError(400, "You can't move through occupied spaces ({0}).".format(f.to_cell()))

			#create a chat
			chat = "Player {0} moved from {1} to {2}.".format(game.currplayer+1, cell_from, cell_to)

			#check for end of game
			eog = False
			eog_reason = None
			eog_winner = None
			for line in SquareFixed(4,4).lines(3, True):
				one = line[0]
				two = line[1]
				three = line[2]
				if ( (game.get_piece_at(one) is not None) and (game.get_piece_at(one) == game.get_piece_at(two) == game.get_piece_at(three)) ):
					eog = True
					eog_reason = "THREE IN A ROW"
					eog_winner = game.currplayer
					chat += "\n\nPlayer {0} wins due to THREE IN A ROW!".format(eog_winner+1)

			#update the gamestate
			#move the piece
			game.move_piece(face_from.to_tuple(), face_to.to_tuple())

			#update list of states
			reps = game.save_state()
			if reps == 4:
				eog = True
				eog_reason = "POSITION REPETITION"
				eog_winner = (game['currplayer']+1)%2
				chat += "\n\nPlayer {0} wins due to POSITION REPETITION!".format(eog_winner+1)
			elif reps > 1:
				chat += "\n\nThis position has occurred before. The player that repeats a position for the third time loses the game. Repetitions left: {0}.".format(4-game['states'][state])

			#update whoseturn
			game.next_player()
			if (not eog):
				whoseturn = [game.curr_player_id()]
			else:
				whoseturn = []


			#return
			return{
				"state": json.dumps(game.to_state()),
				"whoseturn": whoseturn,
				"chat": chat,
				"renderrep": game.render()
			}
		else:
			raise cherrypy.HTTPError(400, "Unrecognized 'mode' parameter.")

if __name__ == '__main__':
	pass

