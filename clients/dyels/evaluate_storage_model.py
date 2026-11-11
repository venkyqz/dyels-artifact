#!/usr/bin/env python3
import csv
from storage_layout_parser import compare_storage_layouts

ground_truth = "../source-storage-layout.json"
inferred = "inferred-storage-layout.json"

sucess, structure_success, fail, analysis_missing, solc_missing, needs_any_type = compare_storage_layouts(ground_truth, inferred)

with open("Analytics_StorageModelSuccess.csv", 'w') as f:
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerows(sucess)

with open("Analytics_StorageModelTypeFailure.csv", 'w') as f:
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerows(fail.union(structure_success - sucess))

# Comment out unused metrics

# with open("Analytics_StorageModelTypeOnlyFailure.csv", 'w') as f:
#     writer = csv.writer(f, delimiter='\t', lineterminator='\n')
#     writer.writerows(structure_success - sucess)

# with open("Analytics_StorageModelPartialSuccess.csv", 'w') as f:
#     writer = csv.writer(f, delimiter='\t', lineterminator='\n')
#     writer.writerows(structure_success)

# with open("Analytics_StorageModelFailure.csv", 'w') as f:
#     writer = csv.writer(f, delimiter='\t', lineterminator='\n')
#     writer.writerows(fail)

with open("Analytics_StorageVariableMissing.csv", 'w') as f:
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerows(analysis_missing)

with open("Analytics_StorageVariableSolcMissing.csv", 'w') as f:
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerows(solc_missing)
