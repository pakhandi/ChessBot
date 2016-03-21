import numpy as np
import cv2
import sys
from matplotlib import pyplot as plt
from math import *
import shutil
import Geometry
from copy import deepcopy

class ChessBoard:
	# Colors
	RED   = (255,0,0)
	GREEN = (0,255,0)
	BLUE  = (0,0,255)

	# Number of cells to be detected
	FACTOR = 8

	# A very high value
	INT_MAX = 1000000009

	# Number of vertices to be detected for final detection of all vertices
	FINAL_VERTICES_COUNT = 150

	# Amount of relaxation allowed in y-axis detection of corners
	OFFSET = 15

	OFFSET2 = 5

	# Threshold for white and black piece detection
	WHITE_THRESHOLD = 142
	BLACK_THRESHOLD = 80

	# Threshold of probability for pieces
	PROBABILITY_THRESHOLD = 0.01

	# The location of the source file for image
	SOURCE_FILE = None

	# Number of vertices to be detected for initial detection of corners
	INITIAL_VERTICES_COUNT = None

	# The image to be processed and it's grayscale
	img = None
	gray = None

	# List of all vertices that lie on border
	OUTER_VERTICES = []

	# List for all the vertices detected on board at the end
	ALL_VERTICES = []

	# The four corners on the board
	CORNERS = []

	# The topology after probability calculation
	TOPOLOGY = []

	WHITES = [(1,1),(1,4),(2,2),(5,5),(0,7)]
	BLACKS = [(2,4),(6,1),(6,2),(7,7)]

	def __init__(self, SourceFile, InitialVerticesCount, FinalVerticesCount = 150, Offset = 15):
		
		self.SOURCE_FILE = SourceFile
		self.INITIAL_VERTICES_COUNT = InitialVerticesCount

		self.img = cv2.imread(self.SOURCE_FILE)
		

		self.FINAL_VERTICES_COUNT = FinalVerticesCount
		self.OFFSET = Offset

		height = len(self.img)
		width = len(self.img[0])
		print (height,width)

		#self.img = self.img[10:height-10 , 120:590 ]

		#self.gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
		#self.gray = self.sharpen(self.gray)

		self.stock = self.img

		edges = cv2.Canny(self.img,0,100)
		self.gray = edges # cv2.cvtColor(edges,cv2.COLOR_BGR2GRAY)
		plt.imshow(self.gray),plt.show()

		# cropped = self.img[self.ALL_VERTICES[x][y][1]+5:self.ALL_VERTICES[x+1][y+1][1]-5 ,self.ALL_VERTICES[x][y][0]+5:self.ALL_VERTICES[x+1][y+1][0]-5]
		# cropped = self.sharpen(cropped)

		# forWhite = 120

		# for p in self.img:
		# 	for point in p:
		# 		if point[0]>forWhite and point[1]>forWhite and point[2]>forWhite:
		# 			point[0] = point[1] = point[2] = 255

		# plt.imshow(self.img),plt.show()

		self.process()

		self.fixThresholds()

	def sharpen(self,testImg):
		#Create the identity filter, but with the 1 shifted to the right!
		kernel = np.zeros( (9,9), np.float32)
		kernel[4,4] = 2.0   #Identity, times two! 

		#Create a box filter:
		boxFilter = np.ones( (9,9), np.float32) / 81.0

		#Subtract the two:
		kernel = kernel - boxFilter

		custom = cv2.filter2D(testImg, -1, kernel)

		return testImg

	def process(self):
		self.detectFourCorners()
		self.plotFourCorners()
		plt.imshow(self.img),plt.show()
		self.plotOuterEdges()
		self.displayFourEdges()
		self.detectVerticesOnOuterEdges()
		self.plotAllEdges()
		self.detectAllVertices()
		# self.displayAllEdges()

	def update(self, SourceFile):
		self.SOURCE_FILE = SourceFile
		self.img = cv2.imread(self.SOURCE_FILE)
		self.gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
		self.process()
		self.createTopology()

	def detectFourCorners(self):

		INITIAL_VERTICES = cv2.goodFeaturesToTrack(self.gray,int(self.INITIAL_VERTICES_COUNT),0.03,10)
		INITIAL_VERTICES = np.int0(INITIAL_VERTICES)

		vertices = []

		tempImg = deepcopy(self.stock)

		print "="*20

		allDetectedPoints = []

		for i in INITIAL_VERTICES:
			x,y = i.ravel()
			allDetectedPoints.append((x,y))
			vertices.append((x,y))
			cv2.circle(tempImg,(x,y),3,self.GREEN,-1)
		plt.imshow(tempImg),plt.show()

		allDetectedPoints.sort()

		for point in allDetectedPoints:
			print point

		print "="*20

		# Variables to store four corners of the board
		bottom_left_x = self.INT_MAX
		bottom_left_y = 0

		top_left_x = self.INT_MAX
		top_left_y = self.INT_MAX

		bottom_right_x = 0
		bottom_right_y = 0

		top_right_x = 0
		top_right_y = self.INT_MAX

		minny = self.INT_MAX
		maxxy = 0

		# Detecting the four corners of the board
		# ---------------------------------------------------------------------------

		for point in vertices:
			minny = min(point[1],minny)
			maxxy = max(point[1],maxxy)

		print (minny,maxxy)

		print "*"*20

		for point in vertices:
			if(point[1] >= minny - self.OFFSET and point[1] <= minny + self.OFFSET):
				# print point
				if point[0] > top_right_x:
					# to avoid any other vertex on edge to be detected as the corner
					if point[1] - top_right_y < point[0] - top_right_x:
						top_right_x,top_right_y = point[0],point[1]
				if point[0] < top_left_x:
					top_left_x,top_left_y = point[0],point[1]
			if(point[1] >= maxxy - self.OFFSET and point[1] <= maxxy + self.OFFSET):
				print point
				if point[0] > bottom_right_x:
					bottom_right_x,bottom_right_y = point[0],point[1]
				if point[0] < bottom_left_x:
					print point
					bottom_left_x,bottom_left_y = point[0],point[1]
					print bottom_left_x," ",bottom_left_y

		print "*"*20

		self.CORNERS.append((bottom_left_x,bottom_left_y))
		self.CORNERS.append((top_left_x,top_left_y))
		self.CORNERS.append((top_right_x,top_right_y))
		self.CORNERS.append((bottom_right_x,bottom_right_y))

	def plotFourCorners(self):
		tempImg = self.img
		for point in self.CORNERS:
			cv2.circle(tempImg,point,3,self.RED,-1)

	def plotOuterEdges(self):
		tempImg = self.img
		for i in range(0,4):
			cv2.line(tempImg, (self.CORNERS[i]), (self.CORNERS[(i+1)%4]), self.GREEN, 2 )

	def detectVerticesOnOuterEdges(self):
		for i in range(0,4):
			self.OUTER_VERTICES.append( Geometry.partitionLine((self.CORNERS[i]), (self.CORNERS[(i+1)%4]), self.FACTOR) )

	def plotAllEdges(self):
		for j in range(0,2):
			for i in range(0,self.FACTOR+1):
				cv2.line(self.img, (self.OUTER_VERTICES[j][i]) , (self.OUTER_VERTICES[j+2][self.FACTOR - i]), self.RED , 1)

	def detectAllVertices(self):
		# Detecting vertices on the newly constructed board
		self.gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)

		tempVertices = cv2.goodFeaturesToTrack(self.gray,int(self.FINAL_VERTICES_COUNT),0.01,10)
		tempVertices = np.int0(tempVertices)

		newVertices = []

		for i in tempVertices:
			x,y = i.ravel()
			newVertices.append((x,y))

		# Matrix to store coordinates of vertices on the board
		self.ALL_VERTICES = [[(0,0) for x in range(self.FACTOR+2)] for x in range(self.FACTOR+2)]

		# Filling the matrix
		self.ALL_VERTICES[0][0] = (self.CORNERS[1])

		for i in range(0,self.FACTOR):
			for j in range(0,self.FACTOR):
				predicted_x = self.ALL_VERTICES[i][j][0] + int( ( self.OUTER_VERTICES[2][self.FACTOR - i][0] - self.OUTER_VERTICES[0][i][0] ) / 8 )
				predicted_y = self.ALL_VERTICES[i][j][1] + int( ( self.OUTER_VERTICES[3][self.FACTOR - i][1] - self.OUTER_VERTICES[1][i][1] ) / 8 )

				minn_dist = self.INT_MAX

				for point in newVertices:
					this_dist = Geometry.getPointsDistance( point , (predicted_x, self.ALL_VERTICES[i][j][1])  )
					if this_dist < minn_dist:
						self.ALL_VERTICES[i][j+1] = point
						minn_dist = this_dist

				minn_dist = self.INT_MAX

				for point in newVertices:
					this_dist = Geometry.getPointsDistance( point , (self.ALL_VERTICES[i][j][0], predicted_y)  )
					if this_dist < minn_dist:
						self.ALL_VERTICES[i+1][j] = point;
						minn_dist = this_dist

		self.ALL_VERTICES[self.FACTOR][self.FACTOR] = (self.CORNERS[3])

	def createTopology(self):
		# Taking out each cell and deciding if :
		# 1> it is empty
		# 2> it has a black piece
		# 3> it has a white piece

		print self.WHITE_THRESHOLD," ",self.BLACK_THRESHOLD

		self.TOPOLOGY = [["." for x in range(self.FACTOR)] for x in range(self.FACTOR)]

		for i in range(0,self.FACTOR):
			for j in range(0,self.FACTOR):
				filename = str(i)+str(j)+".jpg"

				cropped = self.img[self.ALL_VERTICES[i][j][1]+5:self.ALL_VERTICES[i+1][j+1][1]-5 ,self.ALL_VERTICES[i][j][0]+5:self.ALL_VERTICES[i+1][j+1][0]-5]
				#cropped = img[matrix[i][j][1]:matrix[i+1][j+1][1] ,matrix[i][j][0]:matrix[i+1][j+1][0]]
				cv2.imwrite(filename,cropped)
				shutil.move(filename,"temp/"+filename)
				
				cropped = self.img[self.ALL_VERTICES[i][j][1]+5:self.ALL_VERTICES[i+1][j+1][1]-5 ,self.ALL_VERTICES[i][j][0]+5:self.ALL_VERTICES[i+1][j+1][0]-5]
				cropped = self.sharpen(cropped)


				height = len(cropped)
				width = len(cropped[0])

				width = int(width / 2)
				height = int(height / 2)

				c = 0
				white = 0
				black = 0
				tot = 0

				for x in range(height-self.OFFSET2,height+self.OFFSET2):
					for y in range(width-self.OFFSET2, width+self.OFFSET2):
						p = cropped[x][y]
						c+=1
						tot = tot + p[0] + p[1] + p[2]
						if p[0]<=self.BLACK_THRESHOLD and p[1]<=self.BLACK_THRESHOLD and p[2]<=self.BLACK_THRESHOLD:
							black+=1
						if p[0]>=self.WHITE_THRESHOLD and p[1]>=self.WHITE_THRESHOLD and p[2]>=self.WHITE_THRESHOLD:
							white+=1
				probW = (white*1.0)/(c*1.0)
				probB = (black*1.0)/(c*1.0)

				# Probability of white piece and black piece at every cell
				print i," ",j," ",int(probW*100)," ",int(probB*100)," ",int(tot/c)

				if(probW >= self.PROBABILITY_THRESHOLD and probW > probB):
					self.TOPOLOGY[i][j] = 'W'
				elif probB >= self.PROBABILITY_THRESHOLD:
					self.TOPOLOGY[i][j] = 'B'

	def getFourCorners(self):
		return self.CORNERS

	def getAllVertices(self):
		return self.ALL_VERTICES

	def getTopology(self):
		return self.TOPOLOGY

	def displayFourCorners(self):
		tempImg = deepcopy(self.stock)
		for point in self.CORNERS:
			cv2.circle(tempImg,point,3,self.RED,-1)
		plt.imshow(tempImg),plt.show()

	def displayFourEdges(self):
		tempImg = deepcopy(self.stock)
		for i in range(0,4):
			cv2.line(tempImg, (self.CORNERS[i]), (self.CORNERS[(i+1)%4]), self.GREEN, 2 )
		plt.imshow(tempImg),plt.show()

	def displayAllEdges(self):
		tempImg = deepcopy(self.stock)
		for j in range(0,2):
			for i in range(0,self.FACTOR+1):
				cv2.line(tempImg, (self.OUTER_VERTICES[j][i]) , (self.OUTER_VERTICES[j+2][self.FACTOR - i]), self.RED , 1)
		plt.imshow(tempImg),plt.show()

	def displayAllVertices(self):
		tempImg = deepcopy(self.stock)
		for i in range(0,self.FACTOR+1):
			for j in range(0,self.FACTOR+1):
				cv2.circle(tempImg,(self.ALL_VERTICES[i][j]),5,self.BLUE,-1)
		plt.imshow(tempImg),plt.show()

	def displayTopology(self):
		for i in range(0,self.FACTOR):
			for j in range(0,self.FACTOR):
				print self.TOPOLOGY[i][j],
			print ""

	def fixThresholds(self):
		minn_brightness = self.INT_MAX
		maxx_brightness = 0
		for x in range(0,self.FACTOR):
			for y in range(0,self.FACTOR):
				if (x,y) in self.WHITES:
					continue
				if (x,y) in self.BLACKS:
					continue
				cropped = self.img[self.ALL_VERTICES[x][y][1]+5:self.ALL_VERTICES[x+1][y+1][1]-5 ,self.ALL_VERTICES[x][y][0]+5:self.ALL_VERTICES[x+1][y+1][0]-5]
				cropped = self.sharpen(cropped)

				height = len(cropped)
				width = len(cropped[0])

				width = int(width / 2)
				height = int(height / 2)

				for i in range(height-self.OFFSET2,height+self.OFFSET2):
					for j in range(width-self.OFFSET2,width+self.OFFSET2):
						minn_brightness = min(minn_brightness,cropped[i][j][0],cropped[i][j][1], cropped[i][j][2])
						maxx_brightness = max(maxx_brightness,cropped[i][j][0],cropped[i][j][1], cropped[i][j][2])

				# print x," ",y," ",minn_brightness," ",maxx_brightness

		self.WHITE_THRESHOLD = maxx_brightness 
		self.BLACK_THRESHOLD = minn_brightness 