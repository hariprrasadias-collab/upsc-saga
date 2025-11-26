import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Mapping {
    id: number;
    subject: string;
    syllabus_topic: string;
    paper: string;
    relevance_score: number;
}

interface VisualLinkerProps {
    articleTitle: string;
    mappings: Mapping[];
}

const VisualLinker: React.FC<VisualLinkerProps> = ({ articleTitle, mappings }) => {
    const svgRef = useRef<SVGSVGElement>(null);

    useEffect(() => {
        if (!svgRef.current || mappings.length === 0) return;

        const width = 600;
        const height = 400;

        // Clear previous render
        d3.select(svgRef.current).selectAll("*").remove();

        const svg = d3.select(svgRef.current)
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height])
            .attr("style", "max-width: 100%; height: auto; background: #001f3f; border-radius: 8px;");

        // Prepare data
        const nodes = [
            { id: "article", label: "Article", type: "root", r: 30 },
            ...mappings.map(m => ({
                id: `topic-${m.id}`,
                label: m.syllabus_topic,
                type: "topic",
                paper: m.paper,
                r: 20 + (m.relevance_score * 10) // Size based on relevance
            }))
        ];

        const links = mappings.map(m => ({
            source: "article",
            target: `topic-${m.id}`,
            value: m.relevance_score
        }));

        // Color scale for Papers
        const colorScale = d3.scaleOrdinal<string>()
            .domain(['GS1', 'GS2', 'GS3', 'GS4'])
            .range(['#ec4899', '#8b5cf6', '#3b82f6', '#10b981']);

        // Simulation
        const simulation = d3.forceSimulation(nodes as any)
            .force("link", d3.forceLink(links).id((d: any) => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        // Draw Lines
        const link = svg.append("g")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke-width", d => Math.sqrt(d.value * 5));

        // Draw Nodes
        const node = svg.append("g")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5)
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("r", d => d.r)
            .attr("fill", (d: any) => d.type === 'root' ? '#ff4136' : colorScale(d.paper) || '#6b7280')
            .call(drag(simulation) as any);

        // Labels
        const labels = svg.append("g")
            .attr("class", "labels")
            .selectAll("text")
            .data(nodes)
            .join("text")
            .attr("text-anchor", "middle")
            .attr("dy", (d: any) => d.r + 15)
            .text((d: any) => d.type === 'root' ? 'NEWS' : d.label)
            .attr("fill", "#fff")
            .style("font-size", "10px")
            .style("pointer-events", "none");

        // Tooltip logic could go here

        simulation.on("tick", () => {
            link
                .attr("x1", (d: any) => d.source.x)
                .attr("y1", (d: any) => d.source.y)
                .attr("x2", (d: any) => d.target.x)
                .attr("y2", (d: any) => d.target.y);

            node
                .attr("cx", (d: any) => d.x)
                .attr("cy", (d: any) => d.y);

            labels
                .attr("x", (d: any) => d.x)
                .attr("y", (d: any) => d.y);
        });

        function drag(simulation: any) {
            function dragstarted(event: any) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }

            function dragged(event: any) {
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }

            function dragended(event: any) {
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }

            return d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended);
        }

    }, [mappings, articleTitle]);

    return (
        <div className="visual-linker-container" style={{ marginTop: '20px', marginBottom: '20px' }}>
            <h4 style={{ color: '#7fdbff', marginBottom: '10px' }}>🕸️ Visual Linkages</h4>
            <svg ref={svgRef}></svg>
        </div>
    );
};

export default VisualLinker;
