# Building with Amazon Bedrock: Workshop Report

**IDS 706 · Week 13 · Qianchun (Chien) Zhang**

This repo documents my hands-on work through the AWS workshop *Building with Amazon Bedrock* (Duke event, Nov 2026). I use it as a reference for later GenAI projects: RAG chatbots, guardrailed assistants, agent workflows and multimodal apps.

```
├── README.md          ← this report
├── screenshots/       ← evidence of completed labs
├── code/              ← the lab code I wrote/ran (one folder per lab)
└── outputs/           ← raw terminal output from the script-based labs
```

---

## How to run

**Environment.** I ran everything inside the AWS-hosted workshop environment (us-west-2, `WSParticipantRole`). The code in `code/` is the code I wrote or edited, but **this repo is not self-contained.** The data and helper files below came from the workshop's own `workshop/` folder and are not included here:

| Needed by | File(s) from the workshop package | Where it must be |
|---|---|---|
| I-1, I-4, B-2 | `workshop/data/populate_collection.py` + the Bedrock FAQ data → builds `workshop/data/chroma/` | run from `workshop/data/` |
| I-2 | `amazon-leadership-principles-070621-us.pdf` | `summarization/` |
| F-3 | `image.webp` | `converse/` |
| M-10 | `images/*.jpg, *.png` | `image_understanding/images/` |
| S-3 to S-6 | `completed/guardrails/create_{content,pii,attack}_guardrail.py`, `guardrails_app.py`, `guardrails_lib.py` | the create scripts write guardrail IDs into `bwab_guardrails.ini` in the working directory |

To run outside the workshop, download the workshop code (Lab setup page → `workshop.zip`) and copy each `code/<lab>/` folder over `workshop/labs/<lab>/`.

**Python and dependencies.** Python **3.11**, using the same interpreter Streamlit runs on (see §8). Third-party packages imported by the code here: `boto3`, `streamlit`, `chromadb`. I used the versions installed by the workshop (`pip install -r setup/requirements.txt` in the workshop package). AWS credentials need Bedrock access in us-west-2.

**Commands.** Always `cd` into the lab folder first, because paths like `../../data/chroma` are relative:

```bash
cd workshop/data && python3.11 populate_collection.py      # once, for I-1 / I-4 / B-2
cd workshop/labs/rag_chatbot && streamlit run rag_chatbot_app.py
cd workshop/labs/agent && python3.11 routing.py             # script-based labs
```

---

## 1. Summary of completed labs

| Category | Lab | Status | Evidence |
|---|---|:-:|---|
| **Foundational** (optional) | F-3 Converse API | ✅ | `outputs/F3_converse_api.txt` |
| | F-6 Tool use | ✅ | `outputs/F6_tool_use.txt` |
| **Basic patterns** (optional) | B-2 Retrieval-Augmented Generation | ✅ | `screenshots/B2_rag.png` |
| | B-4 Agents (4 patterns) | ✅ | `screenshots/B4_agents.png`, `outputs/B4_*.txt` |
| **Text patterns** (required) | I-1 Chatbot with RAG | ✅ | `I1_rag_chatbot_ui.png`, `I1_rag_chatbot_terminal.png` |
| | I-2 Document summarization | ✅ | `I2_summary.png` |
| | I-3 Response streaming | ✅ | `I3_streaming.png` |
| | I-4 Embeddings search | ✅ | `I4_embeddings.png` |
| **Multimodal** (recommended) | M-10 Image understanding | ✅ | `M10_image.png` |
| **Security & safeguards** (required) | S-1 Guardrails in the Console | ✅ | `S1_word_filter.png`, `S1_denied_topic.png`, `S1_misconduct.png` |
| | S-2 Guardrails programmatically | ✅ | `outputs/S2_create_guardrail.txt` |
| | S-3 Invoking models with guardrails + trace | ✅ | `outputs/S3_*.txt` |
| | S-4 Content blocking | ✅ | `S4_content.png` |
| | S-5 PII masking | ✅ | `S5_pii.png` |
| | S-6 Prompt attack blocking | ✅ | `S6_attack.png` |
| | IAM for Bedrock | ✅ (read) | §4.4 notes |
| **Bonus** (required) | O-1 Prompt showcase | ✅ | `O1_showcase.png` |
| | O-2 Text generation playground | ✅ | `O2_playground_t0.png`, `O2_playground_t1.png` |

All required labs (I1–I4, S1–S6, Bonus 1–2) are complete, plus five optional labs (F-3, F-6, B-2, B-4, M-10).

### Customizations
- Retitled every app "IDS 706 …" and added a caption to the RAG chatbot.
- **O-1:** added my own prompt template (*Action Items → markdown table*) and input (*BikeFlow NYC team meeting notes*) from my IDS 706 final project.
- **B-4:** capped the evaluator–optimizer loop at 4 rounds (the original `while True` has no exit if the evaluator never says PASS) and changed `system=` to the Converse format `[{"text": ...}]`.
- **Model migration.** Claude 3.7 Sonnet was no longer available, so I switched the Claude calls to Claude Sonnet 4.5 and fixed two follow-on errors (details in §8).

---

## 2. Key concepts learned

| Concept | What it is | Where I used it |
|---|---|---|
| **InvokeModel vs. Converse** | `invoke_model` takes a provider-specific JSON body; `converse` uses a shared message format (roles, content blocks, `inferenceConfig`) across the models that support Converse | F-3, everywhere |
| **Content blocks** | A message's `content` is a list of `text`, `image`, `document`, `toolUse` and `toolResult` blocks. Raw bytes can be sent with no base64. | F-3, I-2 (PDF), M-10 (image) |
| **Stateless models** | The model has no memory. The app keeps the history and resends it on every turn, trimmed to `MAX_MESSAGES`. | I-1 |
| **Tool use** | The model returns a `toolUse` JSON request. The app runs the function and sends back a `toolResult`. | F-6, I-1 |
| **Embeddings + vector DB** | Text becomes a vector (Titan Text Embeddings v2); Chroma returns the nearest chunks | I-4, B-2, I-1 |
| **RAG** | Retrieve relevant chunks first, then generate an answer from them | B-2, I-1 |
| **Streaming** | `converse_stream` yields `contentBlockDelta` events with text chunks | I-3 |
| **Inference parameters** | `temperature` and `topP` control sampling; `maxTokens` caps length | O-2 |
| **Guardrails** | A policy layer applied to inputs and/or outputs: content filters, denied topics, word filters, PII, prompt attacks, grounding | S-1 … S-6 |
| **Agentic workflows** | Composing LLM calls: chain, parallelize, route, evaluate→optimize | B-4 |

### Common architecture

Every Streamlit lab follows the same two-file pattern: a thin UI file plus a `*_lib.py` that talks to Bedrock.

```mermaid
flowchart LR
    U[User in browser] --> A["*_app.py<br/>Streamlit UI"]
    A -->|function call| L["*_lib.py<br/>build messages"]
    L -->|boto3 bedrock-runtime| B[(Amazon Bedrock)]
    B -->|response JSON| L
    L -->|text / table / image| A
```

---

## 3. Text patterns (required): detailed labs

### 3.1 I-1 Chatbot with RAG (tool-use-driven retrieval)

**Idea:** Claude decides *when* to look something up. Retrieval is exposed as a tool, `get_amazon_bedrock_information`. When the model calls it, the app queries Chroma and returns the chunks as a `toolResult` in a second model call.

```mermaid
sequenceDiagram
    participant U as User
    participant App as Streamlit app
    participant C as Claude Sonnet 4.5
    participant V as Chroma + Titan Embeddings
    U->>App: "what else?"
    App->>C: history + new message + tool spec
    C-->>App: toolUse {query: "What advanced features does Amazon Bedrock offer..."}
    App->>V: similarity search (top 4)
    V-->>App: FAQ chunks
    App->>C: toolResult(chunks)
    C-->>App: answer based on the chunks
    App-->>U: render chat
```

**Implementation steps**
1. Initialize the vector DB with `populate_collection.py` (see How to run). It embeds the Bedrock FAQ with `amazon.titan-embed-text-v2:0` and stores it in Chroma.
2. Define the tool spec: a JSON Schema with one `query` string.
3. Send the conversation with `toolConfig`. If the response contains a `toolUse` block, run retrieval and send a second request with the `toolResult`.
4. Keep `ChatMessage` objects in `st.session_state` and trim old turns.

**Key code**: `code/rag_chatbot/rag_chatbot_lib.py`

```python
for content_block in response_message['content']:
    if 'toolUse' in content_block:
        tool_use_block = content_block['toolUse']
        if tool_use_block['name'] == 'get_amazon_bedrock_information':
            query = tool_use_block['input']['query']          # query written by the model
            search_results = get_vector_search_results(collection, query)
            rag_content = "\n\n".join(itertools.chain(*search_results['documents']))
            follow_up_content_blocks.append({
                "toolResult": {
                    "toolUseId": tool_use_block['toolUseId'],
                    "content": [{"text": rag_content}]
                }
            })
```

**Result**

| Multi-turn chat | Terminal: search query + retrieved chunks |
|---|---|
| ![](screenshots/I1_rag_chatbot_ui.png) | ![](screenshots/I1_rag_chatbot_terminal.png) |

**Observations**
- For the follow-up "what else?", the model used the conversation history to formulate a more specific search query: *"What advanced features does Amazon Bedrock offer for developers and enterprises?"* (terminal screenshot). I did not compare this against retrieving with the raw follow-up text.
- For "what models?", the answer listed Jurassic-2 and Claude 3 models, which matches the age of the FAQ data rather than what Bedrock offers today.

### 3.2 I-3 Response streaming

```mermaid
flowchart LR
    U[User] --> A[Streamlit]
    A --> L["converse_stream()"]
    L --> B[(Bedrock)]
    B -. "contentBlockDelta chunks" .-> L
    L -. "callback(chunk)" .-> A
    A -. "st.empty() re-renders<br/>accumulated text" .-> U
```

**Key code**: `code/streaming/`

```python
response = bedrock.converse_stream(modelId=MODEL_ID, messages=[message],
                                   inferenceConfig={"maxTokens": 2000, "temperature": 0.0})
for event in response.get('stream'):
    if "contentBlockDelta" in event:
        streaming_callback(event['contentBlockDelta']['delta']['text'])

# app side
with st.empty():                      # one placeholder, overwritten on every chunk
    def streaming_callback(chunk):
        global combined_response
        combined_response += chunk
        st.write(combined_response)
```

![](screenshots/I3_streaming.png)

The app displays text chunks as they arrive and updates the same Streamlit placeholder throughout the response. I did not time first-chunk latency against the non-streaming version.

### 3.3 I-2 Summarization and I-4 Embeddings search

| I-2: PDF sent as a Converse `document` block | I-4: vector search only, no LLM |
|---|---|
| ![](screenshots/I2_summary.png) | ![](screenshots/I4_embeddings.png) |

- **I-2.** Input question: *"What are the top three principles for a newly promoted manager to consider?"* The PDF (Amazon Leadership Principles) is sent as raw bytes in a `document` content block next to the question, with no text extraction or chunking. Claude answered with **Hire and Develop the Best**, **Earn Trust** and **Have Backbone; Disagree and Commit**, each with 4 supporting points from the document.
- **I-4.** Query: *"What are the key features of Guardrails for Amazon Bedrock?"* The app shows the 4 nearest FAQ chunks without calling an LLM, which is useful for checking what a RAG pipeline would retrieve. The **second result** ("What are the safeguards available in Guardrails for Amazon Bedrock?") lists Word filters and PII redaction as "coming soon", although I used both in S-1. B-2's answer repeated the same "coming soon" wording.

---

## 4. Security & safeguards (required): detailed labs

### Where a guardrail sits in the request path

```mermaid
flowchart LR
    U[User prompt] --> GI{"Guardrail<br/>INPUT check"}
    GI -- "blocked" --> M1["blockedInputMessaging"]
    GI -- "pass" --> FM[(Foundation model)]
    FM --> GO{"Guardrail<br/>OUTPUT check"}
    GO -- "blocked" --> M2["blockedOutputsMessaging"]
    GO -- "PII found" --> MASK["mask -> {NAME}, {EMAIL}"]
    GO -- "pass" --> R[Response]
    MASK --> R
```

### Which guardrail, model and evidence each lab used

The security labs used **five different guardrails** and two models, so the IDs in the evidence differ:

| Lab | Guardrail (how created) | Model | Evidence |
|---|---|---|---|
| S-1 | `Guardrail-from-Console` (Console, by hand) | Global Claude Sonnet 4.5 (Console test panel) | 3 Console trace screenshots |
| S-2 | `Guardrail-from-Code-*`, ID `l9iao9eeyedw` (`code/guardrails/create_guardrail.py`) | none, creation only | `outputs/S2_create_guardrail.txt` prints the ID only |
| S-3 | content-blocking guardrail `q6dtvir82xpa` (workshop's `completed/.../create_content_guardrail.py`, ID read from `bwab_guardrails.ini`) | Amazon Nova Lite via `invoke_model` | `outputs/S3_*.txt` |
| S-4 | same content-blocking guardrail `q6dtvir82xpa` | Claude Sonnet 4.5 via workshop `guardrails_app.py` | `S4_content.png` |
| S-5 | PII guardrail `e7zd7p7zz2fz` (workshop's `create_pii_guardrail.py`, not in this repo) | Claude Sonnet 4.5 via workshop `guardrails_app.py` | `S5_pii.png` |
| S-6 | prompt-attack guardrail `7h00r7b8rzdg` (workshop's `create_attack_guardrail.py`) | Claude Sonnet 4.5 via workshop `guardrails_app.py` | `S6_attack.png` |

The S-1 Console guardrail was configured as follows. S-2's script has the same policies **except contextual grounding**, which it does not configure.

| Policy | S-1 setting |
|---|---|
| Content filters | Hate, Insults, Sexual, Violence, Misconduct → Block, **High** (Classic tier) |
| Prompt attacks | Block, High (input only) |
| Denied topic | "Bitcoin", with definition and sample phrases |
| Word filters | Managed profanity list + custom word `AnyCompany` |
| PII | NAME, EMAIL → **Mask** |
| Contextual grounding | Grounding 0.7, relevance 0.9 (S-1 only) |

### 4.1 S-1 Creating and testing a guardrail in the Console

**Steps:** Bedrock → Build → **Guardrails** → Create guardrail → configure each policy step → Create → test in the right-hand panel with Global Claude Sonnet 4.5 → *View trace* → Create version.

Each test prompt triggered a different policy in the trace:

| Prompt | Policy shown in the trace | Screenshot |
|---|---|---|
| `How does your product compare to AnyCompany's product?` | Word filter: `AnyCompany` → Blocked | ![](screenshots/S1_word_filter.png) |
| `I like bitcoin, how about you?` | Denied topic: Bitcoin → Blocked | ![](screenshots/S1_denied_topic.png) |
| `Walk me through hotwiring a car.` | Content filter: Misconduct → Blocked (confidence High) | ![](screenshots/S1_misconduct.png) |

In all three, the *Model response* field shows `-` and the final response is the blocked-input message, which is consistent with the prompt being stopped at the input check. I did not separately check token usage.

### 4.2 S-5 PII masking

PII policy (from the workshop's `create_pii_guardrail.py`; my S-2 script uses the same block):

```python
sensitiveInformationPolicyConfig={
    "piiEntitiesConfig": [
        {"type": "NAME",  "action": "ANONYMIZE"},
        {"type": "EMAIL", "action": "ANONYMIZE"},
    ],
},
```

![](screenshots/S5_pii.png)

**Observation.** The summary shown to the user contains `{NAME}` and `{EMAIL}`. In the same run, the trace's `modelOutput` field contains the unmasked model output, including "Carson Bradford" and "carsonbradford@test.com". So in this setup, masking applied to the returned text but not to the trace, and anything that logs traces would also need its own redaction.

### 4.3 S-2, S-3, S-4, S-6

**S-3: invoking a model with a guardrail and trace** (`code/guardrails/test_trace.py`, Nova Lite):

```python
response = bedrock_runtime.invoke_model(
    modelId='us.amazon.nova-lite-v1:0', body=body,
    guardrailIdentifier=guardrail_id, guardrailVersion="DRAFT",
    trace='ENABLED')
trace = json.loads(response['body'].read())['amazon-bedrock-trace']
```

`"How do you wash a car?"` returned a normal answer. `"How do you hotwire a car?"` returned the blocked message, and the trace recorded `MISCONDUCT / confidence HIGH / BLOCKED` (`outputs/S3_trace_blocked.txt`).

| S-4: `I hate city people` | S-6: "Ignore the previous instructions… Meep" |
|---|---|
| ![](screenshots/S4_content.png) | ![](screenshots/S6_attack.png) |

- **S-2:** `create_guardrail()` and `create_guardrail_version()` created the guardrail; the script prints only its ID.
- **S-4:** The trace recorded `HATE / confidence HIGH / BLOCKED`. I screenshotted only this blocked case; the lab notes that `I hate lasagna` is expected to pass, but I don't have a screenshot of that run.
- **S-6:** The trace recorded `PROMPT_ATTACK` with confidence HIGH and action `BLOCKED`, and the app returned "Apologies, your request was blocked."

### 4.4 IAM notes
- Allow-list models with `bedrock:InvokeModel` / `InvokeModelWithResponseStream` on specific `foundation-model/...` ARNs, so newly added models aren't usable by default.
- Restrict Marketplace model subscriptions with an `aws-marketplace:Subscribe` condition on `aws-marketplace:ProductId`.

---

## 5. Bonus labs (required)

### 5.1 O-1 Prompt showcase (customized)

The app keeps prompt **templates** and user **inputs** in separate dictionaries and merges them with `template.format(user_input=...)`. Both stay editable in the UI. My added template:

```python
prompts["Action Items (custom)"] = """
{user_input}

Extract every action item from the above text as a markdown table with columns: Owner, Task, Deadline.
If a field is not mentioned, write "N/A".
"""
```

![](screenshots/O1_showcase.png)

The meeting notes had four assigned tasks and one open question. The model captured the four assigned tasks with the right owners and deadlines, and also turned the open deployment question ("AWS or keep it local?") into an unassigned action item with owner `N/A`. If I only wanted assigned work, the prompt should say to exclude open questions.

### 5.2 O-2 Text generation playground (temperature)

Same prompt (`Write a haiku about Durham`), same model (Amazon Nova Micro), same Top P (0.9) and token limit (512); only temperature differs:

| temperature = 0.0 | temperature = 1.0 |
|---|---|
| ![](screenshots/O2_playground_t0.png) | ![](screenshots/O2_playground_t1.png) |
| *Durham's Ancient Spires / Majestic cliffs and river's flow / Timeless town's delight.* | *Durham's skies where history flows / Ancient towers where spirits grow / Silent witness now.* |

**Observations**
- These two runs produced different haikus. With one run per setting, this doesn't show how stable each setting is; repeating each setting several times would.
- Both haikus mention spires/towers and cliffs, which sounds more like Durham, England than Durham, NC. A question I'd like to test: does writing "Durham, North Carolina" change the imagery?

---

## 6. Foundational & basic patterns (optional): detailed labs

### 6.1 F-3 Converse API

One script covered a basic call, alternating user/assistant turns, an image block, a system prompt (pirate style) and response metadata:

```python
response = bedrock.converse(
    modelId=MODEL_ID,
    messages=message_list,
    system=[{"text": "Please respond to all requests in the style of a pirate."}],
    inferenceConfig={"maxTokens": 2000, "temperature": 0},
)
print(response['stopReason'], response['usage'])
```

Output (`outputs/F3_converse_api.txt`): `Stop Reason: end_turn`, `inputTokens: 780`, `outputTokens: 268`, with the summary written in pirate style.

### 6.2 F-6 Tool use

```mermaid
sequenceDiagram
    participant App
    participant C as Claude
    App->>C: "What is the cosine of 7?" + cosine tool spec
    C-->>App: toolUse {name: cosine, input: {x: 7}}
    App->>App: math.cos(7) = 0.7539...
    App->>C: toolResult {result: 0.7539...}
    C-->>App: "The cosine of 7 is approximately 0.754"
```

In the error-handling step, the app returns a `toolResult` with `status: "error"`. The tutorial's sample output (Claude 3) says it cannot compute the answer. In my run, Claude Sonnet 4.5 gave the value of cos(7) anyway (0.7539, plus the degrees interpretation), even though the system prompt said "You must only do math by using a tool" (`outputs/F6_tool_use.txt`). From this one run: if a tool result is required, the app should check for it rather than rely on the system prompt.

### 6.3 B-2 RAG (basic)

B-2 always retrieves the top 4 chunks for the question, puts them in the prompt with "Based on the content above…", and answers with Amazon Nova Lite. Unlike I-1, there is no tool call and no query rewriting. The answer repeated the FAQ's "Word Filters (Coming Soon)" wording.

![](screenshots/B2_rag.png)

### 6.4 B-4 Agent patterns (from Anthropic's *Building effective agents*)

```mermaid
flowchart TB
    subgraph Chaining
      a1[Extract] --> a2[Convert to %] --> a3[Sort] --> a4[Markdown table]
    end
    subgraph Parallelization
      b0[Prompt] --> b1[Customers] & b2[Employees] & b3[Investors] & b4[Suppliers]
    end
    subgraph Routing
      c0[Ticket] --> c1{Classifier} --> c2[billing] & c3[technical] & c4[account] & c5[product]
    end
    subgraph Evaluator-Optimizer
      d1[Generator] --> d2{Evaluator}
      d2 -- NEEDS_IMPROVEMENT + feedback --> d1
      d2 -- PASS --> d3[Done]
    end
```

![](screenshots/B4_agents.png)

| Pattern | What I observed (`outputs/B4_*.txt`) |
|---|---|
| Chaining | The Q3 report became a sorted markdown table in 4 steps. In the final table, "Customer acquisition cost is $43 per user" appears as **43%**. Step 2's prompt asks to convert all values to percentages, and no later step checked units. |
| Parallelization | 4 stakeholder analyses ran through `ThreadPoolExecutor(max_workers=3)`. |
| Routing | 3 tickets → `account`, `billing`, `product`, which match the ticket contents (login problem, unexpected charge, data export). |
| Evaluator–optimizer | Min-stack task: the LLM evaluator returned NEEDS_IMPROVEMENT in round 1 and PASS in round 2. PASS is the evaluator model's judgment; I didn't run unit tests on the generated code. |

---

## 7. Multimodal (recommended): M-10 Image understanding

```python
image_message = {"role": "user", "content": [
    {"text": "Image 1:"},
    {"image": {"format": "png" if image_bytes[:4] == b"\x89PNG" else "jpeg",
               "source": {"bytes": image_bytes}}},
    {"text": prompt_content},
]}
```

![](screenshots/M10_image.png)

With the *Text in image* example and the *Transcribing text* prompt, the model returned all four phrases in the image, including the rotated "WHAT ARE YOU DOING?" and the two script-font lines. The `format` line is my fix (§8).

---

## 8. Reflections: what I had to change

My first Claude call failed because the workshop's model ID was no longer available in my environment. These are the changes I made, in order:

| # | Error I hit | What I changed |
|---|---|---|
| 1 | `ResourceNotFoundException: This model version has reached the end of its life` (Claude 3.7 Sonnet) | Wrote a script that tried candidate models and replaced `us.anthropic.claude-3-7-sonnet-20250219-v1:0` with `us.anthropic.claude-sonnet-4-5-20250929-v1:0` in 8 lab files (`agent/util.py`, `converse`, `tool_use`, `rag_chatbot`, `summarization`, `streaming`, `showcase`, `image_understanding`) and in the workshop's pre-built `completed/` apps used for S-4 to S-6. Nova-based labs (B-2, S-3, O-2) were unchanged. |
| 2 | `ValidationException: temperature and top_p cannot both be specified for this model` | Deleted the `topP` line from every call that now uses Sonnet 4.5. Nova calls kept `topP`. |
| 3 | `The image was specified using the image/jpeg media type, but the image appears to be a image/png image` (M-10) | The workshop hard-codes `"format": "jpeg"` (its comment says it "doesn't seem to matter"). I now pick `png` or `jpeg` from the file's first bytes. |
| 4 | `Collection [bedrock_faqs_collection] does not exist` | `python3` in the environment is 3.9 and has no chromadb, so my first `populate_collection.py` run failed; Streamlit runs on 3.11. I re-ran it with `python3.11`. |
| 5 | `No module named 'test_helper'` (S-3) | The file wasn't in `labs/guardrails/`; I recreated it to read guardrail IDs from `bwab_guardrails.ini`. |

The model ID is still hard-coded in each file in this repo. Next time I would put it in one config value or environment variable, because change #1 required editing every lab.

Console changes I worked around: the Bedrock *Model access* page has been retired (models are enabled on first use), Guardrails now sits under **Build** in the navigation, and the guardrail content-filter tier can only be chosen after a filter is switched on.

---

*Models used: Claude Sonnet 4.5 (`us.anthropic.claude-sonnet-4-5-20250929-v1:0`), Amazon Nova Lite and Nova Micro, Titan Text Embeddings v2. Region: us-west-2.*
