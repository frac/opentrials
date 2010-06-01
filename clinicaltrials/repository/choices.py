# coding: utf-8

## Qualifiers for the relationship of secondary entities with a ClinicalTrial #

INSTITUTIONAL_RELATION = [
    ('SupportSource', 'Source of monetary or material support'), #TRDS 4
    ('SecondarySponsor', 'Secondary sponsor'), #TRDS 6
]

CONTACT_RELATION = [
    ('PublicContact', 'Contact for Public Queries'), #TRDS 7
    ('ScientificContact', 'Contact for Scientific Queries'), #TRDS 8
    ('SiteContact', 'Contact for Site Queries'), #TRDS 8
]

CONTACT_STATUS = [
    ('Active', 'Active and current contact'),
    ('Inactive', 'Inactive or previous contact'),
]

OUTCOME_INTEREST = [
    ('primary', 'Primary'), # TRDS 19
    ('secondary', 'Secondary'), # TRDS 20
]

#################################################### Limited choices fields ###

PUBLISHED_STATUS = 'published'
TRIAL_RECORD_STATUS = [
    ('processing', 'processing'),
    ('published', 'published'),
    ('archived', 'archived'),
]

INCLUSION_GENDER = [('-', 'both'), ('M', 'male'), ('F', 'female'),]

INCLUSION_AGE_UNIT = [
    ('-', 'no limit'),
    ('Y', 'years'),
    ('M', 'months'),
    ('W', 'weeks'),
    ('D', 'days'),
    ('H', 'hours'),
]

######################################################## Descriptor choices ###

TRIAL_ASPECT = [
    ('HealthCondition', 'Health Condition or Problem Studied'), #TRDS 12
    ('Intervention', 'Intervention'), #TRDS 13
]

DESCRIPTOR_LEVEL = [
    ('general', 'General'),
    ('specific', 'Specific'),
]

DESCRIPTOR_VOCABULARY = [
    ('DeCS', 'DeCS: Health Sciences Descriptors'),
    ('ICD-10', 'ICD-10: International Classification of Diseases (10th. rev.)'),
    ('CAS', 'Chemical Abstracts Service'),
]
