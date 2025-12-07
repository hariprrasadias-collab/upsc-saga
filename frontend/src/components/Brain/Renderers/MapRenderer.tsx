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

// Haversine formula for distance in km
function getDistanceFromLatLonInKm(lat1: number, lon1: number, lat2: number, lon2: number) {
    const R = 6371; // Radius of the earth in km
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2)
        ;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const d = R * c; // Distance in km
    return d;
}

function deg2rad(deg: number) {
    return deg * (Math.PI / 180)
}

const MapRenderer: React.FC<MapRendererProps> = ({ content, metadata }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const gRef = useRef<SVGGElement>(null);
    const projectionRef = useRef<d3.GeoProjection | null>(null);

    const [geoData, setGeoData] = useState<any>(null);
    const [locations, setLocations] = useState<Location[]>([]);
    const [tooltip, setTooltip] = useState<{ x: number, y: number, text: string } | null>(null);
    const [theme, setTheme] = useState<'cyber' | 'atlas' | 'ancient'>('cyber');
    const [zoomTransform, setZoomTransform] = useState<d3.ZoomTransform>(d3.zoomIdentity);

    // Practice Mode State
    const [mode, setMode] = useState<'explore' | 'practice'>('explore');
    const [quizIndex, setQuizIndex] = useState(0);
    const [quizScore, setQuizScore] = useState(0);
    const [showResult, setShowResult] = useState(false); // Result of current question
    const [lastGuess, setLastGuess] = useState<{ lat: number, lon: number, distance: number, correct: boolean } | null>(null);
    const [feedbackMsg, setFeedbackMsg] = useState<string>("");

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

        projectionRef.current = projection;

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
        // Only clear paths, not circles which are managed by the other effect?
        // Actually, we should redraw paths here.
        // We use a specific class for paths to differentiate from points if needed,
        // or just clear everything if we assume this effect always runs before the other.
        // But effects run in order of definition usually, or concurrently.
        // Safer to just clear specific elements or rely on data join.
        g.selectAll("path").remove();

        // Draw Colors based on Theme
        let fill = '#1a1a2e';
        let stroke = 'rgba(0, 255, 242, 0.2)';

        if (theme === 'atlas') {
            fill = '#e0e0e0';
            stroke = '#999';
        } else if (theme === 'ancient') {
            fill = '#f4e4bc'; // Parchment
            stroke = '#b08d55'; // Sepia/Brown
        }

        // Draw Map Paths
        // In Ancient mode, we might want less detailed borders or fainter ones
        const strokeWidth = theme === 'ancient' ? 0.3 : 0.5;

        g.selectAll("path")
            .data(geoData.features)
            .enter()
            .append("path")
            .attr("d", path as any)
            .attr("fill", fill)
            .attr("stroke", stroke)
            .attr("stroke-width", strokeWidth);

    }, [geoData, theme]);


    // Render Points (Dynamic based on Mode)
    useEffect(() => {
        if (!gRef.current || !projectionRef.current || !geoData) return;
        const g = d3.select(gRef.current);

        // Remove existing points and lines first
        g.selectAll(".map-point").remove();
        g.selectAll(".feedback-line").remove();
        g.selectAll(".guess-point").remove();

        const pointColor = theme === 'cyber' ? '#ff00dd' : (theme === 'ancient' ? '#8b4513' : '#d32f2f');

        if (mode === 'explore') {
            if (locations.length > 0) {
                g.selectAll("circle.map-point")
                    .data(locations)
                    .enter()
                    .append("circle")
                    .attr("cx", d => projectionRef.current!([d.lon, d.lat])?.[0] || 0)
                    .attr("cy", d => projectionRef.current!([d.lon, d.lat])?.[1] || 0)
                    .attr("r", 6 / (zoomTransform.k || 1))
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
        } else {
            // PRACTICE MODE
            // Show only the CORRECT point IF we are showing results
            if (showResult && locations[quizIndex]) {
                const target = locations[quizIndex];

                // Draw Correct Point
                g.append("circle")
                    .attr("cx", projectionRef.current!([target.lon, target.lat])?.[0] || 0)
                    .attr("cy", projectionRef.current!([target.lon, target.lat])?.[1] || 0)
                    .attr("r", 8 / (zoomTransform.k || 1))
                    .attr("fill", "#2ea043") // Green
                    .attr("stroke", "#fff")
                    .attr("class", "map-point");

                // Draw User Guess
                if (lastGuess) {
                     g.append("circle")
                        .attr("cx", projectionRef.current!([lastGuess.lon, lastGuess.lat])?.[0] || 0)
                        .attr("cy", projectionRef.current!([lastGuess.lon, lastGuess.lat])?.[1] || 0)
                        .attr("r", 6 / (zoomTransform.k || 1))
                        .attr("fill", lastGuess.correct ? "#2ea043" : "#da3633") // Red/Green
                        .attr("class", "guess-point");

                    // Draw Line
                    g.append("line")
                        .attr("x1", projectionRef.current!([target.lon, target.lat])?.[0] || 0)
                        .attr("y1", projectionRef.current!([target.lon, target.lat])?.[1] || 0)
                        .attr("x2", projectionRef.current!([lastGuess.lon, lastGuess.lat])?.[0] || 0)
                        .attr("y2", projectionRef.current!([lastGuess.lon, lastGuess.lat])?.[1] || 0)
                        .attr("stroke", lastGuess.correct ? "#2ea043" : "#da3633")
                        .attr("stroke-width", 2 / (zoomTransform.k || 1))
                        .attr("stroke-dasharray", "4")
                        .attr("class", "feedback-line");
                }
            }
        }

    }, [locations, mode, quizIndex, showResult, lastGuess, zoomTransform, theme]);


    // Click Handler for Map
    const handleMapClick = (event: React.MouseEvent) => {
        if (mode !== 'practice' || showResult) return;
        if (!projectionRef.current || !locations[quizIndex]) return;

        // Get SVG coordinates
        const [svgX, svgY] = d3.pointer(event, svgRef.current);

        // Apply Inverse Transform (Zoom) to get "unzoomed" coordinates relative to G
        // Transform: output = input * k + [tx, ty]
        // input = (output - [tx, ty]) / k
        const transform = zoomTransform;
        const x = (svgX - transform.x) / transform.k;
        const y = (svgY - transform.y) / transform.k;

        // Invert Projection to get Lat/Lon
        const coords = projectionRef.current.invert?.([x, y]);
        if (coords) {
            const [lon, lat] = coords;
            const target = locations[quizIndex];

            // Calculate Distance
            const dist = getDistanceFromLatLonInKm(lat, lon, target.lat, target.lon);
            const threshold = 150; // 150km tolerance (India is big)
            const isCorrect = dist <= threshold;

            setLastGuess({ lat, lon, distance: Math.round(dist), correct: isCorrect });
            setShowResult(true);

            if (isCorrect) {
                setFeedbackMsg(`🎯 Great job! You were off by only ${Math.round(dist)}km.`);
                setQuizScore(prev => prev + 1);
            } else {
                setFeedbackMsg(`❌ Missed! You were off by ${Math.round(dist)}km. See the correct location.`);
            }
        }
    };

    const nextQuestion = () => {
        if (quizIndex < locations.length - 1) {
            setQuizIndex(prev => prev + 1);
            setShowResult(false);
            setLastGuess(null);
            setFeedbackMsg("");
        } else {
            setFeedbackMsg("🎉 Practice Complete!");
        }
    };

    const resetQuiz = () => {
        setQuizIndex(0);
        setQuizScore(0);
        setShowResult(false);
        setLastGuess(null);
        setFeedbackMsg("");
        // Keep in practice mode
    };

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
        // Re-create temporary projection to calculate center (since ref is stable)
        const projection = d3.geoMercator().center([82, 23]).scale(800).translate([width / 2, height / 2]);
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
        <div className={`map-renderer-container ${theme}`}>
            <div className="map-header">
                <h3 style={{color: theme === 'ancient' ? '#8b4513' : 'inherit'}}>
                    {mode === 'explore' ? '📍 AI Cartographer' : '⚔️ Map Practice'}
                </h3>
                <div className="map-controls-row">
                    <button
                        className={`map-btn-sm ${theme === 'cyber' ? 'active' : ''}`}
                        onClick={() => setTheme('cyber')}
                    >
                        🌙 Cyber
                    </button>
                    <button
                        className={`map-btn-sm ${theme === 'atlas' ? 'active' : ''}`}
                        onClick={() => setTheme('atlas')}
                    >
                        ☀️ Atlas
                    </button>
                    <button
                        className={`map-btn-sm ${theme === 'ancient' ? 'active' : ''}`}
                        onClick={() => setTheme('ancient')}
                    >
                        📜 Ancient
                    </button>
                </div>
            </div>

            <div className="mode-toggle-bar" style={{marginBottom: 10, display: 'flex', gap: 10}}>
                <button
                    className={`map-btn-sm ${mode === 'explore' ? 'active' : ''}`}
                    onClick={() => { setMode('explore'); handleReset(); }}
                >
                    Explore
                </button>
                <button
                    className={`map-btn-sm ${mode === 'practice' ? 'active' : ''}`}
                    onClick={() => { setMode('practice'); handleReset(); }}
                >
                    Practice
                </button>
            </div>

            {mode === 'practice' && locations.length > 0 && (
                 <div className="instruction-box">
                    <div style={{display:'flex', justifyContent:'space-between', marginBottom: 5}}>
                        <span><strong>Question {quizIndex + 1}/{locations.length}</strong></span>
                        <span>Score: {quizScore}</span>
                    </div>
                    {quizIndex < locations.length ? (
                        <div style={{fontSize: '1.1rem', marginBottom: 5}}>
                            Locate <strong>{locations[quizIndex].name}</strong> on the map.
                        </div>
                    ) : (
                        <div style={{color: '#2ea043', fontWeight: 'bold'}}>
                            Session Complete! You scored {quizScore}/{locations.length}.
                            <button onClick={resetQuiz} style={{marginLeft: 10, padding: '2px 8px', borderRadius: 4, cursor:'pointer'}}>Restart</button>
                        </div>
                    )}

                    {feedbackMsg && (
                        <div style={{marginTop: 5, padding: 5, background: 'rgba(0,0,0,0.2)', borderRadius: 4}}>
                            {feedbackMsg}
                            {showResult && quizIndex < locations.length - 1 && (
                                <button
                                    onClick={nextQuestion}
                                    style={{
                                        marginLeft: 10,
                                        background: '#238636',
                                        color: 'white',
                                        border: 'none',
                                        padding: '4px 12px',
                                        borderRadius: 4,
                                        cursor: 'pointer'
                                    }}
                                >
                                    Next ➡️
                                </button>
                            )}
                             {showResult && quizIndex === locations.length - 1 && (
                                <button
                                    onClick={() => setFeedbackMsg("🎉 All Done! Review the map or Restart.")}
                                    style={{
                                        marginLeft: 10,
                                        background: '#238636',
                                        color: 'white',
                                        border: 'none',
                                        padding: '4px 12px',
                                        borderRadius: 4,
                                        cursor: 'pointer'
                                    }}
                                >
                                    Finish
                                </button>
                            )}
                        </div>
                    )}
                 </div>
            )}

            <div className="map-viewport">
                <div className="map-float-controls">
                    <button onClick={() => handleZoom(1.5)}>+</button>
                    <button onClick={() => handleZoom(0.75)}>-</button>
                    <button onClick={handleReset}>↺</button>
                </div>

                <div style={{ position: 'absolute', top: 10, left: 10, color: theme === 'ancient' ? '#8b4513' : 'rgba(255,255,255,0.5)', fontSize: '0.7rem', zIndex: 5, pointerEvents: 'none' }}>
                    {mode === 'explore' ? `Points: ${locations.length}` : 'Quiz Mode Active'}
                </div>

                <svg
                    ref={svgRef}
                    width="100%"
                    height="600"
                    viewBox="0 0 600 600"
                    onClick={handleMapClick}
                    style={{cursor: mode === 'practice' && !showResult ? 'crosshair' : 'default'}}
                >
                    <g ref={gRef}></g>
                </svg>

                {tooltip && mode === 'explore' && (
                    <div
                        className="map-tooltip"
                        style={{ top: tooltip.y - 40, left: tooltip.x + 20 }}
                    >
                        {tooltip.text}
                    </div>
                )}
            </div>

            {mode === 'explore' && (
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
            )}
        </div>
    );
};

export default MapRenderer;
