# Benchmark Suites Reference

Publicly available, citable benchmark suites organized by workload domain. Always prefer these over synthetic/generated data for research credibility and reproducibility.

## Selection Guidelines

| Workload Domain | Recommended Suite | Why |
|----------------|-------------------|-----|
| SpMV / SpMM / Sparse LA | SuiteSparse Matrix Collection | Industry standard, 2900+ real matrices, widely cited |
| Graph traversal / analytics | SNAP datasets | Real social/web/bio networks, standard in graph research |
| Graph benchmarking | LDBC Social Network Benchmark | Standardized graph workloads with defined metrics |
| Graph generation | Graph500 RMAT | Reproducible synthetic graphs with controlled properties |
| Deep learning inference | MLPerf Inference | Industry consortium benchmark, peer-reviewed methodology |
| DL model benchmarking | torchbench | PyTorch-maintained, covers diverse model architectures |
| HPC kernels | Rodinia / Parboil / PolyBench/GPU | Classic GPU benchmark suites, heavily cited in HPC |
| Ray tracing / tree traversal | Blender / PBRT benchmark scenes | Standard rendering benchmarks |
| Recommendation systems | Criteo Terabyte / DLRM configs | Industry-standard recommendation workloads |

---

## 1. Sparse Linear Algebra

### SuiteSparse Matrix Collection (formerly UF Sparse Matrix Collection)

- **Domain**: Sparse matrix computations (SpMV, SpMM, sparse solvers)
- **URL**: https://sparse.tamu.edu/
- **Size**: 2,900+ matrices from real applications (FEM, circuit sim, web graphs, etc.)
- **Citation**:
```bibtex
@article{davis2011university,
  title={The University of Florida Sparse Matrix Collection},
  author={Davis, Timothy A. and Hu, Yifan},
  journal={ACM Transactions on Mathematical Software},
  volume={38},
  number={1},
  pages={1--25},
  year={2011},
  publisher={ACM}
}
```

**Recommended matrices for SpMV benchmarking:**

| Matrix | Rows | NNZ | Domain | Notes |
|--------|------|-----|--------|-------|
| `cage15` | 5.15M | 99.2M | DNA electrophoresis | Large, irregular |
| `ldoor` | 952K | 42.5M | Structural mechanics | Symmetric, well-conditioned |
| `webbase-1M` | 1M | 3.1M | Web graph | Very sparse, power-law |
| `cant` | 62K | 4.0M | FEM cantilever | Small, dense blocks |
| `pdb1HYS` | 36K | 4.3M | Protein data bank | Symmetric, moderate |
| `consph` | 83K | 6.0M | FEM sphere | Symmetric |
| `cop20k_A` | 121K | 2.6M | FEM | Irregular |
| `rma10` | 47K | 2.3M | 3D reservoir model | Nonsymmetric |
| `shipsec1` | 141K | 7.8M | Ship structure | Symmetric, large blocks |
| `scircuit` | 171K | 959K | Circuit simulation | Very sparse |

**Download and load:**
```bash
# Download a specific matrix (Matrix Market format)
wget https://sparse.tamu.edu/MM/DNVS/shipsec1.tar.gz
tar xzf shipsec1.tar.gz

# Or download via ssgetpy (Python)
pip install ssgetpy
```

```python
import scipy.io
import scipy.sparse
import ssgetpy

# Method 1: ssgetpy (recommended)
results = ssgetpy.search(name='cage15')
results[0].download(destpath='./matrices', extract=True)

# Method 2: Direct Matrix Market loading
matrix = scipy.io.mmread('cage15/cage15.mtx')
csr = scipy.sparse.csr_matrix(matrix)

print(f"Shape: {csr.shape}, NNZ: {csr.nnz}")
print(f"Density: {csr.nnz / (csr.shape[0] * csr.shape[1]):.6f}")
print(f"Avg NNZ/row: {csr.nnz / csr.shape[0]:.1f}")
```

---

## 2. Graph Analytics

### SNAP (Stanford Network Analysis Project)

- **Domain**: Real-world network datasets (social, web, biological, infrastructure)
- **URL**: https://snap.stanford.edu/data/
- **Size**: 80+ datasets, from thousands to billions of edges
- **Citation**:
```bibtex
@misc{snapnets,
  title={SNAP Datasets: Stanford Large Network Dataset Collection},
  author={Leskovec, Jure and Krevl, Andrej},
  howpublished={\url{https://snap.stanford.edu/data}},
  year={2014}
}
```

**Recommended datasets:**

| Dataset | Nodes | Edges | Type |
|---------|-------|-------|------|
| `web-Google` | 876K | 5.1M | Directed web graph |
| `com-Orkut` | 3.1M | 117M | Undirected social network |
| `soc-LiveJournal1` | 4.8M | 69M | Directed social network |
| `roadNet-CA` | 2.0M | 5.5M | Undirected road network |
| `wiki-Talk` | 2.4M | 5.0M | Directed communication |

**Download and load:**
```bash
wget https://snap.stanford.edu/data/web-Google.txt.gz
gunzip web-Google.txt.gz
```

```python
import numpy as np
import scipy.sparse

# Load edge list (skip comment lines starting with #)
edges = np.loadtxt('web-Google.txt', comments='#', dtype=np.int64)
rows, cols = edges[:, 0], edges[:, 1]
n = max(rows.max(), cols.max()) + 1
adj = scipy.sparse.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))

print(f"Nodes: {n}, Edges: {adj.nnz}")
```

### LDBC Social Network Benchmark

- **Domain**: Graph database and analytics benchmarking
- **URL**: https://ldbcouncil.org/benchmarks/snb/
- **Size**: Configurable scale factors (SF1 to SF10000)
- **Citation**:
```bibtex
@article{angles2020ldbc,
  title={The LDBC Social Network Benchmark},
  author={Angles, Renzo and others},
  journal={arXiv preprint arXiv:2001.02299},
  year={2020}
}
```

### Graph500 RMAT Generators

- **Domain**: Synthetic graph generation with controllable properties
- **URL**: https://graph500.org/
- **Use case**: When you need reproducible synthetic graphs with power-law degree distributions
- **Citation**:
```bibtex
@inproceedings{murphy2010introducing,
  title={Introducing the Graph 500},
  author={Murphy, Richard C. and others},
  booktitle={Cray User's Group (CUG)},
  year={2010}
}
```

---

## 3. Deep Learning Inference

### MLPerf Inference

- **Domain**: DL inference latency and throughput benchmarking
- **URL**: https://mlcommons.org/benchmarks/inference-datacenter/
- **Size**: Multiple model categories (vision, NLP, recommendation, medical)
- **Citation**:
```bibtex
@article{reddi2020mlperf,
  title={MLPerf Inference Benchmark},
  author={Reddi, Vijay Janapa and others},
  journal={arXiv preprint arXiv:1911.02549},
  year={2020}
}
```

### torchbench

- **Domain**: PyTorch model benchmarking
- **URL**: https://github.com/pytorch/benchmark
- **Size**: 50+ models covering vision, NLP, audio, generative
- **Download:**
```bash
git clone https://github.com/pytorch/benchmark.git
cd benchmark
pip install -e .
```

---

## 4. HPC Kernels

### Rodinia

- **Domain**: GPU computing benchmark suite (structured/unstructured grids, data mining, etc.)
- **URL**: https://rodinia.cs.virginia.edu/
- **Citation**:
```bibtex
@inproceedings{che2009rodinia,
  title={Rodinia: A Benchmark Suite for Heterogeneous Computing},
  author={Che, Shuai and others},
  booktitle={IEEE IISWC},
  year={2009}
}
```

### Parboil

- **Domain**: Throughput computing benchmarks
- **URL**: http://impact.crhc.illinois.edu/parboil/parboil.aspx
- **Citation**:
```bibtex
@inproceedings{stratton2012parboil,
  title={Parboil: A Revised Benchmark Suite for Scientific and Commercial Throughput Computing},
  author={Stratton, John A. and others},
  journal={IMPACT Technical Report},
  year={2012}
}
```

### PolyBench/GPU

- **Domain**: Polyhedral compilation benchmarks ported to GPU
- **URL**: https://github.com/sgrauerg/polybenchGpu
- **Citation**:
```bibtex
@article{grauer2012auto,
  title={Auto-parallelization of PolyBench Benchmarks on GPU},
  author={Grauer-Gray, Scott and others},
  year={2012}
}
```

---

## 5. Ray Tracing / Tree Traversal

### Blender Benchmark Scenes

- **Domain**: Path tracing / ray tracing performance
- **URL**: https://opendata.blender.org/
- **Scenes**: Monster, Junkshop, Classroom, Barcelona Pavilion

### PBRT Test Scenes

- **Domain**: Physically-based rendering research
- **URL**: https://pbrt.org/scenes-v4
- **Citation**:
```bibtex
@book{pharr2023physically,
  title={Physically Based Rendering: From Theory to Implementation},
  author={Pharr, Matt and Jakob, Wenzel and Humphreys, Greg},
  edition={4th},
  year={2023},
  publisher={MIT Press}
}
```

---

## 6. Recommendation Systems

### Criteo Terabyte

- **Domain**: Click-through rate prediction
- **URL**: https://ailab.criteo.com/download-criteo-1tb-click-logs-dataset/
- **Size**: ~1TB, 4 billion examples, 13 integer + 26 categorical features
- **Citation**:
```bibtex
@misc{criteo2014terabyte,
  title={Criteo 1TB Click Logs Dataset},
  author={{Criteo AI Lab}},
  year={2014},
  howpublished={\url{https://ailab.criteo.com/}}
}
```

### DLRM Benchmark Configs

- **Domain**: Deep Learning Recommendation Model
- **URL**: https://github.com/facebookresearch/dlrm
- **Citation**:
```bibtex
@article{naumov2019deep,
  title={Deep Learning Recommendation Model for Personalization and Recommendation Systems},
  author={Naumov, Maxim and others},
  journal={arXiv preprint arXiv:1906.00091},
  year={2019}
}
```

### Avazu

- **Domain**: Click-through rate prediction (mobile ads)
- **URL**: https://www.kaggle.com/c/avazu-ctr-prediction/data
- **Size**: ~40M examples, 23 features

---

## Usage Notes

1. **Always cite the benchmark suite** in your report — this is what gives results credibility
2. **Document the exact version/subset** used (e.g., "SuiteSparse cage15, downloaded 2025-01-15")
3. **Include download commands** in your scripts for reproducibility
4. **Verify data integrity** after download (check dimensions, NNZ, checksums if available)
5. **Use multiple matrices/datasets** to show results aren't specific to one input
