import { generateCSVTaskId } from './taskUtils';

export interface Slot {
    id: string;
    time: string;
    subject: string;
    activity: string;
    status: 'pending' | 'completed' | 'skipped' | 'rescheduled';
    resource_link?: string;
    originalDate?: string;
}

export interface DayPlan {
    date: string;
    day: string;
    slots: Slot[];
}

export const parseCSV = (csvText: string): DayPlan[] => {
    const lines = csvText.split('\n').filter(line => line.trim() !== '');
    // Skip headers
    const dataRows = lines.slice(1);

    const dayMap: { [key: string]: DayPlan } = {};
    const completedTasks = new Set(JSON.parse(localStorage.getItem('completedTasks') || '[]'));

    dataRows.forEach((row) => {
        // Simple split for now as data seems simple and doesn't contain quoted commas in our generation script
        const columns = row.split(',').map(c => c.trim());

        // Date,Day,Slot_Type,Time,Subject,Topic,Activity_Type,Resources
        const date = columns[0];
        const dayName = columns[1];
        const time = columns[3];
        const subject = columns[4];
        const topic = columns[5];
        const activityType = columns[6];
        const resources = columns[7];

        if (!date || columns.length < 5) return;

        if (!dayMap[date]) {
            dayMap[date] = {
                date: date,
                day: dayName,
                slots: []
            };
        }

        // Use content-based ID to prevent collisions on CSV regeneration
        const taskId = generateCSVTaskId(date, time, subject, topic);
        const isCompleted = completedTasks.has(taskId);

        dayMap[date].slots.push({
            id: taskId, // Now a string
            time: time,
            subject: subject,
            activity: `${topic} (${activityType})`,
            status: isCompleted ? 'completed' : 'pending',
            resource_link: resources !== 'N/A' ? resources : undefined,
            originalDate: date
        });
    });

    return Object.values(dayMap).sort((a, b) => a.date.localeCompare(b.date));
};
