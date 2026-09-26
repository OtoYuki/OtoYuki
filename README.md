<div align="center">

<img src="assets/banner.png" width="100%" alt="~/s1re.sh $ whoami: Sushant Hona. Systems engineering · Informatics." />

<br/>

**Rust and systems engineer. I measure what Nextflow pipelines cost, process by process, then make them cost less.**<br/>
<sub>Technical Director at <a href="https://press1.dev">press1-inc</a> · Kathmandu, UTC+5:45 · taking contract work</sub>

<br/>

<a href="#-engagements"><img src="https://img.shields.io/badge/status-taking%20contract%20work-D8A664?style=flat-square&labelColor=141C10" alt="Status: taking contract work" /></a>
<a href="mailto:sushanthona04@gmail.com"><img src="https://img.shields.io/badge/email-sushanthona04%40gmail.com-99920B?style=flat-square&labelColor=141C10&logo=gmail&logoColor=FBFFE1" alt="Email: sushanthona04@gmail.com" /></a>
<a href="https://github.com/OtoYuki/nf-audit"><img src="https://img.shields.io/github/v/release/OtoYuki/nf-audit?style=flat-square&label=nf-audit&labelColor=141C10&color=8A9A86&logo=rust&logoColor=FBFFE1" alt="nf-audit latest release" /></a>
<a href="https://github.com/OtoYuki/proteus"><img src="https://img.shields.io/github/v/release/OtoYuki/proteus?style=flat-square&label=proteus&labelColor=141C10&color=8A9A86&logo=rust&logoColor=FBFFE1" alt="proteus latest release" /></a>
<a href="https://www.linkedin.com/in/sushanthona"><img src="https://img.shields.io/badge/linkedin-sushanthona-5A6042?style=flat-square&labelColor=141C10" alt="LinkedIn" /></a>

</div>

<br/>

### `//` NOW

**Pipeline cost and performance, measured.** A batch scheduler reserves what a task *requests*, not what it uses, and the gap is already recorded in two files every Nextflow run writes. I built [**nf-audit**](https://github.com/OtoYuki/nf-audit) to read them, then pointed it at 61 of nf-core/rnaseq's public full-size AWS test runs, five years of releases.

<a href="https://github.com/OtoYuki/nf-audit/blob/main/examples/rnaseq-star_salmon-releases.md"><img src="assets/rnaseq-idle-share.svg" width="100%" alt="Stacked columns for 30 nf-core/rnaseq star_salmon releases, 3.1 to 3.26.0: allocated cost per full-size AWS test run fell from $138.66 to $59.64, while the share reserved and never used stayed between 62% and 68% in 28 of 30 releases. Click for the source table." /></a>

- **62–68% of allocated cost was never used**, in 28 of 30 `star_salmon` releases, while the cost of a run fell from $138.66 (3.1) to $59.64 (3.26.0).
- **`QUALIMAP_RNASEQ` requests 6 CPUs and 36 GiB** in every release. No task of it ever averaged more than 1.08 cores.
- **`RSEM_CALCULATEEXPRESSION` hit its 16-hour limit** and failed the `star_rsem` test in four releases, on a 12-CPU / 72 GiB reservation whose completed tasks average a median of 1.04 cores. I reported it in [nf-core/rnaseq#1957](https://github.com/nf-core/rnaseq/issues/1957). An nf-core member confirmed the numbers and opened [#1959](https://github.com/nf-core/rnaseq/pull/1959) to right-size it.
- **The parsing is checked:** nf-audit's requested CPU-hours match the figure in Nextflow's own report header on all 61 runs, to within 0.1 CPU-hours.

<sub>Dollar figures use Seqera Compute list rates ($0.10/CPU-h, $0.025/GiB-h) as one yardstick across runs. They are not what AWS billed nf-core. Every number, with the command and report behind it, is in <a href="https://github.com/OtoYuki/nf-audit/tree/main/examples"><code>nf-audit/examples</code></a>.</sub>

**→ Send me a trace.** The `execution_trace_*.txt` and `execution_report_*.html` from one recent run are enough, and I don't need access to your code. I'll tell you within a day whether an audit is worth your money: [sushanthona04@gmail.com](mailto:sushanthona04@gmail.com)

<br/>

### `//` PROOF

<table>
<tr>
<td width="50%" valign="top">

**[nf-audit](https://github.com/OtoYuki/nf-audit)** &nbsp;<sub>Rust · MIT</sub>

Where the CPU-hours and dollars of a Nextflow run go: per-process cost, unused allocation, retry waste, cost per sample, and a right-sized `nextflow.config`. Reads the trace and report every run already writes. Offline, on any executor.

<sub>`inspect` · `analyze` · `compare` · a public 61-run corpus in `examples/`</sub>

</td>
<td width="50%" valign="top">

**[proteus](https://github.com/OtoYuki/proteus)** &nbsp;<sub>Rust · MIT / Apache-2.0</sub>

The protein-engineering design loop as one binary: mutate, fold, batch-QC structures into Parquet, score variants with ESM-2, view them in the terminal or a browser, plus a GA4GH TES 1.1 server.

<sub>Every number that has an independent implementation is checked against it in CI on every push: mdtraj, FreeSASA, cctbx, PLIP.</sub>

</td>
</tr>
<tr>
<td width="50%" valign="top">

**Press1POS** &nbsp;<sub>Rust · Tauri v2 · React · private</sub>

Offline-first point of sale for Android: device app, sync layer, Railway backend and owner portal. I led it end to end as Technical Director at [press1-inc](https://press1.dev). It is in live testing in US stores.

<sub>Code review on every change, mine included. Architecture decisions recorded in the repo.</sub>

</td>
<td width="50%" valign="top">

**[nf-core/rnaseq#1957](https://github.com/nf-core/rnaseq/issues/1957)** &nbsp;<sub>upstream issue</sub>

`RSEM_CALCULATEEXPRESSION` timing out at 16 h in the full-size `star_rsem` tests of 3.22.1 and 3.23.0–3.25.0. The evidence came from the public megatest reports, alongside a local benchmark of the RSEM command at 1–12 threads.

<sub>Fix in review upstream: <a href="https://github.com/nf-core/rnaseq/pull/1959">#1959</a> (72 GB → 16 GB, 16 h → 24 h).</sub>

</td>
</tr>
</table>

<br/>

### `//` ENGAGEMENTS

Fixed fee, agreed before work starts. Every proposal states what will be measured and how.

| Engagement | What you get | Time | Fee |
|---|---|---|---|
| **Diagnostic** | One production pipeline profiled on your data and infrastructure. You get cost and wall time by process, a ranked list of fixes with the projected saving on each, and a 45-minute readout. | 5 business days | $1,200, credited against the next tier |
| **Audit & fix** | The diagnostic, plus the top fixes implemented: resource right-sizing, spot and retry strategy, storage and staging layout, container and executor configuration. You get before-and-after benchmarks on your own data and a handover document. | 3–4 weeks | $4,500, 50% on signature |
| **Hot-path rewrite** | One bottleneck step reimplemented in Rust, benchmarked against the incumbent on your data, tested, containerised, and dropped into your workflow with nothing else changed. | 6 weeks | from $8,000, 50% on signature |

Also available by the hour for Rust backend and performance work on existing services. Contracts and invoices in USD, by wire or Payoneer.

<br/>

### `//` METHOD

- **I measure before I touch anything**, and I don't promise percentages I haven't seen on your data.
- **Scope in writing** before work starts, and a short written update at every milestone.
- **Every change reviewed and benchmarked**, with a handover document at the end.
- **Offline-first by default.** I build systems that keep working when the network doesn't.

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

### `//` RECORD

- **Technical Director, [press1-inc](https://press1.dev).** I run a five-person team working with US stakeholders. I wrote the company's founding charter, engineering constitution and review process, and led Press1POS. The team also shipped [deliverykingco.com](https://deliverykingco.com).
- **BSc (Hons) Computing (AI), First Class.** London Metropolitan University, taught at Islington College, 2025.
- **Kathmandu, UTC+5:45.** Daily overlap from 8am to 1pm US Eastern.

<br/>

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/s1re-mark-contour-cream.svg" />
  <img src="assets/s1re-mark-contour-ink.svg" width="40" alt="s1re" />
</picture>
<br/>
<sub>Send a trace file. I reply within a day. · <a href="mailto:sushanthona04@gmail.com">sushanthona04@gmail.com</a></sub>
</div>
