class Drawable:
    def getPoints(self):
        return NotImplementedError("Drawable.getPoints() not implemented.") 

    def getXs(self):
        return Point.getValues(self.getPoints(), Point.X)
        
    def getYs(self):
        return Point.getValues(self.getPoints(), Point.Y)

class Segment(Drawable):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @classmethod
    def makeDiagonal(cls, vertexA, vertexB):
        return cls(vertexA.point, vertexB.point)
        
    def intersectsProperlyWith(self, cd):
        ab = self
        a = self.a
        b = self.b
        c = cd.a
        d = cd.b
        if c.isCollinearWith(a, b) or d.isCollinearWith(a, b) or \
           a.isCollinearWith(c, d) or b.isCollinearWith(c, d):
            return False
        return c.isLeftOf(ab) ^ d.isLeftOf(ab) and \
               a.isLeftOf(cd) ^ b.isLeftOf(cd)

    def intersects(self, cd):
        a = self.a
        b = self.b
        c = cd.a
        d = cd.b
        if self.intersectsProperlyWith(cd):
            return True
        elif c.isBetween(a, b) or \
             d.isBetween(a, b) or \
             a.isBetween(c, d) or \
             b.isBetween(c, d):
            return True
        else:
            return False

    def getPoints(self):
        points = [self.a, self.b]
        return points

class Point:
    X = 0
    Y = 1
    def __init__(self, coordinates):
        self.dim = len(coordinates)
        self.coord = coordinates
  
    def __getitem__(self, key):
        if key < self.dim:
            return self.coord[key]
        raise KeyError

    @staticmethod
    def Area2(a, b, c):
        X = Point.X
        Y = Point.Y
        return (b[X] - a[X]) * (c[Y] - a[Y]) - \
               (c[X] - a[X]) * (b[Y] - a[Y])
    
    def isLeftOf(self, ab):
        return Point.Area2(ab.a, ab.b, self) > 0

    def isNotRightOf(self, ab):
        return Point.Area2(ab.a, ab.b, self) >= 0

    def isCollinearWith(self, a, b):
        return Point.Area2(a, b, self) == 0
    
    def isBetween(self, a, b):
        c = self
        X = Point.X
        Y = Point.Y
        if not c.isCollinearWith(a, b):
            return False
        if a[X] != b[X]:
            return ((a[X] <= c[X]) and (c[X] <= b[X])) or \
                   ((a[X] >= c[X]) and (c[X] >= b[X]))
        else:
            return ((a[Y] <= c[Y]) and (c[Y] <= b[Y])) or \
                   ((a[Y] >= c[Y]) and (c[Y] >= b[Y]))

    @staticmethod
    def getValues(points, i):
        values = []
        for p in points:
            values.append(p[i])
        return values

        
class Vertex:
    def __init__(self, vnum, coordinates):
        self.vnum = vnum
        self.point = Point(coordinates)
        self.isEar = False
        self.prev = None
        self.next = None

    def isInCone(self, coneVertex):
        previousVertex = coneVertex.prev
        nextVertex = coneVertex.next
        ab = Segment(coneVertex.point, self.point)
        ba = Segment(self.point, coneVertex.point)
        if coneVertex.isConvex():
            return previousVertex.point.isLeftOf(ab) and \
                   nextVertex.point.isLeftOf(ba)
        else:
            return not (nextVertex.point.isNotRightOf(ab) and \
                        previousVertex.point.isNotRightOf(ba))

    def isConvex(self):
        currentPoint = self.point
        previousPoint = self.prev.point
        nextPoint = self.next.point
        return previousPoint.isNotRightOf(Segment(currentPoint, nextPoint))
    
class Polygon(Drawable):
    def __init__(self, vertices=None):
        self.vnum = 0
        self.head = None
        if vertices != None:
            self.addVertices(vertices)

    def addVertex(self, coordinates):
        p = Vertex(self.vnum, coordinates)
        if self.head == None:
            self.head = p
            self.head.next = self.head.prev = p
        else:
            p.next = self.head
            p.prev = self.head.prev
            self.head.prev = p
            p.prev.next = p
        self.vnum += 1

    def addVertices(self, vertices):
        for coordinates in vertices:
            self.addVertex(coordinates)

    def getPolygonArea2(self):
        total = 0
        p = self.head
        a = p.next
        while True:
            total += Point.Area2(p.point, a.point, a.next.point)
            a = a.next
            if(a.next == self.head):
                break
        return total

    def hasAlmostDiagonal(self, a, b):
        diagonal = Segment(a.point, b.point)
        c = self.head
        while True:
            c1 = c.next
            edge = Segment(c.point, c1.point)
            if c != a and c1 != a and \
               c != b and c1 != b and \
               diagonal.intersects(edge):
                return False
            c = c.next
            if c == self.head:
                break
        return True

    def hasDiagonal(self, a, b):
        return a.isInCone(b) and b.isInCone(a) and self.hasAlmostDiagonal(a, b)

    def earInit(self):
        v1 = self.head
        while True:
            v2 = v1.next
            v0 = v1.prev
            v1.isEar = self.hasDiagonal(v0, v2)
            v1 = v1.next
            if v1 == self.head:
                break

    def triangulate(self):
        diagonals = []
        n = self.vnum
        self.earInit()
        while n > 3:
            v2 = self.head
            while True:
                if v2.isEar:
                    v3 = v2.next
                    v4 = v3.next
                    v1 = v2.prev
                    v0 = v1.prev
                    diagonals.append(Segment.makeDiagonal(v1, v3))
                    v1.isEar = self.hasDiagonal(v0, v3)
                    v3.isEar = self.hasDiagonal(v1, v4)
                    v1.next = v3
                    v3.prev = v1
                    self.head = v3
                    n-=1
                    break
                v2 = v2.next
                if v2 == self.head:
                    break
        return diagonals
    
    def getPoints(self):
        points = []
        v = self.head
        while True:
            points.append(v.point)
            v = v.next
            if v == self.head:
                break
        points.append(self.head.point)
        return points

star = [
    (0, 0),
    (1, 1),
    (2, 0),
    (2, 2),
    (3, 2),
    (2, 3),
    (1, 4),
    (0, 3),
    (-1, 2),
    (0, 2),
]

poly18 = [
    (0,0),
    (10,7),
    (12,3),
    (20,8),
    (13,17),
    (10,12),
    (12,14),
    (14,9),
    (8,10),
    (6,14),
    (10,15),
    (7,17),
    (0,16),
    (1,13),
    (3,15),
    (5,8),
    (-2,9),
    (5,5),
]
