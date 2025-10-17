CREATE TABLE companies (
    id serial PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    email text NOT NULL,
    "password" text NOT NULL,
    "description" varchar(1000),
    company_logo text
);

CREATE TABLE jobs (
    id serial PRIMARY KEY,
    title varchar(100) NOT NULL,
    "location" varchar(100) NOT NULL,
    role_overview varchar(1000) NOT NULL,
    responsibilities varchar(600) NOT NULL,
    requirements varchar(600) NOT NULL,
    nice_to_haves varchar(600) NOT NULL,
    benefits varchar(600),
    pay_range text,
    posted_date timestamp DEFAULT NOW(),
    closing_date date,
    company_id int NOT NULL
        REFERENCES companies (id)
        ON DELETE CASCADE
);

CREATE TABLE employment_types (
    id serial PRIMARY KEY,
    "type" varchar(100) NOT NULL
);

CREATE TABLE departments (
    id serial PRIMARY KEY,
    "name" varchar(100) NOT NULL
);

CREATE TABLE employment_types_jobs (
    id serial PRIMARY KEY,
    employment_type_id int NOT NULL
        REFERENCES employment_types (id)
        ON DELETE CASCADE,
    job_id int NOT NULL
        REFERENCES jobs (id)
        ON DELETE CASCADE,
    UNIQUE (employment_type_id, job_id)
);

CREATE TABLE departments_jobs (
    id serial PRIMARY KEY,
    department_id int NOT NULL
        REFERENCES departments (id)
        ON DELETE CASCADE,
    job_id int NOT NULL
        REFERENCES jobs (id)
        ON DELETE CASCADE,
    UNIQUE (department_id, job_id)
);