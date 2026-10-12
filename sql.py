

import sqlite3

# Connect to the existing database
conn = sqlite3.connect("vehiclecare.db")

# Enable foreign key support
conn.execute("PRAGMA foreign_keys = ON")

# Create cursor
cursor = conn.cursor()

# 1. CREATE TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_number TEXT PRIMARY KEY,
    make TEXT NOT NULL,
    vehicle_type TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    odometer INTEGER NOT NULL CHECK (odometer >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


# 2. execute() - Insert one vehicle
cursor.execute("""
INSERT OR IGNORE INTO vehicles
(make, vehicle_number, vehicle_type, model, year, odometer)
VALUES (?, ?, ?, ?, ?, ?)
""", ("Suzuki", "AP39CD1234", "Two-Wheeler",
      "Suzuki Access", 2024, 12500))

conn.commit()


# 3. executemany() - Insert multiple vehicles
vehicles = [
    ("Honda", "AP39CD2345", "Two-Wheeler",
     "Honda Activa", 2023, 10000),

    ("Hyundai", "AP39CD3456", "Four-Wheeler",
     "Hyundai i20", 2022, 25000),

    ("Maruti", "AP39CD4567", "Four-Wheeler",
     "Maruti Swift", 2021, 30000)
]

cursor.executemany("""
INSERT OR IGNORE INTO vehicles
(make, vehicle_number, vehicle_type, model, year, odometer)
VALUES (?, ?, ?, ?, ?, ?)
""", vehicles)

conn.commit()


# 4. fetchall() - Display all vehicles
cursor.execute("SELECT * FROM vehicles")

rows = cursor.fetchall()

print("ALL VEHICLES:")
for row in rows:
    print(row)


# 5. fetchone() - Search for one vehicle
cursor.execute("""
SELECT * FROM vehicles
WHERE vehicle_number = ?
""", ("AP39CD2345",))

row = cursor.fetchone()

print("\nSELECTED VEHICLE:")
print(row)


# 6. execute() - Update odometer reading
cursor.execute("""
UPDATE vehicles
SET odometer = ?
WHERE vehicle_number = ?
""", (11000, "AP39CD2345"))

conn.commit()

print("\nVehicle odometer updated.")


# 7. execute() - Delete one vehicle
cursor.execute("""
DELETE FROM vehicles
WHERE vehicle_number = ?
""", ("AP39CD4567",))

conn.commit()

print("Vehicle deleted.")


# 8. Display final records
cursor.execute("SELECT * FROM vehicles")

print("\nFINAL VEHICLE RECORDS:")
for row in cursor.fetchall():
    print(row)


# 9. Close database connection
conn.close()

print("\nDatabase connection closed.")
conn.close()
