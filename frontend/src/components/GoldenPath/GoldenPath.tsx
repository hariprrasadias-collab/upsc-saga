import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import './GoldenPath.css';
import { brainService } from '../../services/BrainService';

interface Node {
    id: string;
    label: string;
    yield: number;
    effort: number;
    roi: number;
    group: string;
    musk_category?: string; // DELETE, ACCELERATE, FOCUS
    is_trending?: boolean;
    has_mnemonic?: boolean;
    days_since_revision?: number;
    x?: number;
    y?: number;
}

interface Link {
    source: string | Node;
    target: string | Node;
}

interface GraphData {
    nodes: Node[];
    edges: Link[];
}

const GoldenPath: React.FC = () => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [graphData, setGraphData] = useState<GraphData | null>(null);
    const [timeBudget, setTimeBudget] = useState<number>(100);
    const [optimalPath, setOptimalPath] = useState<Node[]>([]);
    const [stats, setStats] = useState({ totalYield: 0, totalEffort: 0 });
    const [loading, setLoading] = useState<boolean>(false);
    const [filters, setFilters] = useState({
        FOCUS: true,
        ACCELERATE: true,
        DELETE: true
    });
    const [tooltip, setTooltip] = useState<{ x: number, y: number, data: Node } | null>(null);
    const [subjects, setSubjects] = useState<string[]>([]);
    const [topics, setTopics] = useState<string[]>([]);
    const [selectedSubject, setSelectedSubject] = useState<string>('All');
    const [selectedTopic, setSelectedTopic] = useState<string>('All');
    const [energyLevel, setEnergyLevel] = useState<number>(50);
    const [optimizationMode, setOptimizationMode] = useState<string>('STANDARD');

    // Fetch Graph Data
    useEffect(() => {
        setLoading(true);
        fetch('http://localhost:5000/api/golden-path/graph')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Transform data for D3 (it mutates objects)
                    const nodes = data.data.nodes.map((n: any) => ({ ...n.data, id: n.id }));
                    const edges = data.data.edges.map((e: any) => ({ source: e.source, target: e.target }));
                    setGraphData({ nodes, edges });

                    // Extract unique subjects and topics
                    const uniqueSubjects = Array.from(new Set(nodes.map((n: any) => n.group))).sort() as string[];
                    const uniqueTopics = Array.from(new Set(nodes.map((n: any) => n.label))).sort() as string[];
                    setSubjects(uniqueSubjects);
                    setTopics(uniqueTopics);
                }
            })
            .catch(err => console.error("Failed to fetch graph:", err))
            .finally(() => setLoading(false));
    }, []);

    // Render Graph
    useEffect(() => {
        if (!graphData || !svgRef.current) return;

        const width = svgRef.current.clientWidth;
        const height = svgRef.current.clientHeight;

        // Clear previous render
        d3.select(svgRef.current).selectAll("*").remove();

        const svg = d3.select(svgRef.current)
            .attr("viewBox", [0, 0, width, height])
            .call(d3.zoom().scaleExtent([0.1, 4]).on("zoom", (event) => {
                g.attr("transform", event.transform);
            }) as any);

        const g = svg.append("g");

        // Filter Nodes
        const activeNodes = graphData.nodes.filter(n => {
            const categoryMatch = filters[n.musk_category as keyof typeof filters] !== false;
            const subjectMatch = selectedSubject === 'All' || n.group === selectedSubject;
            const topicMatch = selectedTopic === 'All' || n.label === selectedTopic;
            return categoryMatch && subjectMatch && topicMatch;
        });

        const activeNodeIds = new Set(activeNodes.map(n => n.id));
        const activeEdges = graphData.edges.filter(e => {
            const sourceId = typeof e.source === 'object' ? (e.source as Node).id : e.source;
            const targetId = typeof e.target === 'object' ? (e.target as Node).id : e.target;
            return activeNodeIds.has(sourceId as string) && activeNodeIds.has(targetId as string);
        });

        // Simulation - OPTIMIZED FOR VISIBILITY
        const simulation = d3.forceSimulation(activeNodes as any)
            .force("link", d3.forceLink(activeEdges).id((d: any) => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius((d: any) => (10 + (d.yield || 0)) * 1.5).iterations(2));

        // Links
        const link = g.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(activeEdges)
            .join("line")
            .attr("class", "link")
            .attr("stroke", "#555")
            .attr("stroke-opacity", 0.3);

        // Nodes
        const node = g.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(activeNodes)
            .join("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended) as any)
            .on("mouseover", (event, d: any) => {
                setTooltip({ x: event.pageX, y: event.pageY, data: d });
            })
            .on("mouseout", () => {
                setTooltip(null);
            });

        // Node Circles
        const colorScale = d3.scaleLinear<string>()
            .domain([5, 30]) // Effort range approx
            .range(["#2ecc71", "#e74c3c"]); // Green to Red

        node.append("circle")
            .attr("r", (d: any) => 10 + (d.yield / 1.5)) // Slightly larger base size
            .attr("fill", (d: any) => {
                const baseColor = colorScale(d.effort);
                // If Revision mode, desaturate/darken fresh items, highlight old ones?
                // Or just use border for status.
                return baseColor;
            })
            .attr("fill-opacity", 0.8)
            .attr("stroke", (d: any) => {
                if (d.is_trending) return '#ff5722'; // Orange/Red for Trending
                if (d.musk_category === 'DELETE') return '#e74c3c';
                if (d.musk_category === 'ACCELERATE') return '#f1c40f';
                if (d.musk_category === 'FOCUS') return '#2ecc71';
                return '#fff';
            })
            .attr("stroke-width", (d: any) => d.is_trending ? 4 : (d.musk_category ? 3 : 1))
            .attr("stroke-dasharray", (d: any) => d.is_trending ? "3,3" : "none");

        // Icons / Badges
        const icons = node.append("g").attr("transform", "translate(-8, -8)");

        // Trending Icon
        icons.filter((d:any) => d.is_trending).append("text")
            .text("🔥")
            .attr("x", -10)
            .attr("y", -5)
            .style("font-size", "12px");

        // Mnemonic Icon
        icons.filter((d:any) => d.has_mnemonic).append("text")
            .text("🧠")
            .attr("x", 10)
            .attr("y", -5)
            .style("font-size", "12px");

        // Labels
        node.append("text")
            .attr("dx", 15)
            .attr("dy", ".35em")
            .text((d: any) => d.label)
            .style("font-size", "10px")
            .style("fill", "#ddd")
            .style("pointer-events", "none")
            .style("text-shadow", "1px 1px 2px #000");

        simulation.on("tick", () => {
            link
                .attr("x1", (d: any) => d.source.x)
                .attr("y1", (d: any) => d.source.y)
                .attr("x2", (d: any) => d.target.x)
                .attr("y2", (d: any) => d.target.y);

            node
                .attr("transform", (d: any) => `translate(${d.x},${d.y})`);
        });

        function dragstarted(event: any, d: any) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event: any, d: any) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event: any, d: any) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        // Highlight Path Effect
        if (optimalPath.length) {
            const pathIds = new Set(optimalPath.map(n => n.id));

            // Highlight Nodes
            svg.selectAll(".node circle")
                .transition().duration(500)
                .style("stroke", (d: any) => pathIds.has(d.id) ? "#ffd700" : null)
                .style("stroke-width", (d: any) => pathIds.has(d.id) ? 5 : null)
                .style("filter", (d: any) => pathIds.has(d.id) ? "drop-shadow(0 0 10px #ffd700)" : null)
                .attr("r", (d: any) => pathIds.has(d.id) ? (10 + (d.yield / 1.5)) * 1.2 : (10 + (d.yield / 1.5)));

            // Highlight Edges
            svg.selectAll(".link")
                .transition().duration(500)
                .style("stroke", (d: any) => pathIds.has(d.source.id) && pathIds.has(d.target.id) ? "#ffd700" : "#555")
                .style("stroke-width", (d: any) => pathIds.has(d.source.id) && pathIds.has(d.target.id) ? 3 : 1)
                .style("stroke-opacity", (d: any) => pathIds.has(d.source.id) && pathIds.has(d.target.id) ? 1 : 0.1);
        }

        return () => {
            simulation.stop();
        };
    }, [graphData, filters, optimalPath, selectedSubject, selectedTopic]);

    const handleOptimize = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:5000/api/golden-path/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    time_budget: timeBudget,
                    energy_level: energyLevel,
                    subject: selectedSubject,
                    topic: selectedTopic,
                    mode: optimizationMode
                })
            });
            const data = await res.json();
            if (data.success) {
                setOptimalPath(data.data.path);
                setStats({
                    totalYield: data.data.total_yield,
                    totalEffort: data.data.total_effort
                });
            }
        } catch (err) {
            console.error("Optimization failed:", err);
        } finally {
            setLoading(false);
        }
    };

    const toggleFilter = (category: keyof typeof filters) => {
        setFilters(prev => ({ ...prev, [category]: !prev[category] }));
    };

    // Filter topics based on selected subject
    const availableTopics = selectedSubject === 'All'
        ? topics
        : topics.filter(t => graphData?.nodes.some(n => n.label === t && n.group === selectedSubject));

    return (
        <div className="golden-path-container">
            <div className="gp-sidebar">
                <h2>The Golden Path</h2>

                <div className="gp-controls">
                    <div className="gp-input-group">
                        <label>Subject</label>
                        <select
                            className="gp-input"
                            value={selectedSubject}
                            onChange={(e) => {
                                setSelectedSubject(e.target.value);
                                setSelectedTopic('All');
                            }}
                        >
                            <option value="All">All Subjects</option>
                            {subjects.map(s => <option key={s} value={s}>{s}</option>)}
                        </select>
                    </div>

                    <div className="gp-input-group">
                        <label>Topic</label>
                        <select
                            className="gp-input"
                            value={selectedTopic}
                            onChange={(e) => setSelectedTopic(e.target.value)}
                        >
                            <option value="All">All Topics</option>
                            {availableTopics.map(t => <option key={t} value={t}>{t}</option>)}
                        </select>
                    </div>

                    <div className="gp-input-group">
                        <label>Time Budget (Hours)</label>
                        <input
                            type="number"
                            className="gp-input"
                            value={isNaN(timeBudget) ? '' : timeBudget}
                            onChange={(e) => setTimeBudget(parseFloat(e.target.value))}
                            placeholder="e.g. 100"
                        />
                    </div>

                    <div className="gp-input-group">
                        <label>Energy Level ({energyLevel}%)</label>
                        <input
                            type="range"
                            min="0"
                            max="100"
                            value={energyLevel}
                            onChange={(e) => setEnergyLevel(parseInt(e.target.value))}
                            style={{ width: '100%', cursor: 'pointer' }}
                            title="Low Energy: Prioritize quick wins. High Energy: Tackle hard topics."
                        />
                        <div style={{ fontSize: '0.75rem', color: '#888', marginTop: '2px', textAlign: 'center' }}>
                            {energyLevel < 30 ? "Drain Mode: Quick Wins" : energyLevel > 80 ? "Flow State: Deep Work" : "Normal"}
                        </div>
                    </div>

                    <div className="gp-input-group">
                        <label>Optimization Strategy</label>
                        <div style={{ display: 'flex', gap: '5px' }}>
                            <button
                                className={`gp-btn ${optimizationMode === 'STANDARD' ? 'active' : ''}`}
                                onClick={() => setOptimizationMode('STANDARD')}
                                style={{ flex: 1, fontSize: '0.8rem', opacity: optimizationMode === 'STANDARD' ? 1 : 0.5 }}
                                title="Maximize Marks Gained per Hour"
                            >
                                Standard
                            </button>
                            <button
                                className={`gp-btn ${optimizationMode === 'REVISION' ? 'active' : ''}`}
                                onClick={() => setOptimizationMode('REVISION')}
                                style={{ flex: 1, fontSize: '0.8rem', opacity: optimizationMode === 'REVISION' ? 1 : 0.5, borderColor: '#3498db', color: '#3498db' }}
                                title="Prioritize Forgotten Topics (Retention)"
                            >
                                Revision
                            </button>
                        </div>
                    </div>

                    <div className="gp-filters" style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                        <button
                            className="gp-btn"
                            title="Focus: High Yield, Low Effort topics. The core of your preparation."
                            style={{ flex: 1, fontSize: '0.8rem', opacity: filters.FOCUS ? 1 : 0.4, borderColor: '#2ecc71', color: '#2ecc71', boxShadow: filters.FOCUS ? '0 0 10px rgba(46, 204, 113, 0.3)' : 'none' }}
                            onClick={() => toggleFilter('FOCUS')}
                        >
                            FOCUS
                        </button>
                        <button
                            className="gp-btn"
                            title="Accelerate: Quick wins to boost your score rapidly."
                            style={{ flex: 1, fontSize: '0.8rem', opacity: filters.ACCELERATE ? 1 : 0.4, borderColor: '#f1c40f', color: '#f1c40f', boxShadow: filters.ACCELERATE ? '0 0 10px rgba(241, 196, 15, 0.3)' : 'none' }}
                            onClick={() => toggleFilter('ACCELERATE')}
                        >
                            ACCEL
                        </button>
                        <button
                            className="gp-btn"
                            title="Delete: Low ROI topics. Avoid these to save time."
                            style={{ flex: 1, fontSize: '0.8rem', opacity: filters.DELETE ? 1 : 0.4, borderColor: '#e74c3c', color: '#e74c3c', boxShadow: filters.DELETE ? '0 0 10px rgba(231, 76, 60, 0.3)' : 'none' }}
                            onClick={() => toggleFilter('DELETE')}
                        >
                            DELETE
                        </button>
                    </div>

                    <button className="gp-btn" onClick={handleOptimize} disabled={loading}>
                        {loading ? 'Consulting Oracle...' : 'Find Optimal Path'}
                    </button>

                    {optimalPath.length > 0 && (
                        <>
                            <button className="gp-btn gp-btn-commit" onClick={async () => {
                                if (!confirm("Are you sure you want to commit this strategy? This will become your active directive.")) return;
                                const success = await brainService.ingestDirective(optimalPath);
                                if (success) {
                                    alert("Strategy Committed! The Brain is now aligned with this path.");
                                } else {
                                    alert("Failed to commit strategy. The Brain is unreachable.");
                                }
                            }} style={{ background: 'rgba(46, 204, 113, 0.2)', borderColor: '#2ecc71', boxShadow: '0 0 15px rgba(46, 204, 113, 0.4)' }}>
                                Commit Strategy
                            </button>
                            <button className="gp-btn gp-btn-reset" onClick={() => {
                                setOptimalPath([]);
                                setStats({ totalYield: 0, totalEffort: 0 });
                            }} style={{ background: 'rgba(231, 76, 60, 0.2)', borderColor: '#e74c3c' }}>
                                Reset Path
                            </button>
                        </>
                    )}
                </div>

                {optimalPath.length > 0 && (
                    <div className="gp-stats">
                        <h3>Optimal Strategy</h3>
                        <div className="gp-stat-item">
                            <span>Total Yield (Marks):</span>
                            <span className="gp-stat-value" style={{ color: '#f1c40f' }}>{stats.totalYield.toFixed(0)}</span>
                        </div>
                        <div className="gp-stat-item">
                            <span>Total Effort (Hours):</span>
                            <span className="gp-stat-value" style={{ color: '#e74c3c' }}>{stats.totalEffort.toFixed(1)}</span>
                        </div>
                        <div className="gp-stat-item">
                            <span>Topics Covered:</span>
                            <span className="gp-stat-value">{optimalPath.length}</span>
                        </div>
                    </div>
                )}
            </div>

            <div className="gp-graph-area">
                <svg ref={svgRef} style={{ width: '100%', height: '100%' }}></svg>
                {loading && <div className="loading-overlay">Consulting the Oracle...</div>}

                {tooltip && (
                    <div className="d3-tooltip" style={{ left: tooltip.x + 15, top: tooltip.y + 15 }}>
                        <div className="tooltip-title">{tooltip.data.label}</div>
                        <div className="tooltip-row">
                            <span>Category:</span>
                            <span className="tooltip-val" style={{
                                color: tooltip.data.musk_category === 'FOCUS' ? '#2ecc71' :
                                    tooltip.data.musk_category === 'DELETE' ? '#e74c3c' : '#f1c40f'
                            }}>{tooltip.data.musk_category}</span>
                        </div>
                        <div className="tooltip-row">
                            <span>Yield:</span>
                            <span className="tooltip-val">{tooltip.data.yield}</span>
                        </div>
                        <div className="tooltip-row">
                            <span>Effort:</span>
                            <span className="tooltip-val">{tooltip.data.effort}h</span>
                        </div>
                        <div className="tooltip-row">
                            <span>ROI:</span>
                            <span className="tooltip-val">{tooltip.data.roi?.toFixed(2)}</span>
                        </div>
                        {tooltip.data.is_trending && (
                             <div className="tooltip-row" style={{ color: '#ff5722' }}>
                                <span>🔥 Trending Topic</span>
                             </div>
                        )}
                        {tooltip.data.has_mnemonic && (
                             <div className="tooltip-row" style={{ color: '#9b59b6' }}>
                                <span>🧠 Mnemonic Available</span>
                             </div>
                        )}
                        {tooltip.data.days_since_revision !== undefined && tooltip.data.days_since_revision < 900 && (
                            <div className="tooltip-row">
                                <span>Last Rev:</span>
                                <span className="tooltip-val">{tooltip.data.days_since_revision}d ago</span>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default GoldenPath;
