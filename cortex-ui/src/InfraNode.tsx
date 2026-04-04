/**
 * Custom React Flow Node Component for Infrastructure Resources
 * 
 * This component provides specialized rendering and connection points for infrastructure nodes
 * (e.g., AWS Regions, VPCs, Subnets, EC2 instances) with support for parent-child nesting.
 * 
 * Key Features:
 * - Multiple connection handles for different relationship types
 * - Parent container nodes with semi-transparent backgrounds for visual nesting
 * - Distinct visual styling to differentiate from software components
 */
import { Handle, Position, type NodeProps } from 'reactflow';

/**
 * InfraNode - Custom node renderer for INFRA_RESOURCE type nodes
 * 
 * Supports both regular infrastructure nodes and parent container nodes.
 * Parent nodes (those with CONTAINS relationships) are rendered larger with
 * semi-transparent backgrounds to visually contain their children.
 * 
 * Connection Points:
 * 1. TARGET TOP: Receives HOSTED_ON connections from software (Containers/Apps)
 * 2. SOURCE TOP: Emits connections to other infrastructure or software
 * 3. TARGET BOTTOM: Receives connections from parent infrastructure
 */
export default function InfraNode({ data }: NodeProps) {
    const isParent = data.isParent || false;

    return (
        <div style={{
            padding: isParent ? '40px 20px 20px 20px' : '10px',
            borderRadius: '8px',
            background: isParent ? 'rgba(220, 220, 220, 0.3)' : '#f4f4f4',  // Semi-transparent for parents
            border: isParent ? '2px dashed #999' : '1px solid #999',        // Dashed border for parents
            textAlign: 'center',
            width: '100%',
            height: '100%',
            minWidth: isParent ? '300px' : '160px',
            minHeight: isParent ? '200px' : 'auto',
            fontSize: '12px',
            color: '#333',
            boxShadow: isParent ? '0 4px 8px rgba(0,0,0,0.15)' : '0 2px 4px rgba(0,0,0,0.1)',
            fontFamily: 'sans-serif',
            position: 'relative',
            boxSizing: 'border-box'
        }}>
            {/* TARGET TOP: Receives HOSTED_ON connections from software components */}
            <Handle
                type="target"
                position={Position.Top}
                id="target-top"
                style={{ background: '#555', borderRadius: 0 }}
            />

            {/* Node content - positioned at top for parent nodes */}
            <div style={{
                fontWeight: 'bold',
                marginBottom: '4px',
                position: isParent ? 'absolute' : 'relative',
                top: isParent ? '10px' : 'auto',
                left: isParent ? '20px' : 'auto',
                width: isParent ? 'auto' : '100%'
            }}>
                {data.kind}
            </div>
            <div style={{
                position: isParent ? 'absolute' : 'relative',
                top: isParent ? '10px' : 'auto',
                left: isParent ? '120px' : 'auto',
                width: isParent ? 'auto' : '100%'
            }}>
                {data.name}
            </div>

            {/* SOURCE TOP: Emits connections to other nodes */}
            <Handle
                type="source"
                position={Position.Top}
                id="source-top"
                style={{ left: '70%', background: '#555' }}
            />

            {/* TARGET BOTTOM: Receives connections from parent infrastructure */}
            <Handle
                type="target"
                position={Position.Bottom}
                id="target-bottom"
                style={{ background: '#555' }}
            />
        </div>
    );
}