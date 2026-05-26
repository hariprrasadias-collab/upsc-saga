import { API_BASE_URL } from '../../config';

import React, { useState } from 'react';
import './ArticleEditor.css'; // Reuse styles
import { useToast } from '../Toast';

interface QuestionEditorProps {
    onClose: () => void;
    onSave: () => void;
}

const QuestionEditor: React.FC<QuestionEditorProps> = ({ onClose, onSave }) => {
    const [questionText, setQuestionText] = useState('');
    const [subject, setSubject] = useState('History');
    const [topic, setTopic] = useState('');
    const [difficulty, setDifficulty] = useState('Medium');
    const [optionA, setOptionA] = useState('');
    const [optionB, setOptionB] = useState('');
    const [optionC, setOptionC] = useState('');
    const [optionD, setOptionD] = useState('');
    const [correctOption, setCorrectOption] = useState('A');
    const [saving, setSaving] = useState(false);
    const { addToast } = useToast();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/questions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question_text: questionText,
                    subject,
                    topic,
                    difficulty,
                    options: JSON.stringify([optionA, optionB, optionC, optionD]),
                    correct_option: correctOption
                })
            });

            if (res.ok) {
                addToast('Question added successfully', 'success');
                onSave();
                onClose();
            } else {
                addToast('Failed to add question', 'error');
            }
        } catch (error) {
            addToast('Error adding question', 'error');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content animate-scale-in" style={{ maxWidth: '800px' }}>
                <div className="modal-header">
                    <h2>Add New Question</h2>
                    <button className="close-btn" onClick={onClose} aria-label="Close dialog">
                        <span aria-hidden="true">×</span>
                    </button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Question Text</label>
                        <textarea
                            value={questionText}
                            onChange={e => setQuestionText(e.target.value)}
                            required
                            rows={3}
                            placeholder="Enter the question here..."
                        />
                    </div>

                    <div className="form-row" style={{ display: 'flex', gap: '1rem' }}>
                        <div className="form-group" style={{ flex: 1 }}>
                            <label>Subject</label>
                            <select value={subject} onChange={e => setSubject(e.target.value)}>
                                <option value="History">History</option>
                                <option value="Geography">Geography</option>
                                <option value="Polity">Polity</option>
                                <option value="Economics">Economics</option>
                                <option value="Science">Science</option>
                                <option value="Environment">Environment</option>
                            </select>
                        </div>
                        <div className="form-group" style={{ flex: 1 }}>
                            <label>Topic</label>
                            <input
                                type="text"
                                value={topic}
                                onChange={e => setTopic(e.target.value)}
                                placeholder="e.g. Indus Valley"
                                required
                            />
                        </div>
                        <div className="form-group" style={{ flex: 1 }}>
                            <label>Difficulty</label>
                            <select value={difficulty} onChange={e => setDifficulty(e.target.value)}>
                                <option value="Easy">Easy</option>
                                <option value="Medium">Medium</option>
                                <option value="Hard">Hard</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Options</label>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            <input
                                type="text"
                                value={optionA}
                                onChange={e => setOptionA(e.target.value)}
                                placeholder="Option A"
                                required
                            />
                            <input
                                type="text"
                                value={optionB}
                                onChange={e => setOptionB(e.target.value)}
                                placeholder="Option B"
                                required
                            />
                            <input
                                type="text"
                                value={optionC}
                                onChange={e => setOptionC(e.target.value)}
                                placeholder="Option C"
                                required
                            />
                            <input
                                type="text"
                                value={optionD}
                                onChange={e => setOptionD(e.target.value)}
                                placeholder="Option D"
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Correct Option</label>
                        <select value={correctOption} onChange={e => setCorrectOption(e.target.value)}>
                            <option value="A">Option A</option>
                            <option value="B">Option B</option>
                            <option value="C">Option C</option>
                            <option value="D">Option D</option>
                        </select>
                    </div>

                    <div className="modal-actions">
                        <button type="button" className="cancel-btn" onClick={onClose}>Cancel</button>
                        <button type="submit" className="save-btn" disabled={saving}>
                            {saving ? 'Saving...' : 'Add Question'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default QuestionEditor;
