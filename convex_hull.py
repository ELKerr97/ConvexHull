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
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        line = [line]
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        line = [line]
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    # points are QPointF -> (x,y)
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        # SORT THE POINTS BY INCREASING X-VALUE
        points.sort(key=lambda x: x.x())
        t2 = time.time()

        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        # polygon = [QLineF(points[i], points[(i + 1) % 3]) for i in range(3)]
        polygon = self.getPolygonFromPoints(self.convex_hull_solver(points))
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, GREEN)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))

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
            # return merged hull with new divided points (recursion)
            return self.merge_two_hulls(
                self.convex_hull_solver(lower_points),
                self.convex_hull_solver(upper_points)
            )

    # combine two hulls
    # return a list of sorted points representing the shape of the new hull
    # send list of tangent lines (adjacent points in list) to GUI
    # right and left hulls are lists of QPointF's (x,y)
    def merge_two_hulls(self, left_hull, right_hull):
        new_hull = []

        # rightmost of left hull will be last point in list of points sorted by x value
        rightmost_of_left = max(left_hull, key=lambda point: point.x())
        # leftmost of right hull will be the first point in list of points sorted by x value
        leftmost_of_right = min(right_hull, key=lambda point: point.x())

        # sort hulls
        left_hull = self.sort_hull(left_hull)
        right_hull = self.sort_hull(right_hull)

        # find upper tangent line
        upper_tangent_line_points = self.find_upper_tangent(left_hull, right_hull, rightmost_of_left, leftmost_of_right)
        # self.blinkTangent(QLineF(upper_tangent_line_points[0], upper_tangent_line_points[1]), RED)
        # find lower tangent line
        lower_tangent_line_points = self.find_lower_tangent(left_hull, right_hull, rightmost_of_left, leftmost_of_right)
        # self.blinkTangent(QLineF(lower_tangent_line_points[0], lower_tangent_line_points[1]), BLUE)

        # get new points for merged hull
        combinedHullPoints = self.combineHullsWithTangents(
            left_hull
            , right_hull
            , upper_tangent_line_points
            , lower_tangent_line_points
        )
        new_hull.append(combinedHullPoints)

        polygon = self.getPolygonFromPoints(combinedHullPoints)
        # return new hull as polygon
        return combinedHullPoints

    def combineHullsWithTangents(self, leftHull, rightHull, upperTan, lowerTan):
        points = []
        currLeftIndex = 0
        currRightIndex = 0

        while True:
            points.append(leftHull[currLeftIndex])
            if leftHull[currLeftIndex] == upperTan[0]:
                # jump to right hull and continue
                currRightIndex = rightHull.index(upperTan[1])
                break
            else:
                currLeftIndex += 1
                if currLeftIndex == len(leftHull):
                    currLeftIndex = 0

        while True:
            points.append(rightHull[currRightIndex])
            if rightHull[currRightIndex] == lowerTan[1]:
                currLeftIndex = leftHull.index(lowerTan[0])
                break
            else:
                currRightIndex += 1
                if currRightIndex == len(rightHull):
                    currRightIndex = 0

        while currLeftIndex != 0:
            points.append(leftHull[currLeftIndex])
            currLeftIndex += 1
            if currLeftIndex == len(leftHull):
                break

        return points

    def getPolygonFromPoints(self, points):
        polygon = []
        # connect each point to each other
        for i in range(len(points) - 1):
            newLine = QLineF(points[i], points[i + 1])
            polygon.append(newLine)
        # connect last point to first point
        polygon.append(QLineF(points[len(points) - 1], points[0]))
        return polygon

    # sort a hull's points by decreasing slope between leftmost and rest of points
    def sort_hull(self, points):
        sorted_hull = []
        left_most = points[0]

        # leftmost point at the beginning
        sorted_hull.append(left_most)

        # remove leftmost from list
        points.remove(left_most)

        # sort according to decreasing slope
        points.sort(key=lambda point: self.find_slope(left_most, point), reverse=True)

        # add to list
        for i in range(len(points)):
            sorted_hull.append(points[i])

        # self.showHull(self.getPolygonFromPoints(points), BLUE)

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

        # start with line between rightmost of left and leftmost of right
        current_tangent_line = [rightmost_of_left, leftmost_of_right]
        change_made = True

        # keep track of current indices starting at closest points between hulls.
        # Guaranteed to have at least two points.
        # Start at next point in clockwise direction for right hull
        right_hull_current_index = 1
        # Start at next point in counter-clockwise direction for lef hull
        left_hull_current_index = left_hull_points.index(rightmost_of_left) - 1

        # length of list of points representing hulls to enable index folding
        left_hull_length = len(left_hull_points)
        right_hull_length = len(right_hull_points)

        # keep switching between right and left hulls until no change is made in current tangent line
        while change_made:

            # default to no change
            change_made = False

            # will run until slope decreases
            while True:

                # new slope found between current tan line point on left hull and next right hull point
                new_slope = self.find_slope(current_tangent_line[0], right_hull_points[right_hull_current_index])
                # current slope found between current tan line points
                current_slope = self.find_slope(current_tangent_line[0], current_tangent_line[1])

                # if the new slope is greater than the current slope, replace point2 in the tangent line
                if new_slope > current_slope:

                    # replace point 2 in the tangent line
                    current_tangent_line[1] = right_hull_points[right_hull_current_index]
                    # move on to next point in right hull, moving clockwise
                    right_hull_current_index += 1

                    # if we've reached the end of the right hull, wrap back around
                    if right_hull_current_index == right_hull_length:
                        right_hull_current_index = 0

                # if the new slope is less than the current slope, we need to switch pivots
                elif new_slope < current_slope:
                    # switch
                    break

            # will run until slope increases
            while True:

                # new slope found between current tan line point on right hull and next left hull point
                new_slope = self.find_slope(current_tangent_line[1], left_hull_points[left_hull_current_index])
                # current slope found between current tan line points
                current_slope = self.find_slope(current_tangent_line[1], current_tangent_line[0])

                # If the new slope is less than the current slope, replace point1 in the tangent line
                if new_slope < current_slope:

                    # replace point1 in the tangent line
                    current_tangent_line[0] = left_hull_points[left_hull_current_index]
                    # move on to next point in right hull, moving counter-clockwise
                    left_hull_current_index -= 1

                    # if we've reached the end of the hull, wrap back around
                    if left_hull_current_index == -1:
                        left_hull_current_index = left_hull_length - 1

                    # a change in the tangent line was made, we need to switch back to the right side.
                    change_made = True

                # if the new slope is greater than the current slope, we break.
                # if a change was made, we'll switch
                elif new_slope > current_slope:
                    # switch if change was made
                    break

        # return a QLineF containing QPoints representing upper tangent line
        return current_tangent_line[0], current_tangent_line[1]

    # find the lower tangent of two hulls
    # inverse of find_upper_tangent
    def find_lower_tangent(self, left_hull_points, right_hull_points, rightmost_of_left, leftmost_of_right):

        # start with line between rightmost of left and leftmost of right
        current_tangent_line = [rightmost_of_left, leftmost_of_right]
        change_made = True

        # length of list of points representing hulls to enable index folding
        left_hull_length = len(left_hull_points)
        right_hull_length = len(right_hull_points)

        # keep track of current indices starting at closest points between hulls.
        # Guaranteed to have at least two points.
        # Start at next point in counter-clockwise direction for right hull
        right_hull_current_index = len(right_hull_points) - 1
        # Start at next point in clockwise direction for lef hull
        left_hull_current_index = left_hull_points.index(rightmost_of_left) + 1
        if(left_hull_current_index == len(left_hull_points)):
            left_hull_current_index = 0

        # keep switching between right and left hulls until no change is made in current tangent line
        while change_made:

            # default to no change
            change_made = False

            # will run until slope increases
            while True:

                # new slope found between current tan line point on left hull and next right hull point
                new_slope = self.find_slope(current_tangent_line[0], right_hull_points[right_hull_current_index])
                # current slope found between current tan line points
                current_slope = self.find_slope(current_tangent_line[0], current_tangent_line[1])

                # if the new slope is less than the current slope, replace point2 in the tangent line
                if new_slope < current_slope:

                    # replace point 2 in the tangent line
                    current_tangent_line[1] = right_hull_points[right_hull_current_index]
                    # move on to next point in right hull, moving counter-clockwise
                    right_hull_current_index -= 1

                    # if we've reached the end of the right hull, wrap back around
                    if right_hull_current_index == -1:
                        right_hull_current_index = right_hull_length - 1

                # if the new slope is greater than the current slope, we need to switch pivots
                elif new_slope > current_slope:
                    # switch
                    break

                else:
                    break

            # will run until slope decreases
            while True:

                # new slope found between current tan line point on right hull and next left hull point
                new_slope = self.find_slope(current_tangent_line[1], left_hull_points[left_hull_current_index])
                # current slope found between current tan line points
                current_slope = self.find_slope(current_tangent_line[1], current_tangent_line[0])

                # If the new slope is greater than the current slope, replace point1 in the tangent line
                if new_slope > current_slope:

                    # replace point1 in the tangent line
                    current_tangent_line[0] = left_hull_points[left_hull_current_index]
                    # move on to next point in right hull, moving clockwise
                    left_hull_current_index += 1

                    # if we've reached the end of the hull, wrap back around
                    if left_hull_current_index == left_hull_length:
                        left_hull_current_index = 0

                    # a change in the tangent line was made, we need to switch back to the right side.
                    change_made = True

                # if the new slope is less than the current slope, we break.
                # if a change was made, we'll switch
                elif new_slope < current_slope:
                    # switch if change was made
                    break

                else:
                    break

        # return a QLineF containing QPoints representing upper tangent line
        return current_tangent_line[0], current_tangent_line[1]
