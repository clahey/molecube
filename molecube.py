from enum import Enum

class Color(Enum):
    WHITE = 0
    YELLOW = 1
    BLUE = 2
    ORANGE = 3
    CYAN = 4
    BLACK = 5
    GREEN = 6 # Two Corners
    RED = 7 # Three edges
    PURPLE = 8 # Three edges

VALUE_COUNT = 9

def colorToValue(colorOrValue):
    if ('value' in dir(colorOrValue)):
        return colorOrValue.value
    else:
        return colorOrValue

class Signal:
    def __init__(self):
        self.observers = {}
        self.nextId = 1

    def subscribe(self, callback, notifyImmediately = False):
        id = self.nextId
        self.nextId = self.nextId + 1
        self.observers[id] = callback
        if notifyImmediately:
            callback()
        return id

    def unsubscribe(self, id):
        del self.observers[id]
    
    def trigger(self):
        for callback in self.observers.values():
            callback()

class Point:
    def __init__(self, index):
        self.value = None
        self.index = index
        self.possibleValues = [True] * VALUE_COUNT
        self.dirtySignal = Signal()

    def setImpossible(self, value):
        value = colorToValue(value)
        self.possibleValues[value] = False
        if sum(self.possibleValues) == 1:
            self.value = self.possibleValues.index(True)
        self.markDirty()

    def setValue(self, value):
        value = colorToValue(value)
        self.value = value
        self.possibleValues = [False] * VALUE_COUNT
        self.possibleValues[value] = True
        self.markDirty()

    def getValue(self):
        return self.value

    def isSolved(self):
        return self.value != None

    def markDirty(self):
        self.dirtySignal.trigger()

class Region:
    def __init__(self, points, available = range(0, VALUE_COUNT)):
        if (len(points) != len(available)):
            raise ValueError("len(points) = %d, len(available) = %d" % (len(points), len(available)))
        self.dirty = True
        self.points = points
        self.available = {}
        for value in available:
            self.available[value] = self.available.get(colorToValue(value), 0) + 1
        for point in self.points:
            point.dirtySignal.subscribe (self.markDirty)
    def markDirty(self):
        self.dirty = True

class Cube:
    def __init__(self, points, regions):
        self.points = points
        self.regions = regions

    @staticmethod
    def createDefault():
        points = [ Point(e) for e in range(0, 27) ]
        points[13].setValue(0)
        points[4].setValue(Color.WHITE)
        points[10].setValue(Color.YELLOW)
        points[14].setValue(Color.BLUE)
        points[16].setValue(Color.ORANGE)
        points[12].setValue(Color.CYAN)
        points[22].setValue(Color.BLACK)
                        
        
        regions = [ Region([points[e] for e in range(0, 9)]),
                    Region([points[e] for e in [0, 1, 2, 9, 10, 11, 18, 19, 20]]),
                    Region([points[e] for e in range(0, 25, 3)]),
                    Region([points[e] for e in range(18, 27)]),
                    Region([points[e] for e in [6, 7, 8, 15, 16, 17, 24, 25, 26]]),
                    Region([points[e] for e in range(2, 27, 3)]),
                    # Corners
                    Region([points[e] for e in range(0, 27, 2) if not points[e].isSolved()],
                           [Color.WHITE, Color.YELLOW, Color.BLUE, Color.ORANGE, Color.CYAN, Color.BLACK, Color.GREEN, Color.GREEN]),
                    # Edges
                    Region([points[e] for e in range(1, 26, 2) if not points[e].isSolved()],
                           [Color.WHITE, Color.YELLOW, Color.BLUE, Color.ORANGE, Color.CYAN, Color.BLACK, Color.RED, Color.RED, Color.RED, Color.PURPLE, Color.PURPLE, Color.PURPLE]),
                    ]
        return Cube(points, regions)

cube = Cube.createDefault()
