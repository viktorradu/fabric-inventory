from lib import *
import os, csv, argparse
from math import ceil
from pathlib import Path


def validate_capacity_list(file_path: str) -> list:
    """Validate capacity list file and return list of capacity IDs."""
    path = Path(file_path)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"File not found: {file_path}")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"Not a file: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        raise argparse.ArgumentTypeError(f"File is not a valid text file: {file_path}")
    
    capacity_ids = [line.strip() for line in content.splitlines() if line.strip()]
    if not capacity_ids:
        raise argparse.ArgumentTypeError(f"File contains no capacity IDs: {file_path}")
    
    return capacity_ids


parser = argparse.ArgumentParser(description='Fabric Inventory CLI')
parser.add_argument('--capacity-list', type=str, help='Path to text file with capacity IDs (one per line)')
parser.add_argument('--output', type=str, help='Output directory for the scan results')
parser.add_argument('--tenant', type=str, help='Tenant ID for the Service Principal')
parser.add_argument('--client', type=str, help='Client ID for the Service Principal')
parser.add_argument('--secret', type=str, help='Client secret for the Service Principal')

args = parser.parse_args()  
if args.output:
    output = args.output
else:
    output = 'output'

Path(output).mkdir(parents=True, exist_ok=True)

capacity_ids = None
if args.capacity_list:
    capacity_ids = validate_capacity_list(args.capacity_list)
    print(f"Loaded {len(capacity_ids)} capacity IDs from {args.capacity_list}")

client = Client()
if args.tenant and args.client and args.secret:
    client.set_sp_credentials(tenant_id=args.tenant, client_id=args.client, client_secret=args.secret)
scan = Scan(client)

if capacity_ids:
    workspaces = scan.list_workspaces_by_capacities(capacity_ids)
else:
    workspaces = scan.list_workspaces()
if 'error' not in workspaces:
    batch_size = 100
    batch_count = ceil(len(workspaces) / batch_size)
    for batch in range(0, batch_count):
        batch_workspaces = workspaces[batch * batch_size:(batch + 1) * batch_size]
        workspace_ids = [workspace['id'] for workspace in batch_workspaces]
        print(f"Scaning workspace batch {batch + 1} out of {batch_count}")
        scan_result = scan.scan_workspaces(workspace_ids)
        print(f"Scan completed for {len(workspace_ids)} workspaces.")
        
        for collection in scan_result.keys():      
            if len(scan_result[collection]) > 0:
                file_path = f'{output}/{collection}.csv'
                if batch == 0 and os.path.exists(file_path):
                    os.remove(file_path)
                with open(file_path, 'a', newline='', encoding="utf-8") as file:
                    writer = csv.DictWriter(file,fieldnames=scan_result[collection][0].keys(),extrasaction='ignore', quoting=csv.QUOTE_ALL, lineterminator='\n')
                    if batch == 0:
                        writer.writeheader()
                    writer.writerows(scan_result[collection])
else:
    print(workspaces.error)
