CREATE TABLE companies (
    id serial PRIMARY KEY,
    "name" varchar(100) NOT NULL UNIQUE,
    "location" varchar(100) NOT NULL,
    email text NOT NULL UNIQUE,
    "password" text NOT NULL,
    "description" varchar(1000),
    logo text DEFAULT 'logo_placeholder.png'
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

-- initial passwords == 'secret'
INSERT INTO companies ("name", "location", email, "password")
VALUES ('Admin', 'Everywhere, World', 'admin@job_board.com', '$2b$12$EOyJaTWBTsvtBEVJlvj1S.sqYDYujWBvWw4BZRr8p80QzfnXhJv/m');

INSERT INTO companies ("name", "location", email, "password", "description")
VALUES
('BlueTech Solutions', 'Silicon Valley, CA', 'contact@bluetech.com', '$2b$12$EOyJaTWBTsvtBEVJlvj1S.sqYDYujWBvWw4BZRr8p80QzfnXhJv/m', 'Leading provider of innovative cloud-based solutions and enterprise software.'),
('PurpleWave Media', 'New York, NY', 'info@purplewavemedia.com', '$2b$12$EOyJaTWBTsvtBEVJlvj1S.sqYDYujWBvWw4BZRr8p80QzfnXhJv/m', 'A dynamic digital marketing agency specializing in content creation and social media strategy.'),
('GreenLeaf Eco', 'Austin, TX', 'support@greenleaf.eco', '$2b$12$EOyJaTWBTsvtBEVJlvj1S.sqYDYujWBvWw4BZRr8p80QzfnXhJv/m', 'Dedicated to sustainable energy solutions and environmental consulting.'),
('Quantum Leap AI', 'Boston, MA', 'careers@quantumleap.ai', '$2b$12$EOyJaTWBTsvtBEVJlvj1S.sqYDYujWBvWw4BZRr8p80QzfnXhJv/m', 'Pioneering advancements in artificial intelligence and machine learning for various industries.'),
('Starlight Gaming', 'Los Angeles, CA', 'hr@starlightgaming.com', '$2b$12$EOyJaTWBTsvtBEVJlvj1S.sqYDYujWBvWw4BZRr8p80QzfnXhJv/m', 'An independent game development studio creating immersive and engaging experiences for players worldwide.'),
('Apex Health', 'Chicago, IL', 'connect@apexhealth.com', '$2b$12$EOyJaTWBTsvtBEVJlvj1S.sqYDYujWBvWw4BZRr8p80QzfnXhJv/m', 'A healthcare technology company focused on improving patient outcomes through data analytics.'),
('SilverLining Finance', 'London, UK', 'contact@silverlining.finance', '$2b$12$EOyJaTWBTsvtBEVJlvj1S.sqYDYujWBvWw4BZRr8p80QzfnXhJv/m', 'Providing cutting-edge fintech solutions for personal and corporate finance management.');