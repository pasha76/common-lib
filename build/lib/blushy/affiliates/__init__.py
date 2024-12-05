import importlib
import glob
import os  # Add this import

# Print current path
print(f"Current path: {os.getcwd()}")

affiliates=dict()

files = glob.glob(f"{os.getcwd()}/utils/affiliates/vendors/*.py")
print(files)
for file in files:
    vendor_name=file.split('/')[-1].replace('.py','')
    affilate_processor = importlib.import_module(f"blushy.affiliates.vendors.{vendor_name}").generate_product_adjust_url
    affiliates[vendor_name] = affilate_processor