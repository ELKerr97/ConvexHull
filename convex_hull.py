import math

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)


# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		# SORT THE POINTS BY INCREASING X-VALUE
		points.sort(key=lambda x: x.x())
		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	def convex_hull_solver(self, points):
		# base cases
		# merge going back up (on return)
		if len(points) == 2 or len(points) == 3:
			return points
			# sort the hulls
			# merge the hulls
			# return merged hull
		else:
			lower_points, upper_points = self.divide_points_in_half(points)
			# keep dividing points in half
			return self.merge_two_hulls(
				self.convex_hull_solver(lower_points),
				self.convex_hull_solver(upper_points)
			)
			# return merged hull with new divided points (recursion)

	# combine two hulls
		# return a list of sorted points representing the shape of the new hull
		# send list of tangent lines (adjacent points in list) to GUI
	def merge_two_hulls(self, left_hull, right_hull):
		new_hull = []

		rightmost_of_left = left_hull[-1]
		leftmost_of_right = right_hull[-1]

		# sort hulls
		left_hull = self.sort_hull(left_hull)
		right_hull = self.sort_hull(right_hull)

		# find upper tangent line
		upper_tangent_line = self.find_upper_tangent(left_hull, right_hull, rightmost_of_left, leftmost_of_right)

		# find lower tangent line
		lower_tangent_line = self.find_lower_tangent(left_hull, right_hull, rightmost_of_left, leftmost_of_right)

		# get new points for merged hull

		# send edges lines up to GUI

		# return new hull as points
		return new_hull

	# sort a hull's points by decreasing slope between leftmost and rest of points
	def sort_hull(self, points):
		sorted_hull = []
		left_most = points[0]

		# leftmost point at the beginning
		sorted_hull.append(left_most)

		# remove leftmost from list
		points.remove(0)

		# sort according to decreasing slope
		points.sort(key=lambda point: self.find_slope(left_most, point), reverse=True)

		# add to list
		sorted_hull.append(points)

		return sorted_hull

	# find the slope between two points
	def find_slope(self, start_point, end_point):

		slope = (end_point.y() - start_point.y()) / (end_point.x() - start_point.x())

		return slope

	# split up points based on x-values
	def divide_points_in_half(self, points):
		length = len(points)
		mid = math.floor(length / 2)
		lower_half = []
		upper_half = []
		for i in range(0, mid):
			lower_half.append(points[i])

		for i in range(mid, length):
			upper_half.append(points[i])

		return lower_half, upper_half

	# find the upper tangent of two hulls
	def find_upper_tangent(self, left_hull_points, right_hull_points, rightmost_of_left, leftmost_of_right):

		current_tangent_line = [rightmost_of_left, leftmost_of_right]
		change_made = True

		# keep track of current indices starting at closest points between hulls
		right_hull_current_index = right_hull_points.index(leftmost_of_right) + 1
		left_hull_current_index = left_hull_points.index(rightmost_of_left) - 1

		# length of list of points representing hulls
		left_hull_length = len(left_hull_points)
		right_hull_length = len(right_hull_points)

		# keep switching between right and left hulls until no change is made in current tangent line
		while change_made:

			# default to no change
			change_made = False

			# will run until slope decreases
			while True:

				new_slope = self.find_slope(current_tangent_line[0], right_hull_points[right_hull_current_index])
				current_slope = self.find_slope(current_tangent_line[0], current_tangent_line[1])

				if new_slope > current_slope:

					current_tangent_line[1] = right_hull_points[right_hull_current_index]
					right_hull_current_index += 1

					# if we've reached the end of the hull, wrap back around
					if right_hull_current_index == right_hull_length:
						right_hull_current_index = 0

				elif new_slope < current_slope:
					# switch
					break

			# will run until slope increases
			while True:

				new_slope = self.find_slope(current_tangent_line[1], left_hull_points[left_hull_current_index])
				current_slope = self.find_slope(current_tangent_line[1], current_tangent_line[0])

				if new_slope < current_slope:

					current_tangent_line[0] = left_hull_points[left_hull_current_index]
					left_hull_current_index -= 1

					# if we've reached the end of the hull, wrap back around
					if left_hull_current_index == -1:
						left_hull_current_index = left_hull_length - 1

					# a change in the tangent line was made, we need to switch again
					change_made = True

				elif new_slope > current_slope:
					# switch
					break

		# return a tuple containing QPoints representing upper tangent line
		return current_tangent_line[0], current_tangent_line[1]

	# find the lower tangent of two hulls
	# inverse of find_upper_tangent
	def find_lower_tangent(self, left_hull_points, right_hull_points, rightmost_of_left, leftmost_of_right):
		# return a tuple containing QPoints representing lower tangent line
		return []
