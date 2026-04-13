# LEARNINGS: Advanced Data Analysis & Document Synthesis

## 🛠️ Technical Insights

### 1. Tool Selection (Search vs. Code)
*   **The Problem**: If you ask an LLM to "summarize the strategy" but the files are attached exclusively to the Code Interpreter, it might attempt to parse a PDF using a library like `pdfminer` in the sandbox, which is slow and error-prone.
*   **The Learning**: For binary formats like PDF, **`file_search` (Vector Stores)** is vastly superior. For tabular data like CSV, **`code_interpreter`** is the gold standard. A robust analyst agent needs access to *both* simultaneously with explicit instructions on which to use for what.

### 2. Retrieval of Generated Assets
*   **The Problem**: `code_interpreter` generates charts in its own temporary environment. Accessing these requires a specific sequence of API calls.
*   **The Learning**: You must iterate through the `files` in the message content, identify `image_file` types, and then use the `client.files.content(file_id)` endpoint to download them. This "pull" mechanism is essential for automated workflows.

### 3. Absolute Path Resolution
*   **The Problem**: Using relative paths like `../../.env` or `data/sales.csv` assumes the script is run from a specific subdirectory. Running from the project root (`python ./pocs/...`) causes `FileNotFoundError`.
*   **The Learning**: Always resolve paths relative to the script's `__file__`. Using `Path(__file__).resolve().parent` ensures the script is bulletproof regardless of the current working directory.

### 4. SDK Version & Structure Variance
*   **The Problem**: Following standard v1.x documentation often results in `AttributeError: 'Beta' object has no attribute 'vector_stores'`.
*   **The Learning**: In some SDK environments (like the `2.30.0` version found in this POC), certain Beta features like `vector_stores` are promoted to the top-level `client` object, while others like `assistants` remain under `.beta`. Using `dir(client)` to inspect the available attributes is a critical debugging step for platform migrations.

### 5. Sandbox Limitations
*   **The Learning**: The Code Interpreter sandbox is ephemeral and doesn't have internet access. All "ground truth" data must be uploaded *before* the run starts. You cannot "fetch" a new dataset from within the Python sandbox.

## 🚀 Recommendation for AI Scout
We should build a "Financial/Strategy Audit" tool for AI Scout using this pattern. Instead of the user reading through 100-page project specs, they can upload the PDF and a budget spreadsheet to a dedicated "Analyst Thread" within AI Scout to get instant variance analysis and visual summaries.
