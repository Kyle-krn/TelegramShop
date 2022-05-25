-- upgrade --
CREATE TABLE IF NOT EXISTS "test" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "string" VARCHAR(255) NOT NULL UNIQUE
);
COMMENT ON TABLE "test" IS 'Костыль, фиксит ошибку клавиатуры, в callback максимум 32 кирилические буквы влезает, это крайне мало';
-- downgrade --
DROP TABLE IF EXISTS "test";
