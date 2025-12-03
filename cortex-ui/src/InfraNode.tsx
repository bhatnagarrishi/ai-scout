/**
 * Custom React Flow Node Component for Infrastructure Resources
 * 
 * This component provides specialized rendering and connection points for infrastructure nodes
 * (e.g., AWS Regions, VPCs, Subnets, EC2 instances) to support inverted hierarchy visualization.
 * 
 * Key Features:
 * - Multiple connection handles for different relationship types
 * - Inverted hierarchy support (children above parents in infrastructure)
 * - Distinct visual styling to differentiate from software components
 */
import { Handle, Position, type NodeProps } from 'reactflow';

/**
 * InfraNode - Custom node renderer for INFRA_RESOURCE type nodes
 * 
 * Connection Points:
 * 1. TARGET TOP: Receives HOSTED_ON connections from software (Containers/Apps)
 * 2. SOURCE TOP: Emits CONTAINS connections UP to child infrastructure (inverted hierarchy)
 * 3. TARGET BOTTOM: Receives CONTAINS connections from parent infrastructure
 * 
 * Example hierarchy flow (inverted - children above parents):
 *   EC2 Instance (top)
 *        ↑ CONTAINS (source-top → target-bottom)
 *      VPC
 *        ↑ CONTAINS (source-top → target-bottom)
 *   AWS Region (bottom)
 */
export default function InfraNode({ data }: NodeProps) {
    return (
        <div style={{
            padding: '10px',
            borderRadius: '8px',
            background: '#f4f4f4',        // Light grey background for infrastructure
            border: '1px solid #999',
            textAlign: 'center',
            minWidth: '160px',
            fontSize: '12px',
            color: '#333',                 // Dark text for readability
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            fontFamily: 'sans-serif'
        }}>
            {/* TARGET TOP: Receives HOSTED_ON connections from software components */}
            <Handle
                type="target"
                position={Position.Top}
                id="target-top"
                style={{ background: '#555', borderRadius: 0 }}  // Square handle for visual distinction
            />

            {/* Node content */}
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{data.kind}</div>
            <div>{data.name}</div>

            {/* SOURCE TOP: Emits CONTAINS connections UP to child infrastructure (inverted hierarchy) */}
            <Handle
                type="source"
                position={Position.Top}
                id="source-top"
                style={{ left: '70%', background: '#555' }}  // Offset to avoid overlap with target-top
            />

            {/* TARGET BOTTOM: Receives CONTAINS connections from parent infrastructure */}
            <Handle
                type="target"
                position={Position.Bottom}
                id="target-bottom"
                style={{ background: '#555' }}
            />
        </div>
    );
}