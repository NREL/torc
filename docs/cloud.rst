###################
Cloud Compute Nodes
###################
We currently do not perform compute node scheduling in cloud environments, but plan to add it soon.

You can install and configure torc in the cloud with a "bring-your-own-nodes" paradigm. If you
configure a workflow in a database accessible from your compute nodes, you can run ``torc local
run-jobs`` from each node to pull and execute jobs.
