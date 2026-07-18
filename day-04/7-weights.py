import numpy as np

exam_score = 80
attendance = 40

weights = {
    "exam": 0.8,
    "attendance": 0.2
}

result = (
    exam_score * weights["exam"] +
    attendance * weights["attendance"]
)

print(f"Final result: {result:.2f}")