from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from math import sqrt
from sys import exit

from subprocess import Popen, DEVNULL

from resmon import LineSegment, reorder_step


def write_head(file):
    with open("head.tex", "r") as head:
        for line in head:
            f.write(line)

def write_foot(file):
    with open("foot.tex", "r") as head:
        for line in head:
            f.write(line)

parser = ArgumentParser(description="Generate LATEX code exemplifying Lemma 5, analogous to Figure 3.",
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-l", type=float, nargs="+",
                    default=[0., 0., .15, .0, .35, .02, .42, .04, .6, .12, .85, .3, .92, .45, 1., 1.],
                    help="coordinates of the lower line, in the format x1 y1 x2 y2 ... x_t y_t")
parser.add_argument("-u", type=float, nargs="+",
                    default=[0, 0, .38, .17, .74, .45, 1., 1.],
                    help="coordinates of the upper line, in the format x1 y1 x2 y2 ... x_t y_t")
parser.add_argument("-n", type=str, default="normal.tex", help="output path for normal line")
parser.add_argument("-o", type=str, default="onestep.tex", help="output path for one-step visualization")
parser.add_argument("-a", type=str, default="allsteps.tex", help="output path for allsteps visualization")
parser.add_argument("-p", type=float, default=0.005,
                    help="minimum precision for drawing the rainbow gradient")
parser.add_argument('--compile', default=False, action='store_true', help="compile pdfs with pdflatex")
args = parser.parse_args()

precision = args.p
lower = args.l
upper = args.u
normal_path = args.n
onestep_path = args.o
allsteps_path = args.a
do_compile = args.compile

if len(lower) % 2 == 1:
    print("Coordinate list for lower line must have even number.")
    exit(1)
if len(upper) < 2:
    print("Coordinate list for upper line must have at least two elements.")
    exit(2)
if len(upper) % 2 == 1:
    print("Coordinate list for upper line must have even number.")
    exit(3)

points = []
for i in range(0, len(lower), 2):
    points.append((lower[i], lower[i+1]))

upper_changes = []
last = upper[:2]
for i in range(2, len(upper), 2):
    upper_changes.append((upper[i] - last[0], upper[i+1] - last[1]))
    last = (upper[i], upper[i+1])

length = 0
for i in range(len(points) - 1):
    x1, y1 = points[i]
    x2, y2 = points[i + 1]
    length += sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
curve = []
length_so_far = 0
for i in range(len(points) - 1):
    x1, y1 = points[i]
    x2, y2 = points[i + 1]
    segment_length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    curve.append(LineSegment(x2 - x1, y2 - y1, (length_so_far / length, (length_so_far + segment_length) / length)))
    length_so_far += segment_length

with open(normal_path, "w") as f:
    write_head(f)
    f.write("\draw (axis cs:0, 0) coordinate (x);")
    for e in curve:
        f.write(e.to_tikz(precision))
    write_foot(f)

with open(onestep_path, "w") as f:
    write_head(f)
    a1, rest = reorder_step(upper_changes[0][0], upper_changes[0][1], curve)
    f.write("\draw (axis cs:0, 0) coordinate (x);")
    for e in a1:
        f.write(e.to_tikz(precision))
    for e in rest:
        f.write(e.to_tikz(precision))
    write_foot(f)

with open(allsteps_path, "w") as f:
    write_head(f)
    rest = curve
    f.write("\draw (axis cs:0, 0) coordinate (x);")
    for x, y in upper_changes:
        a, rest = reorder_step(x, y, rest)
        for e in a:
            f.write(e.to_tikz(precision))
    write_foot(f)

if do_compile:
    Popen(["pdflatex", normal_path], stdout=DEVNULL)
    Popen(["pdflatex", onestep_path], stdout=DEVNULL)
    Popen(["pdflatex", allsteps_path], stdout=DEVNULL)