# fabric-inventory

The script is designed to extract Microsoft Fabric workspace metadata along with users, semantic models, and datasources into csv files.

Run pip install to ensure the dependencies are installed
```
pip install -r .\requirements.txt 
```

Run the script
```
python inventory-cli.py --output output_folder
```

To use Service Principal for authentiction provide --tenant, --client, --secret arguments when running the script.

The script will append data to files in the output folder (path variable in invenroty.py). Remove files from the output folder before running to avoid duplicate records.
