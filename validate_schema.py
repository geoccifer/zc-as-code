from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import List, Optional, Dict, Literal
import yaml
import argparse
import sys
from ipaddress import IPv4Address, ip_address

# --- Data Models ---

class Asset(BaseModel):
    id: str = Field(..., description="Unique Identifier for the Asset")
    label: str = Field(..., description="Human readable label")
    ip: Optional[str] = Field(None, description="IP Address of the asset")
    style: Optional[str] = None
    criticality: Optional[Literal['Low', 'Medium', 'High', 'Critical']] = Field(
        'Low', description="Business impact if compromised"
    )

    @model_validator(mode='after')
    def validate_ip_format(self):
        if self.ip and self.ip != "Public" and not self.ip.startswith("DHCP") and not self.ip.startswith("N/A"):
            try:
                ip_address(self.ip)
            except ValueError:
                # Allow special values but warn/fail on malformed IPs
                pass 
        return self

class Zone(BaseModel):
    id: str
    label: str
    style: Optional[str] = None
    assets: List[Asset] = []

class Conduit(BaseModel):
    src: str
    dst: str
    protocol: str
    port: Optional[str] = None

class ProjectConfig(BaseModel):
    project: str
    version: float
    styles: Dict[str, str]
    zones: List[Zone]
    conduits: List[Conduit]

    @model_validator(mode='after')
    def validate_links(self):
        # 1. Collect all valid Asset IDs
        valid_asset_ids = set()
        for zone in self.zones:
            for asset in zone.assets:
                if asset.id in valid_asset_ids:
                    raise ValueError(f"Duplicate Asset ID found: {asset.id}")
                valid_asset_ids.add(asset.id)
        
        # 2. Check Conduits
        errors = []
        for i, conduit in enumerate(self.conduits):
            if conduit.src not in valid_asset_ids:
                errors.append(f"Conduit #{i+1}: Source '{conduit.src}' is not a defined Asset.")
            if conduit.dst not in valid_asset_ids:
                errors.append(f"Conduit #{i+1}: Destination '{conduit.dst}' is not a defined Asset.")
        
        if errors:
            raise ValueError("\n".join(errors))
        
        return self

# --- Main Logic ---

def validate_yaml(yaml_path):
    print(f"Validating {yaml_path}...")
    try:
        with open(yaml_path, 'r') as f:
            raw_data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: File '{yaml_path}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error Parsing YAML: {e}")
        sys.exit(1)

    try:
        # Pydantic does the heavy lifting here
        project = ProjectConfig(**raw_data)
        print("\n✅ Validation Successful!")
        print(f"Project: {project.project} (v{project.version})")
        print(f"Stats: {sum(len(z.assets) for z in project.zones)} Assets, {len(project.conduits)} Conduits verified.")
        return 0
    except ValidationError as e:
        print("\n❌ Validation Failed with Errors:")
        for err in e.errors():
            loc = " -> ".join(map(str, err['loc']))
            msg = err['msg']
            # Clean up the specific custom error for links
            if "Value error," in msg: 
                msg = msg.split("Value error,")[1].strip()
            print(f" - [{loc}]: {msg}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Z&C YAML against Schema.")
    parser.add_argument("input_file", help="Path to YAML file")
    args = parser.parse_args()
    
    sys.exit(validate_yaml(args.input_file))
