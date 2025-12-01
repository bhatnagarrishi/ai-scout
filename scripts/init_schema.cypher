// --------------------------------------------------------
// 1. Core Identity Constraints (Priority 2 Strategy)
// --------------------------------------------------------

// The Internal UUID must be unique across all nodes
CREATE CONSTRAINT node_id_unique IF NOT EXISTS
FOR (n:BaseNode) REQUIRE n.id IS UNIQUE;

// The Human Readable Slug (e.g., 'payment-service') must be unique
CREATE CONSTRAINT node_slug_unique IF NOT EXISTS
FOR (n:BaseNode) REQUIRE n.slug IS UNIQUE;

// --------------------------------------------------------
// 2. Identity "Rosetta Stone" Indexes (Performance)
// These allow the Ingestion Engine to find nodes by external IDs fast
// --------------------------------------------------------

// Find nodes by Git URL
CREATE INDEX identity_git_url IF NOT EXISTS
FOR (n:BaseNode) ON (n.git_repo_url);

// Find nodes by AWS ARN
CREATE INDEX identity_aws_arn IF NOT EXISTS
FOR (n:BaseNode) ON (n.aws_arn);

// Find nodes by Kubernetes UID
CREATE INDEX identity_k8s_uid IF NOT EXISTS
FOR (n:BaseNode) ON (n.k8s_uid);

// --------------------------------------------------------
// 3. Search Indexes (For Visualization/UI)
// --------------------------------------------------------

CREATE INDEX node_name IF NOT EXISTS
FOR (n:BaseNode) ON (n.name);

CREATE INDEX node_kind IF NOT EXISTS
FOR (n:BaseNode) ON (n.kind);
