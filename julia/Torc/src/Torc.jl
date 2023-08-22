module Torc

include("api/APIClient.jl")
include("workflow_builder.jl")
import OpenAPI
import .APIClient

function make_api(database_url::AbstractString)
    """Instantiate an OpenAPI object from a database URL."""
    return APIClient.DefaultApi(OpenAPI.Clients.Client(database_url))
end

export make_api
export WorkflowBuilder
export add_file!
export add_job!
export add_aws_scheduler!
export add_local_scheduler!
export add_slurm_scheduler!
export add_resource_requirements!
export add_user_data!
export configure_resource_monitoring!
export build!

end # module Torc
