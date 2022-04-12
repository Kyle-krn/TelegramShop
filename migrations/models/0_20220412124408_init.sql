-- upgrade --
CREATE TABLE IF NOT EXISTS "archivestringattrs" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "string" VARCHAR(255) NOT NULL UNIQUE
);
COMMENT ON TABLE "archivestringattrs" IS 'Костыль, фиксит ошибку клавиатуры, в callback максимум 32 кирилические буквы влезает, это крайне мало';
CREATE TABLE IF NOT EXISTS "uploadphoto" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "path" VARCHAR(255) NOT NULL,
    "photo_id" VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT NOT NULL UNIQUE,
    "username" VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS "favoriteproduct" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "product_id" INT NOT NULL,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "profile" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(50),
    "last_name" VARCHAR(50),
    "phone_number" VARCHAR(15),
    "postcode" INT,
    "city" VARCHAR(100),
    "address" TEXT,
    "user_id" INT NOT NULL UNIQUE REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "searchuserdata" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "min_price" DECIMAL(1000,2),
    "max_price" DECIMAL(1000,2),
    "attrs" JSONB,
    "search" BOOL NOT NULL  DEFAULT False,
    "category_id" INT NOT NULL,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "usercart" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "product_id" INT NOT NULL,
    "quantity" INT NOT NULL  DEFAULT 1,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
