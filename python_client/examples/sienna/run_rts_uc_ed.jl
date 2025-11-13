using PowerSystems
using PowerSimulations
using HydroPowerSimulations
const PSI = PowerSimulations
using PowerSystemCaseBuilder
using Dates
using Ipopt #solver
using HiGHS
using HSL

import Logging

function build_simulation(
    output_dir::AbstractString,
    simulation_name::AbstractString,
    partitions::SimulationPartitions,
    index::Union{Nothing, Integer} = nothing,
)
    solver = optimizer_with_attributes(HiGHS.Optimizer, "mip_rel_gap" => 0.5)

    sys_DA = build_system(PSISystems, "modified_RTS_GMLC_DA_sys"; skip_serialization = true)
    sys_RT = build_system(PSISystems, "modified_RTS_GMLC_RT_sys"; skip_serialization = true)

    template_uc = template_unit_commitment(;
        network = NetworkModel(CopperPlatePowerModel; use_slacks = true),
    )
    set_device_model!(template_uc, ThermalStandard, ThermalStandardUnitCommitment)
    set_device_model!(template_uc, HydroDispatch, HydroDispatchRunOfRiver)

    template_ed = template_economic_dispatch(;
        network = NetworkModel(CopperPlatePowerModel; use_slacks = true),
    )
    empty!(template_ed.services)
    models = SimulationModels(;
        decision_models = [
            DecisionModel(template_uc, sys_DA; optimizer = solver, name = "UC"),
            DecisionModel(template_ed, sys_RT; optimizer = solver, name = "ED"),
        ],
    )
    feedforward = Dict(
        "ED" => [
            SemiContinuousFeedforward(;
                component_type = ThermalStandard,
                source = OnVariable,
                affected_values = [ActivePowerVariable],
            ),
        ],
    )
    DA_RT_sequence = SimulationSequence(;
        models = models,
        ini_cond_chronology = InterProblemChronology(),
        feedforwards = feedforward,
    )

    sim = Simulation(;
        name = simulation_name,
        steps = partitions.num_steps,
        models = models,
        sequence = DA_RT_sequence,
        simulation_folder = output_dir,
    )

    status = build!(
        sim;
        index = index,
        partitions = partitions,
        serialize = isnothing(index),
        console_level = Logging.Info,
        file_level = Logging.Info,
    )
    if status != PowerSimulations.SimulationBuildStatus.BUILT
        error("failed to build: $status")
    end
    return sim
end

function execute_simulation(sim, args...; kwargs...)
    println("running execute_simulation args = $(args) kwargs = $(kwargs)")
    status = execute!(sim)
    if status != PSI.RunStatus.SUCCESSFULLY_FINALIZED
        error("Simulation failed to execute: status=$status")
    end
end

#results = SimulationResults(sim);
#uc_results = get_decision_problem_results(results, "UC"); # UC stage result metadata
#ed_results = get_decision_problem_results(results, "ED"); # ED stage result metadata
#
#
#read_variables(uc_results)
#read_parameters(uc_results)
#
function main()
    process_simulation_partition_cli_args(build_simulation, execute_simulation, ARGS...)
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
