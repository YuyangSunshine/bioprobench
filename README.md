<div align="center">
  <a href="https://yuyangsunshine.github.io/BioPro-Project/">
    <img src="https://img.shields.io/badge/🌟_Part_of-BioProProject_Series-0052cc?style=for-the-badge&logo=google-chrome&logoColor=white" alt="BioProProject Series"/>
  </a>
</div>
<br>
<div align="center">
  <img src="https://github.com/YuyangSunshine/bioprotocolbench/blob/main/figures/logo-v3.png?raw=true" alt="BioProBench Logo" width="380"/>

  <br />
  <strong>Comprehensive Dataset and Benchmark in Biological Protocol Understanding and Reasoning</strong>
  <br />

  [![ArXiv](https://img.shields.io/badge/ArXiv-paper-B31B1B.svg?style=flat-square&logo=arXiv&logoColor=Red)](https://arxiv.org/pdf/2505.07889)
  [![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Dataset-FFD210.svg?style=flat-square&logo=HuggingFace&logoColor=black)](https://huggingface.co/BioProBench)
  [![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg?style=flat-square)](https://creativecommons.org/licenses/by-nc/4.0/)
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/YuyangSunshine/bioprotocolbench/pulls)
</div>

> **BioProBench** is the first large-scale, integrated multi-task benchmark designed specifically for Large Language Models (LLMs) in the life sciences. It moves beyond simple declarative QA to encompass a comprehensive suite of tasks critical for true procedural text comprehension and execution.

---

## 📖 Overview

Biological protocols are the fundamental bedrock of reproducible and safe life science research. While LLMs have shown remarkable capabilities on general tasks, their systematic evaluation on highly specialized, accuracy-critical, and inherently procedural texts remains limited. 

BioProBench fills this gap by providing a robust framework to evaluate LLMs on diverse aspects of protocol understanding and reasoning. It serves as the foundational evaluation environment for downstream execution agents like our [**BioProAgent**](https://github.com/YuyangSunshine/bioproagent).

<div align="center">
  <img src="https://github.com/YuyangSunshine/bioprotocolbench/blob/main/figures/overview.png?raw=true" alt="BioProBench Overview" width="900" style="border-radius: 8px;"/>
</div>

### ✨ Key Features
* 📚 **Unprecedented Scale:** Grounded in a highly-curated, open-source corpus of **22,413 original biological protocols**, yielding **523,784 high-quality structured instances**.
* 🎯 **Comprehensive Tasks:** A suite of **5 core tasks** challenging LLMs on temporal dependencies, conditional logic, and generation:
  * `[PQA]` Protocol Question Answering 
  * `[ORD]` Step Ordering
  * `[ERR]` Error Correction
  * `[GEN]` Protocol Generation
  * `[REA]` Protocol Reasoning
* 🧬 **Broad Domain Coverage:** Data sourced from **5 authoritative repositories** spanning **16 biological subdomains**.
* 🔬 **Standardized Evaluation:** A robust framework combining standard NLP metrics with novel domain-specific measures (e.g., Step Recall, Step Precision).

---

## 🤖 Portable Agent Skill (New!)

> 💡 **Build your own Scientific AI? We've got you covered.**

We have encapsulated our evaluation framework into a self-contained, easily deployable agent skill. 
Located in [`skills/evaluate-protocol-outputs/`](./skills/evaluate-protocol-outputs/), this module can be directly imported into other AI agent environments (e.g., AutoGen, LangChain, or custom frameworks) independently of this repository, while retaining full BioProBench compatibility. 

---

## 📊 Dataset Structure

<div align="center">
  <img src="https://github.com/YuyangSunshine/bioprotocolbench/blob/main/figures/samples.jpg?raw=true" alt="BioProBench Samples" width="900" style="border-radius: 8px;"/>
</div>

BioProBench provides a layered data design to support various model development stages. All data files are rigorously formatted in JSON and split into **Train/Test** sets.

| Task | Description | File Names |
| :--- | :--- | :--- |
| **PQA** | Question Answering | `PQA_train.json`, `PQA_test.json` |
| **ORD** | Step Ordering | `ORD_train.json`, `ORD_test.json` |
| **ERR** | Error Correction | `ERR_train.json`, `ERR_test.json` |
| **GEN** | Protocol Generation | `GEN_train.json`, `GEN_test.json` |
| **REA** | Protocol Reasoning | `REA_train.json`, `REA_test.json` |
| **Corpus**| Full Raw Corpus | `protocols-io.json`, `Nature-Protocols.json`, etc. |

* 📥 **Download Access:** [Hugging Face Repository](https://huggingface.co/BioProBench)

---

## ✏️ Quick Start: Inference & Evaluation

To keep the repository clean, we've organized our inference and evaluation scripts logically. Click to expand the instructions below.

<details>
<summary><b>1. Running Inference (API or Local Models)</b></summary>
<br>

For researchers who wish to reproduce our results or benchmark new models, we provide easy-to-use inference scripts in the `Scripts/` directory.

**Using an API (e.g., OpenAI, Anthropic, Gemini):**
```bash
cd Scripts
python generate_response.py

```

*Configuration in `generate_response.py`:*

```python
API_KEY = 'YOUR_API_KEY'             
BASE_URL = '[https://api.openai.com/v1](https://api.openai.com/v1)' 
MODEL_NAME = 'o3-mini'               
TASK_NAME = 'PQA'  # Options: 'PQA', 'ORD', 'ERR', 'REA-ERR', 'GEN', 'REA-GEN'

```

**Using Local Models (Huggingface):**

```bash
cd Scripts
python generate_response_local.py

```

*Configuration in `generate_response_local.py`:*

```python
MODEL_NAME = 'meta-llama/Meta-Llama-3-8B-Instruct' 
TASK_NAME = 'PQA'                                  
TEST_FILE_PATH = f"../Data/{TASK_NAME.split('-')[-1]}_test.json"

```

</details>

<details>
<summary><b>2. Evaluation</b></summary>
<br>

Each task has a standalone evaluation script in the `Metrics/` directory.

| Task | Script | Output Metrics |
| --- | --- | --- |
| **GEN** | `./Metrics/GEN.py` | BLEU, Keyword-based, Step Recall/Precision |
| **PQA** | `./Metrics/PQA.py` | Accuracy, Brier Score |
| **ERR** | `./Metrics/ERR.py` | Accuracy, Precision, Recall, F1 |
| **ORD** | `./Metrics/ORD.py` | Exact Match, Kendall's tau |
| **REA** | `./Metrics/REA-ERR.py` | Accuracy, Precision, Recall, Consistency |

**Usage Example:**

1. Open the script (e.g., `ERR.py`) and set your model's response path:
```python
output_file_path = "/absolute/path/to/model_response.json" 

```


2. Execute the evaluation:
```bash
cd Metrics
python ERR.py

```

</details>

---

## 🔬 Key Findings & Beyond Benchmarking

After evaluating 12 mainstream open-source and closed-source LLMs (including frontier models), we uncovered critical insights:

* **Surface vs. Deep Understanding:** Top models perform well on qualitative tasks (e.g., ~74% PQA-Acc.), but struggle drastically with quantitative precision and safety awareness.
* **The Generation Bottleneck:** Performance plummets on **Step Ordering** (ORD-EM ~50%) and **Protocol Generation** (GEN-BLEU <15%), highlighting a profound difficulty in managing temporal dependencies and generating coherent procedures.
* **Domain Models Fall Short:** Interestingly, smaller bio-specific models often lag behind general frontier LLMs on complex procedural content, suggesting structural reasoning capacity is as vital as domain vocabulary.

### 🚀 Introducing BioProAgent (ICLR 2026 LLA Workshop)

While BioProBench *diagnoses* the cognitive gaps of LLMs, wet-lab environments demand zero-defect physical execution. To bridge the gap from computer simulation to in vitro experiments, we introduce **BioProAgent**.

By grounding probabilistic LLM reasoning within a deterministic Finite State Machine (FSM) and enforcing a strict **"Design-Verify-Rectify"** workflow, BioProAgent achieves **95.6% physical compliance** and an 88.7% success rate in error recovery.

---

## 📝 More Research from Our Group

Explore our related initiatives pushing the boundaries of AI in science:

* 🧪 **[ChemCoTBench](https://www.google.com/search?q=https://howardli1984.github.io/ChemCoTBench.github.io/)**: A step-by-step, application-oriented benchmark evaluating LLM reasoning in chemical applications.
* 🧬 **[ProLLaMA](https://github.com/PKU-YuanGroup/ProLLaMA)**: A multitask protein language model enhanced by the Evolutionary Protein Generation Framework (EPGF).

---

## 🤝 Contributing & Contact

We welcome contributions! Whether it's adding new protocol sources, creating novel tasks, or improving annotations, your pull requests are highly appreciated.

For dataset access, collaboration inquiries, or support, please reach out to:
📧 **sunshineliuyuyang@gmail.com**

---

## 📜 Citation

If you find our benchmark, datasets, or the overarching BioProProject useful in your research, please consider citing our work:

```bibtex
@inproceedings{liu2026bioprobench,
  title={BioProBench: A Corpus and Benchmark for Biological Protocol Reasoning in Autonomous Science},
  author={Liu, Yuyang and Lv, Liuzhenghao and Zhang, Xiancheng and Wang, Jingya and Yuan, Li and Tian, Yonghong},
  booktitle={Proceedings of the 43rd International Conference on Machine Learning (ICML)},
  year={2026}
}

@inproceedings{liu2026bioproagent,
  title={BioProAgent: Neuro-Symbolic Grounding for Constrained Scientific Planning},
  author={Liu, Yuyang and Wang, Jingya and Lv, Liuzhenghao and Tian, Yonghong},
  booktitle={ACL 2026 Oral},
  year={2026}
}

```
