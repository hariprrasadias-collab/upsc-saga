import React, { useState, useEffect } from 'react';

interface Question {
    id: number;
    category: string;
    topic: string;
    question_text: string;
    options: string[];
    correct_option: string;
    explanation: string;
    difficulty: string;
}

const PracticeMode: React.FC = () => {
    const [topics, setTopics] = useState<Record<string, string[]>>({});
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('');
    const [questions, setQuestions] = useState<Question[]>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [showExplanation, setShowExplanation] = useState(false);
    const [selectedOption, setSelectedOption] = useState<string | null>(null);

    useEffect(() => {
        fetchTopics();
    }, []);

    const fetchTopics = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/csat/topics');
            const data = await response.json();
            setTopics(data);
        } catch (error) {
            console.error('Error fetching topics:', error);
        }
    };

    const fetchQuestions = async () => {
        if (!selectedCategory || !selectedTopic) return;
        try {
            const response = await fetch(`http://localhost:5000/api/csat/questions?category=${selectedCategory}&topic=${selectedTopic}`);
            const data = await response.json();
            setQuestions(data);
            setCurrentQuestionIndex(0);
            setShowExplanation(false);
            setSelectedOption(null);
        } catch (error) {
            console.error('Error fetching questions:', error);
        }
    };

    const handleOptionSelect = (option: string) => {
        if (selectedOption) return; // Prevent changing answer
        setSelectedOption(option);
        setShowExplanation(true);
    };

    const nextQuestion = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
            setShowExplanation(false);
            setSelectedOption(null);
        }
    };

    const currentQuestion = questions[currentQuestionIndex];

    return (
        <div className="practice-mode">
            <div className="filters">
                <select
                    value={selectedCategory}
                    onChange={(e) => { setSelectedCategory(e.target.value); setSelectedTopic(''); }}
                >
                    <option value="">Select Category</option>
                    {Object.keys(topics).map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                    ))}
                </select>

                <select
                    value={selectedTopic}
                    onChange={(e) => setSelectedTopic(e.target.value)}
                    disabled={!selectedCategory}
                >
                    <option value="">Select Topic</option>
                    {selectedCategory && topics[selectedCategory]?.map(topic => (
                        <option key={topic} value={topic}>{topic}</option>
                    ))}
                </select>

                <button
                    className="start-btn"
                    onClick={fetchQuestions}
                    disabled={!selectedCategory || !selectedTopic}
                >
                    Start Practice
                </button>
            </div>

            {questions.length > 0 && currentQuestion && (
                <div className="question-card">
                    <div className="question-header">
                        <span className="q-number">Question {currentQuestionIndex + 1}/{questions.length}</span>
                        <span className={`difficulty ${currentQuestion.difficulty.toLowerCase()}`}>
                            {currentQuestion.difficulty}
                        </span>
                    </div>

                    <p className="question-text">{currentQuestion.question_text}</p>

                    <div className="options-grid">
                        {currentQuestion.options.map((option, idx) => (
                            <button
                                key={idx}
                                className={`option-btn 
                  ${selectedOption === option ? (option === currentQuestion.correct_option ? 'correct' : 'wrong') : ''}
                  ${selectedOption && option === currentQuestion.correct_option ? 'correct' : ''}
                `}
                                onClick={() => handleOptionSelect(option)}
                                disabled={!!selectedOption}
                            >
                                {option}
                            </button>
                        ))}
                    </div>

                    {showExplanation && (
                        <div className="explanation-box">
                            <h3>Explanation</h3>
                            <p>{currentQuestion.explanation}</p>
                            {currentQuestionIndex < questions.length - 1 ? (
                                <button className="next-btn" onClick={nextQuestion}>Next Question →</button>
                            ) : (
                                <p className="completion-msg">Topic Completed! 🎉</p>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default PracticeMode;
