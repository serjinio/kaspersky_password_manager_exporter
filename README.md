# Passwords exporter script for Kaspersky password manager

Script to migrate TXT export of Kaspersky password manager key vault 
to KeePass-compatible format.

## Usage

1. Export your passwords from Kaspersky password manger 
1. Run this script to produce CSVs compatible for importing 
into the KeePass2 (general CSV import).

Run: 

```
python convert.py --infile <infile>
```

This will produce several `.csv` files which can be directly imported 
into the KeePass2.
