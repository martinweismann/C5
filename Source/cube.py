
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class Cube:
	def __init__(self, n = 5, otherCube = None):
		self.n = n
		self._grid =  [[[0 for x in range(self.n)] for y in range(self.n)] for z in range(self.n)]
		self.highestItem = 0
		self.firstOpenStone = 0

		if (otherCube):
			for z in range(0,self.n):
				for y in range(0,self.n):
					for x in range(0,self.n):
						self._grid[z][y][x] = otherCube._grid[z][y][x]
			self.firstOpenStone = otherCube.firstOpenStone
			self.highestItem = otherCube.highestItem

	def samePattern(self, otherCube):
		if not (self.highestItem == otherCube.highestItem):
			return False
		if not (self.firstOpenStone == otherCube.firstOpenStone):
			return False
		for z in range(0,self.n):
				for y in range(0,self.n):
					for x in range(0,self.n):
						if not ( (self._grid[z][y][x] > 0) == (otherCube._grid[z][y][x] > 0) ):
							return False
		return True
	def isSolved(self):
		return self.nextOpenStone() == -1

	def nextOpenStone(self, linear = True):
		if linear:
			return self.firstOpenStone
		else:
			index = [ self.firstOpenStone // (self.n*self.n)]
			index.append(  (self.firstOpenStone - self.n*self.n*index[0])//self.n )
			index.append(  (self.firstOpenStone - self.n*self.n*index[0] - self.n*index[1]) )
			return index

		#for z in range(0,self.n):
		#	for y in range(0,self.n):
		#		for x in range(0,self.n):
		#			if (self._grid[z][y][x] == 0):
		#				return [z,y,x]
		#return None


	def insertOrientationAt(self, indexLinear, orientation):
		index = [ indexLinear // (self.n*self.n)]
		index.append(  (indexLinear - self.n*self.n*index[0])//self.n )
		index.append(  (indexLinear - self.n*self.n*index[0] - self.n*index[1]) )

		if not (indexLinear == index[0]*self.n*self.n + index[1]*self.n + index[2]):
			raise "indexLinear != index[0]*self.n*self.n + index[1]*self.n + index[2]"

		newIndices = []
		for orientPoint in orientation:
			newIndex = [ orientPoint[k] + index[k] for k in range(0,3) ]

			lower = [i<self.n for i in newIndex]
			higher = [i>=0 for i in newIndex]
			if all(lower) and all(higher) and self._grid[ newIndex[0] ][ newIndex[1] ][ newIndex[2] ] == 0:
				newIndices.append(newIndex)
			else:
				return None

		# print("len(newIndices) = {:d}".format(len(newIndices)))
		if len(newIndices) != self.n:
			raise("Error")
		cube = Cube(self.n, self)
		cube.highestItem = self.highestItem + 1
		for point in newIndices:
			# print(point)
			cube._grid[ point[0] ][ point[1] ][ point[2] ] = cube.highestItem
		
		cube.firstOpenStone = -1
		for z in range(0,cube.n):
			for y in range(0,cube.n):
				for x in range(0,cube.n):
					if (cube._grid[z][y][x] == 0):
						cube.firstOpenStone = z * cube.n*cube.n + y*cube.n + x
						return cube
		return cube

	def plot(self):
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')

		markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_', 'P', 'X', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
		for nItemIndex in range(1, self.highestItem+1):
			xs = []
			ys = []
			zs = []
			for z in range(0,self.n):
				for y in range(0,self.n):
					for x in range(0,self.n):
						if (self._grid[z][y][x] == nItemIndex):
							xs.append(x)
							ys.append(y)
							zs.append(z)
			# print("len(zs)={:d}".format(len(zs)))
			ax.scatter(xs, ys, zs, marker=markers[ (nItemIndex-1) % len(markers)])

		ax.set_xlabel('X Label')
		ax.set_ylabel('Y Label')
		ax.set_zlabel('Z Label')
		ax.set_xlim([0,self.n-1])
		ax.set_ylim([0,self.n-1])
		ax.set_zlim([0,self.n-1])

		plt.show()
