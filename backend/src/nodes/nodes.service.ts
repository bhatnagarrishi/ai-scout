import { Injectable } from '@nestjs/common';
import { Neo4jService } from '../neo4j/neo4j.service';

@Injectable()
export class NodesService {
    constructor(private readonly neo4jService: Neo4jService) { }

    async createOrUpdateNode(nodeData: any) {
        const { kind, metadata, spec, status, version_context } = nodeData;
        const { id, slug, name, labels, identity_aliases } = metadata;

        // Construct Cypher query to merge node
        // Using MERGE on id to ensure uniqueness
        const cypher = `
      MERGE (n:BaseNode {id: $id})
      SET n.kind = $kind,
          n.slug = $slug,
          n.name = $name,
          n.labels = $labels,
          n.identity_aliases = $identity_aliases,
          n.spec = $spec,
          n.status = $status,
          n.version_context = $version_context,
          n.updated_at = datetime()
      // Add specific label based on kind
      WITH n
      CALL apoc.create.addLabels(n, [$kind]) YIELD node
      RETURN n
    `;

        const params = {
            id,
            kind,
            slug: slug || id, // Fallback to id if slug is missing
            name,
            labels: JSON.stringify(labels || {}),
            identity_aliases: JSON.stringify(identity_aliases || {}),
            spec: JSON.stringify(spec || {}),
            status: JSON.stringify(status || {}),
            version_context: JSON.stringify(version_context || {})
        };

        // Note: Storing complex objects as JSON strings for simplicity in this phase.
        // In a real graph, we might want to explode these into properties or separate nodes.
        // Also using APOC to add dynamic labels.

        const result = await this.neo4jService.write(cypher, params);
        return result.records[0].get('n').properties;
    }

    async getGraph() {
        const cypher = `
      MATCH (n:BaseNode)
      OPTIONAL MATCH (n)-[r]->(m)
      RETURN collect(distinct n) as nodes, collect(distinct r) as relationships
    `;

        const result = await this.neo4jService.read(cypher);
        if (result.records.length === 0) {
            return { nodes: [], relationships: [] };
        }

        const nodes = result.records[0].get('nodes').map((node: any) => ({
            id: node.properties.id,
            labels: node.labels,
            properties: node.properties
        }));
        const relationships = result.records[0].get('relationships').map((rel: any) => ({
            id: rel.identity.toString(),
            start: rel.start.toString(),
            end: rel.end.toString(),
            type: rel.type,
            properties: rel.properties
        }));

        return { nodes, relationships };
    }
}
