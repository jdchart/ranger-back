from rangerback import GBIF
from utils import write_json
import os

OUTPATH = os.path.join(os.getcwd(), "TEST")
if os.path.isdir(OUTPATH) == False:
    os.makedirs(OUTPATH)

gbif = GBIF()

results = gbif.search()


for i, item in enumerate(results):
    write_json(os.path.join(OUTPATH, f"{i}.json"), item)