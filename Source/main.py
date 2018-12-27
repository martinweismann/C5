
import cube
import math
import numpy
import matplotlib.pyplot as plt
import random

from sortedcontainers import SortedList


def CreateStones(dimension):
	stones = []
	if (dimension == 6):
		# working, but not solved
		# https://www.knobelbox.com/geduldsspiele/wuerfelpuzzle/9/der-t-wuerfel?c=7
		inStones = [ [[ 0,0,0], [ 1,0,0], [ 2,0,0], [ 1,1,0]],
						[[-1,0,0], [ 0,0,0], [ 1,0,0], [ 0,1,0]],
						[[-2,0,0], [-1,0,0], [ 0,0,0], [-1,1,0]],
						[[-1,-1,0],[0,-1,0], [1,-1,0], [0,0,0]] ]
	elif (dimension == 5):
		# working
		# https://www.connexxion24.com/downloads/anleitungen/Anleitung-DE-GB-FR-ES-125er-Wuerfel-25-Puzzlteteile-Denkspiel-Knobelspiel-Geduldspiel-2561-doc-1.pdf
		inStones = [ [[ 0,0,0], [ 1,0,0], [ 2,0,0], [ 3,0,0], [ 1,1,0]],
						[[-1,0,0], [ 0,0,0], [ 1,0,0], [ 2,0,0], [ 0,1,0]],
						[[-2,0,0], [-1,0,0], [ 0,0,0], [ 1,0,0], [-1,1,0]],
						[[-3,0,0], [-2,0,0], [-1,0,0], [ 0,0,0], [-2,1,0]],
						[[-1,-1,0],[0,-1,0], [1,-1,0], [2,-1,0], [0,0,0]] ]
	elif (dimension == 4):
		# working
		inStones = [ [[ 0,0,0], [ 1,0,0], [ 2,0,0], [ 1,1,0]],
						[[-1,0,0], [ 0,0,0], [ 1,0,0], [ 0,1,0]],
						[[-2,0,0], [-1,0,0], [ 0,0,0], [-1,1,0]],
						[[-3,0,0], [-2,0,0], [-1,0,0], [-2,1,0]],
						[[-1,-1,0],[0,-1,0], [1,-1,0], [0,0,0]] ]
	else:
		raise "Only n=4 or 5 supported!"
	
	n = 4
	for z in range(0, n):
		phi_z = 90*z*math.pi/180
		Rz = [ [math.cos(phi_z), -math.sin(phi_z), 0], [math.sin(phi_z), math.cos(phi_z), 0], [0, 0, 1] ]
		for y in range(0, n):
			phi_y = 90*y*math.pi/180
			Ry = [ [math.cos(phi_y), 0, math.sin(phi_y)], [0, 1, 0], [-math.sin(phi_y), 0, math.cos(phi_y)] ]
			for x in range(0, n):
				phi_x = 90*x*math.pi/180
				Rx = [ [1, 0, 0], [0, math.cos(phi_x), -math.sin(phi_x)], [0, math.sin(phi_x), math.cos(phi_x)] ]
				for inStone in inStones:
					newStone = []
					for inVoxel in inStone:
						ooNoRound = numpy.matmul(Rz, numpy.matmul(Ry, numpy.matmul(Rx, inVoxel)))
						newStone.append( [int(round(r)) for r in ooNoRound] )

					# only append unique stones
					oosIsAlreadyIn = False
					for oldStone in stones:
						isSame = True
						for k in range(0, len(oldStone)):
							for l in range(0, len(oldStone[k])):
								if not (oldStone[k][l] == newStone[k][l]):
									isSame = False
						if (isSame):
							oosIsAlreadyIn = True
							break
					if not oosIsAlreadyIn:
						stones.append(newStone)
	return stones

class Statistics:
	def __init__(self):
		self.nTried = []
		self.nSuccesses = []
		self.nToTry = []
		self.nNewlyGenerated = []
		self.FillingFactor = []

class CubeSolver:

	def generatePotentialNexts(self, cube):
		nextVoxel = cube.nextOpenVoxel()
		if (nextVoxel == -1):
			return []
		print(str(nextVoxel) + " = " + str(cube.nextOpenVoxel(False)) + " FF={:3d}% =\n".format(
			cube.fillingFactor(True) )
			 + cube.hash()
			)

		nexts = []
		# generatePotentialNexts.iStone = random.randint(0, len(stones))
		self._iStoneCounter += 1
		for iStone in range(0, len(self.stones)):
			o = self.stones[(iStone + self._iStoneCounter)%len(self.stones)]
			newCube = cube.insertStoneAt(nextVoxel, o)
			if newCube:
				nexts.append(newCube)
		return nexts

	def __init__(self, dimension):
		self.stones = CreateStones(dimension)
		print("Creating solver with dimension = {:d} and {:d} stones".format(dimension, len(self.stones)) )

		self.tryNext = SortedList(key = lambda x : x.fillingFactor())
		self.failures = SortedList(key = lambda x : x.fillingFactor())
		self.successes = []

		firstCube = cube.Cube(n=dimension)
		self.tryNext.add(firstCube)
		
		# statistics:
		self.statistics = Statistics()

		self.highestFillingFactor = [firstCube.fillingFactor(), firstCube]
		self._iStoneCounter = 0

	def UpdateHistory(self):
		self.statistics.nToTry.append(len(self.tryNext))
		self.statistics.nSuccesses.append(len(self.successes))
		self.statistics.nTried.append(len(self.failures) + len(self.successes))
		self.statistics.nNewlyGenerated.append(len(self.nextCubes))

	def ReportStatus(self):
		print("Highest Filling Factor = FF={:3d}%, First Open Voxel: ({:d}, {:s}), Stones=\n{:s}".format(
			self.highestFillingFactor[1].fillingFactor(True), self.highestFillingFactor[1].nextOpenVoxel(True),
			str(self.highestFillingFactor[1].nextOpenVoxel(False)),self.highestFillingFactor[1].hash() )
			)
		print("Tried: {:8d} ({:8d} vs {:8d})".format( len(self.successes) + len(self.failures), len(self.failures), len(self.successes)) )
		print("ToTry: {:8d} (current)".format(len(self.tryNext)))

	def PickFromPotentialNexts(self):
		nUniques = 0
		for aNew in self.nextCubes:
			bIsAlreadyIn = False
			for old in self.failures.irange(aNew, aNew):
				if old.samePattern(aNew):
					bIsAlreadyIn = True
					break
			if not bIsAlreadyIn:
				for old in self.tryNext.irange(aNew, aNew):
					if old.samePattern(aNew):
						bIsAlreadyIn = True
						break
			if not bIsAlreadyIn:
				nUniques = nUniques + 1
				if not aNew.CanBeSolved(self.stones):
					doMultiline = False
					if (doMultiline):
						aHash = aNew.hash(doMultiline)
						print("The new generated cube can certainly not be solved = {:s}".format(aHash))
					self.failures.add(aNew)
				else:
					self.tryNext.add(aNew)

		print("Generated {:3d} unique, solvable nextCubes (from {:d} potential nextCubes)".format(nUniques, len(self.nextCubes)))

	def solve(self):
		while (len(self.tryNext) > 0):
			print("\nNext iteration:")
			curCube = self.tryNext.pop()
			if self.highestFillingFactor[0] < curCube.fillingFactor():
				self.highestFillingFactor = [ curCube.fillingFactor(), curCube]
			if curCube.isSolved():
				self.successes.append(curCube)
				print("The {:5d}. solution to the cube is =\n{:s}".format(len(self.successes), curCube.hash(True)))
			else:
				self.failures.add(curCube)

			doPlot = False
			if doPlot:
				curCube.plot()
			
			self.nextCubes = self.generatePotentialNexts(curCube)
			self.PickFromPotentialNexts()

			self.UpdateHistory()
			self.nextCubes = []
			self.statistics.FillingFactor.append(curCube.fillingFactor(True))

			self.ReportStatus()
			if self.statistics.nTried[-1] > 1e6:
				print("Stopping \"solve()\" after {:d} iterations".format(self.statistics.nTried[-1]))
				break

	def epilog(self):
		xAxis = range(0, len(self.statistics.nTried))
		plt.plot(xAxis, self.statistics.nToTry, xAxis, self.statistics.nNewlyGenerated, xAxis, self.statistics.FillingFactor)
		plt.xlabel('Iteration')
		plt.ylabel('#')
		plt.legend(['nTry', 'nNewlyGenerated', 'FillingFactor (%)'])
		plt.show()

		solver.ReportStatus()
		self.highestFillingFactor[1].plot()


solver = CubeSolver(5)
try:
	print("Solving C5")
	solver.solve()
except KeyboardInterrupt:
	print("Interrupted")

print("DONE")
solver.epilog()
