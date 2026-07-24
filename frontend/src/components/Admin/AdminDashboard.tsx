import { API_BASE_URL } from '../../config';

import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';
import { useToast } from '../Toast';
import ArticleEditor from './ArticleEditor';
import QuestionEditor from './QuestionEditor';

interface Question {
    id: number;
    question_text: string;
    subject: string;
    topic: string;
    difficulty: string;
    correct_option: string;
}

interface Article {
    id: number;
    title: string;
    content: string;
    tags: string;
    source: string;
    category: string;
    created_at: string;
}

interface Stats {
    total_questions: number;
    total_users: number;
    total_articles: number;
    weekly_tests: number;
}

const AdminDashboard: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'overview' | 'questions' | 'articles'>('overview');
    const [stats, setStats] = useState<Stats | null>(null);
    const [questions, setQuestions] = useState<Question[]>([]);
    const [articles, setArticles] = useState<Article[]>([]);
    const [showArticleEditor, setShowArticleEditor] = useState(false);
    const [showQuestionEditor, setShowQuestionEditor] = useState(false);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const { addToast } = useToast();

    useEffect(() => {
        fetchStats();
    }, []);

    useEffect(() => {
        if (activeTab === 'questions') {
            fetchQuestions(page);
        } else if (activeTab === 'articles') {
            fetchArticles(page);
        }
    }, [activeTab, page]);

    const fetchStats = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/stats`);
            if (res.ok) {
                const data = await res.json();
                setStats(data);
            }
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    };

    const fetchQuestions = async (pageNum: number) => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/questions?page=${pageNum}`);
            if (res.ok) {
                const data = await res.json();
                setQuestions(data.questions);
                setTotalPages(data.pages);
            }
        } catch (error) {
            addToast('Failed to load questions', 'error');
        }
    };

    const fetchArticles = async (pageNum: number) => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/articles?page=${pageNum}`);
            if (res.ok) {
                const data = await res.json();
                setArticles(data.articles);
                setTotalPages(data.pages);
            }
        } catch (error) {
            addToast('Failed to load articles', 'error');
        }
    };

    const handleDeleteQuestion = async (id: number) => {
        if (!confirm('Are you sure you want to delete this question?')) return;

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/questions/${id}`, {
                method: 'DELETE'
            });

            if (res.ok) {
                addToast('Question deleted', 'success');
                fetchQuestions(page); // Refresh
            } else {
                addToast('Failed to delete question', 'error');
            }
        } catch (error) {
            addToast('Error deleting question', 'error');
        }
    };

    const handleDeleteArticle = async (id: number) => {
        if (!confirm('Are you sure you want to delete this article?')) return;

        try {
            const res = await fetch(`${API_BASE_URL}/api/admin/articles/${id}`, {
                method: 'DELETE'
            });

            if (res.ok) {
                addToast('Article deleted', 'success');
                fetchArticles(page);
            } else {
                addToast('Failed to delete article', 'error');
            }
        } catch (error) {
            addToast('Error deleting article', 'error');
        }
    };

    const handleArticleSaved = () => {
        fetchArticles(page);
        fetchStats(); // Update stats too
    };

    return (
        <div className="admin-container animate-fade-in">
            <div className="admin-sidebar">
                <div className="admin-logo">🛡️ Admin Panel</div>
                <nav className="admin-nav">
                    <button
                        className={`nav-btn ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                    >
                        📊 Overview
                    </button>
                    <button
                        className={`nav-btn ${activeTab === 'questions' ? 'active' : ''}`}
                        onClick={() => setActiveTab('questions')}
                    >
                        ❓ Question Bank
                    </button>
                    <button
                        className={`nav-btn ${activeTab === 'articles' ? 'active' : ''}`}
                        onClick={() => setActiveTab('articles')}
                    >
                        📝 Articles
                    </button>
                </nav>
            </div>

            <div className="admin-content">
                {activeTab === 'overview' && (
                    <div className="overview-panel animate-slide-in-up">
                        <h1>Dashboard Overview</h1>
                        <div className="stats-grid">
                            <div className="stat-card">
                                <h3>Total Questions</h3>
                                <div className="stat-value">{stats?.total_questions || 0}</div>
                            </div>
                            <div className="stat-card">
                                <h3>Active Users</h3>
                                <div className="stat-value">{stats?.total_users || 0}</div>
                            </div>
                            <div className="stat-card">
                                <h3>Knowledge Articles</h3>
                                <div className="stat-value">{stats?.total_articles || 0}</div>
                            </div>
                            <div className="stat-card">
                                <h3>Tests This Week</h3>
                                <div className="stat-value">{stats?.weekly_tests || 0}</div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'questions' && (
                    <div className="questions-panel animate-slide-in-up">
                        <div className="panel-header">
                            <h1>Question Bank</h1>
                            <button className="add-btn" onClick={() => setShowQuestionEditor(true)}>+ Add Question</button>
                        </div>

                        <div className="questions-table-container">
                            <table className="admin-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Question</th>
                                        <th>Subject</th>
                                        <th>Topic</th>
                                        <th>Difficulty</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {questions.map(q => (
                                        <tr key={q.id}>
                                            <td>#{q.id}</td>
                                            <td className="col-text">{q.question_text.substring(0, 60)}...</td>
                                            <td>{q.subject}</td>
                                            <td>{q.topic}</td>
                                            <td>
                                                <span className={`badge badge-${q.difficulty}`}>
                                                    {q.difficulty}
                                                </span>
                                            </td>
                                            <td>
                                                <button className="action-btn edit" aria-label={`Edit question ${q.id}`}><span aria-hidden="true">✏️</span></button>
                                                <button
                                                    className="action-btn delete"
                                                    aria-label={`Delete question ${q.id}`}
                                                    onClick={() => handleDeleteQuestion(q.id)}
                                                >
                                                    <span aria-hidden="true">🗑️</span>
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="pagination">
                            <button
                                disabled={page === 1}
                                onClick={() => setPage(p => p - 1)}
                            >
                                Previous
                            </button>
                            <span>Page {page} of {totalPages}</span>
                            <button
                                disabled={page === totalPages}
                                onClick={() => setPage(p => p + 1)}
                            >
                                Next
                            </button>
                        </div>
                    </div>
                )}

                {activeTab === 'articles' && (
                    <div className="articles-panel animate-slide-in-up">
                        <div className="panel-header">
                            <h1>Article Manager</h1>
                            <button
                                className="add-btn"
                                onClick={() => setShowArticleEditor(true)}
                            >
                                + Add Article
                            </button>
                        </div>

                        <div className="questions-table-container">
                            <table className="admin-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Title</th>
                                        <th>Tags</th>
                                        <th>Source</th>
                                        <th>Category</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {articles.map(a => (
                                        <tr key={a.id}>
                                            <td>#{a.id}</td>
                                            <td className="col-text" title={a.title}>{a.title}</td>
                                            <td>{a.tags}</td>
                                            <td>{a.source}</td>
                                            <td>
                                                <span className="badge badge-medium">
                                                    {a.category || 'General'}
                                                </span>
                                            </td>
                                            <td>
                                                <button className="action-btn edit" aria-label={`Edit article ${a.title}`}><span aria-hidden="true">✏️</span></button>
                                                <button
                                                    className="action-btn delete"
                                                    aria-label={`Delete article ${a.title}`}
                                                    onClick={() => handleDeleteArticle(a.id)}
                                                >
                                                    <span aria-hidden="true">🗑️</span>
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="pagination">
                            <button
                                disabled={page === 1}
                                onClick={() => setPage(p => p - 1)}
                            >
                                Previous
                            </button>
                            <span>Page {page} of {totalPages}</span>
                            <button
                                disabled={page === totalPages}
                                onClick={() => setPage(p => p + 1)}
                            >
                                Next
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {showArticleEditor && (
                <ArticleEditor
                    onClose={() => setShowArticleEditor(false)}
                    onSave={handleArticleSaved}
                />
            )}
            {showQuestionEditor && (
                <QuestionEditor
                    onClose={() => setShowQuestionEditor(false)}
                    onSave={() => {
                        fetchQuestions(page);
                        fetchStats();
                        setShowQuestionEditor(false);
                    }}
                />
            )}
        </div>
    );
};

export default AdminDashboard;
