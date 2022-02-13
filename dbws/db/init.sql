create database adccali CHARACTER SET utf8 COLLATE utf8_general_ci;
use adccali;
		
CREATE TABLE patterns (
    id INT(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    pattern TEXT NOT NULL,
    description TEXT NOT NULL
);
-- Llave foranea
CREATE TABLE searches (
    id_pattern INT(10) NOT NULL,
    pmid INT(10) NOT NULL,
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    PRIMARY KEY (id_pattern,pmid)
);

INSERT INTO 
    patterns (pattern, description)
VALUES 
    ('Breast cancer AND 2020/01/01:2021/01/01[dp]','Principales'),
    ('Breast cancer','Main'),
    ('Cancer de cervix','Principales'),
    ('Cervical Cancer','Main'),
    ('Cancer de prostata','Principales'),
    ('Prostate cancer','Main'),
    ('Cancer de pulmon','Principales'),
    ('Lung cancer','Main');

-- INSERT INTO 
--     searches (id_pattern, pmid, title, abstract)
-- VALUES 
--     (1,'1','Principales','Principales'),
--     (2,'1','Main','Principales'),
--     (3,'1','Principales','Principales'),
--     (4,'1','Main','Principales'),
--     (5,'1','Principales','Principales'),
--     (6,'1','Main','Principales'),
--     (7,'1','Principales','Principales'),
--     (8,'1','Main','Principales');
