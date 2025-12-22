use petgraph::graph::{DiGraph, NodeIndex};
use petgraph::visit::EdgeRef;
use std::collections::HashMap;

#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct JobNode {
    pub id: i64,
    pub name: String,
    pub status: Option<String>,
}

pub struct DagLayout {
    pub graph: DiGraph<JobNode, ()>,
    pub positions: HashMap<NodeIndex, (f64, f64)>,
    pub width: f64,
    pub height: f64,
}

impl DagLayout {
    pub fn new() -> Self {
        Self {
            graph: DiGraph::new(),
            positions: HashMap::new(),
            width: 0.0,
            height: 0.0,
        }
    }

    pub fn add_node(&mut self, job: JobNode) -> NodeIndex {
        self.graph.add_node(job)
    }

    pub fn add_edge(&mut self, from: NodeIndex, to: NodeIndex) {
        self.graph.add_edge(from, to, ());
    }

    /// Compute a layered (Sugiyama-style) layout for the DAG
    pub fn compute_layout(&mut self) {
        // Step 1: Topological sort to determine layers
        let layers = self.compute_layers();

        // Step 2: Assign positions based on layers
        self.assign_positions(&layers);
    }

    fn compute_layers(&self) -> Vec<Vec<NodeIndex>> {
        use petgraph::visit::Topo;

        let mut layers: Vec<Vec<NodeIndex>> = Vec::new();
        let mut node_layer: HashMap<NodeIndex, usize> = HashMap::new();

        // Topological traversal
        let mut topo = Topo::new(&self.graph);
        while let Some(node) = topo.next(&self.graph) {
            // Find the maximum layer of all predecessors
            let mut max_predecessor_layer = 0;
            for edge in self
                .graph
                .edges_directed(node, petgraph::Direction::Incoming)
            {
                if let Some(&layer) = node_layer.get(&edge.source()) {
                    max_predecessor_layer = max_predecessor_layer.max(layer + 1);
                }
            }

            node_layer.insert(node, max_predecessor_layer);

            // Add to appropriate layer
            while layers.len() <= max_predecessor_layer {
                layers.push(Vec::new());
            }
            layers[max_predecessor_layer].push(node);
        }

        // Sort nodes within each layer to group related subgraphs together
        // Group by their parent nodes to keep subgraphs visually connected
        for layer in &mut layers {
            layer.sort_by(|a, b| {
                // Get predecessor indices as sort keys
                let a_preds: Vec<usize> = self
                    .graph
                    .edges_directed(*a, petgraph::Direction::Incoming)
                    .map(|e| e.source().index())
                    .collect();
                let b_preds: Vec<usize> = self
                    .graph
                    .edges_directed(*b, petgraph::Direction::Incoming)
                    .map(|e| e.source().index())
                    .collect();

                // Sort by first predecessor, then by job name for consistency
                match (a_preds.first(), b_preds.first()) {
                    (Some(a_pred), Some(b_pred)) => a_pred.cmp(b_pred).then_with(|| {
                        let a_name = &self.graph[*a].name;
                        let b_name = &self.graph[*b].name;
                        a_name.cmp(b_name)
                    }),
                    (Some(_), None) => std::cmp::Ordering::Less,
                    (None, Some(_)) => std::cmp::Ordering::Greater,
                    (None, None) => {
                        let a_name = &self.graph[*a].name;
                        let b_name = &self.graph[*b].name;
                        a_name.cmp(b_name)
                    }
                }
            });
        }

        layers
    }

    fn assign_positions(&mut self, layers: &[Vec<NodeIndex>]) {
        let layer_height = 8.0; // Vertical spacing between layers
        let node_width = 3.0; // Horizontal spacing between nodes

        self.height = layers.len() as f64 * layer_height;

        for (layer_idx, layer_nodes) in layers.iter().enumerate() {
            let layer_width = layer_nodes.len() as f64 * node_width;
            self.width = self.width.max(layer_width);

            let y = layer_idx as f64 * layer_height;

            for (node_idx, &node) in layer_nodes.iter().enumerate() {
                let x = node_idx as f64 * node_width;
                self.positions.insert(node, (x, y));
            }
        }
    }

    /// Get node position in normalized coordinates [0, 1]
    #[allow(dead_code)]
    pub fn get_normalized_position(&self, node: NodeIndex) -> Option<(f64, f64)> {
        self.positions.get(&node).map(|&(x, y)| {
            let norm_x = if self.width > 0.0 {
                x / self.width
            } else {
                0.5
            };
            let norm_y = if self.height > 0.0 {
                y / self.height
            } else {
                0.5
            };
            (norm_x, norm_y)
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_dag() {
        let mut dag = DagLayout::new();

        let n1 = dag.add_node(JobNode {
            id: 1,
            name: "Job 1".to_string(),
            status: Some("completed".to_string()),
        });

        let n2 = dag.add_node(JobNode {
            id: 2,
            name: "Job 2".to_string(),
            status: Some("running".to_string()),
        });

        let n3 = dag.add_node(JobNode {
            id: 3,
            name: "Job 3".to_string(),
            status: Some("pending".to_string()),
        });

        dag.add_edge(n1, n2);
        dag.add_edge(n2, n3);

        dag.compute_layout();

        assert!(dag.positions.contains_key(&n1));
        assert!(dag.positions.contains_key(&n2));
        assert!(dag.positions.contains_key(&n3));
    }
}
