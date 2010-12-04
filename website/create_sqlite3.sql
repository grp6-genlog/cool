BEGIN;CREATE TABLE "profiles_user" (
    "login" varchar(70) NOT NULL PRIMARY KEY,
    "password" varchar(50) NOT NULL,
    "number_of_seats" integer NOT NULL,
    "date_of_birth" date NOT NULL,
    "smoker" bool NOT NULL,
    "communities" varchar(100) NOT NULL,
    "money_per_km" real NOT NULL,
    "name" varchar(100) NOT NULL,
    "gender" varchar(1) NOT NULL,
    "bank_account_number" varchar(30) NOT NULL,
    "car_id" varchar(50) NOT NULL,
    "phone_number" varchar(20) NOT NULL,
    "car_description" text NOT NULL,
    "smartphone_id" varchar(100) NOT NULL,
    "mail" varchar(75) NOT NULL
)
;COMMIT;
BEGIN;CREATE TABLE "requests_request" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" varchar(70) NOT NULL,
    "departure_point_lat" real NOT NULL,
    "departure_point_long" real NOT NULL,
    "departure_range" real NOT NULL,
    "arrival_point_lat" real NOT NULL,
    "arrival_point_long" real NOT NULL,
    "arrival_range" real NOT NULL,
    "departure_time" datetime NOT NULL,
    "max_delay" integer NOT NULL,
    "nb_requested_seats" integer NOT NULL,
    "cancellation_margin" datetime NOT NULL
)
;
CREATE INDEX "requests_request_403f60f" ON "requests_request" ("user_id");COMMIT;
BEGIN;CREATE TABLE "proposals_proposal" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" varchar(70) NOT NULL,
    "car_id" varchar(50) NOT NULL,
    "car_description" text NOT NULL,
    "number_of_seats" integer NOT NULL,
    "money_per_km" real NOT NULL,
    "departure_time" datetime NOT NULL
)
;
CREATE TABLE "proposals_routepoints" (
    "id" integer NOT NULL PRIMARY KEY,
    "proposal_id" integer NOT NULL REFERENCES "proposals_proposal" ("id"),
    "latitude" real NOT NULL,
    "longitude" real NOT NULL
)
;
CREATE INDEX "proposals_proposal_403f60f" ON "proposals_proposal" ("user_id");
CREATE INDEX "proposals_routepoints_9e9fb7e" ON "proposals_routepoints" ("proposal_id");COMMIT;
BEGIN;CREATE TABLE "offers_offer" (
    "id" integer NOT NULL PRIMARY KEY,
    "request_id" integer NOT NULL,
    "proposal_id" integer NOT NULL,
    "status" varchar(1) NOT NULL,
    "driver_ok" bool NOT NULL,
    "non_driver_ok" bool NOT NULL
)
;
CREATE INDEX "offers_offer_792812e8" ON "offers_offer" ("request_id");
CREATE INDEX "offers_offer_9e9fb7e" ON "offers_offer" ("proposal_id");COMMIT;
BEGIN;CREATE TABLE "rides_ride" (
    "id" integer NOT NULL PRIMARY KEY,
    "offer_id" integer NOT NULL,
    "manuel_mode" bool NOT NULL,
    "ride_started" bool NOT NULL
)
;
CREATE INDEX "rides_ride_78131311" ON "rides_ride" ("offer_id");COMMIT;
BEGIN;CREATE TABLE "evaluations_evaluation" (
    "id" integer NOT NULL PRIMARY KEY,
    "ride_id" integer NOT NULL,
    "user_from_id" varchar(70) NOT NULL,
    "content" text NOT NULL,
    "locked" bool NOT NULL
)
;
CREATE INDEX "evaluations_evaluation_661b7e46" ON "evaluations_evaluation" ("ride_id");
CREATE INDEX "evaluations_evaluation_109d1495" ON "evaluations_evaluation" ("user_from_id");COMMIT;
