/**
 * Auto-layout utility using Dagre algorithm for hierarchical graph visualization.
 * 
 * Note: We use 'type' imports for Edge and Node to avoid naming conflicts with
 * the built-in DOM Node type (from @types/node). This ensures TypeScript correctly
 * resolves to ReactFlow's Node type which has the 'id' property.
 */
import dagre from 'dagre';
import { Position, type Edge, type Node } from 'reactflow';

// Standard dimensions for all nodes in the graph
const nodeWidth = 180;
const nodeHeight = 80;

/**
 * Applies hierarchical layout to React Flow nodes and edges using Dagre.
 * 
 * @param nodes - Array of React Flow nodes to layout
 * @param edges - Array of React Flow edges defining connections
 * @returns Object containing layouted nodes with calculated positions and original edges
 */
export const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
    // Initialize Dagre graph instance
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));

    // Configure layout: 'TB' = Top to Bottom (hierarchical/tree layout)
    // Alternative options: 'LR' (Left to Right), 'BT' (Bottom to Top), 'RL' (Right to Left)
    dagreGraph.setGraph({ rankdir: 'TB' });

    // Register all nodes with their dimensions in the Dagre graph
    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });

    // Register all edges (connections) in the Dagre graph
    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });

    // Execute the layout algorithm - this calculates positions for all nodes
    dagre.layout(dagreGraph);

    // Map the calculated positions back to React Flow nodes
    const layoutedNodes = nodes.map((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        return {
            ...node,
            // Configure edge connection points for hierarchical flow
            targetPosition: Position.Top,    // Edges enter from top
            sourcePosition: Position.Bottom, // Edges exit from bottom
            position: {
                // Dagre returns center coordinates, adjust for top-left positioning
                x: nodeWithPosition.x - nodeWidth / 2,
                y: nodeWithPosition.y - nodeHeight / 2,
            },
        };
    });

    return { nodes: layoutedNodes, edges };
};