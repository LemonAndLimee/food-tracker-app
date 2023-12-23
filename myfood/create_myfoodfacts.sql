CREATE TABLE Product(
    code INTEGER PRIMARY KEY NOT NULL,
    product_name TEXT NOT NULL,
    generic_name TEXT,
    brands TEXT,
    quantity VARCHAR(10) NOT NULL,
    stores TEXT,
    serving_size INTEGER,

    energy_kcal_100g INTEGER NOT NULL,
    fat_100g INTEGER NOT NULL,
    saturated_fat_100g INTEGER NOT NULL,
    carbohydrates_100g INTEGER NOT NULL,
    sugars_100g INTEGER NOT NULL,
    fibre_100g INTEGER,
    proteins_100g INTEGER NOT NULL,
    sodium_100g INTEGER NOT NULL,

    energy_kcal_serving INTEGER,
    fat_serving INTEGER,
    saturated_fat_serving INTEGER,
    carbohydrates_serving INTEGER,
    sugars_serving INTEGER,
    fibre_serving INTEGER,
    proteins_serving INTEGER,
    sodium_serving INTEGER
)