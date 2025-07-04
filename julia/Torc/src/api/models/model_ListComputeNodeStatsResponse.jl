# This file was generated by the Julia OpenAPI Code Generator
# Do not modify this file directly. Modify the OpenAPI specification instead.


@doc raw"""list_compute_node_stats_response

    ListComputeNodeStatsResponse(;
        items=nothing,
        skip=nothing,
        max_limit=nothing,
        count=nothing,
        total_count=nothing,
        has_more=nothing,
    )

    - items::Vector{ComputeNodeStatsModel}
    - skip::Int64
    - max_limit::Int64
    - count::Int64
    - total_count::Int64
    - has_more::Bool
"""
Base.@kwdef mutable struct ListComputeNodeStatsResponse <: OpenAPI.APIModel
    items::Union{Nothing, Vector} = nothing # spec type: Union{ Nothing, Vector{ComputeNodeStatsModel} }
    skip::Union{Nothing, Int64} = nothing
    max_limit::Union{Nothing, Int64} = nothing
    count::Union{Nothing, Int64} = nothing
    total_count::Union{Nothing, Int64} = nothing
    has_more::Union{Nothing, Bool} = nothing

    function ListComputeNodeStatsResponse(items, skip, max_limit, count, total_count, has_more, )
        o = new(items, skip, max_limit, count, total_count, has_more, )
        OpenAPI.validate_properties(o)
        return o
    end
end # type ListComputeNodeStatsResponse

const _property_types_ListComputeNodeStatsResponse = Dict{Symbol,String}(Symbol("items")=>"Vector{ComputeNodeStatsModel}", Symbol("skip")=>"Int64", Symbol("max_limit")=>"Int64", Symbol("count")=>"Int64", Symbol("total_count")=>"Int64", Symbol("has_more")=>"Bool", )
OpenAPI.property_type(::Type{ ListComputeNodeStatsResponse }, name::Symbol) = Union{Nothing,eval(Base.Meta.parse(_property_types_ListComputeNodeStatsResponse[name]))}

function OpenAPI.check_required(o::ListComputeNodeStatsResponse)
    o.skip === nothing && (return false)
    o.max_limit === nothing && (return false)
    o.count === nothing && (return false)
    o.total_count === nothing && (return false)
    o.has_more === nothing && (return false)
    true
end

function OpenAPI.validate_properties(o::ListComputeNodeStatsResponse)
    OpenAPI.validate_property(ListComputeNodeStatsResponse, Symbol("items"), o.items)
    OpenAPI.validate_property(ListComputeNodeStatsResponse, Symbol("skip"), o.skip)
    OpenAPI.validate_property(ListComputeNodeStatsResponse, Symbol("max_limit"), o.max_limit)
    OpenAPI.validate_property(ListComputeNodeStatsResponse, Symbol("count"), o.count)
    OpenAPI.validate_property(ListComputeNodeStatsResponse, Symbol("total_count"), o.total_count)
    OpenAPI.validate_property(ListComputeNodeStatsResponse, Symbol("has_more"), o.has_more)
end

function OpenAPI.validate_property(::Type{ ListComputeNodeStatsResponse }, name::Symbol, val)






end
