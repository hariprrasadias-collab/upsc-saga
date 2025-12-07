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

// --- Utils ---

// Haversine formula for distance in km
function getDistanceFromLatLonInKm(lat1: number, lon1: number, lat2: number, lon2: number) {
    const R = 6371;
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2)
        ;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const d = R * c;
    return d;
}

function deg2rad(deg: number) {
    return deg * (Math.PI / 180)
}

// Simple Audio Synth
const playSound = (type: 'correct' | 'wrong' | 'tick' | 'win') => {
    try {
        const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
        if (!AudioContext) return;
        const ctx = new AudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);

        const now = ctx.currentTime;

        if (type === 'correct') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(600, now);
            osc.frequency.exponentialRampToValueAtTime(1200, now + 0.1);
            gain.gain.setValueAtTime(0.1, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
            osc.start(now);
            osc.stop(now + 0.3);
        } else if (type === 'wrong') {
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(200, now);
            osc.frequency.linearRampToValueAtTime(100, now + 0.3);
            gain.gain.setValueAtTime(0.1, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
            osc.start(now);
            osc.stop(now + 0.3);
        } else if (type === 'tick') {
            osc.type = 'square';
            osc.frequency.setValueAtTime(800, now);
            gain.gain.setValueAtTime(0.02, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
            osc.start(now);
            osc.stop(now + 0.05);
        } else if (type === 'win') {
             // Arpeggio
            osc.type = 'triangle';
            gain.gain.value = 0.1;

            [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
                 const osc2 = ctx.createOscillator();
                 const gain2 = ctx.createGain();
                 osc2.connect(gain2);
                 gain2.connect(ctx.destination);
                 osc2.frequency.value = freq;
                 const start = now + (i * 0.1);
                 gain2.gain.setValueAtTime(0.1, start);
                 gain2.gain.exponentialRampToValueAtTime(0.01, start + 0.3);
                 osc2.start(start);
                 osc2.stop(start + 0.3);
            });
        }
    } catch (e) {
        console.error("Audio Error", e);
    }
};


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
    const [streak, setStreak] = useState(0);
    const [showResult, setShowResult] = useState(false);
    const [lastGuess, setLastGuess] = useState<{ lat: number, lon: number, distance: number, correct: boolean } | null>(null);
    const [feedbackMsg, setFeedbackMsg] = useState<string>("");

    // Timer State
    const [timeLeft, setTimeLeft] = useState(15);
    const timerRef = useRef<any>(null);

    const zoomBehavior = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

    // --- Data Loading ---

    // 1. Parse Locations
    useEffect(() => {
        let foundLocations: Location[] = [];
        const extract = (data: any) => {
            if (!data) return [];
            if (data.locations && Array.isArray(data.locations)) return data.locations;
            if (Array.isArray(data)) return data;
            return [];
        };

        if (metadata) {
            if (typeof metadata === 'string') {
                try {
                    foundLocations = extract(JSON.parse(metadata));
                } catch (e) {}
            } else {
                foundLocations = extract(metadata);
            }
        }

        if (foundLocations.length === 0) {
            try {
                foundLocations = extract(JSON.parse(content));
            } catch (e) {}
        }
        setLocations(foundLocations);
    }, [content, metadata]);

    // 2. Smart Projection & Map Fetching
    useEffect(() => {
        if (locations.length === 0) return;

        // Check bounds
        const lats = locations.map(l => l.lat);
        const lons = locations.map(l => l.lon);
        const minLat = Math.min(...lats);
        const maxLat = Math.max(...lats);
        const minLon = Math.min(...lons);
        const maxLon = Math.max(...lons);

        // India Bounds (approx)
        const isIndia = (minLat >= 6 && maxLat <= 38 && minLon >= 68 && maxLon <= 98);

        const fetchMap = async () => {
            try {
                let url = 'https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson';
                let projCenter: [number, number] = [0, 20];
                let projScale = 150;

                if (isIndia) {
                    url = 'https://raw.githubusercontent.com/geohacker/india/master/district/india_district.geojson';
                    projCenter = [82, 23];
                    projScale = 800;
                }

                const res = await fetch(url);
                if (res.ok) {
                    const data = await res.json();
                    setGeoData({
                        geojson: data,
                        center: projCenter,
                        scale: projScale,
                        type: isIndia ? 'india' : 'world'
                    });
                }
            } catch (error) {
                console.error("Failed to load map data", error);
            }
        };
        fetchMap();
    }, [locations]);


    // --- Game Logic ---

    // Timer Tick
    useEffect(() => {
        if (mode === 'practice' && !showResult && quizIndex < locations.length) {
            if (timeLeft > 0) {
                timerRef.current = setTimeout(() => {
                    setTimeLeft(prev => prev - 1);
                    if (timeLeft <= 5) playSound('tick');
                }, 1000);
            } else {
                // Time's up!
                handleTimeOut();
            }
        }
        return () => {
            if (timerRef.current) clearTimeout(timerRef.current);
        };
    }, [timeLeft, mode, showResult, quizIndex, locations.length]);

    const handleTimeOut = () => {
        if (!locations[quizIndex]) return;
        playSound('wrong');
        setStreak(0);
        setShowResult(true);
        setFeedbackMsg("⏰ Time's up!");
        setLastGuess(null); // No guess made
    };

    const handleMapClick = (event: React.MouseEvent) => {
        if (mode !== 'practice' || showResult) return;
        if (!projectionRef.current || !locations[quizIndex]) return;

        const [svgX, svgY] = d3.pointer(event, svgRef.current);
        const transform = zoomTransform;
        const x = (svgX - transform.x) / transform.k;
        const y = (svgY - transform.y) / transform.k;

        const coords = projectionRef.current.invert?.([x, y]);
        if (coords) {
            const [lon, lat] = coords;
            const target = locations[quizIndex];
            const dist = getDistanceFromLatLonInKm(lat, lon, target.lat, target.lon);

            // Dynamic threshold based on map scale? For now fixed.
            const threshold = geoData?.type === 'india' ? 150 : 500;
            const isCorrect = dist <= threshold;

            setLastGuess({ lat, lon, distance: Math.round(dist), correct: isCorrect });
            setShowResult(true);

            if (isCorrect) {
                playSound('correct');
                setFeedbackMsg(`🎯 Great! Off by ${Math.round(dist)}km.`);
                setQuizScore(prev => prev + 1);
                setStreak(prev => prev + 1);
            } else {
                playSound('wrong');
                setFeedbackMsg(`❌ Missed by ${Math.round(dist)}km.`);
                setStreak(0);
            }
        }
    };

    const nextQuestion = () => {
        if (quizIndex < locations.length - 1) {
            setQuizIndex(prev => prev + 1);
            setShowResult(false);
            setLastGuess(null);
            setFeedbackMsg("");
            setTimeLeft(15); // Reset Timer
        } else {
            playSound('win');
            setFeedbackMsg("🎉 Practice Complete!");
        }
    };

    const resetQuiz = () => {
        setQuizIndex(0);
        setQuizScore(0);
        setStreak(0);
        setShowResult(false);
        setLastGuess(null);
        setFeedbackMsg("");
        setTimeLeft(15);
    };


    // --- Drawing ---

    // 1. Map Base
    useEffect(() => {
        if (!svgRef.current || !gRef.current || !geoData) return;

        const svg = d3.select(svgRef.current);
        const width = 600;
        const height = 600;

        const projection = d3.geoMercator()
            .center(geoData.center)
            .scale(geoData.scale)
            .translate([width / 2, height / 2]);

        projectionRef.current = projection;
        const path = d3.geoPath().projection(projection);

        // Zoom setup
        zoomBehavior.current = d3.zoom<SVGSVGElement, unknown>()
            .scaleExtent([1, 8])
            .on("zoom", (event) => {
                if (gRef.current) {
                    d3.select(gRef.current).attr("transform", event.transform);
                    setZoomTransform(event.transform);
                }
            });
        svg.call(zoomBehavior.current);

        // Draw Map
        const g = d3.select(gRef.current);
        g.selectAll("path").remove();

        let fill = '#1a1a2e';
        let stroke = 'rgba(0, 255, 242, 0.2)';
        if (theme === 'atlas') { fill = '#e0e0e0'; stroke = '#999'; }
        else if (theme === 'ancient') { fill = '#f4e4bc'; stroke = '#b08d55'; }

        g.selectAll("path")
            .data(geoData.geojson.features)
            .enter()
            .append("path")
            .attr("d", path as any)
            .attr("fill", fill)
            .attr("stroke", stroke)
            .attr("stroke-width", theme === 'ancient' ? 0.3 : 0.5);

    }, [geoData, theme]);

    // 2. Points & Game Overlay
    useEffect(() => {
        if (!gRef.current || !projectionRef.current || !geoData) return;
        const g = d3.select(gRef.current);

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
                    .on("mouseover", (event, d) => setTooltip({ x: event.pageX, y: event.pageY, text: d.name }))
                    .on("mouseout", () => setTooltip(null));
            }
        } else {
            // PRACTICE MODE
            if (showResult && locations[quizIndex]) {
                const target = locations[quizIndex];

                // Correct Point
                g.append("circle")
                    .attr("cx", projectionRef.current!([target.lon, target.lat])?.[0] || 0)
                    .attr("cy", projectionRef.current!([target.lon, target.lat])?.[1] || 0)
                    .attr("r", 8 / (zoomTransform.k || 1))
                    .attr("fill", "#2ea043")
                    .attr("stroke", "#fff")
                    .attr("class", "map-point");

                // User Guess
                if (lastGuess) {
                     g.append("circle")
                        .attr("cx", projectionRef.current!([lastGuess.lon, lastGuess.lat])?.[0] || 0)
                        .attr("cy", projectionRef.current!([lastGuess.lon, lastGuess.lat])?.[1] || 0)
                        .attr("r", 6 / (zoomTransform.k || 1))
                        .attr("fill", lastGuess.correct ? "#2ea043" : "#da3633")
                        .attr("class", "guess-point");

                    // Line
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
    }, [locations, mode, quizIndex, showResult, lastGuess, zoomTransform, theme, geoData]); // Added geoData to deps


    // --- Render Helpers ---

    const handleZoom = (factor: number) => {
        if (!svgRef.current || !zoomBehavior.current) return;
        d3.select(svgRef.current).transition().duration(300).call(zoomBehavior.current.scaleBy, factor);
    };

    const handleReset = () => {
        if (!svgRef.current || !zoomBehavior.current) return;
        d3.select(svgRef.current).transition().duration(750).call(zoomBehavior.current.transform, d3.zoomIdentity);
    };

    const flyToLocation = (loc: Location) => {
        if (!svgRef.current || !zoomBehavior.current || !geoData) return;
        // Re-calculate projection for center
        const projection = d3.geoMercator().center(geoData.center).scale(geoData.scale).translate([300, 300]);
        const [x, y] = projection([loc.lon, loc.lat]) || [0, 0];
        const scale = 4;
        const translate = [300 - scale * x, 300 - scale * y];

        d3.select(svgRef.current)
            .transition()
            .duration(1500)
            .call(zoomBehavior.current.transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
    };

    return (
        <div className={`map-renderer-container ${theme}`}>
            <div className="map-header">
                <h3 style={{color: theme === 'ancient' ? '#8b4513' : 'inherit'}}>
                    {mode === 'explore' ? '📍 AI Cartographer' : '⚔️ Map Arena'}
                </h3>
                <div className="map-controls-row">
                    <button className={`map-btn-sm ${theme === 'cyber' ? 'active' : ''}`} onClick={() => setTheme('cyber')}>🌙 Cyber</button>
                    <button className={`map-btn-sm ${theme === 'atlas' ? 'active' : ''}`} onClick={() => setTheme('atlas')}>☀️ Atlas</button>
                    <button className={`map-btn-sm ${theme === 'ancient' ? 'active' : ''}`} onClick={() => setTheme('ancient')}>📜 Ancient</button>
                </div>
            </div>

            <div className="mode-toggle-bar" style={{marginBottom: 10, display: 'flex', gap: 10}}>
                <button className={`map-btn-sm ${mode === 'explore' ? 'active' : ''}`} onClick={() => { setMode('explore'); handleReset(); }}>Explore</button>
                <button className={`map-btn-sm ${mode === 'practice' ? 'active' : ''}`} onClick={() => { setMode('practice'); handleReset(); resetQuiz(); }}>Practice</button>
            </div>

            {mode === 'practice' && locations.length > 0 && (
                 <div className="instruction-box">
                    <div className="hud-row">
                        <div className="hud-stat">
                            <span className="hud-label">Question</span>
                            <span className="hud-value">{quizIndex + 1}/{locations.length}</span>
                        </div>
                         <div className="hud-stat">
                            <span className="hud-label">Streak</span>
                            <span className={`hud-value ${streak > 2 ? 'streak-fire' : ''}`}>
                                {streak} 🔥
                            </span>
                        </div>
                        <div className="hud-stat">
                            <span className="hud-label">Score</span>
                            <span className="hud-value">{quizScore}</span>
                        </div>
                    </div>

                    {/* Timer Bar */}
                    {!showResult && quizIndex < locations.length && (
                        <div className="timer-bar-container">
                            <div
                                className={`timer-bar-fill ${timeLeft < 5 ? 'critical' : ''}`}
                                style={{width: `${(timeLeft / 15) * 100}%`}}
                            ></div>
                        </div>
                    )}

                    {quizIndex < locations.length ? (
                        <div className="question-text">
                            Locate <strong>{locations[quizIndex].name}</strong>
                        </div>
                    ) : (
                        <div className="completion-box">
                            Session Complete! You scored {quizScore}/{locations.length}.
                            <button onClick={resetQuiz} className="retry-btn">Restart</button>
                        </div>
                    )}

                    {feedbackMsg && (
                        <div className={`feedback-box ${lastGuess?.correct ? 'success' : 'failure'}`}>
                            {feedbackMsg}
                            {showResult && (
                                <button
                                    onClick={quizIndex < locations.length - 1 ? nextQuestion : () => setFeedbackMsg("🎉 All Done!")}
                                    className="next-btn"
                                >
                                    {quizIndex < locations.length - 1 ? 'Next ➡️' : 'Finish'}
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

                <div className="map-info-overlay">
                    {mode === 'explore' ? `${locations.length} Locations` : geoData?.type === 'india' ? '🇮🇳 India Focus' : '🌍 World Map'}
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
                    <div className="map-tooltip" style={{ top: tooltip.y - 40, left: tooltip.x + 20 }}>
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
