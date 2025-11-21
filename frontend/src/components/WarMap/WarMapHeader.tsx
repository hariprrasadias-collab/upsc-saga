// /frontend/src/components/WarMap/WarMapHeader.tsx
import React from 'react';
import './WarMapHeader.css'; // Make sure this CSS file exists
import AddTaskForm from './AddTaskForm'; // Now WarMapHeader imports AddTaskForm

interface WarMapHeaderProps {
  showAddForm: boolean;
  onToggleAddForm: () => void; // Toggles the visibility of the AddTaskForm
  selectedDateStr: string; // The currently selected date from WarMapContainer
  onTaskActionComplete: () => void; // Called after task is created or form is cancelled
}

const WarMapHeader: React.FC<WarMapHeaderProps> = ({
  showAddForm,
  onToggleAddForm,
  selectedDateStr,
  onTaskActionComplete,
}) => {
  return (
    <header className="war-map-header">
      {!showAddForm ? (
        <>
          <h1>The War Map</h1>
          <p>Plan your campaigns and rituals here. Conquer the UPSC!</p>
          <button className="create-task-btn" onClick={onToggleAddForm}>
            Convene War Council (New Task)
          </button>
        </>
      ) : (
        <AddTaskForm
          selectedDateStr={selectedDateStr}
          onTaskCreated={onTaskActionComplete} // Calls parent to refresh & close form
          onCancel={onTaskActionComplete}     // Calls parent to close form
        />
      )}
    </header>
  );
};

export default WarMapHeader;