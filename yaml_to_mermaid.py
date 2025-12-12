import yaml
import argparse
import sys
import os

# Config - Defaults
DEFAULT_INPUT_YAML = "ICS-2024_6-Purdue.yaml"
DEFAULT_OUTPUT_FILE = "ICS-2024_6-Purdue.md"

def generate_mermaid(input_file, output_file):
    print(f"Reading from {input_file}...")
    try:
        # 1. Load the YAML file
        with open(input_file, 'r') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)

    # Detect output format
    is_markdown = output_file.lower().endswith('.md')
    
    mermaid_lines = []
    if is_markdown:
        mermaid_lines.append("```mermaid")
    
    mermaid_lines.append("flowchart TD")
    
    # 2. Add Class Definitions (Styling)
    mermaid_lines.append("    %% Classes definitions")
    mermaid_lines.append("    classDef internet fill:#4fc3f7,stroke:#333,stroke-width:2px,color:black")
    mermaid_lines.append("    classDef firewall fill:#e64a19,stroke:#333,stroke-width:2px,color:white")
    mermaid_lines.append("    classDef level4 fill:#e0e0e0,stroke:#333,stroke-width:2px")
    mermaid_lines.append("    classDef level3 fill:#eeeeee,stroke:#333,stroke-width:2px")
    mermaid_lines.append("    classDef level2 fill:#f5f5f5,stroke:#333,stroke-width:2px")
    mermaid_lines.append("    classDef level1 fill:#fafafa,stroke:#333,stroke-width:2px")
    mermaid_lines.append("    classDef level0 fill:#ffffff,stroke:#333,stroke-width:2px")
    mermaid_lines.append("    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px")

    # Map YAML style keys to Mermaid classes
    style_map = {
        "internet": "internet",
        "firewall": "firewall",
        "level_4": "level4",
        "level_3": "level3",
        "level_2": "level2",
        "level_1": "level1",
        "level_0": "level0"
    }

    # Zone Background Colors (Map ID to fill color/style)
    # These are hardcoded based on the "pretty" prototype but could be in YAML ideally.
    # For now, we use a simple mapping based on the zone ID suffix
    zone_styles = {
        "ZONE_L5": "fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,stroke-dasharray: 5 5,color:#01579b",
        "ZONE_L4": "fill:#f5f5f5,stroke:#616161,stroke-width:2px,stroke-dasharray: 5 5",
        "ZONE_L3": "fill:#f5f5f5,stroke:#616161,stroke-width:2px,stroke-dasharray: 5 5",
        "ZONE_L2": "fill:#f5f5f5,stroke:#616161,stroke-width:2px,stroke-dasharray: 5 5",
        "ZONE_L1": "fill:#f5f5f5,stroke:#616161,stroke-width:2px,stroke-dasharray: 5 5",
        "ZONE_L0": "fill:#f5f5f5,stroke:#616161,stroke-width:2px,stroke-dasharray: 5 5"
    }

    # 3. Apply Zone Styles
    mermaid_lines.append("\n    %% Subgraph Styling (Zones)")
    for z_id, style_str in zone_styles.items():
        mermaid_lines.append(f"    style {z_id} {style_str}")

    # 4. Iterate through ZONES
    for zone in data.get('zones', []):
        z_id = zone['id']
        z_label = zone['label']
        z_assets = zone.get('assets', [])
        
        # Start a Subgraph for the Zone
        mermaid_lines.append(f'\n    subgraph {z_id} ["{z_label}"]')
        
        # Create Nodes for each Asset inside the Zone
        for asset in z_assets:
            a_id = asset['id']
            a_label = asset['label']
            a_ip = asset.get('ip', '')
            
            # Determine Class
            # First check if asset has specific style
            asset_style_key = asset.get('style')
            # If not, check zone style
            if not asset_style_key:
                asset_style_key = zone.get('style')
            
            mermaid_class = style_map.get(asset_style_key, "default")

            # Node format: ID["Label<br/>IP"]:::class
            label_content = a_label
            if a_ip:
                label_content += f"<br/>{a_ip}"
            
            node_str = f'        {a_id}["{label_content}"]:::{mermaid_class}'
            mermaid_lines.append(node_str)
            
        mermaid_lines.append('    end')  # Close the subgraph

    # 5. Generate Links (Conduits)
    mermaid_lines.append('\n    %% Links')
    for conduit in data.get('conduits', []):
        src = conduit['src']
        dst = conduit['dst']
        proto = conduit.get('protocol', 'Traffic')
        port = conduit.get('port', '')
        
        # Link format: SRC -- "Protocol (Port)" --> DST
        link_label = f'{proto} ({port})' if port else proto
        mermaid_lines.append(f'    {src} -- "{link_label}" --> {dst}')

    # 6. Global Link Styling
    mermaid_lines.append('\n    %% Link Styling')
    mermaid_lines.append('    linkStyle default interpolate basis')

    if is_markdown:
        mermaid_lines.append("```")

    # 7. Save to file
    with open(output_file, 'w') as f:
        f.write('\n'.join(mermaid_lines))

    print(f"Success! Mermaid diagram saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert YAML architecture to Mermaid diagram.")
    parser.add_argument("input_file", nargs="?", default=DEFAULT_INPUT_YAML, help="Path to input YAML file")
    parser.add_argument("output_file", nargs="?", default=DEFAULT_OUTPUT_FILE, help="Path to output Mermaid file")
    
    args = parser.parse_args()
    
    generate_mermaid(args.input_file, args.output_file)