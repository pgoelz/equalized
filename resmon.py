import colorsys
from math import sqrt, ceil


EPS = 0.00005

class LineSegment:
    """Representation of a line segment in a curve, only with relative dimensions.

    `style` is a variable that allows to keep track of which segment comes from where, which is used for coloring in the
    `to_tikz` method. It should be a pair of floats in [0, 1], giving the fraction of the overall original curve lying
    to the left of the starting point of the segment and of the endpoint of the segment, respectively.
    """
    def __init__(self, x, y, style):
        self.x = x
        self.y = y
        self.style = style

    def split(self, fraction):
        left_style = (self.style[0], self.style[0] + fraction * (self.style[1] - self.style[0]))
        right_style = (left_style[1], self.style[1])
        left = LineSegment(fraction * self.x, fraction * self.y, left_style)
        right = LineSegment((1 - fraction) * self.x, (1 - fraction) * self.y, right_style)
        return left, right

    def __repr__(self):
        return f"LineSegment({repr(self.x)}, {repr(self.y)}, {repr(self.style)})"

    def get_color(self, lower_frac, upper_frac):
        avg_frac = (lower_frac + upper_frac) / 2
        hue = (self.style[0] + (self.style[1] - self.style[0]) * avg_frac)
        (r, g, b) = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        return round(255 * r), round(255 * g), round(255 * b)

    def to_tikz(self, precision):
        s = []
        num_segments = ceil(sqrt(self.x**2 + self.y**2) / precision)
        x = self.x / num_segments
        y = self.y / num_segments
        for i in range(num_segments):
            red, green, blue = self.get_color(i / (num_segments + 1), (i + 1) / (num_segments + 1))
            s.append(f"\\draw[very thick,line cap=round,draw={{rgb,255:red,{red}; green,{green}; blue,{blue}}}] (x) "
                     f"-- ++(axis direction cs:{x},{y}) coordinate (x);")
        return "\n".join(s)


def reorder_step(segment_x, segment_y, curve):
    """Perform one step of the algorithm described in Lemma 5.

    Args:
        segment_x (float): width of the required section, i.e., width of the first line segment of the upper curve
        segment_y (float): height of the required section
        curve (list of LineSegment): the lower curve, to be permuted
    Returns:
        (found_section, rest) of type (list of LineSegment, list of LineSegment)
        `found_section` is a subsegment of `curve` with a total width of `segment_x` and height of `segment_y`.
        `rest` is the remainder of `curve` after cutting out `found_segment`.
    """

    # rounding error mitigation
    if abs(sum(e.x for e in curve) - segment_x) < EPS:
        assert abs(sum(e.y for e in curve) - segment_y) < EPS
        return curve, []

    # The algorithm moves two pointers `l` and `r` across the line segments of `curve`. In a continuous sweep of a
    # window of width `segment_x` over the curve, look at the pair of line segments that the left and right end of the
    # window touch. Our sequence of `(l, r)` should be exactly that sequence.
    l = 0
    r = 0
    # Invariants: x_lleft_rleft = sum(e.x for e in range(l, r))
    #             y_lleft_rleft = sum(e.y for e in range(l, r))
    x_lleft_rleft = 0
    y_lleft_rleft = 0
    while x_lleft_rleft + curve[r].x < segment_x:
        x_lleft_rleft += curve[r].x
        y_lleft_rleft += curve[r].y
        r += 1

    while l < len(curve) and r < len(curve):
        # Assertion I:
        assert x_lleft_rleft - curve[l].x < segment_x
        # Assertion II:
        assert x_lleft_rleft + curve[r].x >= segment_x

        # In each iteration, try to find a section of width `segment_x` and height `segment_y` that begins somewhere on
        # `curve[l]` and ends somewhere on `curve[r]`.
        # Denote the x-coordinate of the starting point of `curve[l]` by A, the x-coordinate of its endpoint by B,
        # denote the x-coordinate of the starting point of `curve[r]` by C, the x-coordinate of its endpoint by D.
        # Then, the left end of the section must lie between A and B and its right end between C and D.
        # We begin by finding the x-position of the leftmost (min) such frame and the rightmost (max) such frame.
        # `min_l_pos` gives the x-position of the left end of the min frame, relative to the distance of A
        # `min_r_pos` gives the x-position of the right end of the min frame, relative to the distance of C
        # The minimum frame will be constrained either by hitting A at its left end or C at its right end.
        # `min_l_pos` gives the x-position of the left end of the max frame, relative to the distance of A
        # `min_r_pos` gives the x-position of the right end of the max frame, relative to the distance of C
        # The maximum frame will be constrained either by hitting D at its right end or B at its left end.

        #   <---segment_x--->
        # A | B    ...    C | D

        # x_lleft_rleft = dist(A, C)
        if segment_x >= x_lleft_rleft:
            # left blocked at A
            min_l_pos = 0
            min_r_pos = segment_x - x_lleft_rleft
        else:
            # left blocked at C
            min_l_pos = x_lleft_rleft - segment_x
            min_r_pos = 0

        right_aligned_x = x_lleft_rleft + curve[r].x - curve[l].x

        # right_aligned_x = dist(B, D)
        if segment_x >= right_aligned_x:
            # right blocked at D
            max_l_pos = curve[l].x - (segment_x - right_aligned_x)
            max_r_pos = curve[r].x
        else:
            # right blocked at B
            max_l_pos = curve[l].x
            max_r_pos = curve[r].x - (right_aligned_x - segment_x)

        # Based on these coordinates, we can compute the height of the minimum and maximum frame
        # Shifting the frame between its leftmost and rightmost position linearly increases the height, at a slope
        # induced by the difference in slopes between `curve[l]` and `curve[r]`.
        min_y_diff = y_lleft_rleft - min_l_pos / curve[l].x * curve[l].y + min_r_pos / curve[r].x * curve[r].y
        max_y_diff = y_lleft_rleft - max_l_pos / curve[l].x * curve[l].y + max_r_pos / curve[r].x * curve[r].y

        if min_y_diff <= segment_y <= max_y_diff:
            if not max_y_diff == min_y_diff:
                fr = (segment_y - min_y_diff) / (max_y_diff - min_y_diff)
            else:
                fr = 0
            of_left = (fr * max_l_pos + (1 - fr) * min_l_pos) / curve[l].x
            of_right = (fr * max_r_pos + (1 - fr) * min_r_pos) / curve[r].x
            l1, l2 = curve[l].split(of_left)
            r1, r2 = curve[r].split(of_right)

            mid1 = []
            if l1.x > 0 or l1.y > 0:
                mid1.append(l1)
            if r2.x > 0 or r2.y > 0:
                mid1.append(r2)
            mid2 = []
            if l2.x > 0 or l2.y > 0:
                mid2.append(l2)
            mid3 = []
            if r1.x > 0 or r1.y > 0:
                mid3.append(r1)

            return (mid2 + curve[l+1:r] + mid3), (curve[:l] + mid1 + curve[r+1:])
        else:
            if x_lleft_rleft - curve[l].x + curve[r].x == segment_x:
                # as long as curve[l].x > 0, will directly satisfy Assertions I & II
                x_lleft_rleft += curve[r].x - curve[l].x
                y_lleft_rleft += curve[r].y - curve[l].y
                l += 1
                r += 1
            elif x_lleft_rleft - curve[l].x + curve[r].x < segment_x:
                # Assume that Assumption I will hold
                # Only weaken Assumption II, which held previously
                x_lleft_rleft += curve[r].x
                y_lleft_rleft += curve[r].y
                r += 1
            else:
                # Assume that Assumption II will hold
                # Only weaken Assumption I, which held previously
                x_lleft_rleft -= curve[l].x
                y_lleft_rleft -= curve[l].y
                l += 1

    raise Exception("This code should not be reachable. Most likely, additional rounding-error mitigation is needed.")


if __name__ == "__main__":
    LS = LineSegment
    assert (repr(reorder_step(1, 1, [LS(.5, .5, (0.0, 0.5)), LS(.5, .5, (.5, 1.))]))
            == "([LineSegment(0.5, 0.5, (0.0, 0.5)), LineSegment(0.5, 0.5, (0.5, 1.0))], [])")
    assert (repr(reorder_step(.5, .5, [LS(.7, .3, (0, 0.5)), LS(.3, .7, (.5, 1.))]))
            == ("([LineSegment(0.35, 0.15, (0.25, 0.5)), LineSegment(0.15, 0.35, (0.5, 0.75))], [LineSegment(0.35, 0.15"
                ", (0, 0.25)), LineSegment(0.15, 0.35, (0.75, 1.0))])"))