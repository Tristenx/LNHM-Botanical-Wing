-- Liverpool Natural History Museum Database Schema (SQL Server)

-- Drop any existing table 
DROP TABLE alpha.recording
DROP TABLE alpha.plant
DROP TABLE alpha.city
DROP TABLE alpha.country
DROP TABLE alpha.botanist


-- Botanist table
CREATE TABLE alpha.botanist (
    botanist_id INT PRIMARY KEY,
    botanist_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20)
);


-- Country table 
CREATE TABLE alpha.country (
    country_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);


-- City table
CREATE TABLE alpha.city (
    city_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);


-- Plant table
CREATE TABLE alpha.plant (
    plant_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(100),
    country_id INTEGER REFERENCES country(country_id),
    city_id INTEGER REFERENCES city(city_id),
    latitude DECIMAL,
    longitude DECIMAL
);


-- Recording table
CREATE TABLE alpha.recording (
    id INT IDENTITY(1,1), 
    plant_id INTEGER REFERENCES plant(plant_id),
    botanist_id INTEGER REFERENCES botanist(botanist_id),
    temperature DECIMAL,
    last_watered TIMESTAMP,
    soil_moisture DECIMAL,
    recording_taken DATETIME
);

