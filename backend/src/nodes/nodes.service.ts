import { Injectable } from '@nestjs/common';
import { Neo4jService } from '../neo4j/neo4j.service';
import { CreateNodeDto } from './dto/create-node.dto';

@Injectable()
export class NodesService {
    constructor(private readonly neo4jService: Neo4jService) { }

    async createOrUpdateNode(nodeData: any) {
        // 1. Destructure specific fields
        const { kind, metadata, spec, status, version_context, parentId } = nodeData;
        const { id, slug, name, labels, identity_aliases } = metadata;

        // 2. Prepare properties for Searchability (Flattening)
        // We define a "props" object to hold what we want searchable on the root node
        const nodeProps = {
            id,
            kind,
            slug: slug || id,
            name,
            updated_at: new Date().toISOString(),
            // FLATTEN these so the Indexes work!
            // If identity_aliases has 'aws_arn', it becomes n.aws_arn
            ...identity_aliases
        };

        const cypher = `
      // A. Merge the Node Identity
      MERGE (n:BaseNode {id: $id})
      
      // B. Set Searchable Properties (The Rosetta Stone)
      SET n += $nodeProps 
      // This updates id, slug, name, and flattened aliases
      
      // C. Set Complex Data (Spec/Status can remain serialized for now if huge)
      SET n.labels = $labels, 
          n.spec = $spec, 
          n.status = $status,
          n.version_context = $version_context
      
      // D. Apply Dynamic Label (e.g., :System, :Container)
      WITH n
      CALL apoc.create.addLabels(n, [$kind]) YIELD node
      
      // E. Handle Hierarchy (The "Contains" Edge)
      // This is conditional: Only runs if $parentId is provided
      WITH n
      CALL apoc.do.when(
        $parentId IS NOT NULL,
        'MATCH (p:BaseNode {id: $parentId}) MERGE (p)-[:CONTAINS]->(n) RETURN p',
        'RETURN n',
        {parentId: $parentId, n:n}
      ) YIELD value
      
      RETURN n
    `;

        const params = {
            id,
            kind,
            nodeProps, // Passed as a native object (Neo4j driver handles this)
            parentId: parentId || null, // Ensure null if undefined

            // Complex objects: We can keep these stringified for now 
            // OR pass as native Maps if you want to query inside them later.
            // For now, let's keep stringify for spec/status to keep it simple.
            labels: JSON.stringify(labels || {}),
            spec: JSON.stringify(spec || {}),
            status: JSON.stringify(status || {}),
            version_context: JSON.stringify(version_context || {})
        };

        const result = await this.neo4jService.write(cypher, params);
        return result.records[0].get('n').properties;
    }

    async getGraph() {
        // We fetch the start node UUID and end node UUID explicitly
        const cypher = `
      MATCH (n:BaseNode)
      OPTIONAL MATCH (n)-[r]->(m:BaseNode)
      RETURN collect(distinct n) as nodes, 
             collect(distinct {
                source: n.id, 
                target: m.id, 
                type: type(r),
                id: elementId(r)
             }) as relationships
    `;

        const result = await this.neo4jService.read(cypher);

        // Safety check
        if (result.records.length === 0) return { nodes: [], relationships: [] };

        const nodes = result.records[0].get('nodes').map((node: any) => ({
            id: node.properties.id,
            labels: node.labels,
            properties: node.properties
        }));

        // Now relationships already contain the UUIDs as 'source' and 'target'
        // Filter out nulls (where n has no relationships)
        const relationships = result.records[0].get('relationships')
            .filter(r => r.target !== null)
            .map((rel: any) => ({
                id: rel.id,
                start: rel.source, // Using UUID now
                end: rel.target,   // Using UUID now
                type: rel.type
            }));

        return { nodes, relationships };
    }
}
