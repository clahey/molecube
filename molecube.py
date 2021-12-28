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

class ChangeType(Enum):
    COLOR_SET = 0
    COLOR_IMPOSSIBLE = 1

VALUE_COUNT = 9

def colorToValue(colorOrValue):
    if ('value' in dir(colorOrValue)):
        return colorOrValue.value
    else:
        return colorOrValue

class ContradictionError(Exception):
    pass

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
    
    def trigger(self, value = None):
        for callback in self.observers.values():
            callback(value)

class Point(object):
    def __init__(self, index):
        self.value = None
        self.index = index
        self.possibleValues = [True] * VALUE_COUNT
        self.dirtySignal = Signal()

    def __str__(self):
        possibleValues = [index for (possible, index) in zip(self.possibleValues, range(VALUE_COUNT)) if possible]
        possibleValuesString = 'possible %s' % (possibleValues)
        valueString = 'value %s' % (self.value)
        return 'Point %d, %s' % (self.index, valueString if self.value != None else possibleValuesString)

    def setImpossible(self, value):
        value = colorToValue(value)
        self.possibleValues[value] = False
        if sum(self.possibleValues) == 1:
            solvedValue = self.possibleValues.index(True)
            self.value = solvedValue
            self.dirtySignal.trigger({"type": ChangeType.COLOR_SET, "point": self, "value": solvedValue})
        else:
            self.dirtySignal.trigger({"type": ChangeType.COLOR_IMPOSSIBLE, "point": self, "value": value})

    def setValue(self, value):
        value = colorToValue(value)
        if not self.possibleValues[value]:
            raise ContradictionError("Value %d is not possible at point %s" % (value, self))
        if not self.isSolved():
            self.value = value
            self.possibleValues = [False] * VALUE_COUNT
            self.possibleValues[value] = True
            self.dirtySignal.trigger({"type": ChangeType.COLOR_SET, "point": self, "value": value})

    def getValue(self):
        return self.value

    def isSolved(self):
        return self.value != None

    def clone(self):
        cls = self.__class__
        clone = cls.__new__(cls)

        clone.value = self.value
        clone.index = self.index
        clone.possibleValues = [e for e in self.possibleValues]
        clone.dirtySignal = Signal()
        return clone

class Region(object):
    def __init__(self, points, available = range(0, VALUE_COUNT)):
        if (len(points) > len(available)):
            raise ValueError("len(points) = %d, len(available) = %d" % (len(points), len(available)))
        self.dirty = True
        self.points = points
        self.available = {}
        for value in available:
            self.available[colorToValue(value)] = self.available.get(colorToValue(value), 0) + 1
        for point in self.points:
            if point.isSolved():
                self.markSolved(point)
            else:
                point.dirtySignal.subscribe (self.markDirty)

    def __str__(self):
        return 'Region unsolved points %s, available %s, dirty %s' % (
            ' '.join([str(p.index) for p in self.points if not p.isSolved()]),
            self.available, self.dirty)
    def markDirty(self, change):
        if (change["type"] == ChangeType.COLOR_SET):
            self.markSolved(change["point"])
        self.dirty = True

    def markSolved(self, point):
        value = point.getValue()
        if self.available.get(value, 0) == 0:
            raise ContradictionError("Point %s set to %d, but that value isn't avaliable in region %s" % (point, value, self))
        else:
            self.available[value] -= 1
    def clone(self, points):
        cls = self.__class__
        clone = cls.__new__(cls)

        clone.dirty = self.dirty
        clone.points = [points[e.index] for e in self.points]
        clone.available = self.available.copy()
        for point in clone.points:
            if not point.isSolved():
                point.dirtySignal.subscribe (clone.markDirty)
        return clone

class Cube(object):
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

    def __str__(self):
        return "Cube [\n%s\n]" % '\n'.join(map(lambda p: ' ' + str(p), self.points + self.regions))

    def clone(self):
        cls = self.__class__
        clone = cls.__new__(cls)

        clone.points = [e.clone() for e in self.points]
        clone.regions = [e.clone(clone.points) for e in self.regions]
        return clone
cube = Cube.createDefault()
