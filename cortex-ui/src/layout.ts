/**
 * Auto-layout utility using Dagre algorithm for hierarchical graph visualization.
 * 
 * This module handles the automatic positioning of nodes in a hierarchical layout,
 * with special support for inverted infrastructure hierarchies where child nodes
 * appear above their parents.
 * 
 * Note: We use 'type' imports for Edge and Node to avoid naming conflicts with
 * the built-in DOM Node type (from @types/node).
 */
import dagre from 'dagre';
import { type Node, type Edge, Position } from 'reactflow';

// Node dimensions used by the layout algorithm
const nodeWidth = 200;
const nodeHeight = 80;

/**
 * Applies hierarchical layout to React Flow nodes and edges using Dagre.
 * 
 * Features:
 * - Top-to-bottom hierarchical layout
 * - Inverted hierarchy support for infrastructure (children above parents)
 * - Configurable spacing between nodes and ranks
 * - Compound node support (nested nodes)
 * 
 * @param nodes - Array of React Flow nodes to layout
 * @param edges - Array of React Flow edges defining connections
 * @returns Object containing layouted nodes with calculated positions and original edges
 */
export const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
    // Initialize Dagre graph instance with compound support
    const dagreGraph = new dagre.graphlib.Graph({ compound: true });
    dagreGraph.setDefaultEdgeLabel(() => ({}));

    // Configure layout algorithm
    // rankdir: 'TB' = Top to Bottom
    // ranksep: Vertical spacing between ranks (levels)
    // nodesep: Horizontal spacing between nodes on the same rank
    dagreGraph.setGraph({ rankdir: 'TB', ranksep: 80, nodesep: 50 });

    // Register all nodes with their dimensions
    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });

        // Register parent-child relationship for compound layout
        if (node.parentNode) {
            dagreGraph.setParent(node.id, node.parentNode);
        }
    });

    /**
     * Register edges with special handling for infrastructure hierarchy.
     * 
     * For infrastructure CONTAINS relationships, we invert the edge direction
     * in the layout algorithm (but not in the visual rendering) to achieve
     * an inverted hierarchy where:
     * - EC2 Instance appears at the top
     * - VPC appears in the middle
     * - AWS Region appears at the bottom
     * 
     * This creates a more intuitive visualization where detailed resources
     * are shown above their containing infrastructure.
     */
    edges.forEach((edge) => {
        const sourceNode = nodes.find((n) => n.id === edge.source);

        // Detect infrastructure hierarchy edges that should be inverted
        const isInfraHierarchy =
            sourceNode?.data?.kind === 'INFRA_RESOURCE' &&
            edge.label === 'CONTAINS';  // e.g., Region CONTAINS VPC

        if (isInfraHierarchy) {
            // Invert the edge for layout calculation (child above parent)
            dagreGraph.setEdge(edge.target, edge.source);
        } else {
            // Normal edge direction
            dagreGraph.setEdge(edge.source, edge.target);
        }
    });

    // Execute the layout algorithm - calculates positions for all nodes
    dagre.layout(dagreGraph);

    // Map calculated positions back to React Flow nodes
    const layoutedNodes = nodes.map((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);

        // Dagre gives global coordinates (center x, center y) for all nodes.
        // React Flow expects:
        // - Top-level nodes: Global coordinates (top-left x, top-left y)
        // - Child nodes: Relative coordinates to parent (top-left x, top-left y)

        let position = {
            x: nodeWithPosition.x - nodeWidth / 2,
            y: nodeWithPosition.y - nodeHeight / 2,
        };

        // If node has a parent, convert global Dagre coordinates to relative React Flow coordinates
        if (node.parentNode) {
            const parentNode = dagreGraph.node(node.parentNode);
            if (parentNode) {
                // Calculate parent's top-left corner in global space
                const parentX = parentNode.x - parentNode.width / 2;
                const parentY = parentNode.y - parentNode.height / 2;

                // Relative position = Child Global - Parent Global
                position = {
                    x: position.x - parentX,
                    y: position.y - parentY
                };
            }
        }

        return {
            ...node,
            // Default connection positions (custom nodes can override with specific handles)
            targetPosition: Position.Top,
            sourcePosition: Position.Bottom,
            position: position,
            // Update dimensions if Dagre calculated new ones (e.g. for parents)
            style: {
                ...node.style,
                // Use Dagre's calculated dimensions if available, otherwise keep original
                width: nodeWithPosition.width || node.style?.width,
                height: nodeWithPosition.height || node.style?.height
            }
        };
    });

    return { nodes: layoutedNodes, edges };
};