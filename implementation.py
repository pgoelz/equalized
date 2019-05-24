EPS = 0.0000005


def get_pos(buckets):
    """Total number of positive agents in list of buckets."""
    s = 0
    for prob, bucket_size in buckets:
        s += prob * bucket_size
    return s


def get_neg(buckets):
    """Total number of negative agents in list of buckets."""
    s = 0
    for prob, bucket_size in buckets:
        s += (1 - prob) * bucket_size
    return s


def get_cardinality(allocation):
    """Total number of agents in list of buckets."""
    s = 0
    for _, amount in allocation:
        s += amount
    return s


def find_intersection(k, group_buckets, this_pos, this_neg, other_pos, other_neg):
    """If other groups are not the bottleneck, optimal number of positive and negative allocations inside given group
    that is achievable.

    Returns: (float, float)
        Pair (x_gross, y_gross). In geometric interpretation, (x_gross/this_pos, y_gross/this_neg) is where the lower
        boundary of the group convex shape intersects the cardinality line.

    Args:
        k (int): desired allocation size, across all groups
        group_buckets (list of (float, int)): list of pairs (prob, bucket size), in decreasing order of prob
        this_pos (float): should equal get_pos(group_buckets)
        this_neg (float): should equal get_neg(group_buckets)
        other_pos (float): should equal sum of get_pos(b) for all other buckets b
        other_neg (float): should equal sum of get_neg(b) for all other buckets b
    """

    x_gross = 0  # = x*this_pos
    y_gross = 0  # = y*this_neg
    for (prob, bucket_size) in group_buckets:
        assert bucket_size > 0
        x_diff = prob * bucket_size
        y_diff = (1 - prob) * bucket_size
        assert x_diff + y_diff > 0

        old_cardinality = (x_gross * (1 + other_pos / this_pos)
                           + y_gross * (1 + other_neg / this_neg))
        cardinality_diff = (x_diff * (1 + other_pos / this_pos)
                            + y_diff * (1 + other_neg / this_neg))
        assert cardinality_diff > 0
        cardinality = old_cardinality + cardinality_diff

        if cardinality <= k:
            x_gross += x_diff
            y_gross += y_diff
        else:
            needed_increase = k - old_cardinality
            x_gross += x_diff * needed_increase / cardinality_diff
            y_gross += y_diff * needed_increase / cardinality_diff

    return x_gross, y_gross


def find_opt_fair(k, buckets_by_group):
    """Find maximally efficient allocation satisfying equalized odds.

    Returns: (list of list of (float, float))
        For each group, the list contains a list of pairs (prob, al) where al is the number of items allocated in
        expectation to the bucket with probability prob.

    Args:
        k (int): desired allocation size
        buckets_by_group (list of list of (float, int)): For each group, the list contains a list of pairs (prob, size)
                                                         where size is the size of the bucket with probability prob, and
                                                         the pairs are ordered in decreasing size of prob.
    """

    poss = [get_pos(buckets) for buckets in buckets_by_group]
    negs = [get_neg(buckets) for buckets in buckets_by_group]

    total_pos = sum(poss)
    total_neg = sum(negs)

    xs = []
    ys = []
    x_grosss = []
    y_grosss = []
    for group_buckets, pos, neg in zip(buckets_by_group, poss, negs):
        x_gross, y_gross = find_intersection(k, group_buckets, pos, neg, total_pos - pos, total_neg - neg)
        x_grosss.append(x_gross)
        y_grosss.append(y_gross)
        xs.append(x_gross / pos)
        ys.append(y_gross / neg)

    x_star = min(xs)
    allocations = []
    for pos, neg, x, y, x_gross, y_gross, group_buckets in zip(poss, negs, xs, ys, x_grosss, y_grosss, buckets_by_group):
        threshold = []
        card = x_gross + y_gross
        rem = card
        for (prob, bucket_size) in group_buckets:
            al = min(rem, bucket_size)
            threshold.append(al)
            rem -= al

        uniform_rate = k / (total_pos + total_neg)
        if x <= uniform_rate + EPS:
            rho = 0
        else:
            rho = (x_star - uniform_rate) / (x - uniform_rate)

        allocation = []
        for (prob, bucket_size), threshold_alloc in zip(group_buckets, threshold):
            allocation.append((prob, rho * threshold_alloc + (1 - rho) * uniform_rate * bucket_size))

        allocations.append(allocation)

    return allocations


def optimal_nonfair_efficiency(k, buckets_by_group):
    rem = k
    efficiency = 0
    all_buckets = [pair for buckets in buckets_by_group for pair in buckets]
    all_buckets.sort(reverse=True)

    for prob, size in all_buckets:
        al = min(rem, size)
        efficiency += prob * al
        rem -= al
        if rem <= EPS:
            return efficiency
    if rem >= EPS:
        raise ValueError(f"k={k} is larger than total number of agents.")
    return efficiency


def plot_convex_shape(group_buckets, color):
    pos = get_pos(group_buckets)
    neg = get_neg(group_buckets)

    points = [(0., 0.)]
    for prob, size in group_buckets:
        x_last, y_last = points[-1]
        x = x_last + prob * size / pos
        y = y_last + (1 - prob) * size / neg
        points.append((x, y))
    for prob, size in group_buckets:
        x_last, y_last = points[-1]
        x = x_last - prob * size / pos
        y = y_last - (1 - prob) * size / neg
        points.append((x, y))

    points_text = [f"({x}, {y})" for x, y in points]

    return f"\\addplot [fill={color},fill opacity=.2,very thick,draw={color}] coordinates {{{' '.join(points_text)}}};"


def plot_cardinality_line(k, total_pos, total_neg):
    return f"\\addplot [c2,very thick] {{{k/total_neg} - {total_pos / total_neg}*x}};"