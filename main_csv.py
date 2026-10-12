
import argparse
import csv
import os
from datetime import date, datetime, timedelta

# Vehicle Care - CSV-based storage
# No SQLite is used in this program.

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "vehicles": "vehicles.csv",
    "fuel_purchases": "fuel_purchases.csv",
    "fuel_consumption": "fuel_consumption.csv",
    "service_details": "service_details.csv",
    "repair_expenses": "repair_expenses.csv",
    "insurance": "insurance.csv",
    "spare_parts": "spare_parts.csv",
    "maintenance_schedule": "maintenance_schedule.csv",
}

FIELDS = {
    "vehicles": [
        "vehicle_number", "make", "vehicle_type", "model",
        "year", "odometer", "created_at"
    ],
    "fuel_purchases": [
        "Vehicle_Number", "Date", "Fuel_Type", "Quantity",
        "Price_Per_Litre", "Total_Amount"
    ],
    "fuel_consumption": [
        "Vehicle_Number", "Date", "Odometer", "Litres_Used"
    ],
    "service_details": [
        "id", "vehicle_number", "service_date", "service_type",
        "description", "cost", "next_service_date"
    ],
    "repair_expenses": [
        "id", "vehicle_number", "repair_date", "description", "cost"
    ],
    "insurance": [
        "id", "vehicle_number", "provider", "policy_number",
        "start_date", "expiry_date", "premium"
    ],
    "spare_parts": [
        "id", "vehicle_number", "part_name", "replacement_date",
        "quantity", "cost", "notes"
    ],
    "maintenance_schedule": [
        "id", "vehicle_number", "task", "due_date",
        "due_odometer", "status", "notes"
    ],
}


def path_for(table):
    return os.path.join(DATA_DIR, FILES[table])


def read_records(table):
    path = path_for(table)

    if not os.path.exists(path):
        return []

    with open(path, "r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def append_record(table, record):
    path = path_for(table)
    fields = FIELDS[table]
    exists = os.path.exists(path) and os.path.getsize(path) > 0

    if exists:
        with open(path, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            existing_header = next(reader, [])

        if existing_header != fields:
            raise ValueError(
                f"CSV header mismatch in {FILES[table]}. "
                "Existing file was not changed."
            )

    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)

        if not exists:
            writer.writeheader()

        writer.writerow(record)


def update_records(table, records):
    """Replace a CSV's contents only after validating its header."""
    path = path_for(table)
    fields = FIELDS[table]

    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "r", newline="", encoding="utf-8-sig") as file:
            header = next(csv.reader(file), [])

        if header != fields:
            raise ValueError(
                f"CSV header mismatch in {FILES[table]}. "
                "Existing file was not changed."
            )

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def validate_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Use date format YYYY-MM-DD."
        )


def validate_month(value):
    try:
        datetime.strptime(value, "%Y-%m")
        return value
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Use month format YYYY-MM, for example 2026-10."
        )


def vehicle_exists(vehicle_number):
    return any(
        row["vehicle_number"].upper() == vehicle_number.upper()
        for row in read_records("vehicles")
    )


def require_vehicle(vehicle_number):
    if not vehicle_exists(vehicle_number):
        raise ValueError(
            f"Vehicle {vehicle_number} not found in vehicles.csv. "
            "Add the vehicle first."
        )


def next_id(table):
    records = read_records(table)
    return max(
        (int(row.get("id") or 0) for row in records),
        default=0
    ) + 1


def show_records(table):
    records = read_records(table)

    if not records:
        print(f"No records found in {FILES[table]}.")
        return

    for record in records:
        print(record)

# ==========================================
# VEHICLE FUNCTIONS
# ==========================================

def add_vehicle(args):
    if vehicle_exists(args.vehicle_number):
        print("Error: Vehicle number already exists.")
        return

    record = {
        "vehicle_number": args.vehicle_number.upper(),
        "make": args.make,
        "vehicle_type": args.vehicle_type,
        "model": args.model,
        "year": args.year,
        "odometer": args.odometer,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    append_record("vehicles", record)
    print("Vehicle added successfully!")


def vehicle_list(args):
    records = read_records("vehicles")

    if not records:
        print("No vehicles found.")
        return

    for row in records:
        print(
            f"{row['vehicle_number']} | "
            f"{row['make']} {row['model']} | "
            f"{row['vehicle_type']} | "
            f"Year: {row['year']} | "
            f"Odometer: {row['odometer']} km"
        )


# ==========================================
# FUEL PURCHASE
# ==========================================

def fuel_purchase(args):
    require_vehicle(args.vehicle_number)

    total = args.quantity * args.price_per_litre

    record = {
        "Vehicle_Number": args.vehicle_number.upper(),
        "Date": args.date,
        "Fuel_Type": args.fuel_type,
        "Quantity": args.quantity,
        "Price_Per_Litre": args.price_per_litre,
        "Total_Amount": round(total, 2),
    }

    append_record("fuel_purchases", record)

    print("Fuel purchase saved successfully.")
    print(f"Total amount: Rs. {total:.2f}")


# ==========================================
# FUEL CONSUMPTION
# ==========================================

def fuel_consumption(args):
    require_vehicle(args.vehicle_number)

    vehicles = read_records("vehicles")
    vehicle = next(
        row for row in vehicles
        if row["vehicle_number"].upper()
        == args.vehicle_number.upper()
    )

    previous_odometer = int(vehicle["odometer"])

    if args.odometer <= previous_odometer:
        print(
            f"Error: Odometer must be greater than "
            f"{previous_odometer} km."
        )
        return

    distance = args.odometer - previous_odometer

    # Update the vehicle's odometer.
    vehicle["odometer"] = str(args.odometer)
    update_records("vehicles", vehicles)

    record = {
        "Vehicle_Number": args.vehicle_number.upper(),
        "Date": args.date,
        "Odometer": args.odometer,
        "Litres_Used": args.litres_used,
    }

    append_record("fuel_consumption", record)

    efficiency = distance / args.litres_used

    print("Fuel consumption saved successfully.")
    print(f"Distance travelled: {distance} km")
    print(f"Fuel efficiency: {efficiency:.2f} km/litre")


# ==========================================
# SERVICE DETAILS
# ==========================================

def add_service(args):
    require_vehicle(args.vehicle_number)

    record = {
        "id": next_id("service_details"),
        "vehicle_number": args.vehicle_number.upper(),
        "service_date": args.service_date,
        "service_type": args.service_type,
        "description": args.description,
        "cost": args.cost,
        "next_service_date": args.next_service_date or "",
    }

    append_record("service_details", record)

    print("Service details saved successfully.")

# REPAIR EXPENSES
def add_repair(args):
    require_vehicle(args.vehicle_number)

    record = {
        "id": next_id("repair_expenses"),
        "vehicle_number": args.vehicle_number.upper(),
        "repair_date": args.repair_date,
        "description": args.description,
        "cost": args.cost
    }

    append_record("repair_expenses", record)
    print("Repair expense added successfully!")


def update_repair(args):
    require_vehicle(args.vehicle_number)

    records = read_records("repair_expenses")
    found = False

    for row in records:
        if (row["id"] == str(args.id)
                and row["vehicle_number"].upper() == args.vehicle_number.upper()):
            row["repair_date"] = args.repair_date
            row["description"] = args.description
            row["cost"] = str(args.cost)
            found = True
            break

    if found:
        update_records("repair_expenses", records)
        print("Repair expense updated successfully!")
    else:
        print("Repair record not found.")


def delete_repair(args):
    records = read_records("repair_expenses")
    updated = [
        row for row in records
        if not (
            row["id"] == str(args.id)
            and row["vehicle_number"].upper() == args.vehicle_number.upper()
        )
    ]

    if len(updated) == len(records):
        print("Repair record not found.")
    else:
        update_records("repair_expenses", updated)
        print("Repair expense deleted successfully!")


def add_many_repairs(args):
    require_vehicle(args.vehicle_number)

    records = read_records("repair_expenses")

    for description, cost in args.items:
        record = {
            "id": next_id("repair_expenses"),
            "vehicle_number": args.vehicle_number.upper(),
            "repair_date": args.repair_date,
            "description": description,
            "cost": cost
        }
        append_record("repair_expenses", record)

    print("Multiple repair expenses added successfully!")


# INSURANCE
def add_insurance(args):
    require_vehicle(args.vehicle_number)

    record = {
        "id": next_id("insurance"),
        "vehicle_number": args.vehicle_number.upper(),
        "provider": args.provider,
        "policy_number": args.policy_number,
        "start_date": args.start_date,
        "expiry_date": args.expiry_date,
        "premium": args.premium
    }

    append_record("insurance", record)
    print("Insurance details added successfully!")


# SPARE PARTS
def add_spare_part(args):
    require_vehicle(args.vehicle_number)

    record = {
        "id": next_id("spare_parts"),
        "vehicle_number": args.vehicle_number.upper(),
        "part_name": args.part_name,
        "replacement_date": args.replacement_date,
        "quantity": args.quantity,
        "cost": args.cost,
        "notes": args.notes
    }

    append_record("spare_parts", record)
    print("Spare part details added successfully!")


# MAINTENANCE SCHEDULE
def schedule_maintenance(args):
    require_vehicle(args.vehicle_number)

    record = {
        "id": next_id("maintenance_schedule"),
        "vehicle_number": args.vehicle_number.upper(),
        "task": args.task,
        "due_date": args.due_date,
        "due_odometer": args.due_odometer if args.due_odometer is not None else "",
        "status": "Pending",
        "notes": args.notes or ""
    }

    append_record("maintenance_schedule", record)
    print("Maintenance scheduled successfully!")

# FUEL EFFICIENCY REPORT
def fuel_efficiency(args):
    records = read_records("fuel_consumption")
    vehicle_number = args.vehicle_number.upper()

    selected = [
        row for row in records
        if row["Vehicle_Number"].upper() == vehicle_number
    ]

    if len(selected) < 2:
        print("At least two fuel consumption records are needed.")
        return

    selected.sort(key=lambda row: row["Date"])

    first = selected[0]
    last = selected[-1]

    distance = int(last["Odometer"]) - int(first["Odometer"])
    litres = sum(float(row["Litres_Used"]) for row in selected)

    if distance <= 0 or litres <= 0:
        print("Insufficient or invalid data to calculate fuel efficiency.")
        return

    efficiency = distance / litres

    print("\n--- Fuel Efficiency Report ---")
    print("Vehicle:", vehicle_number)
    print("Distance:", distance, "km")
    print("Fuel used:", round(litres, 2), "litres")
    print("Fuel efficiency:", round(efficiency, 2), "km/litre")


# MONTHLY EXPENSE REPORT
def monthly_report(args):
    tables = [
        ("fuel_purchases", "fuel_purchases"),
        ("service_details", "service"),
        ("repair_expenses", "repair"),
        ("insurance", "insurance"),
        ("spare_parts", "spare parts")
    ]

    total_expense = 0

    print("\n--- Monthly Vehicle Expense Report ---")
    print("Month:", args.month)

    for table, label in tables:
        records = read_records(table)
        amount = 0

        for row in records:
            if table == "fuel_purchases":
                record_date = row["Date"]
                cost = float(row["Total_Amount"])
            elif table == "service_details":
                record_date = row["service_date"]
                cost = float(row["cost"])
            elif table == "repair_expenses":
                record_date = row["repair_date"]
                cost = float(row["cost"])
            elif table == "insurance":
                record_date = row["start_date"]
                cost = float(row["premium"])
            else:
                record_date = row["replacement_date"]
                cost = float(row["cost"])

            if record_date.startswith(args.month):
                amount += cost

        total_expense += amount
        print(f"{label.title()} expense: Rs. {amount:.2f}")

    print(f"Total monthly expense: Rs. {total_expense:.2f}")


# UPCOMING MAINTENANCE
def upcoming_maintenance(args):
    records = read_records("maintenance_schedule")
    today = date.today()
    found = False

    print("\n--- Upcoming Maintenance ---")

    for row in records:
        if row["status"].lower() != "pending":
            continue

        try:
            due = date.fromisoformat(row["due_date"])
        except (ValueError, TypeError):
            continue

        if due >= today:
            print(
                f"Vehicle: {row['vehicle_number']} | "
                f"Task: {row['task']} | "
                f"Due date: {row['due_date']} | "
                f"Due odometer: {row['due_odometer'] or 'Not specified'}"
            )
            found = True

    if not found:
        print("No upcoming maintenance records found.")


# SHOW RECORDS
def show(args):
    table_names = {
        "vehicles": "vehicles",
        "fuel_purchases": "fuel_purchases",
        "fuel_consumption": "fuel_consumption",
        "service_details": "service_details",
        "repair_expenses": "repair_expenses",
        "insurance": "insurance",
        "spare_parts": "spare_parts",
        "maintenance_schedule": "maintenance_schedule"
    }

    table = args.table

    if table not in table_names:
        print("Invalid table name.")
        return

    show_records(table_names[table])


# EXPORT CSV
def export_csv(args):
    import shutil

    table = args.table

    if table not in FILES:
        print("Invalid table name.")
        return

    source = path_for(table)

    if not os.path.exists(source) or not read_records(table):
        print(f"No records to export from {table}.")
        return

    export_dir = os.path.join(DATA_DIR, "exports")
    os.makedirs(export_dir, exist_ok=True)

    destination = os.path.join(export_dir, FILES[table])
    shutil.copyfile(source, destination)

    print("CSV exported successfully to:", destination)

# COMMAND-LINE ARGUMENTS
def build_parser():
    parser = argparse.ArgumentParser(
        description="Vehicle Care - Smart Vehicle Maintenance Tracker (CSV)"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # ADD VEHICLE
    p = subparsers.add_parser("add_vehicle")
    p.add_argument("--vehicle-number", required=True)
    p.add_argument("--make", required=True)
    p.add_argument("--vehicle-type", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--odometer", type=int, required=True)
    p.set_defaults(func=add_vehicle)

    # LIST VEHICLES
    p = subparsers.add_parser("vehicle_list")
    p.set_defaults(func=vehicle_list)

    # FUEL PURCHASE
    p = subparsers.add_parser("fuel_purchase")
    p.add_argument("--vehicle-number", required=True)
    p.add_argument("--date", dest="purchase_date", type=validate_date, required=True)
    p.add_argument("--fuel-type", required=True)
    p.add_argument("--quantity", type=float, required=True)
    p.add_argument("--price-per-litre", type=float, required=True)

    def run_fuel_purchase(args):
        args.date = args.purchase_date
        fuel_purchase(args)

    p.set_defaults(func=run_fuel_purchase)

    # FUEL CONSUMPTION
    p = subparsers.add_parser("fuel_consumption")
    p.add_argument("--vehicle-number", required=True)
    p.add_argument("--date", type=validate_date, required=True)
    p.add_argument("--odometer", type=int, required=True)
    p.add_argument("--litres-used", type=float, required=True)
    p.set_defaults(func=fuel_consumption)

    # SERVICE DETAILS
    p = subparsers.add_parser("add_service")
    p.add_argument("--vehicle-number", required=True)
    p.add_argument("--service-date", type=validate_date, required=True)
    p.add_argument("--service-type", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--cost", type=float, required=True)
    p.add_argument("--next-service-date", type=validate_date)
    p.set_defaults(func=add_service)

    # ADD REPAIR
    p = subparsers.add_parser("add_repair")
    p.add_argument("--vehicle-number", required=True)
    p.add_argument("--repair-date", type=validate_date, required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--cost", type=float, required=True)
    p.set_defaults(func=add_repair)

    # UPDATE REPAIR
    p = subparsers.add_parser("update_repair")
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--vehicle-number", required=True)
    p.add_argument("--repair-date", type=validate_date, required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--cost", type=float, required=True)
    p.set_defaults(func=update_repair)

    # DELETE REPAIR
    p = subparsers.add_parser("delete_repair")
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--vehicle-number", required=True)
    p.set_defaults(func=delete_repair)

    # ADD MULTIPLE REPAIRS
    p = subparsers.add_parser("add_many_repairs")
    p.add_argument("--vehicle-number", required=True)
    p.add_argument("--repair-date", type=validate_date, required=True)
    p.add_argument(
        "--items",
        nargs="+",
        required=True,
        metavar="DESCRIPTION:COST"
    )

    def run_many_repairs(args):
        parsed_items = []
        for item in args.items:
            try:
                description, cost = item.rsplit(":", 1)
                parsed_items.append((description, float(cost)))
            except ValueError:
                raise ValueError(
                    "Each item must use DESCRIPTION:COST format."
                )
        args.items = parsed_items
        add_many_repairs(args)

    p.set_defaults(func=run_many_repairs)

    # INSURANCE
    p = subparsers.add_parser("add_insurance")
    p.add_argument("--vehicle-number", required=True)
    p.add_argument("--provider", required=True)
    p.add_argument("--policy-number", required=True)
    p.add_argument("--start-date", type=validate_date, required=True)
    p.add_argument("--expiry-date", type=validate_date, required=True)
    p.add_argument("--premium", type=float, required=True)
    p.set_defaults(func=add_insurance)

    # SPARE PARTS
    p = subparsers.add_parser("add_spare_part")
    p.add_argument("--vehicle-number", required=True)
    p.add_argument("--part-name", required=True)
    p.add_argument("--replacement-date", type=validate_date, required=True)
    p.add_argument("--quantity", type=int, required=True)
    p.add_argument("--cost", type=float, required=True)
    p.add_argument("--notes", default="")
    p.set_defaults(func=add_spare_part)

    # SCHEDULE MAINTENANCE
    p = subparsers.add_parser("schedule_maintenance")
    p.add_argument("--vehicle-number", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--due-date", type=validate_date, required=True)
    p.add_argument("--due-odometer", type=int)
    p.add_argument("--notes", default="")
    p.set_defaults(func=schedule_maintenance)

    # FUEL EFFICIENCY
    p = subparsers.add_parser("fuel_efficiency")
    p.add_argument("--vehicle-number", required=True)
    p.set_defaults(func=fuel_efficiency)

    # MONTHLY REPORT
    p = subparsers.add_parser("monthly_report")
    p.add_argument("--month", type=validate_month, required=True)
    p.set_defaults(func=monthly_report)

    # UPCOMING MAINTENANCE
    p = subparsers.add_parser("upcoming_maintenance")
    p.set_defaults(func=upcoming_maintenance)

    # SHOW RECORDS
    p = subparsers.add_parser("show")
    p.add_argument(
        "--table",
        choices=list(FILES.keys()),
        required=True
    )
    p.set_defaults(func=show)

    # EXPORT CSV
    p = subparsers.add_parser("export_csv")
    p.add_argument("table", choices=list(FILES.keys()))
    p.set_defaults(func=export_csv)

    return parser


# MAIN PROGRAM
def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except (ValueError, OSError, csv.Error) as error:
        print("Error:", error)


if __name__ == "__main__":
    main()
