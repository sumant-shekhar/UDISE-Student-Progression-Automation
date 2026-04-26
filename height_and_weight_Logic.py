import random
import sys

class_data = {
    1: {"height_cm": 115, "weight_kg": 21},
    2: {"height_cm": 122, "weight_kg": 23},
    3: {"height_cm": 128, "weight_kg": 26},
    4: {"height_cm": 133, "weight_kg": 29},
    5: {"height_cm": 138, "weight_kg": 32},
    6: {"height_cm": 144, "weight_kg": 36},
    7: {"height_cm": 149, "weight_kg": 40},
    8: {"height_cm": 156, "weight_kg": 45},
    9: {"height_cm": 164, "weight_kg": 51},
    10: {"height_cm": 170, "weight_kg": 56},
}

# choose Class student
selected_class = 1

# Base values
base_height = class_data[selected_class]["height_cm"]
base_weight = class_data[selected_class]["weight_kg"]

# Generate random values within ±5
student_height = str(random.randint(base_height - 5, base_height + 5))
student_weight = str(random.randint(base_weight - 3, base_weight + 5))

print(student_height)
print(student_weight)
sys.exit()