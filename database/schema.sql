-- ============================================================
-- LiveLong AI – Database Schema v3
-- ============================================================

CREATE TABLE IF NOT EXISTS symptoms (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    keywords    TEXT NOT NULL,
    severity    TEXT NOT NULL CHECK(severity IN ('low','medium','critical')),
    description TEXT
);

CREATE TABLE IF NOT EXISTS conditions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    symptom_ids   TEXT NOT NULL,
    severity      TEXT NOT NULL CHECK(severity IN ('low','medium','critical')),
    description   TEXT
);

CREATE TABLE IF NOT EXISTS cost_ranges (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    condition_id    INTEGER NOT NULL,
    care_type       TEXT NOT NULL CHECK(care_type IN ('govt','private','clinic','home')),
    min_cost        INTEGER NOT NULL,
    max_cost        INTEGER NOT NULL,
    includes        TEXT,
    consult_cost    INTEGER DEFAULT 0,
    medicine_cost   INTEGER DEFAULT 0,
    test_cost       INTEGER DEFAULT 0,
    stay_cost       INTEGER DEFAULT 0,
    FOREIGN KEY (condition_id) REFERENCES conditions(id)
);

CREATE TABLE IF NOT EXISTS hospitals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    city        TEXT NOT NULL,
    type        TEXT NOT NULL CHECK(type IN ('govt','private','clinic')),
    address     TEXT,
    phone       TEXT,
    emergency   INTEGER DEFAULT 0,
    rating      REAL DEFAULT 4.0,
    strength    TEXT,
    distance_km REAL DEFAULT 3.0
);

CREATE TABLE IF NOT EXISTS recommendations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    symptoms_input  TEXT,
    city            TEXT,
    budget          INTEGER,
    severity_result TEXT,
    recommendation  TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SYMPTOMS
-- ============================================================
INSERT OR IGNORE INTO symptoms (name, keywords, severity, description) VALUES
('fever',           'fever,temperature,high temp,pyrexia,hot body',           'low',      'Body temperature above 38°C'),
('high_fever',      'very high fever,104,105,burning up,extreme fever',       'medium',   'Body temperature above 39.5°C'),
('cough',           'cough,coughing,dry cough,wet cough,persistent cough',    'low',      'Persistent cough'),
('severe_cough',    'blood cough,coughing blood,hemoptysis,chest cough',      'critical', 'Coughing blood or severe chest cough'),
('cold',            'cold,runny nose,sneezing,nasal,stuffy nose,congestion',  'low',      'Common cold symptoms'),
('headache',        'headache,head pain,migraine,head ache,migraine attack',  'low',      'Head pain or migraine'),
('severe_headache', 'severe headache,worst headache,thunderclap,sudden head', 'critical', 'Sudden severe headache'),
('chest_pain',      'chest pain,chest pressure,chest tightness,heart pain',  'critical', 'Pain or pressure in chest'),
('stomach_pain',    'stomach pain,abdominal pain,stomach ache,belly pain,gastric','medium','Pain in abdominal area'),
('vomiting',        'vomiting,nausea,throwing up,vomit,feeling sick',        'medium',   'Vomiting or persistent nausea'),
('diarrhea',        'diarrhea,loose motion,loose stools,dysentery,watery stools','medium','Frequent loose stools'),
('breathlessness',  'breathless,shortness of breath,difficulty breathing,cant breathe,cannot breathe','critical','Difficulty breathing'),
('skin_rash',       'rash,skin rash,itching,hives,urticaria,skin allergy',   'low',      'Skin rash or itching'),
('joint_pain',      'joint pain,arthritis,knee pain,body ache,muscle pain',  'low',      'Pain in joints'),
('dizziness',       'dizziness,dizzy,lightheaded,vertigo,spinning head',     'medium',   'Feeling of dizziness'),
('fainting',        'fainted,fainting,unconscious,passed out,loss of consciousness','critical','Loss of consciousness'),
('eye_pain',        'eye pain,red eye,eye infection,conjunctivitis,burning eyes','low',  'Eye pain or infection'),
('ear_pain',        'ear pain,earache,ear infection,ear discharge',          'low',      'Ear pain or infection'),
('diabetes_symptom','excessive thirst,frequent urination,blurry vision,sudden weight loss,sugar symptoms','medium','Possible diabetes symptoms'),
('dengue_symptom',  'dengue,bone pain,retro orbital,platelet,rash fever,dengue symptoms','critical','Possible dengue symptoms'),
('back_pain',       'back pain,lower back,spine pain,backache',              'low',      'Lower or upper back pain'),
('sore_throat',     'sore throat,throat pain,tonsil,difficulty swallowing',  'low',      'Throat pain or tonsillitis'),
('weakness',        'weakness,fatigue,tiredness,no energy,exhausted,lethargic','low',   'General weakness or fatigue'),
('high_bp',         'high blood pressure,hypertension,bp high,blood pressure high','medium','High blood pressure symptoms');

-- ============================================================
-- CONDITIONS
-- ============================================================
INSERT OR IGNORE INTO conditions (name, symptom_ids, severity, description) VALUES
('Common Cold',           '1,3,5,22',     'low',      'Viral upper respiratory infection'),
('Flu / Influenza',       '2,3,6,23',     'medium',   'Influenza virus infection'),
('Gastroenteritis',       '9,10,11',      'medium',   'Stomach flu or food poisoning'),
('Dengue Fever',          '1,6,14,20',    'critical', 'Dengue viral infection – needs urgent care'),
('Hypertensive Crisis',   '7,24',         'critical', 'Dangerously high blood pressure'),
('Cardiac Emergency',     '8,12',         'critical', 'Possible cardiac event – call 108 immediately'),
('Migraine',              '6',            'low',      'Severe recurring headache'),
('Skin Allergy',          '13',           'low',      'Allergic skin reaction'),
('Diabetes (suspected)',  '19',           'medium',   'Possible uncontrolled diabetes'),
('Respiratory Distress',  '12,4',         'critical', 'Breathing emergency – call 108'),
('Musculoskeletal Pain',  '14,21',        'low',      'Joint, muscle, or back pain'),
('Eye Infection',         '17',           'low',      'Conjunctivitis or eye infection'),
('Ear Infection',         '18',           'low',      'Otitis media or ear canal infection'),
('Throat Infection',      '22,3',         'low',      'Tonsillitis or pharyngitis'),
('Generalised Weakness',  '23,15',        'low',      'Fatigue or general body weakness');

-- ============================================================
-- COST RANGES  (with breakdown columns)
-- ============================================================
INSERT OR IGNORE INTO cost_ranges (condition_id, care_type, min_cost, max_cost, includes, consult_cost, medicine_cost, test_cost, stay_cost) VALUES
-- Common Cold (id=1)
(1,'home',    100,  500,  'OTC medicines + rest',             0,   300, 0,    0),
(1,'clinic',  200,  700,  'Consultation + medicines',         200, 300, 0,    0),
(1,'govt',    0,    200,  'Free consultation + subsidised meds',50, 100, 0,   0),
(1,'private', 600,  1800, 'Consultation + tests + medicines', 500, 400, 300,  0),
-- Flu (id=2)
(2,'home',    300,  800,  'Antiviral OTC + rest',             0,   600, 0,    0),
(2,'clinic',  400,  1000, 'Consultation + antiviral',         300, 500, 0,    0),
(2,'govt',    50,   400,  'Subsidised care',                  50,  200, 100,  0),
(2,'private', 800,  2800, 'Full workup + medicines',          600, 600, 500,  0),
-- Gastroenteritis (id=3)
(3,'home',    200,  600,  'ORS + rest',                       0,   400, 0,    0),
(3,'clinic',  400,  1200, 'Consultation + ORS + medicines',   300, 400, 200,  0),
(3,'govt',    50,   500,  'Subsidised treatment',             50,  200, 150,  0),
(3,'private', 1000, 5000, 'IV fluids + medicines + tests',    600, 800, 800, 1000),
-- Dengue (id=4)
(4,'govt',    500,  4000, 'Ward + blood tests daily',         200, 500,1500, 1500),
(4,'private', 8000,40000, 'ICU + platelet monitoring',       1000,2000,5000,25000),
-- Hypertensive Crisis (id=5)
(5,'govt',    300,  2000, 'ER + medicines + monitoring',      200, 500, 500,  500),
(5,'private', 3000,18000, 'ER + ICU + monitoring',           1000,2000,3000, 8000),
-- Cardiac Emergency (id=6)
(6,'govt',    1000,12000, 'Emergency + basic cardiac care',   500,1000,2500, 6000),
(6,'private',50000,350000,'ICU + surgery + stent',          5000,10000,30000,200000),
-- Migraine (id=7)
(7,'home',    100,  400,  'OTC painkillers + rest',           0,   300, 0,    0),
(7,'clinic',  300,  900,  'Consultation + prescription',      300, 400, 0,    0),
(7,'govt',    0,    300,  'Consultation + medicines',         50,  200, 0,    0),
(7,'private', 700,  2500, 'Neurologist + medicines',          800, 500, 500,  0),
-- Skin Allergy (id=8)
(8,'home',    100,  500,  'Antihistamine cream/tablets',      0,   400, 0,    0),
(8,'clinic',  300,  800,  'Dermatologist + cream',            300, 300, 0,    0),
(8,'govt',    0,    300,  'Subsidised treatment',             50,  200, 0,    0),
(8,'private', 700,  2200, 'Dermatologist + patch test',       800, 400, 600,  0),
-- Diabetes (id=9)
(9,'govt',    200,  900,  'Blood sugar test + consultation',  100, 200, 500,  0),
(9,'private', 1000, 4500, 'HbA1c + full panel + consult',    800, 500,2500,  0),
-- Respiratory Distress (id=10)
(10,'govt',   500,  6000, 'Emergency + oxygen + medicines',   300, 500,1000, 3500),
(10,'private',5000,55000, 'ICU + ventilator if needed',      1000,2000,5000,40000),
-- Musculoskeletal Pain (id=11)
(11,'home',   100,  500,  'Painkillers + rest',               0,   400, 0,    0),
(11,'clinic', 300,  900,  'Consultation + physio',            300, 300, 200,  0),
(11,'govt',   0,    400,  'Subsidised care',                  50,  200, 100,  0),
(11,'private',900,  3500, 'Specialist + tests + physio',      800, 500,1200,  0),
-- Eye Infection (id=12)
(12,'home',   100,  350,  'Eye drops OTC',                    0,   300, 0,    0),
(12,'clinic', 200,  700,  'Ophthalmologist visit',            300, 300, 0,    0),
(12,'govt',   0,    250,  'Free eye care',                    50,  150, 0,    0),
(12,'private',600,  1800, 'Specialist + drops + tests',       700, 400, 500,  0),
-- Ear Infection (id=13)
(13,'home',   100,  350,  'OTC ear drops',                    0,   300, 0,    0),
(13,'clinic', 300,  800,  'ENT consultation + drops',         300, 300, 0,    0),
(13,'govt',   0,    350,  'Subsidised ENT care',              50,  200, 0,    0),
(13,'private',700,  2000, 'ENT specialist + medicines',       700, 400, 500,  0),
-- Throat Infection (id=14)
(14,'home',   100,  400,  'Warm fluids + OTC lozenges',       0,   300, 0,    0),
(14,'clinic', 200,  700,  'Consultation + antibiotics',       250, 300, 0,    0),
(14,'govt',   0,    300,  'Subsidised treatment',             50,  200, 0,    0),
(14,'private',600,  1800, 'ENT specialist + culture test',    700, 400, 500,  0),
-- Generalised Weakness (id=15)
(15,'home',   100,  500,  'Rest + vitamins + nutrition',      0,   400, 0,    0),
(15,'clinic', 300,  900,  'Consultation + blood test',        300, 200, 350,  0),
(15,'govt',   50,   400,  'Consultation + basic tests',       50,  150, 200,  0),
(15,'private',800,  2500, 'Specialist + full blood panel',    700, 300,1200,  0);

-- ============================================================
-- HOSPITALS — 10 Cities, 3+ hospitals each
-- ============================================================
INSERT OR IGNORE INTO hospitals (name, city, type, address, phone, emergency, rating, strength, distance_km) VALUES
-- DELHI
('AIIMS New Delhi',              'delhi',     'govt',    'Ansari Nagar, New Delhi',             '011-26588500', 1, 4.5, 'Top-tier research hospital with all specialities', 5.2),
('Safdarjung Hospital',         'delhi',     'govt',    'Ring Road, New Delhi',                '011-26165060', 1, 4.1, 'Large govt hospital with 24/7 emergency wing',     3.1),
('Lok Nayak Hospital',          'delhi',     'govt',    'Jawahar Lal Nehru Marg, Delhi',       '011-23232400', 1, 3.9, 'Affordable care with good emergency services',     4.5),
('Max Super Speciality Saket',  'delhi',     'private', 'Saket, New Delhi',                    '011-26515050', 1, 4.4, 'Premium private care, fast diagnostics',           6.8),
('Apollo Hospital Delhi',        'delhi',     'private', 'Sarita Vihar, New Delhi',             '011-71791090', 1, 4.5, 'Top private hospital with cardiac centre',          8.1),
('Fortis Escorts Heart Inst.',  'delhi',     'private', 'Okhla Road, New Delhi',               '011-47135000', 1, 4.3, 'Specialised cardiac and critical care',             7.4),
('Care Plus Clinic Lajpat Nagar','delhi',    'clinic',  'Lajpat Nagar, New Delhi',             '011-29842200', 0, 4.0, 'Fast OPD, minimal wait time',                      1.2),
-- MUMBAI
('KEM Hospital',                'mumbai',    'govt',    'Parel, Mumbai',                       '022-24107000', 1, 4.2, 'Largest govt hospital in Mumbai with trauma centre',2.3),
('JJ Hospital',                 'mumbai',    'govt',    'Byculla, Mumbai',                     '022-23735555', 1, 4.0, 'Government hospital with strong general medicine',   3.7),
('Nair Hospital',               'mumbai',    'govt',    'Mumbai Central, Mumbai',              '022-23027600', 1, 3.9, 'Affordable, wide coverage of specialities',         4.2),
('Kokilaben Hospital',          'mumbai',    'private', 'Andheri West, Mumbai',                '022-30999999', 1, 4.6, 'Premium care, robotic surgery available',           9.1),
('Lilavati Hospital',           'mumbai',    'private', 'Bandra West, Mumbai',                 '022-26751000', 1, 4.4, 'Top-rated private hospital, all specialities',      7.5),
('Hinduja Hospital',            'mumbai',    'private', 'Mahim, Mumbai',                       '022-24452222', 1, 4.3, 'Comprehensive private care with ICU',               6.3),
('Medicare Polyclinic Dadar',   'mumbai',    'clinic',  'Dadar West, Mumbai',                  '022-24302200', 0, 4.1, 'Quick consultation, affordable fees',               1.5),
-- BANGALORE
('Victoria Hospital',           'bangalore', 'govt',    'Fort Road, Bengaluru',                '080-26701150', 1, 4.0, 'Central govt hospital with trauma care',            2.8),
('Bowring Hospital',            'bangalore', 'govt',    'Shivaji Nagar, Bengaluru',            '080-25561610', 1, 3.8, 'Affordable state-run hospital',                     4.1),
('NIMHANS',                     'bangalore', 'govt',    'Hosur Road, Bengaluru',               '080-46110007', 1, 4.4, 'Premier institution for neurosciences',             5.6),
('Manipal Hospital',            'bangalore', 'private', 'Old Airport Road, Bengaluru',         '080-25023200', 1, 4.5, 'Multi-speciality, advanced diagnostics',            6.2),
('Fortis Hospital Bangalore',   'bangalore', 'private', 'Bannerghatta Rd, Bengaluru',          '080-66214444', 1, 4.3, 'Premium care with cardiology expertise',            7.8),
('Narayana Health City',        'bangalore', 'private', 'Bommasandra, Bengaluru',              '080-71222222', 1, 4.5, 'Affordable private care, cardiac speciality',       9.3),
('HealthFirst Clinic Indiranagar','bangalore','clinic', 'Indiranagar, Bengaluru',              '080-41154321', 0, 4.2, 'Walk-in friendly, minimal wait',                   1.0),
-- CHENNAI
('Govt General Hospital Chennai','chennai',  'govt',    'Park Town, Chennai',                  '044-25305000', 1, 4.1, 'Largest govt hospital in TN, all specialities',    2.5),
('Stanley Medical College',     'chennai',   'govt',    'Old Jail Rd, Chennai',                '044-25281201', 1, 3.9, 'Teaching hospital with wide coverage',              4.0),
('Rajiv Gandhi Govt Hospital',  'chennai',   'govt',    'Park Town, Chennai',                  '044-28193001', 1, 3.8, 'Good trauma and emergency care',                   3.2),
('Apollo Hospital Chennai',     'chennai',   'private', 'Greams Road, Chennai',                '044-28290200', 1, 4.6, 'Premium hospital, globally recognised',             5.4),
('MIOT International',          'chennai',   'private', 'Manapakkam, Chennai',                 '044-22496789', 1, 4.4, 'Advanced orthopaedic and joint care',               7.1),
('Kauvery Hospital',            'chennai',   'private', 'Alwarpet, Chennai',                   '044-28387777', 1, 4.3, 'Strong cardiac and critical care',                  6.8),
('Medisquare Clinic Adyar',     'chennai',   'clinic',  'Adyar, Chennai',                      '044-24413210', 0, 4.0, 'Trusted neighbourhood clinic',                     1.3),
-- HYDERABAD
('Osmania General Hospital',    'hyderabad', 'govt',    'Afzalgunj, Hyderabad',                '040-24600129', 1, 4.0, 'Major govt hospital with 24/7 emergency',          3.5),
('NIMS Hyderabad',              'hyderabad', 'govt',    'Punjagutta, Hyderabad',               '040-23489000', 1, 4.2, 'Premier govt institute for all specialities',       4.8),
('Gandhi Medical College Hosp', 'hyderabad', 'govt',    'Musheerabad, Hyderabad',              '040-23688820', 1, 3.9, 'Affordable government care with lab facilities',   5.1),
('Yashoda Hospital Somajiguda', 'hyderabad', 'private', 'Somajiguda, Hyderabad',               '040-45670000', 1, 4.4, 'Multi-speciality with strong ICU',                 4.2),
('Apollo Hospital Hyderabad',   'hyderabad', 'private', 'Jubilee Hills, Hyderabad',            '040-23607777', 1, 4.5, 'Top-tier private care in Hyderabad',               6.7),
('Care Hospitals Hyderabad',    'hyderabad', 'private', 'Banjara Hills, Hyderabad',            '040-30418888', 1, 4.3, 'Comprehensive private care across specialities',    5.9),
('Sunrise Clinic Ameerpet',     'hyderabad', 'clinic',  'Ameerpet, Hyderabad',                 '040-23742200', 0, 4.0, 'Quick consultations, affordable fees',             1.4),
-- VIZAG (Visakhapatnam)
('King George Hospital Vizag',  'vizag',     'govt',    'Maharanipeta, Visakhapatnam',         '0891-2564891', 1, 4.1, 'Largest govt hospital in Vizag region',            2.9),
('GEMS Hospital Vizag',         'vizag',     'govt',    'Gopalapatnam, Visakhapatnam',         '0891-2876543', 1, 3.9, 'Govt hospital with emergency and surgery',          4.3),
('Seven Hills Hospital',        'vizag',     'private', 'Rockdale Layout, Visakhapatnam',      '0891-2727272', 1, 4.3, 'Leading private hospital in Vizag',                3.1),
('Care Hospital Vizag',         'vizag',     'private', 'Ramnagar, Visakhapatnam',             '0891-6677000', 1, 4.2, 'Multi-speciality private care',                    5.7),
('Medicover Vizag',             'vizag',     'private', 'Steel Plant Road, Visakhapatnam',     '0891-6656789', 1, 4.4, 'Advanced diagnostics and speciality care',          6.5),
('HealthLine Clinic MVP Colony','vizag',     'clinic',  'MVP Colony, Visakhapatnam',           '0891-2511234', 0, 4.0, 'Convenient neighbourhood clinic',                  1.1),
-- NELLORE
('Govt General Hospital Nellore','nellore',  'govt',    'Grand Trunk Road, Nellore',           '0861-2322222', 1, 4.0, 'Main govt hospital in Nellore district',            2.2),
('District Head Quarters Hosp', 'nellore',   'govt',    'Musunuru Road, Nellore',              '0861-2311111', 1, 3.8, 'Govt hospital with maternity and general care',     3.6),
('Narayana Medical College',    'nellore',   'private', 'Chinthareddypalem, Nellore',          '0861-2318888', 1, 4.3, 'Teaching hospital with all specialities',           4.1),
('Sanjivani Hospital',          'nellore',   'private', 'Dargamitta, Nellore',                 '0861-2345678', 1, 4.1, 'Multi-speciality private care',                    3.8),
('Sri Venkateswara Clinic',     'nellore',   'clinic',  'Trunk Road, Nellore',                 '0861-2341234', 0, 3.9, 'Trusted local clinic, quick service',              1.5),
-- KOLKATA
('SSKM Hospital',               'kolkata',   'govt',    'AJC Bose Road, Kolkata',              '033-22044444', 1, 4.1, 'Premier govt hospital, all specialities',           3.4),
('NRS Medical College',         'kolkata',   'govt',    'AJC Bose Road, Kolkata',              '033-22658498', 1, 3.9, 'Large govt teaching hospital',                     4.2),
('RG Kar Medical College',      'kolkata',   'govt',    'Belgachia, Kolkata',                  '033-25551230', 1, 3.8, 'Govt hospital with emergency services',             5.0),
('Apollo Gleneagles',           'kolkata',   'private', 'Canal Circular Rd, Kolkata',          '033-23208200', 1, 4.5, 'Premium private care, all specialities',            5.8),
('Fortis Hospital Kolkata',     'kolkata',   'private', 'Anandapur, Kolkata',                  '033-66284444', 1, 4.3, 'Multi-speciality with strong cardiac unit',         7.2),
('Care Polyclinic Gariahat',    'kolkata',   'clinic',  'Gariahat, Kolkata',                   '033-24639000', 0, 4.0, 'Quick OPD, affordable consultation',               1.6),
-- PUNE
('Sassoon General Hospital',    'pune',      'govt',    'Pune Station Rd, Pune',               '020-26128000', 1, 4.0, 'Largest govt hospital in Pune',                    3.1),
('Aundh District Hospital',     'pune',      'govt',    'Aundh, Pune',                         '020-25880000', 1, 3.9, 'Govt hospital with good general medicine',          4.8),
('Ruby Hall Clinic',            'pune',      'private', 'Sassoon Road, Pune',                  '020-66455100', 1, 4.4, 'Premium private care with cardiac centre',          3.5),
('Jehangir Hospital',           'pune',      'private', 'Sassoon Road, Pune',                  '020-66814444', 1, 4.3, 'Multi-speciality with strong orthopaedic unit',     4.1),
('MedPlus Clinic Kothrud',      'pune',      'clinic',  'Kothrud, Pune',                       '020-25382200', 0, 4.1, 'Convenient walk-in with minimal wait',             1.2),
-- AHMEDABAD
('Civil Hospital Ahmedabad',    'ahmedabad', 'govt',    'Asarwa, Ahmedabad',                   '079-22681800', 1, 4.1, 'Largest govt hospital in Gujarat',                 4.2),
('LG Hospital',                 'ahmedabad', 'govt',    'Maninagar, Ahmedabad',                '079-25323505', 1, 3.9, 'Govt hospital with broad specialities',             5.1),
('Apollo Hospital Ahmedabad',   'ahmedabad', 'private', 'Bhat, Ahmedabad',                     '079-66701000', 1, 4.4, 'Premium care, strong cardiac centre',               7.3),
('Sterling Hospital Ahmedabad', 'ahmedabad', 'private', 'Gurukul Road, Ahmedabad',             '079-40011000', 1, 4.3, 'Multi-speciality with advanced diagnostics',        6.1),
('HealthCare Clinic Navrangpura','ahmedabad','clinic',  'Navrangpura, Ahmedabad',              '079-26444321', 0, 4.0, 'Quick consultation, polyclinic services',           1.8);
