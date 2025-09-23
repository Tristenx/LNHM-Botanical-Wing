-- Liverpool Natural History Museum Database Schema (SQL Server)

DROP TABLE alpha.recording
DROP TABLE alpha.plant
DROP TABLE alpha.coordinate
DROP TABLE alpha.city
DROP TABLE alpha.country
DROP TABLE alpha.botanist

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


-- Coordinate table
CREATE TABLE alpha.coordinate (
    coordinate_id INT PRIMARY KEY,
    latitude DECIMAL,
    longitude DECIMAL
);


-- Plant table
CREATE TABLE alpha.plant (
    plant_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(100),
    country_id INTEGER REFERENCES country(country_id),
    city_id INTEGER REFERENCES city(city_id),
    coordinate_id INTEGER REFERENCES coordinate(coordinate_id)
);


-- Recording table
CREATE TABLE alpha.recording (
    id INT PRIMARY KEY, 
    plant_id INTEGER REFERENCES plant(plant_id),
    botanist_id INTEGER REFERENCES botanist(botanist_id),
    temperature DECIMAL,
    last_watered TIMESTAMP,
    soil_moisture DECIMAL,
    recording_taken DATETIME
);

