/* MapRenderer.ts */
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import './Renderers.css';

interface Location {
    name: string;
    lat: number;
    lon: number;
    reason: string;
}

interface MapRendererProps {
    content: string;
    metadata?: any;
}

const MapRenderer: React.FC<MapRendererProps> = ({ content, metadata }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const gRef = useRef<SVGGElement>(null);
    const [geoData, setGeoData] = useState<any>(null);
    const [locations, setLocations] = useState<Location[]>([]);
    const [tooltip, setTooltip] = useState<{ x: number, y: number, text: string } | null>(null);
    const [theme, setTheme] = useState<'cyber' | 'atlas'>('cyber');
    const [zoomTransform, setZoomTransform] = useState<d3.ZoomTransform>(d3.zoomIdentity);

    // D3 Zoom Behavior instance
    const zoomBehavior = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

    // Parse Locations: Check Metadata FIRST, then Content
    useEffect(() => {
        let foundLocations: Location[] = [];

        // Helper to extract locations from any object
        const extract = (data: any) => {
            if (!data) return [];
            if (data.locations && Array.isArray(data.locations)) return data.locations;
            if (Array.isArray(data)) return data;
            return [];
        };

        // Priority 1: properties on metadata object
        if (metadata) {
            // Check if metadata itself is a string that needs parsing
            if (typeof metadata === 'string') {
                try {
                    const parsed = JSON.parse(metadata);
                    foundLocations = extract(parsed);
                } catch (e) {
                    // ignore
                }
            } else {
                foundLocations = extract(metadata);
            }
        }

        // Priority 2: Try to parse content as JSON if no metadata locations found
        if (foundLocations.length === 0) {
            try {
                const parsed = JSON.parse(content);
                foundLocations = extract(parsed);
            } catch (e) {
                // ignore
            }
        }

        console.log("MapRenderer: Resolved Locations:", foundLocations);
        setLocations(foundLocations);

    }, [content, metadata]);

    // Fetch Map Data
    useEffect(() => {
        const fetchMap = async () => {
            try {
                const res = await fetch('https://raw.githubusercontent.com/geohacker/india/master/district/india_district.geojson');
                if (res.ok) {
                    const data = await res.json();
                    setGeoData(data);
                } else {
                    const resWorld = await fetch('https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson');
                    const dataWorld = await resWorld.json();
                    setGeoData(dataWorld);
                }
            } catch (error) {
                console.error("Failed to load map data", error);
            }
        };
        fetchMap();
    }, []);

    // Initialize D3 and Zoom
    useEffect(() => {
        if (!svgRef.current || !gRef.current || !geoData) return;

        const svg = d3.select(svgRef.current);
        const width = 600;
        const height = 600;

        // India-centric Projection
        const projection = d3.geoMercator()
            .center([82, 23])
            .scale(800)
            .translate([width / 2, height / 2]);

        const path = d3.geoPath().projection(projection);

        // Define Zoom
        zoomBehavior.current = d3.zoom<SVGSVGElement, unknown>()
            .scaleExtent([1, 8])
            .on("zoom", (event) => {
                if (gRef.current) {
                    d3.select(gRef.current).attr("transform", event.transform);
                    setZoomTransform(event.transform);
                }
            });

        svg.call(zoomBehavior.current);

        // Bind Data
        const g = d3.select(gRef.current);
        g.selectAll("*").remove();

        // Draw Colors based on Theme
        const fill = theme === 'cyber' ? '#1a1a2e' : '#e0e0e0';
        const stroke = theme === 'cyber' ? 'rgba(0, 255, 242, 0.2)' : '#999';
        const pointColor = theme === 'cyber' ? '#ff00dd' : '#d32f2f';

        // Draw Map Paths
        g.selectAll("path")
            .data(geoData.features)
            .enter()
            .append("path")
            .attr("d", path as any)
            .attr("fill", fill)
            .attr("stroke", stroke)
            .attr("stroke-width", 0.5);

        // Draw Points
        if (locations.length > 0) {
            g.selectAll("circle")
                .data(locations)
                .enter()
                .append("circle")
                .attr("cx", d => projection([d.lon, d.lat])?.[0] || 0)
                .attr("cy", d => projection([d.lon, d.lat])?.[1] || 0)
                .attr("r", 6 / (zoomTransform.k || 1)) // Keep size constant relative to view? No, scale naturally or inverse
                .attr("fill", pointColor)
                .attr("stroke", "#fff")
                .attr("stroke-width", 1)
                .attr("class", "map-point")
                .on("mouseover", (event, d) => {
                    setTooltip({
                        x: event.pageX,
                        y: event.pageY,
                        text: `${d.name}`
                    });
                })
                .on("mouseout", () => setTooltip(null));
        }

    }, [geoData, locations, theme]); // Re-render on theme change

    // Manual Zoom Control
    const handleZoom = (factor: number) => {
        if (!svgRef.current || !zoomBehavior.current) return;
        d3.select(svgRef.current)
            .transition()
            .duration(300)
            .call(zoomBehavior.current.scaleBy, factor);
    };

    const handleReset = () => {
        if (!svgRef.current || !zoomBehavior.current) return;
        d3.select(svgRef.current)
            .transition()
            .duration(750)
            .call(zoomBehavior.current.transform, d3.zoomIdentity);
    };

    // Fly-To Function
    const flyToLocation = (loc: Location) => {
        if (!svgRef.current || !zoomBehavior.current) return;

        const width = 600;
        const height = 600;
        const projection = d3.geoMercator()
            .center([82, 23])
            .scale(800)
            .translate([width / 2, height / 2]);

        const [x, y] = projection([loc.lon, loc.lat]) || [0, 0];

        // Calculate transform to center this point
        const scale = 4;
        const translate = [width / 2 - scale * x, height / 2 - scale * y];

        d3.select(svgRef.current)
            .transition()
            .duration(1500)
            .call(
                zoomBehavior.current.transform,
                d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
            );
    };


    return (
        <div className={`map-renderer-container glass-card ${theme}`}>
            <div className="map-header">
                <h3>📍 AI Cartographer</h3>
                <div className="map-controls-row">
                    <button className="map-btn-sm" onClick={() => setTheme(prev => prev === 'cyber' ? 'atlas' : 'cyber')}>
                        {theme === 'cyber' ? '🌙 Cyber' : '☀️ Atlas'}
                    </button>
                </div>
            </div>

            <div className="map-viewport">
                <div className="map-float-controls">
                    <button onClick={() => handleZoom(1.5)}>+</button>
                    <button onClick={() => handleZoom(0.75)}>-</button>
                    <button onClick={handleReset}>↺</button>
                </div>

                <div style={{ position: 'absolute', top: 10, left: 10, color: 'rgba(255,255,255,0.5)', fontSize: '0.7rem', zIndex: 5, pointerEvents: 'none' }}>
                    Points: {locations.length} (Lat/Lon)
                </div>

                <svg ref={svgRef} width="100%" height="600" viewBox="0 0 600 600">
                    <g ref={gRef}></g>
                </svg>

                {tooltip && (
                    <div
                        className="map-tooltip"
                        style={{ top: tooltip.y - 40, left: tooltip.x + 20 }}
                    >
                        {tooltip.text}
                    </div>
                )}
            </div>

            <div className="map-legend">
                {locations.map((loc, i) => (
                    <div
                        key={i}
                        className="legend-item interactive"
                        onClick={() => flyToLocation(loc)}
                        title="Click to Fly To"
                    >
                        <span className="dot" style={{ background: theme === 'cyber' ? '#ff00dd' : '#d32f2f' }}></span>
                        <div>
                            <strong>{loc.name}</strong>
                            <div className="legend-desc">{loc.reason}</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MapRenderer;
