# This file was generated by the Julia OpenAPI Code Generator
# Do not modify this file directly. Modify the OpenAPI specification instead.


@doc raw"""compute_node_model

    ComputeNodeModel(;
        hostname=nothing,
        pid=nothing,
        start_time=nothing,
        duration_seconds=nothing,
        is_active=nothing,
        resources=nothing,
        scheduler=nothing,
        _key=nothing,
        _id=nothing,
        _rev=nothing,
    )

    - hostname::String
    - pid::Int64
    - start_time::String
    - duration_seconds::Float64
    - is_active::Bool
    - resources::ComputeNodesResources
    - scheduler::Any
    - _key::String
    - _id::String
    - _rev::String
"""
Base.@kwdef mutable struct ComputeNodeModel <: OpenAPI.APIModel
    hostname::Union{Nothing, String} = nothing
    pid::Union{Nothing, Int64} = nothing
    start_time::Union{Nothing, String} = nothing
    duration_seconds::Union{Nothing, Float64} = nothing
    is_active::Union{Nothing, Bool} = nothing
    resources = nothing # spec type: Union{ Nothing, ComputeNodesResources }
    scheduler::Union{Nothing, Any} = nothing
    _key::Union{Nothing, String} = nothing
    _id::Union{Nothing, String} = nothing
    _rev::Union{Nothing, String} = nothing

    function ComputeNodeModel(hostname, pid, start_time, duration_seconds, is_active, resources, scheduler, _key, _id, _rev, )
        o = new(hostname, pid, start_time, duration_seconds, is_active, resources, scheduler, _key, _id, _rev, )
        OpenAPI.validate_properties(o)
        return o
    end
end # type ComputeNodeModel

const _property_types_ComputeNodeModel = Dict{Symbol,String}(Symbol("hostname")=>"String", Symbol("pid")=>"Int64", Symbol("start_time")=>"String", Symbol("duration_seconds")=>"Float64", Symbol("is_active")=>"Bool", Symbol("resources")=>"ComputeNodesResources", Symbol("scheduler")=>"Any", Symbol("_key")=>"String", Symbol("_id")=>"String", Symbol("_rev")=>"String", )
OpenAPI.property_type(::Type{ ComputeNodeModel }, name::Symbol) = Union{Nothing,eval(Base.Meta.parse(_property_types_ComputeNodeModel[name]))}

function OpenAPI.check_required(o::ComputeNodeModel)
    o.hostname === nothing && (return false)
    o.pid === nothing && (return false)
    o.start_time === nothing && (return false)
    o.resources === nothing && (return false)
    true
end

function OpenAPI.validate_properties(o::ComputeNodeModel)
    OpenAPI.validate_property(ComputeNodeModel, Symbol("hostname"), o.hostname)
    OpenAPI.validate_property(ComputeNodeModel, Symbol("pid"), o.pid)
    OpenAPI.validate_property(ComputeNodeModel, Symbol("start_time"), o.start_time)
    OpenAPI.validate_property(ComputeNodeModel, Symbol("duration_seconds"), o.duration_seconds)
    OpenAPI.validate_property(ComputeNodeModel, Symbol("is_active"), o.is_active)
    OpenAPI.validate_property(ComputeNodeModel, Symbol("resources"), o.resources)
    OpenAPI.validate_property(ComputeNodeModel, Symbol("scheduler"), o.scheduler)
    OpenAPI.validate_property(ComputeNodeModel, Symbol("_key"), o._key)
    OpenAPI.validate_property(ComputeNodeModel, Symbol("_id"), o._id)
    OpenAPI.validate_property(ComputeNodeModel, Symbol("_rev"), o._rev)
end

function OpenAPI.validate_property(::Type{ ComputeNodeModel }, name::Symbol, val)










end
