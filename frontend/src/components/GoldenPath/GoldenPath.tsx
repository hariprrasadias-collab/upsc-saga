import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import './GoldenPath.css';

interface Node {
    id: string;
    label: string;
    yield: number;
    effort: number;
    roi: number;
    group: string;
    musk_category?: string; // DELETE, ACCELERATE, FOCUS
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

    // Fetch Graph Data
    useEffect(() => {
        fetch('http://localhost:5000/api/golden-path/graph')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Transform data for D3 (it mutates objects)
                    const nodes = data.data.nodes.map((n: any) => ({ ...n.data, id: n.id }));
                    const edges = data.data.edges.map((e: any) => ({ source: e.source, target: e.target }));
                    setGraphData({ nodes, edges });
                }
            })
            .catch(err => console.error("Failed to fetch graph:", err));
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
            .call(d3.zoom().on("zoom", (event) => {
                g.attr("transform", event.transform);
            }) as any);

        const g = svg.append("g");

        // Simulation
        const simulation = d3.forceSimulation(graphData.nodes as any)
            .force("link", d3.forceLink(graphData.edges).id((d: any) => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius(30));

        // Links
        const link = g.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(graphData.edges)
            .join("line")
            .attr("class", "link");

        // Nodes
        const node = g.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(graphData.nodes)
            .join("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended) as any);

        // Node Circles (Size based on Yield, Color based on Effort)
        // Color scale: Green (Low Effort) -> Red (High Effort)
        const colorScale = d3.scaleLinear<string>()
            .domain([5, 30]) // Effort range approx
            .range(["#00ff00", "#ff0000"]);

        node.append("circle")
            .attr("r", (d: any) => 5 + (d.yield / 2)) // Size based on yield
            .attr("fill", (d: any) => colorScale(d.effort))
            .attr("fill-opacity", 0.7)
            .attr("stroke", (d: any) => {
                if (d.musk_category === 'DELETE') return '#ff0000';
                if (d.musk_category === 'ACCELERATE') return '#ffff00';
                if (d.musk_category === 'FOCUS') return '#00ffff';
                return '#fff';
            })
            .attr("stroke-width", (d: any) => d.musk_category ? 3 : 1);

        // Labels
        node.append("text")
            .attr("dx", 12)
            .attr("dy", ".35em")
            .text((d: any) => d.label);

        // Tooltips (Simple title for now)
        node.append("title")
            .text((d: any) => `[${d.musk_category || 'N/A'}] Yield: ${d.yield} | Effort: ${d.effort}h | ROI: ${d.roi?.toFixed(2)}`);

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

        return () => {
            simulation.stop();
        };
    }, [graphData]);

    // Highlight Path Effect
    useEffect(() => {
        if (!optimalPath.length || !svgRef.current) return;

        const svg = d3.select(svgRef.current);
        const pathIds = new Set(optimalPath.map(n => n.id));

        // Highlight Nodes
        svg.selectAll(".node")
            .classed("highlighted", (d: any) => pathIds.has(d.id));

        // Highlight Edges (if both source and target are in path)
        svg.selectAll(".link")
            .classed("highlighted", (d: any) => pathIds.has(d.source.id) && pathIds.has(d.target.id));

    }, [optimalPath]);

    const handleOptimize = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:5000/api/golden-path/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ time_budget: timeBudget })
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

    return (
        <div className="golden-path-container">
            <div className="gp-sidebar">
                <h2>The Golden Path</h2>
                <div className="gp-controls">
                    <div className="gp-input-group">
                        <label>Time Budget (Hours)</label>
                        <input
                            type="number"
                            className="gp-input"
                            value={isNaN(timeBudget) ? '' : timeBudget}
                            onChange={(e) => setTimeBudget(parseFloat(e.target.value))}
                        />
                    </div>
                    <button className="gp-btn" onClick={handleOptimize} disabled={loading}>
                        {loading ? 'Calculating...' : 'Find Optimal Path'}
                    </button>
                    {optimalPath.length > 0 && (
                        <>
                            <button className="gp-btn gp-btn-commit" onClick={async () => {
                                try {
                                    const res = await fetch('http://localhost:5000/api/brain/directive', {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'application/json' },
                                        body: JSON.stringify({ path: optimalPath })
                                    });
                                    const data = await res.json();
                                    if (data.success) alert("Strategy Committed to The Brain!");
                                } catch (err) {
                                    console.error("Failed to commit strategy:", err);
                                }
                            }} style={{ marginLeft: '10px', background: 'rgba(0, 255, 0, 0.2)', border: '1px solid #00ff00' }}>
                                Commit
                            </button>
                            <button className="gp-btn gp-btn-reset" onClick={() => {
                                setOptimalPath([]);
                                setStats({ totalYield: 0, totalEffort: 0 });
                            }} style={{ marginLeft: '10px', background: 'rgba(255, 0, 0, 0.2)', border: '1px solid #ff0000' }}>
                                Reset
                            </button>
                        </>
                    )}
                </div>

                {optimalPath.length > 0 && (
                    <div className="gp-stats">
                        <h3>Optimal Strategy</h3>
                        <div className="gp-stat-item">
                            <span>Total Yield (Marks):</span>
                            <span className="gp-stat-value">{stats.totalYield}</span>
                        </div>
                        <div className="gp-stat-item">
                            <span>Total Effort (Hours):</span>
                            <span className="gp-stat-value">{stats.totalEffort}</span>
                        </div>
                        <div className="gp-stat-item">
                            <span>Topics:</span>
                            <span className="gp-stat-value">{optimalPath.length}</span>
                        </div>

                        <h4>Path Sequence:</h4>
                        <ul style={{ paddingLeft: '20px', fontSize: '0.8rem', color: '#ccc' }}>
                            {optimalPath.map((node, i) => (
                                <li key={i} style={{ color: '#ff0' }}>{node.label}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            <div className="gp-graph-area">
                <svg ref={svgRef} style={{ width: '100%', height: '100%' }}></svg>
                {loading && <div className="loading-overlay">Consulting the Oracle...</div>}
            </div>
        </div>
    );
};

export default GoldenPath;
