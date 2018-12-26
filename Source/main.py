
import cube
import math
import numpy
import matplotlib.pyplot as plt

from sortedcontainers import SortedList

def generateOrientations():
	orientations = []
	inorient = [ [[ 0,0,0], [ 1,0,0], [ 2,0,0], [ 3,0,0], [ 1,1,0]],
					[[-1,0,0], [ 0,0,0], [ 1,0,0], [ 2,0,0], [ 0,1,0]],
					[[-2,0,0], [-1,0,0], [ 0,0,0], [ 1,0,0], [-1,1,0]],
					[[-3,0,0], [-2,0,0], [-1,0,0], [ 0,0,0], [-2,1,0]],
					[[-1,-1,0],[0,-1,0], [1,-1,0], [2,-1,0], [0,0,0]] ]

	# # n =4 working
	# inorient = [ [[ 0,0,0], [ 1,0,0], [ 2,0,0], [ 1,1,0]],
	# 				[[-1,0,0], [ 0,0,0], [ 1,0,0], [ 0,1,0]],
	# 				[[-2,0,0], [-1,0,0], [ 0,0,0], [-1,1,0]],
	# 				[[-3,0,0], [-2,0,0], [-1,0,0], [-2,1,0]],
	# 				[[-1,-1,0],[0,-1,0], [1,-1,0], [0,0,0]] ]

	# inorient = [ [[ 0,0,0], [ 1,0,0], [ 2,0,0], [ 3,0,0], [ 4,0,0]],
	# 				 [[-1,0,0], [ 0,0,0], [ 1,0,0], [ 2,0,0], [ 3,0,0]],
	# 				 [[-2,0,0], [-1,0,0], [ 0,0,0], [ 1,0,0], [ 2,0,0]],
	# 				 [[-3,0,0], [-2,0,0], [-1,0,0], [ 0,0,0], [ 1,0,0]],
	# 				 [[-4,0,0], [-3,0,0], [-2,0,0], [-1,0,0], [ 0,0,0]] ]
	
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
				for io in inorient:
					newOrient = []
					for indir in io:
						ooNoRound = numpy.matmul(Rz, numpy.matmul(Ry, numpy.matmul(Rx, indir)))
						newOrient.append( [int(round(r)) for r in ooNoRound] )

					# only append unique orientations
					oosIsAlreadyIn = False
					for oldOrient in orientations:
						isSame = True
						for k in range(0, len(oldOrient)):
							for l in range(0, len(oldOrient[k])):
								if not (oldOrient[k][l] == newOrient[k][l]):
									isSame = False
						if (isSame):
							oosIsAlreadyIn = True
							break
					if not oosIsAlreadyIn:
						orientations.append(newOrient)
	return orientations

orientations = generateOrientations()

print("len(orientations)="+str(len(orientations)))

def generatePotentialNexts(cube):
	nextIndex = cube.nextOpenStone()
	if (nextIndex == -1):
		return []
	print(str(nextIndex) + " = " + str(cube.nextOpenStone(False)) )

	nexts = []
	for o in orientations:
		newCube = cube.insertOrientationAt(nextIndex, o)
		if newCube:
			nexts.append(newCube)
	return nexts


print("Solving C5")

tryNext = SortedList(key = lambda x : x.nextOpenStone())
failures = SortedList(key = lambda x : x.nextOpenStone())
successes = []

firstCube = cube.Cube(n=5)
tryNext.add(firstCube)

nTried = 0

nTried = []
nSuccesses = []
nToTry = []
nNewlyGenerated = []
firstOpenStone = [firstCube.nextOpenStone(), firstCube]

try:
	while (len(tryNext) > 0):
		curCube = tryNext.pop()
		if curCube.isSolved():
			successes.append(curCube)
			print(curCube._grid)
			curCube.plot()
		else:
			failures.add(curCube)

		doPlot = False
		if doPlot:
			curCube.plot()
		nexts = generatePotentialNexts(curCube)

		nUniques = 0
		for aNew in nexts:
			if aNew.isSolved():
				successes.append(aNew)
				print(aNew._grid)
				aNew.plot()
				continue

			bIsAlreadyIn = False
			for old in failures.irange(aNew, aNew):
				if old.samePattern(aNew):
					bIsAlreadyIn = True
					print("Already in!")
					break
			if not bIsAlreadyIn:
				for old in tryNext.irange(aNew, aNew):
					if old.samePattern(aNew):
						bIsAlreadyIn = True
						print("Already in!")
						break
			if not bIsAlreadyIn:
				if firstOpenStone[0] < aNew.nextOpenStone():
					firstOpenStone = [ aNew.nextOpenStone(), aNew]
				tryNext.add(aNew)
				nUniques = nUniques + 1
		print("Generated {:3d} unique nexts (from {:d} nexts)".format(nUniques, len(nexts)))
		print("Hieghest First Open Stone = {:d}, {:s}".format(firstOpenStone[0], str(firstOpenStone[1].nextOpenStone(False)) ))
		nToTry.append(len(tryNext))
		nSuccesses.append(len(successes))
		nTried.append(len(failures) + len(successes))
		nNewlyGenerated.append(len(nexts))
		print("Tried: {:8d} ({:8d} vs {:8d})".format( len(successes) + len(failures), len(failures), len(successes)) )
		print("ToTry: {:8d}".format(len(tryNext)))
		if len(successes) + len(failures) > 1e6:
			break
except KeyboardInterrupt:
	print("Interrupted")

print("DONE")

plt.plot(range(0, len(nTried)), nToTry, range(0, len(nTried)), nNewlyGenerated)
plt.xlabel('Iteration')
plt.ylabel('#ToTry')
plt.show()

firstOpenStone[1].plot()
