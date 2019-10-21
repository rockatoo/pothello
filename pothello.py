from othello import *
from slearn import *

''' input feature
<stone color> (3) none, black, white
<edge> (1) yes, no
<side> (1) yes, no
<legal> (1) yes, no
<capturesize> (8) east, west, south, north, northern-east, northern-west, southern-east, southern-west
'''
class pothello(othello, brain):
	def __init__(self):
		othello.__init__(self)
		brain.__init__(self)
		self.log = []

	def record(self, x, y, omit=False, color = None):
		if color == None:
			color = self.turn
		elif color!=SBLACK or color!=SWHITE:
			raise RuntimeError('unknown turn state')

		self.log.append({'x':x, 'y':y, 'turn':color, 'omit':omit})

	def count_occupied(self, x, y, color = None):
		result = {'e':0, 'w':0, 'n':0, 's':0,'ne':0, 'nw':0, 'se':0, 'sw':0}
		if self.get(x, y) != SNONE:
			return result

		target = color
		if target is None:
			target = self.turn

		other = SNONE
		if target is SBLACK:
			other = SWHITE
		elif target is SWHITE:
			other = SBLACK

		vlist = [
		(-1, -ROW_COUNT, -1, '-'),  # West
		(1, ROW_COUNT, 1, '-'),  # East
		(1, COLUMN_COUNT, 1, '|'),  # South
		(-1, -COLUMN_COUNT, -1, '|'),  # North
		(1, max(ROW_COUNT, COLUMN_COUNT), 1, '/'),  # Northern-East
		(-1, -max(ROW_COUNT, COLUMN_COUNT), -1, '/'),  # Southern-West
		(-1, -max(ROW_COUNT, COLUMN_COUNT), -1, '\\'),  # Northern-West
		(1, max(ROW_COUNT, COLUMN_COUNT), 1, '\\')  # Southern-East
		]
		for i in range(8):
			flag = False
			stone = SNONE
			position = None
			olist = []
			for j in range(vlist[i][0], vlist[i][1], vlist[i][2]):
				if vlist[i][3] == '-':  # Horizontal
					if x+j < 0 or x+j >= ROW_COUNT:
						olist.clear()
						break
					position = (x+j, y)
					stone = self.get(x+j, y)
				elif vlist[i][3] == '|':  # Vertical
					if y+j < 0 or y+j >= COLUMN_COUNT:
						olist.clear()
						break
					position = (x, y+j)
					stone = self.get(x, y+j)
				elif vlist[i][3] == '/':  # Slash
					if x+j < 0 or x+j >= ROW_COUNT or y-j < 0 or y-j >= COLUMN_COUNT:
						olist.clear()
						break
					position = (x+j, y-j)
					stone = self.get(x+j, y-j)
				elif vlist[i][3] == '\\':  # Backslash
					if x+j < 0 or x+j >= ROW_COUNT or y+j < 0 or y+j >= COLUMN_COUNT:
						olist.clear()
						break
					position = (x+j, y+j)
					stone = self.get(x+j, y+j)

				if stone == target:
					if flag:
						for arg in olist:
							if i == 0:  # West
								result['w'] += 1
							elif i == 1:  # East
								result['e'] += 1
							elif i == 2:  # South
								result['s'] += 1
							elif i == 3:  # North
								result['n'] += 1
							elif i == 4:  # Northern-East
								result['ne'] += 1
							elif i == 5:  # Southern-West
								result['sw'] += 1
							elif i == 6:  # Northern-West
								result['nw'] += 1
							elif i == 7:  # Southern-East
								result['se'] += 1
					else:
						olist.clear()
						break
				elif stone == other:
					flag = True
					olist.append(position)
				elif stone == SNONE:
					olist.clear()
					break
		return result

	def feature_spot(self, x, y):
		flist = np.zeros(FACTORS)

		# stone color
		if self.get(x, y) == SNONE:
			flist[0] = 1
		elif self.get(x, y) == SBLACK:
			flist[1] = 1
		elif self.get(x, y) == SWHITE:
			flist[2] = 1
		else:
			raise RuntimeError('unknown stone state')

		# edge
		if (x==0 or x==ROW_COUNT-1) and (y==0 or y==COLUMN_COUNT-1):
			flist[3] = 1
		# side
		elif x==0 or y==0 or x==ROW_COUNT-1 or y==COLUMN_COUNT-1:
			flist[4] = 1

		# legal
		if self.verify(x, y):
			flist[5] = 1

		# capture size
		olist = self.count_occupied(x, y)
		flist[6] = olist['e']
		flist[7] = olist['w']
		flist[8] = olist['s']
		flist[9] = olist['n']
		flist[10] = olist['ne']
		flist[11] = olist['nw']
		flist[12] = olist['se']
		flist[13] = olist['sw']

		return flist

	def feature_spots(self):
		flist = []
		for i in range(COLUMN_COUNT):
			for j in range(ROW_COUNT):
				flist.append(self.feature_spot(j, i))
		return flist