using ArgParse
using JSON
using FastWFOMC

function main()
    parser = ArgParseSettings()
    @add_arg_table parser begin
        "instance"
        help = "WFOMC instance (in a custom JSON format)"
        required = true

        "domainsize"
        help = "domain size"
        required = true
        arg_type = Int
    end

    args = parse_args(parser)
    instance_file = args["instance"]
    domainsize = args["domainsize"]

    # Load JSON instance
    instance = JSON.parsefile(instance_file)

    # Parse the formula
    formula = parse_formula(instance["formula"])

    # Parse arities
    arities = Dict{String, Int}([(k, v) for (k, v) in instance["arities"]])

    # Parse cardinalities and weights
    cardinalities = [(x, domainsize * y) for (x, y) in instance["cardinalities"]]
    weights_data = instance["weights"]
    weights = if !isempty(weights_data)
        WFOMCWeights{Rational{BigInt}}([(k, arities[k]) => (v[1], v[2]) for (k, v) in weights_data])
    else
        WFOMCWeights{Rational{BigInt}}()
    end
    fill_missing_weights!(weights, formula)

    # Create cardinality constraints with arities
    ccs = [CardinalityConstraint((x, arities[x]), y) for (x, y) in cardinalities]

    # Compute WFOMC
    count = compute_wfomc(formula, domainsize, weights; ccs=ccs)
    println("WFOMC: ", count)
end

# Run the script
main()
