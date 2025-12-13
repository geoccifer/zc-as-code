# Z&C as Code: Automated OT Network Segmentation Compliance

**Zone & Conduit (Z&C) Management via Infrastructure as Code.**

This repository implements a modern, Git-driven workflow for managing Industrial Control System (ICS) network segmentation based on the ISA/IEC 62443 standard. It replaces static diagrams with a validated, machine-readable Data Model.

![Generated Diagram](ICS-2024_6-Purdue-HD-1.png)
*Architecture derived from [Palo Alto Networks: What is the Purdue Model for ICS Security?](https://www.paloaltonetworks.com/cyberpedia/what-is-the-purdue-model-for-ics-security)*

## Why "Z&C as Code"?

Traditional management via static diagrams introduces risk:
*   **Drift**: Diagrams rarely match the actual firewall rules.
*   **Errors**: Manual entry leads to typo-driven security holes.
*   **Invisibility**: You can't "diff" a PDF to see who changed a port.

**Z&C as Code** solves this by treating the architecture as software:
1.  **Define** network intent in `YAML`.
2.  **Validate** integrity with `Pydantic`.
3.  **Visualise** automatically with `Mermaid`.

## Getting Started

### Prerequisites

*   Python 3.8+
*   Node.js & NPM (optional, for PNG generation)

### Installation

```bash
pip install -r requirements.txt
```

## Usage

### 1. The Source of Truth: `ICS-2024_6-Purdue.yaml`
Edit this file to define your Assets (PLCs, HMIs, Servers) and Conduits (Firewall connections).

### 2. Validate Data Integrity
Run the schema validator to ensure no broken links or invalid IPs:

```bash
python validate_schema.py "ICS-2024_6-Purdue.yaml"
```

### 3. Generate Diagram
Create a visual representation of your architecture:

```bash
python yaml_to_mermaid.py
```
*Outputs: `ICS-2024_6-Purdue.md`*

### 4. Render PNG (Optional)
If you need a high-resolution image for presentations:

```bash
npx @mermaid-js/mermaid-cli -i "ICS-2024_6-Purdue.md" -o "ICS-2024_6-Purdue-HD.png" --scale 4 --backgroundColor transparent
```

## Project Structure

*   `ICS-2024_6-Purdue.yaml`: **The Master Data.** Defines Zones, Assets, and Conduits.
*   `validate_schema.py`: **The Gatekeeper.** Python/Pydantic script to enforce rules (Referential Integrity, IP formats).
*   `yaml_to_mermaid.py`: **The Renderer.** Converts YAML to a rich Mermaid.js diagram.

## Future Ideas & Roadmap

The current repository is just the foundation (Phase 1). The goal is to move from "Documentation as Code" to "Security as Code."

*   **NSPM Integration**: Build a pipeline that exports this data model to Network Security Policy Management tools to validate actual firewall rules against the defined intent.
*   **OT Sensor Enrichment**: Expose the Z&C model via a lightweight API. OT sensors (like Nozomi, Dragos, or Claroty) could consume this to automatically tag assets with their intended Zone and Criticality context.
*   **Automated Firewall Config**: Generate vendor-agnostic firewall rules (e.g., via Ansible or Terraform) directly from the Conduits defined in the YAML.
*   **CI/CD Compliance**: Add a GitHub Action that fails a build if a new Asset is added without a valid Zone or Criticality tag.

## Contributing

Contributions are welcome! Whether it's fixing a bug in the Python scripts, improving the Mermaid styling, or adding new validation rules (e.g., checking for overlapping IP ranges).

1.  Fork the project.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

If you have ideas for the roadmap above, feel free to open an Issue to discuss!