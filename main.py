
import argparse

parser = argparse.ArgumentParser(
    description="Vehicle Care - Smart Vehicle Maintenance Tracker"
)

subparsers = parser.add_subparsers(
    dest="command",
    required=True
)

subparsers.add_parser("add_vehicle")
subparsers.add_parser("vehicle_list")
subparsers.add_parser("fuel_purchase")
subparsers.add_parser("fuel_consumption")
subparsers.add_parser("add_service")
subparsers.add_parser("add_repair")
subparsers.add_parser("update_repair")
subparsers.add_parser("delete_repair")
subparsers.add_parser("add_many_repairs")
subparsers.add_parser("add_insurance")
subparsers.add_parser("add_spare_part")
subparsers.add_parser("schedule_maintenance")
subparsers.add_parser("fuel_efficiency")
subparsers.add_parser("monthly_report")
subparsers.add_parser("upcoming_maintenance")
subparsers.add_parser("export_csv")

args = parser.parse_args()

print("Vehicle Care - Smart Vehicle Maintenance Tracker")
print("Selected command:", args.command)
