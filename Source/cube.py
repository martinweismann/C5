
import matplotlib.pyplot as plt
from matplotlib import colors as matcolors
from mpl_toolkits.mplot3d import Axes3D
import enum
import numpy as np
import math

class SolvableStatus(enum.Enum):
	UNUSED = 0
	USED = 1
	SOLVABLE = 2


class Cube:
	def __init__(self, n = 5, otherCube = None):
		self.n = n
		self._grid = np.zeros((self.n,self.n,self.n), dtype=int)
		self.highestItem = 0
		self.firstOpenVoxel = 0

		if (otherCube):
			self._grid = otherCube._grid.copy()
			self.firstOpenVoxel = otherCube.firstOpenVoxel
			self.highestItem = otherCube.highestItem

	def samePattern(self, otherCube):
		if not (self.highestItem == otherCube.highestItem):
			return False
		if not (self.firstOpenVoxel == otherCube.firstOpenVoxel):
			return False
		return ((self._grid>0) == (otherCube._grid>0)).all()
	def isSolved(self):
		return self.nextOpenVoxel() == -1

	def nextOpenVoxel(self, linear = True):
		if linear:
			return self.firstOpenVoxel
		else:
			index = [ self.firstOpenVoxel // (self.n*self.n)]
			index.append(  (self.firstOpenVoxel - self.n*self.n*index[0])//self.n )
			index.append(  (self.firstOpenVoxel - self.n*self.n*index[0] - self.n*index[1]) )
			return index

	def calculateStoneAbsolute(self, index, stoneRelative):
		stoneAbsolute = []
		for stoneVoxelRelative in stoneRelative:
			newIndex = [ stoneVoxelRelative[k] + index[k] for k in range(0,3) ]

			lower = [i<self.n for i in newIndex]
			higher = [i>=0 for i in newIndex]
			if all(lower) and all(higher) and self._grid[ newIndex[0] ][ newIndex[1] ][ newIndex[2] ] == 0:
				stoneAbsolute.append(newIndex)
			else:
				return None

		if len(stoneAbsolute) != len(stoneRelative):
			raise("Error: stone does not have the correct size!")
		return stoneAbsolute

	def fittingStones(self, index, stones):
		fittingStonesAbsolute = []
		for stone in stones:
			stoneAbsolute = self.calculateStoneAbsolute(index, stone)
			if (stoneAbsolute == None):
				continue
			fittingStonesAbsolute.append(stoneAbsolute)
		return fittingStonesAbsolute

	"""Returns, whether an overoptimistic heuristic declares this cube as solvable"""
	def CanBeSolved(self, stones):
		status = np.full( (self.n, self.n, self.n), fill_value=SolvableStatus.UNUSED, dtype=SolvableStatus)
		status[self._grid>0] = SolvableStatus.SOLVABLE
		
		for z in range(0,self.n):
			for y in range(0,self.n):
				for x in range(0,self.n):
					if (status[z][y][x] == SolvableStatus.UNUSED):
						fitting = self.fittingStones([z,y,x], stones)
						if (len(fitting) == 0):
							return False
						for fit in fitting:
							for fitCoordinate in fit:
								if status[fitCoordinate[0]] [fitCoordinate[1]] [fitCoordinate[2]] == SolvableStatus.UNUSED:
									status[fitCoordinate[0]] [fitCoordinate[1]] [fitCoordinate[2]] = SolvableStatus.USED
		return True

	def hash(self, multiLine = False):
		
		if (multiLine):
			ret = ''
			for z in range(0,self.n):
				for y in range(0,self.n):
					for x in range(0,self.n):
						ret = ret + chr(64+self._grid[z][y][x])
					ret = ret + '\n'
				ret = ret + '\n'
			return ret
		else:
			ret = ''
			for z in range(0,self.n):
				for y in range(0,self.n):
					for x in range(0,self.n):
						ret = ret + chr(64+self._grid[z][y][x])
			return ret

	def fillingFactor(self, normalized = False):
		fac = (self._grid>0).sum()
		if normalized:
			return int(round(fac/self._grid.size * 100 ))
		else:
			return int(round(fac))


	def insertStoneAt(self, indexLinear, stoneRelative):
		index = [ indexLinear // (self.n*self.n)]
		index.append(  (indexLinear - self.n*self.n*index[0])//self.n )
		index.append(  (indexLinear - self.n*self.n*index[0] - self.n*index[1]) )

		if not (indexLinear == index[0]*self.n*self.n + index[1]*self.n + index[2]):
			raise "indexLinear != index[0]*self.n*self.n + index[1]*self.n + index[2]"

		newIndices = self.calculateStoneAbsolute(index, stoneRelative)
		if (newIndices == None):
			return None
		
		cube = Cube(self.n, self)
		cube.highestItem = self.highestItem + 1
		for point in newIndices:
			cube._grid[ point[0] ][ point[1] ][ point[2] ] = cube.highestItem
		
		cube.firstOpenVoxel = -1
		for z in range(0,cube.n):
			for y in range(0,cube.n):
				for x in range(0,cube.n):
					if (cube._grid[z][y][x] == 0):
						cube.firstOpenVoxel = z * cube.n*cube.n + y*cube.n + x
						return cube
		return cube



	def plotSteps(self):
		colors = np.empty_like(self._grid, dtype=object)
		
		iMax = self.highestItem
		dim = int(math.ceil(math.sqrt(iMax)))
		dim = max([dim, 2])
		_, axes = plt.subplots(dim, dim, subplot_kw=dict(projection='3d'), sharex=True, sharey=True)
		
		colorMap = list(matcolors.CSS4_COLORS.values())
		for stoneIndex in range(1, self.highestItem+1):
			colors[self._grid == stoneIndex] = colorMap[stoneIndex % len(colorMap)]
			voxels = np.full_like(colors, fill_value=True, dtype=bool)
			voxels[colors==None] = False
			ax = axes[(stoneIndex-1)//dim, (stoneIndex-1)%dim]
			ax.voxels(voxels, facecolors=colors, edgecolor='k')
			ax.set_xticks([])
			ax.set_yticks([])
			ax.set_zticks([])
			ax.view_init(30, 30)
		plt.tight_layout()
		plt.show()

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
