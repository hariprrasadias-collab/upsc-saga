/* MapRenderer.ts */
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import './Renderers.css';

interface Location {
    name: string;
    lat: number;
    lon: number;
    reason: string; // Used as the Hint/Description
}

interface Attempt {
    target: Location;
    guess: { lat: number, lon: number } | null;
    distance: number;
    correct: boolean;
    marks: number;
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
const playSound = (type: 'correct' | 'wrong' | 'tick' | 'win' | 'giveup') => {
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
        } else if (type === 'giveup') {
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(300, now);
            osc.frequency.linearRampToValueAtTime(150, now + 0.5);
            gain.gain.setValueAtTime(0.1, now);
            gain.gain.linearRampToValueAtTime(0.01, now + 0.5);
            osc.start(now);
            osc.stop(now + 0.5);
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

// Global Cache for GeoJSON to prevent re-fetching
const geoCache: { [key: string]: any } = {};

const MapRenderer: React.FC<MapRendererProps> = ({ content, metadata }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const gRef = useRef<SVGGElement>(null);
    const projectionRef = useRef<d3.GeoProjection | null>(null);

    const [geoData, setGeoData] = useState<any>(null);
    const [locations, setLocations] = useState<Location[]>([]);
    const [tooltip, setTooltip] = useState<{ x: number, y: number, text: string } | null>(null);
    const [theme, setTheme] = useState<'cyber' | 'atlas' | 'ancient'>('cyber');
    const [zoomTransform, setZoomTransform] = useState<d3.ZoomTransform>(d3.zoomIdentity);
    const [isFullscreen, setIsFullscreen] = useState(false);

    // Practice Mode State
    const [mode, setMode] = useState<'explore' | 'practice' | 'review'>('explore');
    const [quizIndex, setQuizIndex] = useState(0);
    const [streak, setStreak] = useState(0);
    const [showResult, setShowResult] = useState(false);
    const [feedbackMsg, setFeedbackMsg] = useState<string>("");

    // UPSC Scoring State
    const [totalMarks, setTotalMarks] = useState(0);
    const [attempts, setAttempts] = useState<Attempt[]>([]);
    const [reviewIndex, setReviewIndex] = useState(0);

    // Timer State
    const [timeLeft, setTimeLeft] = useState(20);
    const timerRef = useRef<any>(null);

    const zoomBehavior = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

    // --- Data Loading ---

    // 1. Parse Locations
    useEffect(() => {
        let foundLocations: Location[] = [];
        const extract = (data: any) => {
            if (!data) return [];
            let locs = [];
            if (data.locations && Array.isArray(data.locations)) locs = data.locations;
            else if (Array.isArray(data)) locs = data;

            // Normalize
            return locs.map((l: any) => ({
                name: l.name,
                lat: l.lat,
                lon: l.lon,
                reason: l.reason || l.hint || l.description || "Historical Site"
            }));
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
            const cacheKey = isIndia ? 'india' : 'world';

            if (geoCache[cacheKey]) {
                setGeoData(geoCache[cacheKey]);
                return;
            }

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
                    const result = {
                        geojson: data,
                        center: projCenter,
                        scale: projScale,
                        type: isIndia ? 'india' : 'world'
                    };
                    geoCache[cacheKey] = result;
                    setGeoData(result);
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
                handleTimeOut();
            }
        }
        return () => {
            if (timerRef.current) clearTimeout(timerRef.current);
        };
    }, [timeLeft, mode, showResult, quizIndex, locations.length]);

    const recordAttempt = (guess: { lat: number, lon: number } | null, distance: number, correct: boolean, marks: number) => {
        setAttempts(prev => [...prev, {
            target: locations[quizIndex],
            guess,
            distance,
            correct,
            marks
        }]);
        setTotalMarks(prev => parseFloat((prev + marks).toFixed(2)));
    };

    const handleTimeOut = () => {
        if (!locations[quizIndex]) return;
        playSound('wrong');
        setStreak(0);
        setShowResult(true);
        setFeedbackMsg(`⏰ Time's up! It was ${locations[quizIndex].name}.`);
        recordAttempt(null, 9999, false, -0.66);
    };

    const handleGiveUp = () => {
        if (!locations[quizIndex]) return;
        playSound('giveup');
        setStreak(0);
        setShowResult(true);
        setFeedbackMsg(`🏳️ Gave up. It was ${locations[quizIndex].name}.`);
        recordAttempt(null, 9999, false, -0.66);
    };

    const handleMapClick = (event: React.MouseEvent) => {
        if ((mode !== 'practice' && mode !== 'review') || (mode === 'practice' && showResult)) return;

        // Disable clicking in review mode unless we want manual exploration?
        // For now, let's keep clicks disabled in review mode to avoid confusion.
        if (mode === 'review') return;

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

            const threshold = geoData?.type === 'india' ? 150 : 500;
            const isCorrect = dist <= threshold;

            const marks = isCorrect ? 2.00 : -0.66;

            setShowResult(true);
            recordAttempt({ lat, lon }, Math.round(dist), isCorrect, marks);

            if (isCorrect) {
                playSound('correct');
                setFeedbackMsg(`🎯 Correct! ${target.name}.`);
                setStreak(prev => prev + 1);
            } else {
                playSound('wrong');
                setFeedbackMsg(`❌ Missed by ${Math.round(dist)}km. It was ${target.name}.`);
                setStreak(0);
            }
        }
    };

    const nextQuestion = () => {
        if (quizIndex < locations.length - 1) {
            setQuizIndex(prev => prev + 1);
            setShowResult(false);
            setFeedbackMsg("");
            setTimeLeft(20);
        } else {
            playSound('win');
            setQuizIndex(locations.length); // Finish
            setShowResult(false);
            setFeedbackMsg("");
        }
    };

    const resetQuiz = () => {
        setQuizIndex(0);
        setTotalMarks(0);
        setAttempts([]);
        setStreak(0);
        setShowResult(false);
        setFeedbackMsg("");
        setTimeLeft(20);
        setMode('practice');
    };

    const startReview = () => {
        setMode('review');
        setReviewIndex(0);
        flyToReviewItem(0);
    };

    const flyToReviewItem = (index: number) => {
        if (attempts[index]) {
            flyToLocation(attempts[index].target);
        }
    };

    const nextReview = () => {
        if (reviewIndex < attempts.length - 1) {
            const next = reviewIndex + 1;
            setReviewIndex(next);
            flyToReviewItem(next);
        }
    };

    const prevReview = () => {
        if (reviewIndex > 0) {
            const prev = reviewIndex - 1;
            setReviewIndex(prev);
            flyToReviewItem(prev);
        }
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

        const g = d3.select(gRef.current);
        g.selectAll("*").remove();
        svg.selectAll("defs").remove();

        if (theme === 'ancient') {
            const defs = svg.append("defs");
            const filter = defs.append("filter").attr("id", "paper-texture");
            filter.append("feTurbulence")
                .attr("type", "fractalNoise")
                .attr("baseFrequency", "0.04")
                .attr("numOctaves", "5")
                .attr("result", "noise");
            filter.append("feDiffuseLighting")
                .attr("in", "noise")
                .attr("lighting-color", "#f4e4bc")
                .attr("surfaceScale", "2")
                .append("feDistantLight")
                .attr("azimuth", "45")
                .attr("elevation", "60");
        }

        let fill = '#1a1a2e';
        let stroke = 'rgba(0, 255, 242, 0.2)';
        let strokeWidth = 0.5;

        if (theme === 'atlas') { fill = '#e0e0e0'; stroke = '#999'; }
        else if (theme === 'ancient') {
            fill = '#f4e4bc';
            stroke = '#8b4513';
            strokeWidth = 0.3;
        }

        const graticule = d3.geoGraticule();
        g.append("path")
            .datum(graticule())
            .attr("class", "graticule")
            .attr("d", path as any)
            .attr("fill", "none")
            .attr("stroke", theme === 'cyber' ? "rgba(0, 255, 242, 0.05)" : "rgba(0,0,0,0.05)")
            .attr("stroke-width", 0.5);

        g.selectAll("path.feature")
            .data(geoData.geojson.features)
            .enter()
            .append("path")
            .attr("class", "feature")
            .attr("d", path as any)
            .attr("fill", fill)
            .attr("stroke", stroke)
            .attr("stroke-width", strokeWidth)
            .style("filter", theme === 'ancient' ? "url(#paper-texture)" : "none");

    }, [geoData, theme]);

    // 2. Points & Overlay
    useEffect(() => {
        if (!gRef.current || !projectionRef.current || !geoData) return;
        const g = d3.select(gRef.current);

        g.selectAll(".map-point").remove();
        g.selectAll(".feedback-line").remove();
        g.selectAll(".guess-point").remove();
        g.selectAll(".target-ring").remove();

        const pointColor = theme === 'cyber' ? '#ff00dd' : (theme === 'ancient' ? '#8b4513' : '#d32f2f');

        // Helper to draw point
        const drawPoint = (lat: number, lon: number, color: string, radius = 6) => {
            g.append("circle")
                .attr("cx", projectionRef.current!([lon, lat])?.[0] || 0)
                .attr("cy", projectionRef.current!([lon, lat])?.[1] || 0)
                .attr("r", radius / (zoomTransform.k || 1))
                .attr("fill", color)
                .attr("stroke", "#fff")
                .attr("class", "map-point");
        };

        const drawLine = (start: {lat: number, lon: number}, end: {lat: number, lon: number}, color: string) => {
             g.append("line")
                .attr("x1", projectionRef.current!([start.lon, start.lat])?.[0] || 0)
                .attr("y1", projectionRef.current!([start.lon, start.lat])?.[1] || 0)
                .attr("x2", projectionRef.current!([end.lon, end.lat])?.[0] || 0)
                .attr("y2", projectionRef.current!([end.lon, end.lat])?.[1] || 0)
                .attr("stroke", color)
                .attr("stroke-width", 2 / (zoomTransform.k || 1))
                .attr("stroke-dasharray", "4")
                .attr("class", "feedback-line");
        };

        if (mode === 'explore') {
            if (locations.length > 0) {
                // ... existing explore logic ...
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
        }
        else if (mode === 'practice') {
            if (showResult && attempts.length > 0) {
                const currentAttempt = attempts[attempts.length - 1];
                const target = currentAttempt.target;

                // Target Ring
                g.append("circle")
                    .attr("cx", projectionRef.current!([target.lon, target.lat])?.[0] || 0)
                    .attr("cy", projectionRef.current!([target.lon, target.lat])?.[1] || 0)
                    .attr("r", 20 / (zoomTransform.k || 1))
                    .attr("fill", "none")
                    .attr("stroke", "#2ea043")
                    .attr("stroke-width", 2)
                    .attr("class", "target-ring");

                // Correct Point
                drawPoint(target.lat, target.lon, "#2ea043", 8);

                // User Guess
                if (currentAttempt.guess) {
                    drawPoint(currentAttempt.guess.lat, currentAttempt.guess.lon, currentAttempt.correct ? "#2ea043" : "#da3633", 6);
                    drawLine(target, currentAttempt.guess, currentAttempt.correct ? "#2ea043" : "#da3633");
                }
            }
        }
        else if (mode === 'review') {
            if (attempts.length > 0 && attempts[reviewIndex]) {
                const item = attempts[reviewIndex];

                // Draw ALL targets as ghosts
                attempts.forEach(a => {
                    drawPoint(a.target.lat, a.target.lon, "rgba(255,255,255,0.3)", 4);
                });

                // Highlight Current
                // Target
                 g.append("circle")
                    .attr("cx", projectionRef.current!([item.target.lon, item.target.lat])?.[0] || 0)
                    .attr("cy", projectionRef.current!([item.target.lon, item.target.lat])?.[1] || 0)
                    .attr("r", 25 / (zoomTransform.k || 1))
                    .attr("fill", "none")
                    .attr("stroke", "#00fff2")
                    .attr("stroke-width", 2)
                    .attr("class", "target-ring pulse"); // Add CSS pulse?

                drawPoint(item.target.lat, item.target.lon, "#2ea043", 8);

                if (item.guess) {
                     drawPoint(item.guess.lat, item.guess.lon, item.correct ? "#2ea043" : "#da3633", 6);
                     drawLine(item.target, item.guess, "#da3633");
                }
            }
        }
    }, [locations, mode, quizIndex, showResult, attempts, reviewIndex, zoomTransform, theme, geoData]);


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
        <div className={`map-renderer-container ${theme} ${isFullscreen ? 'fullscreen-map' : ''}`}>
            <div className="map-header">
                <h3 style={{color: theme === 'ancient' ? '#8b4513' : 'inherit'}}>
                    {mode === 'explore' ? '📍 AI Cartographer' : (mode === 'review' ? '📝 Review Mode' : '⚔️ Map Arena')}
                </h3>
                <div className="map-controls-row">
                    <button className={`map-btn-sm ${theme === 'cyber' ? 'active' : ''}`} onClick={() => setTheme('cyber')}>🌙 Cyber</button>
                    <button className={`map-btn-sm ${theme === 'atlas' ? 'active' : ''}`} onClick={() => setTheme('atlas')}>☀️ Atlas</button>
                    <button className={`map-btn-sm ${theme === 'ancient' ? 'active' : ''}`} onClick={() => setTheme('ancient')}>📜 Ancient</button>
                    <button className={`map-btn-sm ${isFullscreen ? 'active' : ''}`} onClick={() => setIsFullscreen(!isFullscreen)}>
                        {isFullscreen ? '🔽 Min' : '⤢ Max'}
                    </button>
                </div>
            </div>

            <div className="mode-toggle-bar" style={{marginBottom: 10, display: 'flex', gap: 10}}>
                <button className={`map-btn-sm ${mode === 'explore' ? 'active' : ''}`} onClick={() => { setMode('explore'); handleReset(); }}>Explore</button>
                <button className={`map-btn-sm ${mode === 'practice' ? 'active' : ''}`} onClick={() => { setMode('practice'); handleReset(); resetQuiz(); }}>Practice</button>
                {attempts.length > 0 && <button className={`map-btn-sm ${mode === 'review' ? 'active' : ''}`} onClick={startReview}>Review</button>}
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
                            <span className="hud-label">Marks</span>
                            <span className="hud-value" style={{color: totalMarks < 0 ? '#f85149' : '#3fb950'}}>
                                {totalMarks > 0 ? '+' : ''}{totalMarks}
                            </span>
                        </div>
                    </div>

                    {!showResult && quizIndex < locations.length && (
                        <div className="timer-bar-container">
                            <div
                                className={`timer-bar-fill ${timeLeft < 5 ? 'critical' : ''}`}
                                style={{width: `${(timeLeft / 20) * 100}%`}}
                            ></div>
                        </div>
                    )}

                    {quizIndex < locations.length ? (
                        <div className="question-box">
                            <div className="question-label">Identify the place:</div>
                            <div className="question-text">
                                "{locations[quizIndex].reason || "No description available."}"
                            </div>
                            {!showResult && (
                                <button onClick={handleGiveUp} className="give-up-btn">🏳️ Give Up</button>
                            )}
                        </div>
                    ) : (
                        <div className="completion-box">
                            <div>Session Complete!</div>
                            <div style={{fontSize: '1.5rem', margin: '10px 0', color: totalMarks >= 0 ? '#3fb950' : '#f85149'}}>
                                Final Score: {totalMarks}
                            </div>
                            <div className="completion-actions">
                                <button onClick={resetQuiz} className="retry-btn">Restart</button>
                                <button onClick={startReview} className="next-btn" style={{marginLeft: 10}}>Review Mistakes ➡️</button>
                            </div>
                        </div>
                    )}

                    {feedbackMsg && (
                        <div className={`feedback-box ${attempts[attempts.length-1]?.correct ? 'success' : 'failure'}`}>
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

            {mode === 'review' && (
                <div className="instruction-box">
                    <div className="review-header">
                        Reviewing {reviewIndex + 1} of {attempts.length}
                    </div>
                    <div className="question-text">
                        Target: <strong>{attempts[reviewIndex].target.name}</strong>
                    </div>
                    <div className="review-stat">
                        Your Guess: {attempts[reviewIndex].guess ? `${attempts[reviewIndex].distance}km off` : 'Skipped'}
                        <span className={`badge ${attempts[reviewIndex].correct ? 'correct' : 'wrong'}`}>
                            {attempts[reviewIndex].marks}
                        </span>
                    </div>
                    <div className="review-controls" style={{marginTop: 10, display: 'flex', gap: 10, justifyContent: 'center'}}>
                        <button onClick={prevReview} disabled={reviewIndex === 0} className="map-btn-sm">⬅️ Prev</button>
                        <button onClick={nextReview} disabled={reviewIndex === attempts.length - 1} className="map-btn-sm">Next ➡️</button>
                        <button onClick={resetQuiz} className="map-btn-sm">Exit</button>
                    </div>
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
