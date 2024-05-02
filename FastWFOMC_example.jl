using FastWFOMC

formula = parse_formula(
    "~E(x, x) & " *
    "(~E(x, y) | E(y, x)) & " *
    "(~F(x, y) | E(x, y)) & " *
    "(F(x, y) | ~E(x, y)) & " *
    "(S1(x) | ~F1(x, y)) & " *
    "(S2(x) | ~F2(x, y)) & " *
    "(S3(x) | ~F3(x, y)) & " *
    "(~F(x, y) | F1(x, y) | F2(x, y) | F3(x, y)) & " *
    "(F(x, y) | ~F1(x, y)) & " *
    "(F(x, y) | ~F2(x, y)) & " *
    "(F(x, y) | ~F3(x, y)) & " *
    "(~F1(x, y) | ~F2(x, y)) & " *
    "(~F1(x, y) | ~F3(x, y)) & " *
    "(~F2(x, y) | ~F3(x, y))"
);

n = 6
weights = WFOMCWeights{Rational{BigInt}}(("S1", 1) => (1, -1), ("S2", 1) => (1, -1), ("S3", 1) => (1, -1))
fill_missing_weights!(weights, formula)

count = compute_wfomc(formula, n, weights; ccs=[CardinalityConstraint(("F", 2), 3n)])
@show(count)
