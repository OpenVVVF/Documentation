---
doctype: Index
doc_id: OV-DOCS-INDEX
title: OpenVVVF Documentation Index
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-2
  - chassis-size-3
version: "0.1"
prepared: Thomas Liao
reviewed: (not yet reviewed)
date: "2026-07-30"
status: draft
description: Portal to OpenVVVF product documentation, safety analyses, power-stage guides, and software targets.
nav_order: 0
---

# OpenVVVF Documentation

This repository is the single source of truth for OpenVVVF product documentation, shared hardware data, and documentation tooling.

<div class="landing-grid">

<div class="card">
<h3><a href="Platform/Index.html">Platform</a></h3>
<p>Application-independent control-module documentation: safety analyses, compliance mappings, and architecture. Applies to every power stage and application profile.</p>
<ul>
<li><a href="Platform/Safety/HARA/Core.html"><code>OV-HARA-CORE</code></a> — Core platform hazard analysis and safety requirements</li>
<li><a href="Platform/Safety/HARA/ApplicationProfiles/Motorcycle.html"><code>OV-HARA-PROF-MOTO</code></a> — Motorcycle application profile</li>
<li><a href="Platform/Compliance/ISO26262-Mapping.html"><code>OV-COMP-ISO26262</code></a> — ISO 26262 mapping</li>
<li><a href="Platform/Compliance/IEC61800-5-2-Mapping.html"><code>OV-COMP-IEC61800</code></a> — IEC 61800-5-2 safe-function mapping</li>
</ul>
</div>

<div class="card">
<h3><a href="PowerStages/ChassisSize2/Index.html">Power Stages</a></h3>
<p>Physical chassis and inverter variants. Each power stage is a configurable family with its own assembly, thermal, and user documentation.</p>
<ul>
<li><a href="PowerStages/ChassisSize2/Index.html"><code>OV-CHASSIS-C2-INDEX</code></a> — Chassis Size 2 family</li>
<li><a href="PowerStages/ChassisSize3/Index.html"><code>OV-CHASSIS-C3-INDEX</code></a> — Chassis Size 3 family (in development)</li>
</ul>
</div>

<div class="card">
<h3><a href="Software/Index.html">Software</a></h3>
<p>Firmware and host-software documentation by target MCU or tool.</p>
<ul>
<li><a href="Software/MainMCU/Index.html"><code>OV-SW-MAINMCU-INDEX</code></a> — Main MCU (STM32H723ZG)</li>
<li><a href="Software/SafetyCoprocessor/Index.html"><code>OV-SW-COPROC-INDEX</code></a> — Safety Coprocessor (STM32G474)</li>
<li><a href="Software/RTEHost/Index.html"><code>OV-SW-RTE-INDEX</code></a> — RTE Host tools</li>
<li><a href="Software/Codegen/Index.html"><code>OV-SW-CODEGEN-INDEX</code></a> — Codegen tools</li>
</ul>
</div>

<div class="card">
<h3>Product Manuals</h3>
<p>Assembled product manuals are generated from fragments declared in <code>Data/Products/*.yaml</code> and written to <code>build/manuals/</code>.</p>
<ul>
<li><code>OV-MOTO-C2</code> — OpenVVVF Motorcycle Kit (Chassis Size 2)</li>
</ul>
</div>

</div>
