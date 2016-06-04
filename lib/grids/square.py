# REFERENCES
#	http://www-cs-students.stanford.edu/~amitp/game-programming/grids/

def cell2coords(cell):
	cell = cell.lower()
	x = ord(cell[0]) - ord('a')
	y = int(cell[1])-1
	return (x,y)

def coords2cell(coords):
	return chr(ord('a') + coords[0]) + str(coords[1]+1)

class Face(object):

	dirs = {
		'N': (0,1),
		'NE': (1,1),
		'E': (1,0),
		'SE': (1,-1),
		'S': (0,-1),
		'SW': (-1,-1),
		'W': (-1,0),
		'NW': (-1,1)
	}

	opps = {
		'N': 'S',
		'NE': 'SW',
		'E': 'W',
		'SE': 'NW',
		'S': 'N',
		'SW': 'NE',
		'W': 'E',
		'NW': 'SE'
	}

	def __init__(self, x, y):
		if ( (isinstance(x, int)) and (isinstance(y, int))):
			self.x = x
			self.y = y
		else:
			raise TypeError("'x' and 'y' must be integers.")

	def from_cell(cell):
		cell = cell.lower()
		x = ord(cell[0]) - ord('a')
		y = int(cell[1])-1
		return Face(x,y)

	def __eq__(self, other):
		return (self.x, self.y) == (other.x, other.y)

	def __ne__(self, other):
		return not(self == other)

	def __gt__(self, other):
		return (self.x, self.y) > (other.x, other.y)

	def __lt__(self, other):
		return (self.x, self.y) < (other.x, other.y)

	def __ge__(self, other):
		return (self > other) or (self == other)

	def __le__(self, other):
		return (self < other) or (self == other)

	def __hash__(self):
		return hash((self.x,self.y))

	def __repr__(self):
		return "<Face({0}, {1})>".format(self.x, self.y)

	def neighbours(self, diag=False):
		if diag:
			return [
					Face(self.x, self.y+1), 
					Face(self.x+1, self.y), 
					Face(self.x, self.y-1), 
					Face(self.x-1, self.y),
					Face(self.x+1, self.y+1),
					Face(self.x+1, self.y-1),
					Face(self.x-1, self.y+1),
					Face(self.x-1, self.y-1)
			]
		else:
			return [
				Face(self.x, self.y+1), 
				Face(self.x+1, self.y), 
				Face(self.x, self.y-1), 
				Face(self.x-1, self.y)
			]

	def neighbour(self, dir, dist=1):
		if dir not in Face.dirs:
			raise ValueError("'dir' must be one of the compass directions.")
		d = Face.dirs[dir]
		return Face(self.x+(d[0]*dist), self.y+(d[1]*dist))

	def borders(self):
		return [
			Edge(self.x, self.y+1, 'S'),
			Edge(self.x+1, self.y, 'W'),
			Edge(self.x, self.y, 'S'),
			Edge(self.x, self.y, 'W')
		]

	def corners(self):
		return [
			Vertex(self.x+1, self.y+1),
			Vertex(self.x+1, self.y),
			Vertex(self.x, self.y),
			Vertex(self.x, self.y+1)
		]

	def orth_to(self, other):
		if (not isinstance(other, Face)):
			raise TypeError("You must provide another Face object.")
		return ( (self.x == other.x) or (self.y == other.y) )

	def diag_to(self, other):
		if (not isinstance(other, Face)):
			raise TypeError("You must provide another Face object.")
		return abs(self.x - other.x) == abs(self.y - other.y)

	def relative_to(self, other):
		if (self == other):
			return None

		dir = ""
		#NS first
		if (self.y < other.y):
			dir += 'S'
		elif (self.y > other.y):
			dir += 'N'

		#then EW
		if (self.x < other.x):
			dir += 'W'
		elif (self.x > other.x):
			dir += 'E'

		return dir

	def between(self, other):
		if (self == other):
			return
		if ( (not self.orth_to(other)) and (not self.diag_to(other)) ):
			raise ValueError("Both faces must be either orthogonally or diagonally aligned.")
		dir = other.relative_to(self)
		nxt = self.neighbour(dir)
		while (nxt != other):
			yield nxt
			nxt = nxt.neighbour(dir)

	def to_cell(self):
		return chr(ord('a') + self.x) + str(self.y+1)

	def to_tuple(self):
		return (self.x, self.y)


class Vertex(Face):

	def __repr__(self):
		return "<Vertex({0}, {1})>".format(self.x, self.y)

	def touches(self):
		return [
			Face(self.x, self.y),
			Face(self.x, self.y-1),
			Face(self.x-1, self.y-1),
			Face(self.x-1, self.y)
		]

	def protrudes(self):
		return [
			Edge(self.x, self.y, 'W'),
			Edge(self.x, self.y, 'S'),
			Edge(self.x, self.y-1, 'W'),
			Edge(self.x-1, self.y, 'S')
		]

	def adjacent(self):
		return [
			Vertex(self.x, self.y+1),
			Vertex(self.x+1, self.y),
			Vertex(self.x, self.y-1),
			Vertex(self.x-1, self.y)
		]

class Edge(object):

	def __init__(self, x, y, dir):
		if ( (isinstance(x, int)) and (isinstance(y, int))):
			self.x = x
			self.y = y
		else:
			raise TypeError("'x' and 'y' must be integers.")
		if ( (dir != 'S') and (dir != 'W') ):
			raise ValueError("'Dir' must be either 'S' or 'W'.")
		self.dir = dir

	def __eq__(self, other):
		return (self.x, self.y, self.dir) == (other.x, other.y, other.dir)

	def __ne__(self, other):
		return not(self == other)

	def __gt__(self, other):
		return (self.x, self.y, self.dir) > (other.x, other.y, other.dir)

	def __lt__(self, other):
		return (self.x, self.y, self.dir) < (other.x, other.y, other.dir)

	def __ge__(self, other):
		return (self > other) or (self == other)

	def __le__(self, other):
		return (self < other) or (self == other)

	def __hash__(self):
		return hash((self.x,self.y,self.dir))

	def __repr__(self):
		return "<Edge({0}, {1}, {2})>".format(self.x, self.y, self.dir)

	def joins(self):
		if self.dir == 'W':
			return [
				Face(self.x, self.y),
				Face(self.x-1, self.y)
			]
		else:
			return [
				Face(self.x, self.y),
				Face(self.x, self.y-1)
			]

	def continues(self):
		if self.dir == 'W':
			return [
				Edge(self.x, self.y+1, 'W'),
				Edge(self.x, self.y-1, 'W')
			]
		else:
			return [
				Edge(self.x+1, self.y, 'S'),
				Edge(self.x-1, self.y, 'S')
			]

	def endpoints(self):
		if self.dir == 'W':
			return [
				Vertex(self.x, self.y+1),
				Vertex(self.x, self.y)
			]
		else:
			return [
				Vertex(self.x+1, self.y),
				Vertex(self.x, self.y)
			]

class Square(object):
	
	def __init__(self):
		pass

class SquareFixed(Square):

	def __init__(self, height, width):
		super(SquareFixed, self).__init__()
		self.height = height
		self.width = width

	def faces(self):
		lst = []
		for x in range(self.width):
			for y in range(self.height):
				lst.append(Face(x,y))
		return lst

	def vertices(self):
		s = set()
		for f in self.faces():
			s |= set(f.corners())
		return s

	def edges(self):
		s = set()
		for f in self.faces():
			s |= set(f.borders())
		return s

	def _contains(self, arg):
		if isinstance(arg, Face):
			return arg in self.faces()
		elif isinstance(arg, Edge):
			return arg in self.edges()
		elif isinstance(arg, Vertex):
			return arg in self.vertices()
		else:
			raise TypeError("'arg' must be a Face, Edge, or Vertex.")

	def contains(self, arg):
		if isinstance(arg, list):
			ret = True
			for a in arg:
				if not self._contains(a):
					ret = False
					break
			return ret
		else:
			return self._contains(arg)

	def lines(self, length, diag=False):
		#width
		#lst_width = set()
		if (length-1 <= self.width):
			for x in range(self.width-length+1):
				for y in range(self.height):
					node = []
					for i in range(length):
						node.append((x+i, y))
					yield tuple(node)
					#lst_width.add(tuple(node))

		#height
		#lst_height = set()
		if (length-1 <= self.height):
			for y in range(self.height-length+1):
				for x in range(self.width):
					node = []
					for i in range(length):
						node.append((x, y+i))
					yield tuple(node)
					#lst_height.add(tuple(node))

		lst_diag = []
		dct_diag = {}
		if diag:
			if (length-1 <= min(self.height, self.width)):
				for x in range(self.width):
					for y in range(self.height):
						face = Face(x,y)
						for dir in ('NE', 'SE', 'SW', 'NW'):
							end = face.neighbour(dir, length-1)
							if self.contains(end):
								node = [face.to_tuple(), end.to_tuple()]
								for f in face.between(end):
									node.append(f.to_tuple())
								dct_diag[tuple(sorted(node))] = 1
				lst_diag = sorted(dct_diag.keys())

		# for node in lst_width:
		# 	yield node
		# for node in lst_height:
		# 	yield node
		for node in lst_diag:
			yield node

if __name__ == "__main__":
	s = SquareFixed(4,4)
	for node in s.lines(3, True):
		print(node)
