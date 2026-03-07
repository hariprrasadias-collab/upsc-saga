export interface Topic {
    id: number;
    paper: string;
    subject: string;
    topic: string;
    subtopic: string | null;
    status: string;
    notes: string | null;
    has_notes?: boolean; // New optimization flag
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
