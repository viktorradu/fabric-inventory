# fabric-inventory

The script is designed to extract Microsoft Fabric workspace metadata along with users, semantic models, and datasources into csv files.

Install dependencies:
```
pip install -r .\requirements.txt 
```

Run the script (interactive sign-in):
```
python inventory-cli.py --output output_folder
```

## Capacity list filter

You can limit the scan to specific capacities by passing a text file with one capacity ID per line:

```txt
capacity-id-1
capacity-id-2
capacity-id-3
```

Run with capacity filter:

```
python inventory-cli.py --capacity-list capacities.txt --output output_folder
```

## Service principal authentication

To use service principal authentication, provide `--tenant`, `--client`, and `--secret`:

```
python inventory-cli.py --tenant <tenant-id> --client <client-id> --secret <client-secret> --output output_folder
```

Service principal authentication can be combined with a capacity list:

```
python inventory-cli.py --capacity-list capacities.txt --tenant <tenant-id> --client <client-id> --secret <client-secret> --output output_folder
```

The script writes output files to the folder provided in `--output` (default: `output`).
