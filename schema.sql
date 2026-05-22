-- ============================================================
-- PESO Employment Application System - Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS peso_db;
USE peso_db;

-- Employer Table
CREATE TABLE Employer (
    Employer_ID VARCHAR(10) NOT NULL AUTO_INCREMENT,
    Employer_Name VARCHAR(50) NOT NULL,
    Employer_Address VARCHAR(80) NOT NULL,
    Business_Nature VARCHAR(30) NULL,
    PRIMARY KEY (Employer_ID)
);

-- Applicant Table
CREATE TABLE Applicant (
    Applicant_ID VARCHAR(10) NOT NULL,
    Name VARCHAR(50) NOT NULL,
    Address VARCHAR(80) NOT NULL,
    Birthdate DATE NOT NULL,
    Place_Birth VARCHAR(80) NOT NULL,
    Age INTEGER NOT NULL CHECK (Age > 15),
    Sex CHAR(1) NOT NULL CHECK (Sex IN ('M', 'F', 'O')),
    Height INTEGER NULL CHECK (Height > 0),
    Weight INTEGER NULL CHECK (Weight > 0),
    Religion VARCHAR(20) NULL,
    Civil_Status VARCHAR(15) NOT NULL CHECK (Civil_Status IN ('Single', 'Married', 'Separated', 'Widow')),
    Landline_No VARCHAR(15) NULL,
    Mobile_No VARCHAR(15) NOT NULL,
    Email_Address VARCHAR(80) NULL,
    PRIMARY KEY (Applicant_ID)
);

-- Educational Background Table
CREATE TABLE Educational_Background (
    Educ_Level VARCHAR(20) NOT NULL CHECK (Educ_Level IN ('Elementary', 'High School', 'College')),
    Applicant_ID VARCHAR(10) NOT NULL,
    School_Name VARCHAR(80) NOT NULL,
    HighestLevelComp VARCHAR(80) NOT NULL,
    Year_Graduated INTEGER NOT NULL CHECK (Year_Graduated >= 1970),
    PRIMARY KEY (Educ_Level, Applicant_ID),
    FOREIGN KEY (Applicant_ID) REFERENCES Applicant(Applicant_ID) ON DELETE CASCADE
);

-- Skills Table
CREATE TABLE Skills_Acquired (
    SkillCD VARCHAR(10) NOT NULL,
    Skills VARCHAR(50) NOT NULL,
    PRIMARY KEY (SkillCD)
);

-- Training Certificates Table
CREATE TABLE Training_Certificates (
    TrainingCert_ID INTEGER NOT NULL AUTO_INCREMENT,
    Applicant_ID VARCHAR(10) NOT NULL,
    Training_Cert VARCHAR(80) NOT NULL,
    Training_Period VARCHAR(50) NOT NULL,
    SkillCD VARCHAR(10) NOT NULL,
    PRIMARY KEY (TrainingCert_ID),
    FOREIGN KEY (Applicant_ID) REFERENCES Applicant(Applicant_ID) ON DELETE CASCADE,
    FOREIGN KEY (SkillCD) REFERENCES Skills_Acquired(SkillCD)
);

-- Credentials Table
CREATE TABLE Credentials (
    Credentials_ID INTEGER NOT NULL AUTO_INCREMENT,
    Applicant_ID VARCHAR(10) NOT NULL,
    Credentials_Title VARCHAR(80) NOT NULL,
    PRIMARY KEY (Credentials_ID),
    FOREIGN KEY (Applicant_ID) REFERENCES Applicant(Applicant_ID) ON DELETE CASCADE
);

-- Overseas Filipino Table
CREATE TABLE Overseas_Filipino (
    OF_ID INTEGER NOT NULL AUTO_INCREMENT,
    Applicant_ID VARCHAR(10) NOT NULL,
    If_OverseasFilipino VARCHAR(5) NOT NULL CHECK (If_OverseasFilipino IN ('Yes', 'No')),
    OF_Dependent VARCHAR(20) NULL CHECK (OF_Dependent IN ('Wife/Husband', 'Parents', 'Brother/Sister', 'Son/Daughter')),
    OF_Location VARCHAR(20) NULL CHECK (OF_Location IN ('Land-Based', 'Sea-Based')),
    OF_Status VARCHAR(80) NULL CHECK (OF_Status IN ('Already at the jobsite', 'Vacation', 'Finished contract', 'Willing to go back at work', 'Repatriated')),
    PRIMARY KEY (OF_ID),
    FOREIGN KEY (Applicant_ID) REFERENCES Applicant(Applicant_ID) ON DELETE CASCADE
);

-- Employment Table
CREATE TABLE Employment (
    Employment_ID INTEGER NOT NULL AUTO_INCREMENT,
    Applicant_ID VARCHAR(10) NOT NULL,
    Employment_Status VARCHAR(20) NOT NULL CHECK (Employment_Status IN ('Wage Employed', 'Self Employed', 'Unemployed', 'Finished contract', 'Resigned', 'Terminated/Laid off', 'Close shop')),
    Position_LastEmployer VARCHAR(30) NULL,
    Current_Position VARCHAR(30) NOT NULL,
    Employer_ID VARCHAR(10) NOT NULL,
    PRIMARY KEY (Employment_ID),
    FOREIGN KEY (Applicant_ID) REFERENCES Applicant(Applicant_ID) ON DELETE CASCADE,
    FOREIGN KEY (Employer_ID) REFERENCES Employer(Employer_ID)
);

-- Language Spoken Table
CREATE TABLE Language_Spoken (
    Linguistic_ID INTEGER NOT NULL AUTO_INCREMENT,
    Applicant_ID VARCHAR(10) NOT NULL,
    Linguistic VARCHAR(80) NOT NULL,
    PRIMARY KEY (Linguistic_ID),
    FOREIGN KEY (Applicant_ID) REFERENCES Applicant(Applicant_ID) ON DELETE CASCADE
);

-- ============================================================
-- SIMPLE QUERIES (3)
-- ============================================================

-- Simple 1: Select all applicants
-- SELECT * FROM Applicant;

-- Simple 2: Insert a new skill
-- INSERT INTO Skills_Acquired (SkillCD, Skills) VALUES ('SK001', 'Computer Literacy');

-- Simple 3: Delete an applicant by ID
-- DELETE FROM Applicant WHERE Applicant_ID = 'AP001';

-- ============================================================
-- MODERATE QUERIES (4)
-- ============================================================

-- Moderate 1: Select applicants filtered by civil status
-- SELECT Applicant_ID, Name, Civil_Status FROM Applicant WHERE Civil_Status = 'Single';

-- Moderate 2: Update employment status
-- UPDATE Employment SET Employment_Status = 'Unemployed' WHERE Applicant_ID = 'AP001';

-- Moderate 3: Select applicants with their employer using JOIN
-- SELECT a.Name, e.Employment_Status, emp.Employer_Name
-- FROM Applicant a
-- JOIN Employment e ON a.Applicant_ID = e.Applicant_ID
-- JOIN Employer emp ON e.Employer_ID = emp.Employer_ID;

-- Moderate 4: Select applicants with their languages
-- SELECT a.Name, l.Linguistic
-- FROM Applicant a
-- JOIN Language_Spoken l ON a.Applicant_ID = l.Applicant_ID;

-- ============================================================
-- DIFFICULT QUERIES (3)
-- ============================================================

-- Difficult 1: Count applicants per employment status
-- SELECT Employment_Status, COUNT(*) AS Total
-- FROM Employment
-- GROUP BY Employment_Status
-- ORDER BY Total DESC;

-- Difficult 2: Applicants with more than one training certificate
-- SELECT a.Name, COUNT(t.TrainingCert_ID) AS Total_Trainings
-- FROM Applicant a
-- JOIN Training_Certificates t ON a.Applicant_ID = t.Applicant_ID
-- GROUP BY a.Applicant_ID, a.Name
-- HAVING COUNT(t.TrainingCert_ID) > 1;

-- Difficult 3: Applicants who are overseas Filipinos with dependents
-- SELECT a.Name, o.OF_Dependent, o.OF_Location, o.OF_Status
-- FROM Applicant a
-- JOIN Overseas_Filipino o ON a.Applicant_ID = o.Applicant_ID
-- WHERE o.If_OverseasFilipino = 'Yes' AND o.OF_Dependent IS NOT NULL;
