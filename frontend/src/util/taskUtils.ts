export const generateCSVTaskId = (date: string, time: string, subject: string, topic: string): string => {
    // Create a unique ID based on the task's content rather than its row index.
    // This prevents status collisions when the CSV is regenerated or reordered.
    // Sanitize strings to ensure consistency.
    const cleanDate = (date || '').trim();
    const cleanTime = (time || '').trim();
    const cleanSubject = (subject || '').trim().toLowerCase();
    const cleanTopic = (topic || '').trim().toLowerCase().substring(0, 20); // Limit length to avoid huge keys

    return `csv_${cleanDate}_${cleanTime}_${cleanSubject}_${cleanTopic}`.replace(/\s+/g, '_');
};
