<div align="center">
  <img src="https://github.com/YuyangSunshine/bioprotocolbench/blob/main/figures/logo-v3.png?raw=true" alt="BioProBench Logo" width="300"/>
</div>


# BioProBench: Comprehensive Dataset and Benchmark in Biological Protocol Understanding and Reasoning

> **🌟 Part of the [BioProProject Series](https://yuyangsunshine.github.io/BioPro-Project/)**
> 
> Exploring the frontier of LLMs and AI Agents in biological protocol understanding, reasoning, and automated physical execution.

[![ArXiv](https://img.shields.io/badge/ArXiv-paper-B31B1B.svg?logo=arXiv&logoColor=Red)](https://arxiv.org/pdf/2505.07889)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Dataset-FFD210.svg?logo=HuggingFace&logoColor=black)](https://huggingface.co/BioProBench)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/yourusername/bioprotocolbench/pulls)

**BioProBench is the first large-scale, integrated multi-task benchmark for biological protocol understanding and reasoning, specifically designed for large language models (LLMs). It moves beyond simple QA to encompass a comprehensive suite of tasks critical for procedural text comprehension.**

---

## 📖 Overview

Biological protocols are the fundamental bedrock of reproducible and safe life science research. While LLMs have shown remarkable capabilities on general tasks, their systematic evaluation on highly specialized, accuracy-critical, and inherently procedural texts like biological protocols remains limited. BioProBench fills this gap by providing a robust framework to evaluate LLMs on diverse aspects of protocol understanding and reasoning, serving as the foundational evaluation environment for downstream execution agents like our [BioProAgent](https://github.com/YuyangSunshine/bioproagent).

<div align="center">
  <img src="https://github.com/YuyangSunshine/bioprotocolbench/blob/main/figures/overview.png?raw=true" alt="BioProBench Overview" width="1000"/>
</div>

### ✨ Features
* 📚 **Large-scale Data:** Built upon **27K original biological protocols**, yielding nearly **556K high-quality structured instances**.
* 🎯 **Comprehensive Tasks:** A suite of **five core tasks** challenging LLMs on different facets of procedural understanding and generation:
    * Protocol Question Answering (PQA)
    * Step Ordering (ORD)
    * Error Correction (ERR)
    * Protocol Generation (GEN)
    * Protocol Reasoning (REA)
* 🧬 **Broad Domain Coverage:** Data sourced from 6 major repositories and covering **16 biological subdomains**.
* 🔬 **Standardized Evaluation:** A robust framework combining standard NLP metrics with novel domain-specific measures for accurate performance quantification.
  
---


## 🚀 Motivation

Biological protocols are the operational blueprint for experiments. As biological research increasingly leverages automation and AI, the ability of AI systems to understand and reason about these complex procedures is paramount. Current LLMs, while powerful, face significant challenges:

* Limited Procedural Understanding:
* LLMs struggle with the temporal dependencies, conditional logic, and specific requirements embedded within protocols.
* Lack of Systematic Evaluation: There has been a lack of large-scale, multi-task benchmarks specifically designed to diagnose LLMs' limitations on procedural biological texts.
* Bridging the Gap: Developing AI systems capable of safely automating and even optimizing experiments requires models that can reliably interpret and generate protocols.

BioProBench addresses these challenges by providing the necessary data and tasks for comprehensive evaluation and driving the development of more capable models.

---

## 📊 Dataset Structure

<div align="center">
  <img src="https://github.com/YuyangSunshine/bioprotocolbench/blob/main/figures/samples.jpg?raw=true" alt="BioProBench Logo" width="1000"/>
</div>

BioProBench provides a layered data design to support various model development stages:

* A raw corpus of **27K protocols** for pretraining or RAG applications.
* A substantial downstream **training set of over 550K structured instances** across the five fine-grained tasks for model adaptation.
* A held-out **test set of 1,000 examples per task** for standardized benchmarking.

The dataset and code are publicly available:

* **Code Repository:** [https://github.com/YuyangSunshine/bioprotocolbench](https://github.com/YuyangSunshine/bioprotocolbench/)
* **Hugging Face Dataset:** [https://huggingface.co/BioProBench](https://huggingface.co/BioProBench)

---

## ✏️ Inference

For researchers who wish to reproduce our results or test on models not covered in this paper, we provide an easy-to-use inference script in **Scripts/** directory.

Researchers can choose to run inference tests using either the **API** or a **local model** (e.g., via Huggingface Transformers).

#### Use API:

```
cd Scripts
python generate_response.py
```

Before doing so, you need to modify the content of `generate_response.py` to specify your API key, model name, base URL, and other configuration details：
```
# ================================
# User Configuration
# ================================
        
API_KEY = 'YOUR API-KEY'       # Replace this with your API key
BASE_URL = 'https://api.openai.com/v1'  # Replace with your base URL if different
MODEL_NAME = 'o3-mini'              # Replace with your preferred model
TASK_NAME = 'PQA'                   # Task name used in file paths ('PQA', 'ORD', 'ERR', 'REA-ERR', 'GEN', 'REA-GEN')
```

#### Use Local Models:

```
cd Scripts
python generate_response_local.py
```

Before doing so, you need to modify the content of `generate_response_local.py` to specify your model name and other configuration details：
```
# ================================
# User Configuration
# ================================

MODEL_NAME = 'meta-llama/Meta-Llama-3-8B-Instruct'                 # or other models from huggingface or local path
TASK_NAME = 'PQA'                   # Task name used in file paths ('PQA', 'ORD', 'ERR', 'REA-ERR', 'GEN', 'REA-GEN')
TEST_FILE_PATH = f"../Data/{TASK_NAME.split('-')[-1]}_test.json"
```

---

## 🧪 Evaluation Metrics

We employ a hybrid evaluation framework that combines standard NLP metrics with novel domain-specific measures to accurately quantify model performance across all tasks.

Each task in BioProBench includes standalone evaluation codes within the **Metrics/** directory. To evaluate your model's outputs (Assert model's output is stored in 'generated_response' of each item of JSON file):

#### ✅ Step 1: Locate the evaluation file

Each task corresponds to one script:

| Task                         | Codes       | Metrics     |
| ---------------------------- | ------------ |------------ |
| Protocol Generation (GEN)    | `./Metrics/GEN.py`     |BLEU, Keyword-based, Embedding-based, etc. |
| Protocol QA (PQA)            | `./Metrics/PQA.py`     |Accuracy, Brier Score, etc. |
| Error Correction (ERR)       | `./Metrics/ERR.py`     |Accuracy, Precision, Recall, F1, etc. |
| Step Ordering (ORD)          | `./Metrics/ORD.py`     |Exact Match, Kendall's tau, etc. |
| Experimental Reasoning (REA) | `./Metrics/REA-ERR.py` |Accuracy, Precision, Recall, F1, Consistency, etc. |


#### ✅ Step 2: Modify the script

Open the corresponding evaluation script (e.g., `ERR.py`) and **manually set** the file path to your model’s reponse:

```python
# Inside ERR.py

def main():
    output_file_path = "/absolute/path/to/model_response.json"  # ← Replace this!
    ...
```

Example:

```python
output_file_path = "./ERR_test_o3-mini.json"
```

Then run the script:

```
cd Metrics
python ERR.py
```


#### Output Metrics

Each script prints evaluation results such as:

* Accuracy, Precision, Recall, F1
* Step-level metrics (e.g., Step Recall, Redundancy Penalty)
* Ordering metrics (e.g., Kendall’s Tau)
* Parsing failure rates

#### Portable Agent Skill

We also provide a self-contained evaluation skill in [`skills/evaluate-protocol-outputs/`](./skills/evaluate-protocol-outputs/). It can be copied into other agent environments and used independently of this repository, while retaining a BioProBench-compatible profile.

---

#### 🔬 Key Findings
We evaluated 12 mainstream open-source and closed-source LLMs on BioProBench. Our key findings reveal significant insights into the current capabilities and limitations of LLMs on biological protocols:

* Surface vs. Deep Understanding: While top models perform reasonably well on tasks requiring surface understanding like Protocol Question Answering (e.g., ~70% PQA-Acc.) and Error Correction (e.g., >64% ERR F1), they struggle significantly with tasks demanding deeper procedural understanding and structured generation.
* Challenges in Reasoning and Generation: Performance drops considerably on Step Ordering (e.g., ORD-EM ~50%) and Protocol Generation (e.g., GEN-BLEU <15%), highlighting the difficulty for LLMs in managing temporal dependencies and generating coherent, accurate procedures.
* Model Variances: Comparisons show diverse performance across models. Certain open-source models approach the performance of closed-source models on some tasks, while smaller, bio-specific models often lag behind general LLMs on complex procedural content, suggesting limitations in capacity for capturing intricate dependencies.

Overall, our findings underscore that robust procedural reasoning within biological protocols represents a significant challenge for current LLMs.

---

#### 🤖 Beyond Benchmarking: BioProAgent
> 🎉 Accepted by ICLR 2026 LLA Workshop

While BioProBench diagnoses the cognitive gaps of LLMs, wet-lab environments demand zero-defect physical execution where hallucinations can cause catastrophic equipment damage.

To bridge the gap from computer simulation predictions to in vitro physical experiments, we introduce BioProAgent. Evaluated on the extended BioProBench, BioProAgent grounds probabilistic LLM reasoning within a deterministic Finite State Machine (FSM), enforcing a strict **"Design-Verify-Rectify"** workflow.

It achieves **95.6%** physical compliance and an 88.7% success rate in error recovery, demonstrating that neuro-symbolic constraints are essential for reliable autonomy in irreversible physical environments.

---


## 🤝 Contributing
We welcome contributions to enhance BioProBench, including:
  - New protocol sources
  - 🧪 Additional biological domains
  - 🧠 Novel evaluation tasks
  - 📝 Annotation improvements

---

## 📜 Citation

If you find our benchmark or the overarching BioProProject useful, please consider citing our work:

```bibtex
@article{liu2025bioprobench,
  title={BioProBench: Comprehensive Dataset and Benchmark in Biological Protocol Understanding and Reasoning},
  author={Liu, Yuyang and Lv, Liuzhenghao and Zhang, Xiancheng and Yuan, Li and Tian, Yonghong},
  journal={arXiv preprint arXiv:2505.07889},
  year={2025}
}

@article{liu2026bioproagent,
  title={BioProAgent: Neuro-Symbolic Grounding for Constrained Scientific Planning},
  author={Liu, Yuyang and Wang, Jingya and Lv, Liuzhenghao and Tian, Yonghong},
  journal={arXiv preprint arXiv:2603.00876},
  year={2026}
}
```
---

## 📝 More Research

The following are two important works of our group:

* **ChemCoTBench**: A step-by-step, application-oriented, and high-quality benchmark for evaluating LLM reasoning in chemical applications, click to view the [leaderboard](https://howardli1984.github.io/ChemCoTBench.github.io/#leaderboard)。
* **ProLLaMA**: A multitask protein language model enhanced by the Evolutionary Protein Generation Framework (EPGF), the project code is on [GitHub](https://github.com/PKU-YuanGroup/ProLLaMA)。

---

## 📧 Contact
For dataset access or collaboration inquiries:
sunshineliuyuyang@gmail.com

