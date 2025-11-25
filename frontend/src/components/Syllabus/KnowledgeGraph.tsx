import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import './KnowledgeGraph.css';

interface GraphNode {
    id: string;
    name: string;
    subject: string;
    status: string;
    completion: number;
    group: string;
}

interface GraphEdge {
    source: string;
    target: string;
    type: string;
}

interface GraphData {
    nodes: GraphNode[];
    edges: GraphEdge[];
}

const KnowledgeGraph: React.FC = () => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [graphData, setGraphData] = useState<GraphData | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedSubject, setSelectedSubject] = useState<string>('all');

    useEffect(() => {
        fetchGraphData();
    }, []);

    useEffect(() => {
        if (graphData && svgRef.current) {
            renderGraph();
        }
    }, [graphData, selectedSubject]);

    const fetchGraphData = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/analytics/visualizations/knowledge-graph');
            const data = await res.json();
            setGraphData(data);
            setLoading(false);
        } catch (err) {
            console.error('Failed to fetch knowledge graph:', err);
            setLoading(false);
        }
    };

    const getNodeColor = (node: GraphNode) => {
        // Color by status
        if (node.status === 'mastered') return '#2ecc71';
        if (node.status === 'in-progress') return '#f39c12';
        if (node.status === 'not-started') return '#7f8c8d';
        return '#3498db';
    };

    const getNodeSize = (node: GraphNode) => {
        // Size based on completion
        return 5 + (node.completion / 10);
    };

    const renderGraph = () => {
        if (!svgRef.current || !graphData) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();

        const width = svgRef.current.clientWidth;
        const height = svgRef.current.clientHeight;

        // Filter data by selected subject
        let filteredNodes = graphData.nodes;
        let filteredEdges = graphData.edges;

        if (selectedSubject !== 'all') {
            filteredNodes = graphData.nodes.filter(n => n.subject === selectedSubject);
            const nodeIds = new Set(filteredNodes.map(n => n.id));
            filteredEdges = graphData.edges.filter(e =>
                nodeIds.has(e.source.toString()) && nodeIds.has(e.target.toString())
            );
        }

        // Create force simulation
        const simulation = d3.forceSimulation(filteredNodes as any)
            .force('link', d3.forceLink(filteredEdges)
                .id((d: any) => d.id)
                .distance(80))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(20));

        // Create container
        const g = svg.append('g');

        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.5, 3])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });

        svg.call(zoom as any);

        // Draw edges
        const link = g.append('g')
            .selectAll('line')
            .data(filteredEdges)
            .enter()
            .append('line')
            .attr('class', 'graph-edge')
            .attr('stroke', '#30363d')
            .attr('stroke-width', 2);

        // Draw nodes
        const node = g.append('g')
            .selectAll('circle')
            .data(filteredNodes)
            .enter()
            .append('circle')
            .attr('class', 'graph-node')
            .attr('r', (d: any) => getNodeSize(d))
            .attr('fill', (d: any) => getNodeColor(d))
            .attr('stroke', '#d4a574')
            .attr('stroke-width', 2)
            .call(d3.drag<any, any>()
                .on('start', dragStarted)
                .on('drag', dragged)
                .on('end', dragEnded) as any);

        // Add labels
        const label = g.append('g')
            .selectAll('text')
            .data(filteredNodes)
            .enter()
            .append('text')
            .attr('class', 'graph-label')
            .attr('text-anchor', 'middle')
            .attr('dy', -15)
            .text((d: any) => d.name)
            .style('font-size', '10px')
            .style('fill', '#d4a574')
            .style('pointer-events', 'none');

        // Add tooltips
        node.append('title')
            .text((d: any) => `${d.name}\nSubject: ${d.subject}\nStatus: ${d.status}\nCompletion: ${d.completion}%`);

        // Update positions on tick
        simulation.on('tick', () => {
            link
                .attr('x1', (d: any) => d.source.x)
                .attr('y1', (d: any) => d.source.y)
                .attr('x2', (d: any) => d.target.x)
                .attr('y2', (d: any) => d.target.y);

            node
                .attr('cx', (d: any) => d.x)
                .attr('cy', (d: any) => d.y);

            label
                .attr('x', (d: any) => d.x)
                .attr('y', (d: any) => d.y);
        });

        function dragStarted(event: any) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event: any) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragEnded(event: any) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }
    };

    const subjects = graphData ? [...new Set(graphData.nodes.map(n => n.subject))] : [];

    if (loading) return <div className="graph-loading">Loading Knowledge Graph...</div>;

    return (
        <div className="knowledge-graph">
            <div className="graph-header">
                <h2>🧠 Knowledge Graph</h2>
                <div className="subject-filter">
                    <button
                        className={selectedSubject === 'all' ? 'active' : ''}
                        onClick={() => setSelectedSubject('all')}
                    >
                        All
                    </button>
                    {subjects.map(subject => (
                        <button
                            key={subject}
                            className={selectedSubject === subject ? 'active' : ''}
                            onClick={() => setSelectedSubject(subject)}
                        >
                            {subject}
                        </button>
                    ))}
                </div>
            </div>
            <div className="graph-legend">
                <div className="legend-item">
                    <span className="legend-dot" style={{ background: '#2ecc71' }}></span>
                    <span>Mastered</span>
                </div>
                <div className="legend-item">
                    <span className="legend-dot" style={{ background: '#f39c12' }}></span>
                    <span>In Progress</span>
                </div>
                <div className="legend-item">
                    <span className="legend-dot" style={{ background: '#7f8c8d' }}></span>
                    <span>Not Started</span>
                </div>
            </div>
            <svg ref={svgRef} className="graph-svg"></svg>
        </div>
    );
};

export default KnowledgeGraph;
