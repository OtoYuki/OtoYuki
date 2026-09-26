<div align="center">

<img src="assets/banner.png" width="100%" alt="~/s1re.sh $ whoami: Sushant Hona. Systems engineering · Informatics." />

<br/>

**Rust and systems engineer, working where software meets computational biology.**<br/>
<sub>Pipeline cost and performance · protein-structure tooling · Kathmandu, UTC+5:45</sub>

<br/>

<a href="mailto:sushanthona04@gmail.com"><img src="https://img.shields.io/badge/email-sushanthona04%40gmail.com-99920B?style=flat-square&labelColor=141C10&logo=gmail&logoColor=FBFFE1" alt="Email: sushanthona04@gmail.com" /></a>
<a href="https://www.linkedin.com/in/sushanthona"><img src="https://img.shields.io/badge/linkedin-sushanthona-5A6042?style=flat-square&labelColor=141C10" alt="LinkedIn" /></a>
<a href="https://github.com/OtoYuki/nf-audit"><img src="https://img.shields.io/github/v/release/OtoYuki/nf-audit?style=flat-square&label=nf-audit&labelColor=141C10&color=8A9A86&logo=rust&logoColor=FBFFE1" alt="nf-audit latest release" /></a>
<a href="https://github.com/OtoYuki/proteus"><img src="https://img.shields.io/github/v/release/OtoYuki/proteus?style=flat-square&label=proteus&labelColor=141C10&color=8A9A86&logo=rust&logoColor=FBFFE1" alt="proteus latest release" /></a>

</div>

<br/>

### `//` NOW

Where does the compute in a Nextflow run go? A batch scheduler reserves what a task *requests*, not what it uses, and the gap is already recorded in two files every run writes. I wrote [**nf-audit**](https://github.com/OtoYuki/nf-audit) to read them, then ran it over 61 of nf-core/rnaseq's public full-size AWS test runs, five years of releases.

<a href="https://github.com/OtoYuki/nf-audit/blob/main/examples/rnaseq-star_salmon-releases.md"><img src="assets/rnaseq-idle-share.svg" width="100%" alt="Stacked columns for 30 nf-core/rnaseq star_salmon releases, 3.1 to 3.26.0: allocated cost per full-size AWS test run fell from $138.66 to $59.64, while the share reserved and never used stayed between 62% and 68% in 28 of 30 releases. Click for the source table." /></a>

- **62–68% of allocated cost was never used** in 28 of 30 `star_salmon` releases, while the cost of a run fell from $138.66 (3.1) to $59.64 (3.26.0).
- **`QUALIMAP_RNASEQ` requests 6 CPUs and 36 GiB** in every release. No task of it ever averaged more than 1.08 cores.
- **`RSEM_CALCULATEEXPRESSION` hit its 16-hour limit** and failed the `star_rsem` test in four releases. It runs on a 12-CPU / 72 GiB reservation whose completed tasks average a median of 1.04 cores. I reported it in [nf-core/rnaseq#1957](https://github.com/nf-core/rnaseq/issues/1957), and an nf-core member opened [#1959](https://github.com/nf-core/rnaseq/pull/1959) to right-size it.
- **Checked against Nextflow's own accounting:** nf-audit's requested CPU-hours match the report header on all 61 runs, to within 0.1 CPU-hours. That validates the parsing, not the prices.

<sub>Dollar figures use Seqera Compute list rates ($0.10/CPU-h, $0.025/GiB-h) as one yardstick across runs. They are not what AWS billed nf-core. The commands and the report behind every number are in <a href="https://github.com/OtoYuki/nf-audit/tree/main/examples"><code>nf-audit/examples</code></a>.</sub>

<br/>

### `//` UPSTREAM

Issues and pull requests on projects I don't own, newest first. A daily workflow refreshes this list.

<!-- UPSTREAM:START -->
- [nf-core/rnaseq#1957](https://github.com/nf-core/rnaseq/issues/1957): `star_rsem` full-size tests: `RSEM_CALCULATEEXPRESSION` hit its 16 h limit in 3.22.1 and 3.23.0–3.25.0 <sub>issue · open · 2026-09-25</sub>
<!-- UPSTREAM:END -->

<br/>

### `//` PROJECTS

<table>
<tr>
<td width="50%" valign="top">

**[nf-audit](https://github.com/OtoYuki/nf-audit)** &nbsp;<sub>Rust · MIT</sub>

Where the CPU-hours and dollars of a Nextflow run go: per-process cost, unused allocation, retry waste, cost per sample, and a right-sized `nextflow.config`. It reads the trace and report every run already writes, offline, on any executor.

<sub>`inspect` · `analyze` · `compare` · a public 61-run corpus in `examples/`</sub>

</td>
<td width="50%" valign="top">

**[proteus](https://github.com/OtoYuki/proteus)** &nbsp;<sub>Rust · MIT / Apache-2.0</sub>

The protein-engineering design loop as one binary: mutate, fold, batch-QC structures into Parquet, score variants with ESM-2, view them in the terminal or a browser, plus a GA4GH TES 1.1 server.

<sub>Every number that has an independent implementation is checked against it in CI on every push: mdtraj, FreeSASA, cctbx, PLIP.</sub>

</td>
</tr>
</table>

Also: **Press1POS**, an offline-first point of sale for Android in Rust and Tauri, with a device app, sync layer and cloud backend. It is a private repo at [press1-inc](https://press1.dev), where I'm Technical Director.

<br/>

### `//` PRINCIPLES

- **Measure before optimising**, and say what a number does and doesn't show.
- **Check results against an independent implementation** wherever one exists.
- **Offline-first.** Build software that keeps working when the network doesn't.

<br/>

### `//` STACK

<table>
<tr><td><b>Rust</b></td><td>tokio · axum · serde · clap · sqlx · Arrow / Parquet · ratatui · Tauri v2</td></tr>
<tr><td><b>Pipelines</b></td><td>Nextflow · nf-core · execution traces and reports · AWS Batch and Seqera cost models</td></tr>
<tr><td><b>Science</b></td><td>RNA-seq (STAR, Salmon, RSEM) · protein structure QC · ESM-2 variant scoring</td></tr>
<tr><td><b>Backend&nbsp;&amp;&nbsp;infra</b></td><td>PostgreSQL · Railway · Podman / Docker · Tailscale · Linux</td></tr>
<tr><td><b>Also</b></td><td>Python (uv) · TypeScript · Next.js · React</td></tr>
</table>

<br/>

<div align="center">
<img src="assets/s1re-mark-contour-gold.svg" width="40" alt="s1re" />
<br/>
<sub>BSc (Hons) Computing (AI), First Class · <a href="mailto:sushanthona04@gmail.com">sushanthona04@gmail.com</a></sub>
</div>
