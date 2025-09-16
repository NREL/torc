# HPC

The default Torc-Slurm integration behavior is different than many users' typical Slurm workflow.

Slurm encourages you to schedule all of your compute nodes in one job and then use its CLI tools
(like `srun`) to distribute your jobs across the compute resources in the allocation. A
limitation of this paradigm is that you can't begin any jobs until all compute nodes are
available. This is fine if you only need five nodes. It may not work out as well if you need 1000
nodes.

The default Torc behavior is to acquire compute nodes in independent Slurm jobs. You can begin
running jobs as soon as the first compute node is available.

Slurm provides its `job arrays` feature to easily distribute jobs across resources. It does have
a pre-requisite, however: all jobs need to use similar compute resources (CPU / memory).

The default Torc behavior allows active compute nodes to run available jobs that meet their
current resource constraints.
