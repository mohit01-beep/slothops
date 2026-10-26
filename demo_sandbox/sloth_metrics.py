def calculate_sloth_ratio(hours_worked, output_delivered):
    """Energy-saving ratio calculator."""
    return output_delivered / max(hours_worked, 1)

if __name__ == "__main__":
    print("Sloth ratio:", calculate_sloth_ratio(4, 10))
