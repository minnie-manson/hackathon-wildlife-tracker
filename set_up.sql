DROP TABLE IF EXISTS wildlife;
CREATE TABLE IF NOT EXISTS wildlife (
    id SERIAL PRIMARY KEY,
    genus VARCHAR(255) NOT NULL,
    species VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    time_spotted TIMESTAMP
);
select *
from wildlife;