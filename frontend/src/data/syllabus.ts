// /frontend/src/data/syllabus.ts

export interface SyllabusNode {
    id: string;
    title: string;
    description?: string;
    resources?: string[];
    children?: SyllabusNode[];
    status: 'locked' | 'unlocked' | 'mastered';
}

export const upscSyllabus: SyllabusNode = {
    id: 'root',
    title: 'UPSC CSE SAGA',
    description: 'The journey to LBSNAA. One step at a time.',
    status: 'unlocked',
    children: [
        // ==========================
        // PRELIMS
        // ==========================
        {
            id: 'prelims',
            title: 'Prelims Stage',
            description: 'The Qualifying Round. Objective Type.',
            status: 'unlocked',
            children: [
                {
                    id: 'pre_gs',
                    title: 'General Studies (Paper I)',
                    status: 'unlocked',
                    children: [
                        {
                            id: 'pre_hist',
                            title: 'History of India',
                            description: 'Ancient, Medieval, and Modern History.',
                            resources: ['NCERTs (Old & New)', 'Spectrum: Modern India', 'TN Board History'],
                            status: 'unlocked'
                        },
                        {
                            id: 'pre_art',
                            title: 'Art & Culture',
                            description: 'Architecture, Literature, Music, Dance, and Painting.',
                            resources: ['Nitin Singhania', 'CCRT Website', 'NCERT Class 11 Fine Arts'],
                            status: 'locked'
                        },
                        {
                            id: 'pre_geo',
                            title: 'Geography',
                            description: 'Physical, Social, Economic Geography of India & World.',
                            resources: ['NCERT Class 11 & 12', 'GC Leong', 'Atlas (Oxford/Orient Blackswan)'],
                            status: 'locked'
                        },
                        {
                            id: 'pre_pol',
                            title: 'Indian Polity',
                            description: 'Constitution, Political System, Panchayati Raj, Public Policy, Rights Issues.',
                            resources: ['M. Laxmikanth', 'NCERT Class 11: Indian Constitution at Work'],
                            status: 'locked'
                        },
                        {
                            id: 'pre_eco',
                            title: 'Economy',
                            description: 'Sustainable Development, Poverty, Inclusion, Demographics, Social Sector.',
                            resources: ['Ramesh Singh / Mrunal Notes', 'Economic Survey', 'Union Budget'],
                            status: 'locked'
                        },
                        {
                            id: 'pre_env',
                            title: 'Environment',
                            description: 'Bio-diversity, Climate Change, Ecology (General issues).',
                            resources: ['Shankar IAS Environment', 'PMF IAS', 'Current Affairs'],
                            status: 'locked'
                        },
                        {
                            id: 'pre_sci',
                            title: 'General Science',
                            description: 'Basic Physics, Chemistry, Biology and Current Technology trends.',
                            resources: ['NCERTs (6-10)', 'The Hindu S&T Page'],
                            status: 'locked'
                        }
                    ]
                },
                {
                    id: 'pre_csat',
                    title: 'CSAT (Paper II)',
                    description: 'Qualifying nature (33% required).',
                    status: 'locked',
                    children: [
                        { id: 'csat_reading', title: 'Reading Comprehension', status: 'locked' },
                        { id: 'csat_logic', title: 'Logical Reasoning', status: 'locked' },
                        { id: 'csat_math', title: 'General Mental Ability & Numeracy', status: 'locked' }
                    ]
                }
            ]
        },

        // ==========================
        // MAINS
        // ==========================
        {
            id: 'mains',
            title: 'Mains Stage',
            description: 'The Written Examination. Where rank is decided.',
            status: 'locked',
            children: [
                // --- ESSAY ---
                {
                    id: 'mains_essay',
                    title: 'Essay Paper',
                    description: 'Two essays to be written in 1000-1200 words each.',
                    resources: ['Yojana/Kurukshetra Magazines', 'Editorial Analysis', 'Philosophical Quotes'],
                    status: 'locked'
                },

                // --- GS I ---
                {
                    id: 'gs1',
                    title: 'GS I: Heritage, History, Geography & Society',
                    status: 'locked',
                    children: [
                        {
                            id: 'gs1_culture',
                            title: 'Indian Heritage & Culture',
                            description: 'Art forms, literature and architecture from ancient to modern times.',
                            resources: ['Nitin Singhania', 'NCERT Fine Arts'],
                            status: 'locked'
                        },
                        {
                            id: 'gs1_modern',
                            title: 'Modern Indian History',
                            description: 'Mid-18th century to present: personalities, issues, Freedom Struggle.',
                            resources: ['Spectrum', 'Bipan Chandra'],
                            status: 'locked'
                        },
                        {
                            id: 'gs1_post_indep',
                            title: 'Post-Independence History',
                            description: 'Consolidation and reorganization within the country.',
                            resources: ['Politics in India since Independence (NCERT)', 'PMF IAS Notes'],
                            status: 'locked'
                        },
                        {
                            id: 'gs1_world',
                            title: 'World History',
                            description: '18th century events: Industrial revolution, world wars, colonization, philosophies.',
                            resources: ['Arjun Dev (NCERT)', 'Normal Lowe (Selective)'],
                            status: 'locked'
                        },
                        {
                            id: 'gs1_society',
                            title: 'Indian Society',
                            description: 'Diversity, Role of Women, Poverty, Urbanization, Globalization, Secularism.',
                            resources: ['NCERT Sociology (Class 11/12)', 'Current Affairs'],
                            status: 'locked'
                        },
                        {
                            id: 'gs1_geo_phy',
                            title: 'Physical Geography',
                            description: 'Salient features of world’s physical geography, Geophysical phenomena (Earthquakes, etc).',
                            resources: ['GC Leong', 'NCERT Fundamentals of Physical Geo'],
                            status: 'locked'
                        },
                        {
                            id: 'gs1_geo_res',
                            title: 'Natural Resources',
                            description: 'Distribution of key natural resources across the world.',
                            status: 'locked'
                        }
                    ]
                },

                // --- GS II ---
                {
                    id: 'gs2',
                    title: 'GS II: Governance, Constitution, Polity, Social Justice & IR',
                    status: 'locked',
                    children: [
                        {
                            id: 'gs2_const',
                            title: 'Indian Constitution',
                            description: 'Historical underpinnings, evolution, features, amendments, basic structure.',
                            resources: ['M. Laxmikanth', 'DD Basu'],
                            status: 'locked'
                        },
                        {
                            id: 'gs2_func',
                            title: 'Functions of Union & States',
                            description: 'Issues and challenges pertaining to the federal structure, devolution of powers.',
                            status: 'locked'
                        },
                        {
                            id: 'gs2_separation',
                            title: 'Separation of Powers',
                            description: 'Dispute redressal mechanisms and institutions.',
                            status: 'locked'
                        },
                        {
                            id: 'gs2_parliament',
                            title: 'Parliament & Legislatures',
                            description: 'Structure, functioning, conduct of business, powers & privileges.',
                            status: 'locked'
                        },
                        {
                            id: 'gs2_bodies',
                            title: 'Constitutional/Statutory Bodies',
                            description: 'Appointment, powers, functions and responsibilities.',
                            status: 'locked'
                        },
                        {
                            id: 'gs2_governance',
                            title: 'Governance & Accountability',
                            description: 'E-governance, Citizens Charters, Transparency.',
                            resources: ['ARC Reports', 'NITI Aayog Reports'],
                            status: 'locked'
                        },
                        {
                            id: 'gs2_social',
                            title: 'Social Justice',
                            description: 'Issues relating to Health, Education, Human Resources, Poverty, Hunger.',
                            status: 'locked'
                        },
                        {
                            id: 'gs2_ir',
                            title: 'International Relations',
                            description: 'India and its neighborhood, Bilateral groupings, Global institutions.',
                            resources: ['MEA Website', 'The Hindu/Indian Express', 'Pavneet Singh IR'],
                            status: 'locked'
                        }
                    ]
                },

                // --- GS III ---
                {
                    id: 'gs3',
                    title: 'GS III: Tech, Eco Dev, Bio-diversity, Security & Disaster Mgmt',
                    status: 'locked',
                    children: [
                        {
                            id: 'gs3_eco',
                            title: 'Indian Economy',
                            description: 'Planning, mobilization of resources, growth, development and employment.',
                            resources: ['Mrunal', 'Sriram IAS Economy'],
                            status: 'locked'
                        },
                        {
                            id: 'gs3_budget',
                            title: 'Government Budgeting',
                            description: 'Key concepts of budgeting in India.',
                            status: 'locked'
                        },
                        {
                            id: 'gs3_agri',
                            title: 'Agriculture',
                            description: 'Major crops, irrigation, e-technology, MSP, PDS, Food processing.',
                            status: 'locked'
                        },
                        {
                            id: 'gs3_sci',
                            title: 'Science & Technology',
                            description: 'Indigenization of technology, IT, Space, Computers, Robotics, Nano-tech, Bio-tech.',
                            resources: ['Science Reporter', 'The Hindu S&T'],
                            status: 'locked'
                        },
                        {
                            id: 'gs3_env',
                            title: 'Environment & Conservation',
                            description: 'Environmental pollution and degradation, EIA.',
                            status: 'locked'
                        },
                        {
                            id: 'gs3_disaster',
                            title: 'Disaster Management',
                            description: 'Disaster and disaster management framework.',
                            resources: ['NDMA Guidelines'],
                            status: 'locked'
                        },
                        {
                            id: 'gs3_security',
                            title: 'Internal Security',
                            description: 'Extremism, Cyber security, Money laundering, Border management, Organized crime.',
                            resources: ['Ashok Kumar IPS book'],
                            status: 'locked'
                        }
                    ]
                },

                // --- GS IV ---
                {
                    id: 'gs4',
                    title: 'GS IV: Ethics, Integrity and Aptitude',
                    status: 'locked',
                    children: [
                        {
                            id: 'gs4_ethics',
                            title: 'Ethics and Human Interface',
                            description: 'Essence, determinants, consequences of ethics in human actions.',
                            resources: ['Lexicon for Ethics', 'Subba Rao'],
                            status: 'locked'
                        },
                        {
                            id: 'gs4_attitude',
                            title: 'Attitude',
                            description: 'Content, structure, function; influence on thought and behavior.',
                            status: 'locked'
                        },
                        {
                            id: 'gs4_aptitude',
                            title: 'Aptitude for Civil Services',
                            description: 'Integrity, impartiality, objectivity, empathy, tolerance.',
                            status: 'locked'
                        },
                        {
                            id: 'gs4_ei',
                            title: 'Emotional Intelligence',
                            description: 'Concepts, utilities and application in admin.',
                            status: 'locked'
                        },
                        {
                            id: 'gs4_public',
                            title: 'Public/Civil Service Values',
                            description: 'Status and problems; ethical concerns and dilemmas.',
                            status: 'locked'
                        },
                        {
                            id: 'gs4_probity',
                            title: 'Probity in Governance',
                            description: 'Concept of public service, philosophical basis of governance.',
                            status: 'locked'
                        },
                        {
                            id: 'gs4_case',
                            title: 'Case Studies',
                            description: 'Application of above concepts to specific situations.',
                            status: 'locked'
                        }
                    ]
                }
            ]
        }
    ]
};