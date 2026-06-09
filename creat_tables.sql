-- Таблица стран
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    south_lat FLOAT NOT NULL,   -- южная граница
    north_lat FLOAT NOT NULL,   -- северная граница
    west_lon FLOAT NOT NULL,    -- западная граница
    east_lon FLOAT NOT NULL     -- восточная граница
);

-- Таблица самолетов
CREATE TABLE IF NOT EXISTS aircraft (
    id SERIAL PRIMARY KEY,
    callsign VARCHAR(20) NOT NULL,        -- позывной
    origin_country VARCHAR(100),          -- страна регистрации
    velocity FLOAT,                       -- скорость (м/с)
    baro_altitude FLOAT,                  -- высота (м)
    country_id INTEGER REFERENCES countries(id),  -- связь со страной
    icao24 VARCHAR(10),                   -- уникальный идентификатор
    on_ground BOOLEAN DEFAULT FALSE,      -- на земле
    last_contact INTEGER,                 -- время последнего контакта
    created_at TIMESTAMP DEFAULT NOW()    -- время добавления записи
);

-- Индексы для ускорения поиска
CREATE INDEX IF NOT EXISTS idx_aircraft_country_id ON aircraft(country_id);
CREATE INDEX IF NOT EXISTS idx_aircraft_callsign ON aircraft(callsign);
CREATE INDEX IF NOT EXISTS idx_aircraft_origin_country ON aircraft(origin_country);
CREATE INDEX IF NOT EXISTS idx_aircraft_velocity ON aircraft(velocity);