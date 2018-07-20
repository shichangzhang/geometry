import matplotlib.pyplot as plt
from geometry import *

def drawPolygon(polygon):
    plt.plot(polygon.getXs(), polygon.getYs())

def drawSegment(diagonal):
    plt.plot(diagonal.getXs(), diagonal.getYs())

def drawDiagonals(diagonals):
    for diag in diagonals:
        drawSegment(diag)
    
def draw(points):
    polygon = Polygon(points)
    drawPolygon(polygon)
    diagonals = polygon.triangulate()
    drawDiagonals(diagonals)
    plt.show()

def drawExample():
    draw(poly18)
