export interface Topic {
    id: number;
    paper: string;
    subject: string;
    topic: string;
    subtopic?: string | null; // Frontend property (legacy or computed)
    sub_topic?: string | null; // Database property
    status: string;
    notes: string | null;
    last_updated: string;
    revision_count?: number;
    next_revision_date?: string;
    last_revised_at?: string;
}

export const STATUS_OPTIONS = [
    'Not Started',
    'Reading',
    'Notes Done',
    'Revision 1',
    'Revision 2',
    'Completed'
];
