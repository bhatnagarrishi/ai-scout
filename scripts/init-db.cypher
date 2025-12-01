// Create constraint for unique node IDs if they exist
CREATE CONSTRAINT node_id_unique IF NOT EXISTS FOR (n:BaseNode) REQUIRE n.id IS UNIQUE;

// Create constraint for unique slugs
CREATE CONSTRAINT slug_unique IF NOT EXISTS FOR (n:BaseNode) REQUIRE n.slug IS UNIQUE;

// Note: Since the schema uses generic "metadata.id", we might need to adjust this depending on how we model it in Neo4j.
// For now, assuming we map the JSON model to Neo4j nodes where `id` and `slug` are properties.
