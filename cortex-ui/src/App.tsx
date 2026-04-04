/**
 * Project Cortex - Multi-View Graph Visualization with Custom Infrastructure Nodes
 * 
 * Features:
 * - Three view modes: LOGICAL (C4 architecture), PHYSICAL (infrastructure), ALL (complete graph)
 * - Custom infrastructure nodes with multiple connection handles for inverted hierarchy
 * - Smart edge routing based on relationship types and node kinds
 * - Client-side filtering for performance (fetch once, filter on demand)
 * - Hierarchical auto-layout using Dagre algorithm
 */
import { useCallback, useEffect, useState, useRef, useMemo } from 'react';
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  Panel,
  MarkerType,
} from 'reactflow';
import axios from 'axios';
import 'reactflow/dist/style.css';

import { getLayoutedElements } from './layout';
import InfraNode from './infranode';

/**
 * Custom node type registry
 * INFRA_RESOURCE nodes use the InfraNode component with multiple connection handles
 * Other node types (PLATFORM, SYSTEM, CONTAINER) use default React Flow nodes
 */
const nodeTypes = {
  INFRA_RESOURCE: InfraNode,
};

/**
 * Color scheme for standard (non-infrastructure) nodes
 * Infrastructure nodes handle their own styling in the InfraNode component
 */
const colors: Record<string, string> = {
  PLATFORM: '#ffecd1',  // Light orange - highest abstraction
  SYSTEM: '#d1e8ff',    // Light blue - system boundaries
  CONTAINER: '#d1ffdb', // Light green - deployable units
};

/**
 * View modes control which nodes and edges are visible:
 * - LOGICAL: Software architecture view (hides infrastructure)
 * - PHYSICAL: Infrastructure deployment view (hides abstract groupings)
 * - ALL: Complete graph with all nodes and relationships
 */
type ViewMode = 'LOGICAL' | 'PHYSICAL' | 'ALL';

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [viewMode, setViewMode] = useState<ViewMode>('ALL');

  // Cache full graph data to enable fast client-side filtering without re-fetching
  const fullGraphData = useRef<{ nodes: any[], edges: any[] }>({ nodes: [], edges: [] });

  /**
   * Fetches the complete graph from the backend API.
   * Called once on component mount.
   */
  const fetchGraph = async () => {
    try {
      const response = await axios.get('http://localhost:3000/api/v1/graph');
      const { nodes: rawNodes, relationships: rawRels } = response.data;

      /**
       * Build a map of CONTAINS relationships for parent-child nesting.
       * Key: child node ID, Value: parent node ID
       */
      const containsMap = new Map<string, string>();
      rawRels.forEach((r: any) => {
        if (r.type === 'CONTAINS') {
          // r.start CONTAINS r.end -> r.start is parent, r.end is child
          containsMap.set(r.end, r.start);
        }
      });

      /**
       * Transform Neo4j nodes into React Flow format with parent-child relationships.
       * Nodes with CONTAINS relationships will be nested visually (box-within-box).
       */
      const allNodes = rawNodes.map((n: any) => {
        const isInfra = n.properties.kind === 'INFRA_RESOURCE';
        const parentId = containsMap.get(n.properties.id);

        // Determine if this node is a parent (contains other nodes)
        const isParent = rawRels.some((r: any) => r.type === 'CONTAINS' && r.start === n.properties.id);

        return {
          id: n.properties.id,
          type: isInfra ? 'INFRA_RESOURCE' : 'default',
          // Set parent reference for nested visualization
          parentNode: parentId,
          // Constrain child nodes to stay within parent bounds
          extent: parentId ? 'parent' as const : undefined,
          data: {
            label: `${n.properties.kind}\n${n.properties.name}`,
            kind: n.properties.kind,
            name: n.properties.name,
            isParent: isParent  // Used for styling parent nodes differently
          },
          // Parent nodes need larger dimensions and different styling
          style: !isInfra ? {
            background: colors[n.properties.kind] || '#fff',
            border: '1px solid #777',
            fontSize: 12,
            width: isParent ? 300 : 180,
            height: isParent ? 200 : undefined,
            borderRadius: 5,
            padding: isParent ? '40px 20px 20px 20px' : undefined,
          } : {
            // Infrastructure parent nodes
            width: isParent ? 350 : 200,
            height: isParent ? 250 : undefined,
            padding: isParent ? '40px 20px 20px 20px' : undefined,
          },
          position: { x: 0, y: 0 }  // Will be calculated by layout algorithm
        };
      });

      /**
       * Filter out CONTAINS edges - these are now represented by parent-child nesting.
       * Keep only non-containment relationships (HOSTED_ON, PROTECTS, ROUTES_TO, etc.)
       */
      const allEdges = rawRels
        .filter((r: any) => r.type !== 'CONTAINS')  // Remove CONTAINS edges
        .map((r: any) => {
          let targetHandle = null;
          let sourceHandle = null;

          // Check if target node is infrastructure
          const targetIsInfra = rawNodes.find((n: any) => n.properties.id === r.end)?.properties.kind === 'INFRA_RESOURCE';

          if (targetIsInfra) {
            if (r.type === 'HOSTED_ON') {
              // Software components connect to top of infrastructure nodes
              targetHandle = 'target-top';
            } else if (r.type === 'PROTECTS' || r.type === 'ROUTES_TO') {
              // Other infrastructure relationships
              targetHandle = 'target-bottom';
            }
            // Infrastructure nodes emit connections from their top handle
            sourceHandle = 'source-top';
          }

          return {
            id: `e-${r.start}-${r.end}`,
            source: r.start,
            target: r.end,
            label: r.type,
            type: 'smoothstep',
            markerEnd: { type: MarkerType.ArrowClosed },
            animated: r.type === 'HOSTED_ON',
            sourceHandle: sourceHandle,
            targetHandle: targetHandle
          };
        });

      fullGraphData.current = { nodes: allNodes, edges: allEdges };
      applyFilterAndLayout('ALL', allNodes, allEdges);

    } catch (error) {
      console.error("Failed to fetch graph", error);
    }
  };

  const applyFilterAndLayout = (mode: ViewMode, nodesSource: any[], edgesSource: any[]) => {
    let filteredNodes = [];
    let filteredEdges = [];

    if (mode === 'ALL') {
      filteredNodes = nodesSource;
      filteredEdges = edgesSource;
    } else if (mode === 'LOGICAL') {
      // Filter out Infrastructure nodes
      filteredNodes = nodesSource.filter(n => n.data.kind !== 'INFRA_RESOURCE');
      filteredEdges = edgesSource.filter(e => e.label !== 'HOSTED_ON');
    } else if (mode === 'PHYSICAL') {
      // Show Infrastructure and Containers
      filteredNodes = nodesSource.filter(n =>
        n.data.kind === 'INFRA_RESOURCE' || n.data.kind === 'CONTAINER'
      );

      // Filter edges to only include those between visible nodes
      const validNodeIds = new Set(filteredNodes.map(n => n.id));
      filteredEdges = edgesSource.filter(e =>
        validNodeIds.has(e.source) && validNodeIds.has(e.target)
      );
    }

    // CRITICAL FIX: Clean up parentNode references if the parent is filtered out
    // This prevents "orphaned" nodes from disappearing or rendering incorrectly
    const validNodeIds = new Set(filteredNodes.map(n => n.id));
    filteredNodes = filteredNodes.map(node => {
      // If the node has a parent, but that parent is NOT in the filtered set...
      if (node.parentNode && !validNodeIds.has(node.parentNode)) {
        // ...detach it so it renders as a top-level node
        return {
          ...node,
          parentNode: undefined,
          extent: undefined,
          position: { x: 0, y: 0 } // Reset position to be safe
        };
      }
      return node;
    });

    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
      filteredNodes,
      filteredEdges
    );

    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  };

  const handleModeChange = (mode: ViewMode) => {
    setViewMode(mode);
    applyFilterAndLayout(mode, fullGraphData.current.nodes, fullGraphData.current.edges);
  };

  useEffect(() => {
    fetchGraph();
  }, []);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const btnStyle = (mode: ViewMode) => ({
    padding: '8px 16px',
    marginRight: '5px',
    cursor: 'pointer',
    backgroundColor: viewMode === mode ? '#333' : '#fff',
    color: viewMode === mode ? '#fff' : '#333',
    border: '1px solid #333',
    borderRadius: '4px',
    fontWeight: 'bold' as const
  });

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes} // Register custom node
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Controls />
        <Background color="#aaa" gap={16} />
        <Panel position="top-center">
          <div style={{ background: 'rgba(255,255,255,0.8)', padding: 10, borderRadius: 8 }}>
            <span style={{ marginRight: 10, fontWeight: 'bold' }}>View Mode:</span>
            <button style={btnStyle('LOGICAL')} onClick={() => handleModeChange('LOGICAL')}>Logical</button>
            <button style={btnStyle('PHYSICAL')} onClick={() => handleModeChange('PHYSICAL')}>Physical</button>
            <button style={btnStyle('ALL')} onClick={() => handleModeChange('ALL')}>Full</button>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}