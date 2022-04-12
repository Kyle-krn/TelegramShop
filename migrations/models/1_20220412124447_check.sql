-- upgrade --
ALTER TABLE "usercart" ADD "active" BOOL NOT NULL  DEFAULT True;
-- downgrade --
ALTER TABLE "usercart" DROP COLUMN "active";
