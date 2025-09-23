-- Liverpool Natural History Museum Database Schema (SQL Server)

-- Botanist table
CREATE TABLE IF NOT EXISTS botanist (
    botanist_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20)
);


-- Country table 
CREATE TABLE IF NOT EXISTS country (
    country_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);


-- City table
CREATE TABLE IF NOT EXISTS city (
    city_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);


-- Coordinate table
CREATE TABLE IF NOT EXISTS coordinate (
    coordinate_id SERIAL PRIMARY KEY,
    latitude DECIMAL,
    longitude DECIMAL
);


-- Plant table
CREATE TABLE IF NOT EXISTS plant (
    plant_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(100),
    country_id INTEGER REFERENCES country(country_id),
    city_id INTEGER REFERENCES city(city_id),
    coordinate_id INTEGER REFERENCES coordinate(coordinate_id)
);


-- Recording table
CREATE TABLE IF NOT EXISTS recording (
    id SERIAL PRIMARY KEY, 
    plant_id INTEGER REFERENCES plant(plant_id),
    botanist_id INTEGER REFERENCES botanist(botanist_id),
    temperature DECIMAL,
    last_watered TIMESTAMP,
    soil_moisture DECIMAL,
    recording_taken TIMESTAMP
);

