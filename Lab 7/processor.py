
import math


def validate_height_and_fastpass(rider_spec):
    if not isinstance(rider_spec, str):
        return "Invalid rider specification"

    parts = rider_spec.strip().split(':')

    if len(parts) != 2:
        return "Invalid rider specification. Expected Height:FastPass"

    height_str, pass_str = parts

    try:
        height = int(height_str.strip())
    except ValueError:
        return "Invalid height. Please enter a valid integer"

    if height < 0:
        return "Invalid height. Height cannot be negative"

    pass_str = pass_str.strip().upper()

    pass_map = {"YES": True, "NO": False}

    if pass_str not in pass_map:
        return "Invalid FastPass value. Enter YES or NO"

    has_fastpass = pass_map[pass_str]
    eligible = height >= 120

    status = "FastPass Priority" if has_fastpass else "Standard Entry"

    return f"Height {height}cm: {'Approved' if eligible else 'Denied'} ({status})"


def compute_dispatch_throughput(ride_metric_str):
    if not isinstance(ride_metric_str, str):
        return None

    parts = ride_metric_str.strip().split('/')

    if len(parts) != 2:
        return None

    riders_str, mins_str = parts

    try:
        riders = float(riders_str.strip())
        cycle_mins = float(mins_str.strip())
    except ValueError:
        return None

    if not math.isfinite(riders) or not math.isfinite(cycle_mins):
        return None

    if riders < 0 or cycle_mins <= 0:
        return None

    rate = riders / cycle_mins

    return round(rate, 2)


def resolve_safety_restraint_code(zone_code):
    if not isinstance(zone_code, str) or not zone_code.strip():
        return "Invalid ride zone code"

    prefix = zone_code.strip().upper()[:3]

    restraint_types = {
        "CST": "Over-the-Shoulder Harness",
        "WTR": "Lap Bar and Seatbelt",
        "DRP": "Hydraulic Shoulder Vest",
        "WHL": "Manual Safety Bar"
    }

    return restraint_types.get(prefix, "Unknown ride zone code")


def main():
    print("==== Running validate_height_and_fastpass ====")
    r_input = input("Enter rider spec (Height:FastPass, e.g. 140:YES): ")
    print(validate_height_and_fastpass(r_input))

    print("\n==== Running compute_dispatch_throughput ====")
    t_input = input("Enter riders/mins (e.g. 48/2.5): ")
    result = compute_dispatch_throughput(t_input)

    if result is None:
        print("Invalid ride metrics. Enter valid riders/cycle minutes.")
    else:
        print("Throughput (riders/min):", result)

    print("\n==== Running resolve_safety_restraint_code ====")
    z_input = input("Enter ride zone code (e.g. CST_01, WTR_A): ")
    print("Restraint:", resolve_safety_restraint_code(z_input))


if __name__ == "__main__":
    main()
