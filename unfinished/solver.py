from shapely.geometry import *
import manim

PointPair = tuple[Point, Point]


class CircuitState:
    disjointStructure: LineString
    # blockingLines: list[LineString]
    pairs: list[PointPair]

    def __init__(self, pointPairs: list[PointPair]):
        self.pairs = pointPairs
        # self.blockingSegments = []

    # def nextFix(self, line: LineString):
    #     # check if line intersects any of the segments
    #     for segment in self.blockingSegments:
    #         if not line.intersects(segment):
    #             continue
    #         intersection = line.intersection(segment)
    #         if type(intersection) == Point:
    #             return intersection, segment
    #         elif type(intersection) == MultiPoint:
    #             return intersection.geoms[0], segment
    #     return None

    def drawPath(self, pair: PointPair):
        print(f"drawing {pair}")
        line = LineString(pair)
        if fix := self.nextFix(line):
            intersection, segment = fix
            line = LineString(pair[0], segment.coords[0], pair[1])
        # self.blockingSegments.append(line)

    def draw(self):
        for pair in self.pairs:
            self.drawPath(pair)


circuit = CircuitState(
    [
        ((-100, 0), (100, 0)),
        ((0, -100), (0, 100)),
    ]
)

circuit.draw()


class CreateCircle(manim.Scene):
    def construct(self):
        circle = manim.Circle()  # create a circle
        # circle.set_fill(ORANGE, opacity=0.5)  # set the color and transparency
        self.play(manim.Create(circle))  # show the circle on screen
