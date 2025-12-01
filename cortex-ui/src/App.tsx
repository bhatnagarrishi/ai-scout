/**
 * Project Cortex - Multi-View Graph Visualization
 * 
 * This component provides three different views of the system architecture:
 * 1. LOGICAL (C4): Shows high-level architecture (Platforms, Systems, Containers)
 * 2. PHYSICAL (Infra): Shows infrastructure and deployment (Containers, Infrastructure Resources)
 * 3. ALL (Full Trace): Shows complete graph with all nodes and relationships
 * 
 * The component fetches data once and applies client-side filtering for performance.
 */
import { useCallback, useEffect, useState, useRef } from 'react';
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

// Color scheme for different node types (C4 model inspired)
const colors: Record<string, string> = {
  PLATFORM: '#ffecd1',
  SYSTEM: '#d1e8ff',
  CONTAINER: '#d1ffdb',
  INFRA_RESOURCE: '#e0e0e0'
};

type ViewMode = 'LOGICAL' | 'PHYSICAL' | 'ALL';

export default function App() {
  // React Flow state management
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [viewMode, setViewMode] = useState<ViewMode>('ALL');

  // Cache the full graph data to enable fast client-side filtering without re-fetching
  const fullGraphData = useRef<{ nodes: any[], edges: any[] }>({ nodes: [], edges: [] });

  /**
   * Fetches the complete graph from the backend API.
   * This is called once on component mount.
   */
  const fetchGraph = async () => {
    try {
      const response = await axios.get('http://localhost:3000/api/v1/graph');
      const { nodes: rawNodes, relationships: rawRels } = response.data;

      // Transform API -> Internal Format
      const allNodes = rawNodes.map((n: any) => ({
        id: n.properties.id,
        // We add 'kind' to data so we can filter by it easily later
        data: {
          label: `${n.properties.kind}\n${n.properties.name}`,
          kind: n.properties.kind
        },
        style: {
          background: colors[n.properties.kind] || '#fff',
          border: '1px solid #777',
          fontSize: 12,
          width: 180,
          borderRadius: 5
        },
        position: { x: 0, y: 0 }
      }));

      // Transform Neo4j relationships into React Flow edges
      const allEdges = rawRels.map((r: any) => ({
        id: `e-${r.start}-${r.end}`,
        source: r.start,
        target: r.end,
        label: r.type,  // Relationship type: CONTAINS, HOSTED_ON, etc.
        type: 'smoothstep',
        markerEnd: { type: MarkerType.ArrowClosed },
        animated: r.type === 'HOSTED_ON'  // Visual emphasis for infrastructure relationships
      }));

      // Cache the complete graph for client-side filtering
      fullGraphData.current = { nodes: allNodes, edges: allEdges };

      // Render initial view (all nodes)
      applyFilterAndLayout('ALL', allNodes, allEdges);

    } catch (error) {
      console.error("Failed to fetch graph", error);
    }
  };

  /**
   * Core filtering and layout engine.
   * Pipeline: Filter nodes/edges by view mode -> Apply layout algorithm -> Update state
   * 
   * @param mode - The view mode to apply
   * @param nodesSource - Source nodes to filter from
   * @param edgesSource - Source edges to filter from
   */
  const applyFilterAndLayout = (mode: ViewMode, nodesSource: any[], edgesSource: any[]) => {
    let filteredNodes = [];
    let filteredEdges = [];

    if (mode === 'ALL') {
      // Full Trace: Show everything
      filteredNodes = nodesSource;
      filteredEdges = edgesSource;
    }
    else if (mode === 'LOGICAL') {
      // C4-style logical architecture view
      // Show: PLATFORM, SYSTEM, CONTAINER (software architecture)
      // Hide: INFRA_RESOURCE (infrastructure details)
      filteredNodes = nodesSource.filter(n => n.data.kind !== 'INFRA_RESOURCE');

      // Hide infrastructure relationships (HOSTED_ON) to focus on logical containment
      filteredEdges = edgesSource.filter(e => e.label !== 'HOSTED_ON');
    }
    else if (mode === 'PHYSICAL') {
      // Infrastructure deployment view
      // Show: CONTAINER, INFRA_RESOURCE (what runs where)
      // Hide: PLATFORM, SYSTEM (abstract groupings)
      filteredNodes = nodesSource.filter(n =>
        n.data.kind === 'INFRA_RESOURCE' || n.data.kind === 'CONTAINER'
      );

      // Only show edges between visible nodes (removes orphaned edges)
      const validNodeIds = new Set(filteredNodes.map(n => n.id));
      filteredEdges = edgesSource.filter(e =>
        validNodeIds.has(e.source) && validNodeIds.has(e.target)
      );
    }

    // Apply hierarchical layout algorithm to the filtered graph
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
      filteredNodes,
      filteredEdges
    );

    // Update React Flow state to trigger re-render
    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  };

  /**
   * Handles view mode changes from UI buttons.
   * Re-filters and re-layouts the cached graph data.
   */
  const handleModeChange = (mode: ViewMode) => {
    setViewMode(mode);
    applyFilterAndLayout(mode, fullGraphData.current.nodes, fullGraphData.current.edges);
  };

  // Fetch graph data on component mount
  useEffect(() => {
    fetchGraph();
  }, []);

  // Allow users to manually create edges in the UI (optional feature)
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  /**
   * Dynamic button styles - highlights the active view mode
   */
  const btnStyle = (mode: ViewMode) => ({
    padding: '8px 16px',
    marginRight: '5px',
    cursor: 'pointer',
    backgroundColor: viewMode === mode ? '#333' : '#fff',  // Dark when active
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
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Controls />
        <Background color="#aaa" gap={16} />

        {/* View Mode Selector Panel */}
        <Panel position="top-center">
          <div style={{ background: 'rgba(255,255,255,0.8)', padding: 10, borderRadius: 8 }}>
            <span style={{ marginRight: 10, fontWeight: 'bold' }}>View Mode:</span>
            <button style={btnStyle('LOGICAL')} onClick={() => handleModeChange('LOGICAL')}>
              Logical (C4)
            </button>
            <button style={btnStyle('PHYSICAL')} onClick={() => handleModeChange('PHYSICAL')}>
              Physical (Infra)
            </button>
            <button style={btnStyle('ALL')} onClick={() => handleModeChange('ALL')}>
              Full Trace
            </button>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}