# MariaDB EcoSQL Studio

CODE TO PUSH OPENFLIGHTS DATA TO MARIADB [HEIDISQL]

# 🧠 MariaDB EcoSQL Studio

### CODE TO PUSH OPENFLIGHTS DATA TO MARIADB (HEIDISQL)

---

## 🛫 OPENFLIGHTS DATABASE INITIALIZATION SCRIPT  
**✅ Use ONLY with HeidiSQL connected to MariaDB**

```sql
-- ===============================================================================================================
-- 🛫 OPENFLIGHTS DATABASE INITIALIZATION SCRIPT (MariaDB + HeidiSQL)
-- ✅ Use ONLY with HeidiSQL connected to MariaDB
-- ===============================================================================================================

-- Step 0: Enable Local File Import (Run this before the rest)
SET GLOBAL local_infile = 1;

-- ================================================================
-- Step 1: Create and select the database
-- ================================================================
CREATE DATABASE IF NOT EXISTS openflights;
USE openflights;

SET FOREIGN_KEY_CHECKS = 0;

-- ================================================================
-- Step 2: Create tables
-- ================================================================
CREATE TABLE IF NOT EXISTS airlines (
    airline_id INT PRIMARY KEY,
    name VARCHAR(100),
    alias VARCHAR(50),
    iata VARCHAR(10),
    icao VARCHAR(10),
    callsign VARCHAR(50),
    country VARCHAR(50),
    active CHAR(1)
);

CREATE TABLE IF NOT EXISTS airports (
    airport_id INT PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(50),
    country VARCHAR(50),
    iata VARCHAR(10),
    icao VARCHAR(10),
    latitude DOUBLE,
    longitude DOUBLE,
    altitude INT,
    timezone FLOAT,
    dst VARCHAR(10),
    tz_database_time_zone VARCHAR(50),
    type VARCHAR(50),
    source VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS airports_extended (
    airport_id INT PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(50),
    country VARCHAR(50),
    iata VARCHAR(10),
    icao VARCHAR(10),
    latitude DOUBLE,
    longitude DOUBLE,
    altitude INT,
    timezone FLOAT,
    dst VARCHAR(10),
    tz_database_time_zone VARCHAR(50),
    type VARCHAR(50),
    source VARCHAR(50),
    continent VARCHAR(10),
    iso_country VARCHAR(10),
    municipality VARCHAR(100),
    gps_code VARCHAR(10),
    local_code VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS countries (
    name VARCHAR(100),
    iso_code VARCHAR(10) PRIMARY KEY,
    daid VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS planes (
    name VARCHAR(100),
    iata VARCHAR(10),
    icao VARCHAR(10) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS routes (
    airline VARCHAR(10),
    airline_id INT,
    source_airport VARCHAR(10),
    source_airport_id INT,
    destination_airport VARCHAR(10),
    destination_airport_id INT,
    codeshare VARCHAR(5),
    stops INT,
    equipment VARCHAR(50)
);

-- ================================================================
-- Step 3: Truncate existing data (if any)
-- ================================================================
TRUNCATE TABLE airlines;
TRUNCATE TABLE airports;
TRUNCATE TABLE airports_extended;
TRUNCATE TABLE countries;
TRUNCATE TABLE planes;
TRUNCATE TABLE routes;

-- ================================================================
-- Step 4: Load CSV Data (edit only the file paths below)
-- ================================================================
-- 💡 Replace the example path with your actual folder location
-- For example:  C:/MariaDB/OpenFlights/airlines.csv

LOAD DATA LOCAL INFILE 'C:/MariaDB/OpenFlights/airlines.csv'
INTO TABLE airlines
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'C:/MariaDB/OpenFlights/airport.csv'
INTO TABLE airports
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'C:/MariaDB/OpenFlights/airports-extended.csv'
INTO TABLE airports_extended
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'C:/MariaDB/OpenFlights/countries.csv'
INTO TABLE countries
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'C:/MariaDB/OpenFlights/planes.csv'
INTO TABLE planes
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'C:/MariaDB/OpenFlights/routes.csv'
INTO TABLE routes
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- ================================================================
-- Step 5: Clean invalid data
-- ================================================================
DELETE FROM routes
WHERE source_airport_id NOT IN (SELECT airport_id FROM airports)
   OR destination_airport_id NOT IN (SELECT airport_id FROM airports);

UPDATE routes
SET airline_id = NULL
WHERE airline_id IS NOT NULL
  AND airline_id NOT IN (SELECT airline_id FROM airlines);

-- ================================================================
-- Step 6: Drop old foreign keys if exist
-- ================================================================
ALTER TABLE routes DROP FOREIGN KEY IF EXISTS fk_routes_airlines_new;
ALTER TABLE routes DROP FOREIGN KEY IF EXISTS fk_routes_src_airport_new;
ALTER TABLE routes DROP FOREIGN KEY IF EXISTS fk_routes_dest_airport_new;

-- ================================================================
-- Step 7: Add new foreign keys
-- ================================================================
ALTER TABLE routes 
ADD CONSTRAINT fk_routes_airlines_new 
    FOREIGN KEY (airline_id) REFERENCES airlines(airline_id)
    ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE routes 
ADD CONSTRAINT fk_routes_src_airport_new 
    FOREIGN KEY (source_airport_id) REFERENCES airports(airport_id)
    ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE routes 
ADD CONSTRAINT fk_routes_dest_airport_new 
    FOREIGN KEY (destination_airport_id) REFERENCES airports(airport_id)
    ON DELETE SET NULL ON UPDATE CASCADE;

SET FOREIGN_KEY_CHECKS = 1;

-- ================================================================
-- Step 8: Quick verification
-- ================================================================
SELECT 
    (SELECT COUNT(*) FROM airlines) AS airline_count,
    (SELECT COUNT(*) FROM airports) AS airport_count,
    (SELECT COUNT(*) FROM countries) AS country_count,
    (SELECT COUNT(*) FROM planes) AS plane_count,
    (SELECT COUNT(*) FROM routes) AS route_count;

-- 🎉 Done: OpenFlights database loaded successfully!
-- ===============================================================================================================


What To Do (HeidiSQL Instructions)*

Save this SQL as:

openflights_init.sql

Place all CSVs in the same folder (e.g.):

C:/MariaDB/OpenFlights/

Enable local file loading in MariaDB:

Open HeidiSQL → New Query Tab

Run:

SET GLOBAL local_infile = 1;

Enable in HeidiSQL:

Right-click your session name → Edit → Advanced tab

✅ Tick: “Allow LOAD DATA LOCAL INFILE”

Open the SQL file in HeidiSQL → press F9 (Run).

Wait until all commands execute — the last query shows table counts.

If you see non-zero counts → ✅ your database is successfully loaded.
