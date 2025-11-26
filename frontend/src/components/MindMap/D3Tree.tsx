import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface TreeNode {
    name: string;
    children?: TreeNode[];
}

interface CustomHierarchyNode extends d3.HierarchyNode<TreeNode> {
    x0?: number;
    y0?: number;
    _children?: CustomHierarchyNode[] | undefined;
}

interface D3TreeProps {
    data: TreeNode;
}

const D3Tree: React.FC<D3TreeProps> = ({ data }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const wrapperRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!data || !svgRef.current || !wrapperRef.current) return;

        const width = wrapperRef.current.clientWidth;
        const marginTop = 10;
        const marginBottom = 10;
        const marginLeft = 150;  // Increased from 40 to prevent text truncation

        // Clear previous SVG content
        d3.select(svgRef.current).selectAll("*").remove();

        const root = d3.hierarchy<TreeNode>(data) as CustomHierarchyNode;
        // Increase vertical spacing for better readability
        const dx = 50;
        const dy = width / (root.height + 1);

        const tree = d3.tree<TreeNode>().nodeSize([dx, dy]);

        const diagonal = d3.linkHorizontal<any, any>()
            .x((d) => d.y)
            .y((d) => d.x);

        const svg = d3.select(svgRef.current)
            .attr("viewBox", [-marginLeft, -marginTop, width, dx].join(" "))
            .style("font", "14px sans-serif")
            .style("user-select", "none");

        const gLink = svg.append("g")
            .attr("fill", "none")
            .attr("stroke", "#555")
            .attr("stroke-opacity", 0.4)
            .attr("stroke-width", 1.5);

        const gNode = svg.append("g")
            .attr("cursor", "pointer")
            .attr("pointer-events", "all");

        function update(source: CustomHierarchyNode) {
            const duration = 250;
            const nodes = root.descendants() as CustomHierarchyNode[];
            const links = root.links();

            // Compute the new tree layout.
            tree(root);

            let left = root;
            let right = root;
            let maxRight = 0;
            root.eachBefore((node: any) => {
                if (node.x < (left.x ?? 0)) left = node;
                if (node.x > (right.x ?? 0)) right = node;

                // Estimate text width (approx 8px per char) + node position
                const textWidth = (node.data.name.length * 8) + 20; // 20px padding
                const nodeRight = (node.y ?? 0) + textWidth;
                if (nodeRight > maxRight) maxRight = nodeRight;
            });

            const height = (right.x ?? 0) - (left.x ?? 0) + marginTop + marginBottom;
            const contentWidth = maxRight + marginLeft + 50; // Add extra padding
            const newWidth = Math.max(width, contentWidth);

            // Update SVG height to accommodate the tree size, preventing zooming out
            const newHeight = Math.max(600, height);
            d3.select(svgRef.current).attr("height", newHeight);
            d3.select(svgRef.current).attr("width", newWidth); // Update width too

            const transition = svg.transition()
                .duration(duration)
                .attr("viewBox", [-marginLeft, (left.x ?? 0) - marginTop, newWidth, height].join(" "))
                .tween("resize", (window.ResizeObserver ? null : () => () => svg.dispatch("toggle")) as any);

            // Update the nodes…
            const node = gNode.selectAll<SVGGElement, CustomHierarchyNode>("g")
                .data(nodes, (d: any) => d.id);

            // Enter any new nodes at the parent's previous position.
            const nodeEnter = node.enter().append("g")
                .attr("transform", (_d: any) => `translate(${source.y0 ?? 0},${source.x0 ?? 0})`)
                .attr("fill-opacity", 0)
                .attr("stroke-opacity", 0)
                .on("click", (_event, d) => {
                    d.children = d.children ? undefined : d._children;
                    update(d);
                });

            nodeEnter.append("circle")
                .attr("r", 6)
                .attr("fill", (d) => d._children ? "#555" : "#999")
                .attr("stroke-width", 10);

            nodeEnter.append("text")
                .attr("dy", "0.31em")
                .attr("x", (d) => d._children ? -8 : 8)
                .attr("text-anchor", (d) => d._children ? "end" : "start")
                .text((d) => d.data.name)
                .attr("fill", "white") // High contrast text
                .style("text-shadow", "0 1px 2px rgba(0,0,0,0.8)") // Shadow for readability
                .clone(true).lower()
                .attr("stroke-linejoin", "round")
                .attr("stroke-width", 3)
                .attr("stroke", "#1a1a1a"); // Dark halo

            // Transition nodes to their new position.
            const nodeUpdate = node.merge(nodeEnter).transition(transition as any)
                .attr("transform", (d) => `translate(${d.y},${d.x})`)
                .attr("fill-opacity", 1)
                .attr("stroke-opacity", 1);

            nodeUpdate.select("circle")
                .attr("fill", (d) => d.children ? "#555" : "#999");

            // Transition exiting nodes to the parent's new position.
            node.exit().transition(transition as any).remove()
                .attr("transform", (_d: any) => `translate(${source.y},${source.x})`)
                .attr("fill-opacity", 0)
                .attr("stroke-opacity", 0);

            // Update the links…
            const link = gLink.selectAll<SVGPathElement, d3.HierarchyLink<TreeNode>>("path")
                .data(links, (d: any) => d.target.id);

            // Enter any new links at the parent's previous position.
            const linkEnter = link.enter().append("path")
                .attr("d", (_d: any) => {
                    const o = { x: source.x0 ?? 0, y: source.y0 ?? 0 };
                    return diagonal({ source: o, target: o });
                });

            // Transition links to their new position.
            link.merge(linkEnter).transition(transition as any)
                .attr("d", diagonal as any);

            // Transition exiting links to the parent's new position.
            link.exit().transition(transition as any).remove()
                .attr("d", (_d: any) => {
                    const o = { x: source.x, y: source.y };
                    return diagonal({ source: o, target: o });
                });

            // Stash the old positions for transition.
            root.eachBefore((d: any) => {
                d.x0 = d.x;
                d.y0 = d.y;
            });
        }

        // Initialize the display to show a few nodes.
        root.x0 = dy / 2;
        root.y0 = 0;
        root.descendants().forEach((d: any, i) => {
            d.id = i;
            d._children = d.children as CustomHierarchyNode[] | undefined;
            // if (d.depth && d.data.name.length !== 7) d.children = undefined;
        });

        update(root);

    }, [data]);

    return (
        <div ref={wrapperRef} style={{ width: '100%', overflow: 'auto', border: '1px solid var(--border-color)', borderRadius: '8px', background: 'var(--bg-secondary)' }}>
            <svg ref={svgRef} width="100%" height="600"></svg>
        </div>
    );
};

export default D3Tree;
