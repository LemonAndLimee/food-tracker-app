CREATE TABLE Product(
    code TEXT PRIMARY KEY NOT NULL,
    product_name TEXT NOT NULL,
    generic_name TEXT,
    brands TEXT,
    quantity VARCHAR(10) NOT NULL,
    stores TEXT,
    serving_size VARCHAR(10),

    energy_kcal_100g DECIMAL NOT NULL,
    fat_100g DECIMAL NOT NULL,
    saturates_100g DECIMAL NOT NULL,
    carbohydrates_100g DECIMAL NOT NULL,
    sugars_100g DECIMAL NOT NULL,
    fibre_100g DECIMAL,
    proteins_100g DECIMAL NOT NULL,
    sodium_100g DECIMAL NOT NULL,

    energy_kcal_serving DECIMAL,
    fat_serving DECIMAL,
    saturates_serving DECIMAL,
    carbohydrates_serving DECIMAL,
    sugars_serving DECIMAL,
    fibre_serving DECIMAL,
    proteins_serving DECIMAL,
    sodium_serving DECIMAL
)