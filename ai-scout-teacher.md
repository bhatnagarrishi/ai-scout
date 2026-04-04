This is the blueprint for your personal **AI Scout & Mentor Agent**. You can copy this into a file named `AI_Learning_Agent_Plan.md`.

---

# AI Learning Agent: Project "Scout & Mentor"

## 1. Objective

To build an automated agentic workflow that identifies high-value AI advancements, filters them for practical utility, and generates actionable "3-hour projects." The ultimate goal is to move from passive consumption of AI news to active, portfolio-building implementation.

## 2. Approach

The system follows a **"Signal-to-Action"** philosophy:

*   **Automated Ingestion:** Remove the need to manually check sites.

*   **Utility Filtering:** Use LLMs to discard marketing hype and focus on implementable technology.

*   **Projectization:** Every significant news item is converted into a structured coding exercise.

*   **Public Proof:** Every completed exercise is committed to GitHub to build a visible track record of expertise.

## 3. Architecture / Pipeline

1.  **Ingestion Layer:** n8n monitors RSS feeds (Blogs) and YouTube APIs (Channels).

2.  **Processing Layer:** 

    *   **Filter Node:** Checks keywords.

    *   **AI Agent Node:** Analyzes content and determines if a 3-hour project is feasible.

3.  **Output Layer:** 

    *   **GitHub API:** Creates a new Issue or Repository with the project plan.

    *   **Notification:** Alerts the user (Slack/Email/Discord) that a new "Mission" is ready.

4.  **Learning Loop:** User completes the project -> Commits code -> Summarizes learning in the README.

## 4. Tech Stack

*   **Orchestration:** [n8n](https://n8n.io/) (Self-hosted via npm or Docker).

*   **Brain (LLM):** Claude 3.5 Sonnet (preferred for coding/logic) or GPT-4o.

*   **Data Sources:** 

    *   **RSS:** OpenAI, Anthropic, Google AI, DeepLearning.AI, TLDR AI, Interconnects.

    *   **YouTube API:** Karpathy, Dave Ebbelaar, Everyday AI.

*   **Project Tracking:** GitHub (Issues and Repositories).

*   **Environment:** Python (local venv or Jupyter Notebooks) for project execution.

## 5. Pre-requisites

- [ ] **n8n Local:** Installed and running locally via Node.js (`npx n8n`) or Docker.

- [ ] **Anthropic/OpenAI API Key:** Funded with a small amount (e.g., $5-$10) for LLM reasoning.

- [ ] **GitHub Personal Access Token (PAT):** With permissions for `repo` and `workflow`.

- [ ] **Google Cloud Console Account:** (Optional but recommended) To get a YouTube Data API Key.

- [ ] **Basic Python Knowledge:** Ability to create virtual environments and install packages via `pip`.

## 6. Detailed Steps

### Step 1: Initialize the n8n Workflow

1.  Open n8n and create a new workflow titled "AI Scout & Mentor."

2.  Add a **Schedule Trigger** set to run once every 24 hours (or manually for testing).

### Step 2: Configure Data Sources

1.  **RSS Nodes:** Add one RSS node for each source. 

    *   Example: `https://openai.com/news/rss.xml`

2.  **YouTube Node:** Connect the YouTube node using your API key. Add the channel IDs for the specified creators.

3.  **Merge Node:** Connect all source nodes into a "Merge" node to create a single stream of data.

### Step 3: The AI Brain (Filtering & Planning)

Add an **AI Agent Node** (or Basic LLM Node) with the following System Prompt:

> "You are an AI Master Instructor. I will provide you with titles and summaries from AI news and tutorials. 
> 
> **Filter Criteria:** Only proceed if the content describes a new model, library, tool, or technique that can be tested/implemented in Python within 3 hours. Reject news about funding, policy, or generic 'hype.'
> 
> **Output Requirement:** For accepted items, generate a JSON object:
> 1. Project Title
> 2. Tech Stack (Specific libraries/APIs)
> 3. Action Plan (5 steps to build a Proof of Concept)
> 4. GitHub repo name (A slugified version of the title)"

### Step 4: GitHub Integration

1.  Add a **GitHub Node** to the workflow.

2.  Set the Action to `Create an Issue` or `Create a Repository`.

3.  Map the AI-generated JSON fields to the GitHub Issue body.

4.  (Optional) Add a **Slack or Discord Node** to send yourself a message when a new project is created.

### Step 5: The Execution Workflow (Manual)

1.  Upon notification, open the GitHub Issue.

2.  Initialize a local folder: `mkdir project-name && cd project-name`.

3.  Build the PoC using the AI-generated Action Plan.

4.  **Finalize:** Create a `README.md` containing:

    *   What the technology is.

    *   The code results.

    *   One "Key Insight" learned during the build.

5.  `git commit -m "Project complete"` and push.

---
