import importlib
import glob


affiliates=dict()

files = glob.glob(f"blushy/affiliates/vendors/*.py")
for file in files:
    vendor_name=file.split('/')[-1].replace('.py','')
    affilate_processor = importlib.import_module(f"blushy.affiliates.vendors.{vendor_name}").generate_product_adjust_url
    affiliates[vendor_name] = affilate_processor