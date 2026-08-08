---
doctype: Index
doc_id: OV-DOCS-INDEX
title: OpenVVVF Documentation Index
product_line: openvvvf
applies_to:
  - openvvvf-control-module
  - chassis-size-1
  - chassis-size-2
  - chassis-size-3
version: "0.1"
reviewed: (not yet reviewed)
date: "2026-08-08"
status: draft
description: Portal to OpenVVVF product documentation, safety analyses, power-stage guides, software targets, and test evidence.
nav_order: 0
---

> **Draft v0.1**
> This documentation site is a work in progress. Pages that are still empty or under revision are marked with a **WIP** badge in the sidebar and on the index cards below.

# OpenVVVF Documentation

This repository is the single source of truth for OpenVVVF documentation.

<div class="card">
<h3>Getting Started</h3>
<ul>
<li><strong>New users</strong> - read the <a href="System-Architecture/index.html">System Architecture</a> overview and the <a href="Glossary/index.html">Glossary</a> first.</li>
<li><strong>Installers / Technicians</strong> - go to <a href="Power-Stages/index.html">Power Stages</a> to choose the correct chassis, then open its integration or assembly guide.</li>
<li><strong>Developers</strong> - see the <a href="Control-Assembly/index.html">Control Assembly</a>, <a href="Software/index.html">Software</a>, and <a href="Tools/index.html">Tools</a> sections.</li>
<li><strong>Safety / Compliance Reviewers</strong> - begin with the <a href="Safety-and-Compliance/HARA/Core/index.html">HARA Core</a> and <a href="Safety-and-Compliance/Compliance/index.html">Compliance</a> docs.</li>
</ul>
</div>

<div class="landing-grid">

<div class="card">
<h3><a href="System-Architecture/index.html">System Architecture</a></h3>
<p>Bird's-eye view of the OpenVVVF ecosystem: control module, power stages, software targets, and application profiles.</p>
</div>

<div class="card">
<h3><a href="Glossary/index.html">Glossary</a></h3>
<p>Definitions for RTE, HARA, TARA, HVIL, VCU, and other terms used across the docs.</p>
</div>

<div class="card">
<h3><a href="Control-Assembly/index.html">Control Assembly</a></h3>
<p>The reusable inverter brain. User hardware manual and software manual.</p>
<ul>
<li><a href="Control-Assembly/User-Hardware-Manual/index.html"><code>OV-CA-UHW-INDEX</code></a> - User Hardware Manual <span class="status-badge status-draft">WIP</span></li>
<li><a href="Control-Assembly/Software-Manual/index.html"><code>OV-CA-SWM-INDEX</code></a> - Software Manual <span class="status-badge status-draft">WIP</span></li>
</ul>
</div>

<div class="card">
<h3><a href="Power-Stages/index.html">Power Stages</a></h3>
<p>Physical chassis/inverter assemblies. Each chassis family has a user manual and an assembly guide.</p>
<ul>
<li><a href="Power-Stages/C1/index.html"><code>OV-C1-INDEX</code></a> - Chassis Size 1 <span class="status-badge status-draft">WIP</span></li>
<li><a href="Power-Stages/C2/index.html"><code>OV-C2-INDEX</code></a> - Chassis Size 2 <span class="status-badge status-draft">WIP</span></li>
<li><a href="Power-Stages/C3/index.html"><code>OV-C3-INDEX</code></a> - Chassis Size 3 <span class="status-badge status-draft">WIP</span></li>
</ul>
</div>

<div class="card">
<h3><a href="Safety-and-Compliance/index.html">Safety and Compliance</a></h3>
<p>Hazard analyses and compliance mappings.</p>
<ul>
<li><a href="Safety-and-Compliance/HARA/Core/index.html"><code>OV-SAF-HARA-CORE</code></a> - HARA Core <span class="status-badge status-draft">WIP</span></li>
<li><a href="Safety-and-Compliance/HARA/Application-Profiles/Motorcycle/index.html"><code>OV-SAF-HARA-PROF-MOTO</code></a> - Motorcycle Application Profile</li>
<li><a href="Safety-and-Compliance/Compliance/index.html"><code>OV-COMP-INDEX</code></a> - Compliance</li>
</ul>
</div>

<div class="card">
<h3><a href="Software/index.html">Software</a></h3>
<p>Firmware and host-software documentation by target.</p>
<ul>
<li><a href="Software/Main-MCU/index.html"><code>OV-SW-MAINMCU-INDEX</code></a> - Main MCU</li>
<li><a href="Software/Safety-Coprocessor/index.html"><code>OV-SW-COPROC-INDEX</code></a> - Safety Coprocessor</li>
<li><a href="Software/RTE-Host/index.html"><code>OV-SW-RTE-INDEX</code></a> - RTE Host</li>
<li><a href="Software/Codegen/index.html"><code>OV-SW-CODEGEN-INDEX</code></a> - Codegen <span class="status-badge status-draft">WIP</span></li>
</ul>
</div>

<div class="card">
<h3><a href="Testing/index.html">Testing and Validation</a></h3>
<p>Formal test reports and validation evidence.</p>
<ul>
<li><a href="Testing/Hardware/Motor-Calibration/index.html"><code>OV-TEST-HW-MOTOR-CAL-INDEX</code></a> - Motor Calibration Validation</li>
<li><a href="Testing/Hardware/Motor-Calibration/Resistance.html"><code>OV-TEST-HW-MOTOR-RES-CAL</code></a> - Motor Resistance Calibration Validation</li>
<li><a href="Testing/Hardware/Motor-Calibration/Inductance.html"><code>OV-TEST-HW-MOTOR-IND-CAL</code></a> - Motor Inductance Calibration Validation <span class="status-badge status-draft">WIP</span></li>
</ul>
</div>

<div class="card">
<h3><a href="Tools/index.html">Tools</a></h3>
<p>Support utilities and widgets for working with OpenVVVF.</p>
<ul>
<li><a href="Tools/Telemetry-Plotting/index.html"><code>OV-TOOLS-RTEPLOT</code></a> - Telemetry Plotting</li>
</ul>
</div>

</div>

<div class="sponsors">

<h2>Sponsors</h2>

A special thank you to our sponsors for helping make this project possible:

<div class="sponsor-logos">
  <a href="https://mouser.com"><img src="https://cdn.trustedparts.com/company/dd042a20-7bd6-4e96-92c0-203775acde0d-mouser-logo.svg" alt="Mouser Electronics"></a>
  &nbsp;&nbsp;
  <a href="https://www.mitsubishielectric.com/semiconductors/powerdevices/"><img src="https://upload.wikimedia.org/wikipedia/commons/1/10/Mitsubishi_Electric_logo.svg" alt="Mitsubishi Electric"></a>
  &nbsp;&nbsp;
  <a href="https://sendcutsend.com/"><img src="https://sendcutsend.com/wp-content/uploads/2022/11/scs-logo-text-1-1.svg" alt="SendCutSend"></a>
</div>

</div>
