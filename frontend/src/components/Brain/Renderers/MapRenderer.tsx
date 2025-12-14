/* MapRenderer.ts */
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import './Renderers.css';
import { API_BASE_URL } from '../../../config';

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

function getDistanceFromLatLonInKm(lat1: number, lon1: number, lat2: number, lon2: number) {
    const R = 6371;
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

function deg2rad(deg: number) {
    return deg * (Math.PI / 180)
}

// Simple Audio Synth (Singleton Pattern)
let audioCtx: AudioContext | null = null;

const playSound = (type: 'correct' | 'wrong' | 'tick' | 'win' | 'giveup' | 'hint') => {
    try {
        if (!audioCtx) {
            const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
            if (AudioContext) audioCtx = new AudioContext();
        }
        if (!audioCtx) return;

        // Resume if suspended (browser policy)
        if (audioCtx.state === 'suspended') audioCtx.resume();

        const ctx = audioCtx;
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
        } else if (type === 'hint') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(800, now);
            osc.frequency.exponentialRampToValueAtTime(400, now + 0.3);
            gain.gain.setValueAtTime(0.05, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
            osc.start(now);
            osc.stop(now + 0.3);
        } else if (type === 'win') {
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

    // Modes & Toggles
    const [mode, setMode] = useState<'explore' | 'practice' | 'review'>('explore');
    const [isHardcore, setIsHardcore] = useState(false);
    const [showHintCircle, setShowHintCircle] = useState(false);

    // Quiz State
    const [quizIndex, setQuizIndex] = useState(0);
    const [streak, setStreak] = useState(0);
    const [showResult, setShowResult] = useState(false);
    const [feedbackMsg, setFeedbackMsg] = useState<string>("");
    const [totalMarks, setTotalMarks] = useState(0);
    const [attempts, setAttempts] = useState<Attempt[]>([]);
    const [reviewIndex, setReviewIndex] = useState(0);

    const [timeLeft, setTimeLeft] = useState(20);
    const timerRef = useRef<any>(null);
    const zoomBehavior = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

    // Data Parsing
    const [mapError, setMapError] = useState(false);

    // D3 Zoom Behavior instance


    // Parse Locations
    useEffect(() => {
        let foundLocations: Location[] = [];
        const extract = (data: any) => {
            if (!data) return [];
            let locs = [];
            if (data.locations && Array.isArray(data.locations)) locs = data.locations;
            else if (Array.isArray(data)) locs = data;
            return locs.map((l: any) => ({
                name: l.name,
                lat: l.lat,
                lon: l.lon,
                reason: l.reason || l.hint || l.description || "Historical Site"
            }));

        };

        if (metadata) {
            if (typeof metadata === 'string') {
                try { foundLocations = extract(JSON.parse(metadata)); } catch (e) { }
            } else {
                foundLocations = extract(metadata);
            }
        }
        if (foundLocations.length === 0) {
            try { foundLocations = extract(JSON.parse(content)); } catch (e) { }

            if (foundLocations.length === 0) {
                try {
                    if (content.trim().startsWith('{') || content.trim().startsWith('[')) {
                        foundLocations = extract(JSON.parse(content));
                    }
                } catch (e) { }
            }
        }
        setLocations(foundLocations);
        }, [content, metadata]);

    // Map Fetching
    useEffect(() => {
        if (locations.length === 0) return;
        const lats = locations.map(l => l.lat);
        const lons = locations.map(l => l.lon);
        const minLat = Math.min(...lats);
        const maxLat = Math.max(...lats);
        const minLon = Math.min(...lons);
        const maxLon = Math.max(...lons);
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

                } else {
                    throw new Error("Failed to load India map");
                }
            } catch (error) {
                console.warn("Primary map load failed, trying fallback...", error);
                try {
                    const resWorld = await fetch('https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson');
                    if (resWorld.ok) {
                        const dataWorld = await resWorld.json();
                        setGeoData({
                            geojson: dataWorld,
                            center: [0, 20],
                            scale: 150,
                            type: 'world'
                        });
                    } else {
                        throw new Error("Failed to load world map");
                    }
                } catch (e2) {
                    console.error("All map loads failed", e2);
                    setMapError(true);
                }
            }
        };
        fetchMap();
    }, [locations]);

    // Timer
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
        return () => { if (timerRef.current) clearTimeout(timerRef.current); };
    }, [timeLeft, mode, showResult, quizIndex, locations.length]);

    const submitScore = async (score: number) => {
        try {
            // Mock integration
            console.log("Submitting Score:", score);
            // Use relative URL for production compatibility
            await fetch(`${API_BASE_URL}/api/gamification/reward`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'MAP_WORK_COMPLETE',
                    score: score
                })
            });
        } catch (e) {
            console.error("Failed to submit score", e);
        }
    };

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
        recordAttempt(null, 9999, false, isHardcore ? -1.32 : -0.66);
    };

    const handleGiveUp = () => {
        if (!locations[quizIndex]) return;
        playSound('giveup');
        setStreak(0);
        setShowResult(true);
        setFeedbackMsg(`🏳️ Gave up. It was ${locations[quizIndex].name}.`);
        recordAttempt(null, 9999, false, isHardcore ? -1.32 : -0.66);
    };

    const handleHint = () => {
        if (showHintCircle) return; // Already showing
        playSound('hint');
        setTotalMarks(prev => parseFloat((prev - 1.0).toFixed(2)));
        setShowHintCircle(true);
        setTimeout(() => setShowHintCircle(false), 3000);
    };

    const handleMapClick = (event: React.MouseEvent) => {
        if ((mode !== 'practice' && mode !== 'review') || (mode === 'practice' && showResult)) return;
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

            let marks = 0;
            if (isCorrect) marks = isHardcore ? 4.00 : 2.00;
            else marks = isHardcore ? -1.32 : -0.66;

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
            setShowHintCircle(false);
            setTimeLeft(20);
        } else {
            playSound('win');
            setQuizIndex(locations.length); // Finish
            setShowResult(false);
            setFeedbackMsg("");
            setShowHintCircle(false);
            submitScore(totalMarks);
        }
    };

    const resetQuiz = () => {
        setQuizIndex(0);
        setTotalMarks(0);
        setAttempts([]);
        setStreak(0);
        setShowResult(false);
        setFeedbackMsg("");
        setShowHintCircle(false);
        setTimeLeft(20);
        setMode('practice');
    };

    const startReview = () => {
        setMode('review');
        setReviewIndex(0);
        flyToReviewItem(0);
    };

    const flyToReviewItem = (index: number) => {
        if (attempts[index]) flyToLocation(attempts[index].target);
    };

    const nextReview = () => {
        if (reviewIndex < attempts.length - 1) {
            setReviewIndex(prev => { const n = prev + 1; flyToReviewItem(n); return n; });
        }
    };

    const prevReview = () => {
        if (reviewIndex > 0) {
            setReviewIndex(prev => { const n = prev - 1; flyToReviewItem(n); return n; });
        }
    };

    // --- Drawing ---

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
        d3.select(svgRef.current).transition().duration(1500)
            .call(zoomBehavior.current.transform, d3.zoomIdentity.translate(300 - scale * x, 300 - scale * y).scale(scale));
    };

    // Initialize D3
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
        svg.selectAll(".scale-bar-group").remove(); // Clear previous scale bar

        if (theme === 'ancient') {
            const defs = svg.append("defs");
            const filter = defs.append("filter").attr("id", "paper-texture");
            filter.append("feTurbulence").attr("type", "fractalNoise").attr("baseFrequency", "0.04").attr("numOctaves", "5").attr("result", "noise");
            filter.append("feDiffuseLighting").attr("in", "noise").attr("lighting-color", "#f4e4bc").attr("surfaceScale", "2").append("feDistantLight").attr("azimuth", "45").attr("elevation", "60");
        }

        let fill = '#1a1a2e';
        let stroke = 'rgba(0, 255, 242, 0.2)';
        let strokeWidth = 0.5;

        if (isHardcore) {
            fill = '#000';
            stroke = '#333';
            strokeWidth = 0.2; // Hard to see
        } else if (theme === 'atlas') { fill = '#e0e0e0'; stroke = '#999'; }
        else if (theme === 'ancient') { fill = '#f4e4bc'; stroke = '#8b4513'; strokeWidth = 0.3; }

        const graticule = d3.geoGraticule();
        g.append("path")
            .datum(graticule())
            .attr("class", "graticule")
            .attr("d", path as any)
            .attr("fill", "none")
            .attr("stroke", theme === 'cyber' ? "rgba(0, 255, 242, 0.05)" : "rgba(0,0,0,0.05)")
            .attr("stroke-width", 0.5);

        g.selectAll("path")
            .data(geoData.geojson.features)
            .enter()
            .append("path")
            .attr("class", "feature")
            .attr("d", path as any)
            .attr("fill", fill)
            .attr("stroke", stroke)
            .attr("stroke-width", strokeWidth)
            .style("filter", theme === 'ancient' && !isHardcore ? "url(#paper-texture)" : "none");

    }, [geoData, theme, isHardcore]);

    // Scale Bar Update
    useEffect(() => {
        if (!svgRef.current || !projectionRef.current) return;
        const svg = d3.select(svgRef.current);
        svg.selectAll(".scale-bar-group").remove();

        const k = zoomTransform.k;
        // Approximation: 1 degree latitude ~ 111km
        // At scale S, 1 pixel = X km.
        // D3 Mercator default: 2*PI pixels = World width.
        // This is complex to calculate perfectly dynamic.
        // Simpler: Use a fixed visual bar width (e.g., 100px) and calculate what distance that represents at current center.

        // 1. Get center point inverted
        const center = projectionRef.current.invert?.([300, 300]);
        if (!center) return;

        // 2. Get point 100px to the right
        // We need to account for zoom transform.
        // Screen pixels 300,300 -> Transformed: (300-tx)/k
        const p1 = [(300 - zoomTransform.x) / k, (300 - zoomTransform.y) / k];
        const p2 = [(400 - zoomTransform.x) / k, (300 - zoomTransform.y) / k];

        const c1 = projectionRef.current.invert?.([p1[0], p1[1]]);
        const c2 = projectionRef.current.invert?.([p2[0], p2[1]]);

        if (c1 && c2) {
            const distKm = getDistanceFromLatLonInKm(c1[1], c1[0], c2[1], c2[0]);

            const scaleGroup = svg.append("g")
                .attr("class", "scale-bar-group")
                .attr("transform", "translate(20, 570)"); // Bottom Left

            // Bar
            scaleGroup.append("line")
                .attr("x1", 0).attr("y1", 0)
                .attr("x2", 100).attr("y2", 0)
                .attr("stroke", "#fff")
                .attr("stroke-width", 2);

            // Ticks
            scaleGroup.append("line").attr("x1", 0).attr("y1", -5).attr("x2", 0).attr("y2", 5).attr("stroke", "#fff");
            scaleGroup.append("line").attr("x1", 100).attr("y1", -5).attr("x2", 100).attr("y2", 5).attr("stroke", "#fff");

            // Text
            scaleGroup.append("text")
                .attr("x", 50)
                .attr("y", -10)
                .attr("text-anchor", "middle")
                .attr("fill", "#fff")
                .attr("font-size", "12px")
                .text(`${Math.round(distKm)} km`);
        }
    }, [geoData, locations, theme, zoomTransform]);

    // Overlay Elements
    useEffect(() => {
        if (!gRef.current || !projectionRef.current || !geoData) return;
        const g = d3.select(gRef.current);

        g.selectAll(".map-point").remove();
        g.selectAll(".feedback-line").remove();
        g.selectAll(".guess-point").remove();
        g.selectAll(".target-ring").remove();
        g.selectAll(".hint-circle").remove();

        const pointColor = theme === 'cyber' ? '#ff00dd' : (theme === 'ancient' ? '#8b4513' : '#d32f2f');

        const drawPoint = (lat: number, lon: number, color: string, radius = 6) => {
            g.append("circle")
                .attr("cx", projectionRef.current!([lon, lat])?.[0] || 0)
                .attr("cy", projectionRef.current!([lon, lat])?.[1] || 0)
                .attr("r", radius / (zoomTransform.k || 1))
                .attr("fill", color)
                .attr("stroke", "#fff")
                .attr("class", "map-point");
        };

        const drawLine = (start: { lat: number, lon: number }, end: { lat: number, lon: number }, color: string) => {
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

        // Draw Hint Radar
        if (showHintCircle && locations[quizIndex]) {
            const t = locations[quizIndex];
            g.append("circle")
                .attr("cx", projectionRef.current!([t.lon, t.lat])?.[0] || 0)
                .attr("cy", projectionRef.current!([t.lon, t.lat])?.[1] || 0)
                .attr("r", 50 / (zoomTransform.k || 1)) // Visual radius approx
                .attr("fill", "rgba(0, 255, 242, 0.2)")
                .attr("stroke", "rgba(0, 255, 242, 0.5)")
                .attr("stroke-width", 1)
                .attr("class", "hint-circle pulse");
        }

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
        }
        else if (mode === 'practice') {
            if (showResult && attempts.length > 0) {
                const currentAttempt = attempts[attempts.length - 1];
                const target = currentAttempt.target;

                g.append("circle")
                    .attr("cx", projectionRef.current!([target.lon, target.lat])?.[0] || 0)
                    .attr("cy", projectionRef.current!([target.lon, target.lat])?.[1] || 0)
                    .attr("r", 20 / (zoomTransform.k || 1))
                    .attr("fill", "none")
                    .attr("stroke", "#2ea043")
                    .attr("stroke-width", 2)
                    .attr("class", "target-ring");

                drawPoint(target.lat, target.lon, "#2ea043", 8);

                if (currentAttempt.guess) {
                    drawPoint(currentAttempt.guess.lat, currentAttempt.guess.lon, currentAttempt.correct ? "#2ea043" : "#da3633", 6);
                    drawLine(target, currentAttempt.guess, currentAttempt.correct ? "#2ea043" : "#da3633");
                }
            }
        }
        else if (mode === 'review') {
            if (attempts.length > 0 && attempts[reviewIndex]) {
                const item = attempts[reviewIndex];
                attempts.forEach(a => {
                    drawPoint(a.target.lat, a.target.lon, "rgba(255,255,255,0.3)", 4);
                });
                g.append("circle")
                    .attr("cx", projectionRef.current!([item.target.lon, item.target.lat])?.[0] || 0)
                    .attr("cy", projectionRef.current!([item.target.lon, item.target.lat])?.[1] || 0)
                    .attr("r", 25 / (zoomTransform.k || 1))
                    .attr("fill", "none")
                    .attr("stroke", "#00fff2")
                    .attr("stroke-width", 2)
                    .attr("class", "target-ring pulse");

                drawPoint(item.target.lat, item.target.lon, "#2ea043", 8);

                if (item.guess) {
                    drawPoint(item.guess.lat, item.guess.lon, item.correct ? "#2ea043" : "#da3633", 6);
                    drawLine(item.target, item.guess, "#da3633");
                }
            }
        }
    }, [locations, mode, quizIndex, showResult, attempts, reviewIndex, zoomTransform, theme, geoData, showHintCircle]);


    if (mapError) {
        return <div className="map-error glass-card">⚠️ Unable to load map data. Please check connection.</div>;
    }

    return (
        <div className={`map-renderer-container ${theme} ${isFullscreen ? 'fullscreen-map' : ''}`}>
            <div className="map-header">
                <h3 style={{ color: theme === 'ancient' ? '#8b4513' : 'inherit' }}>
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

            <div className="mode-toggle-bar" style={{ marginBottom: 10, display: 'flex', gap: 10 }}>
                <button className={`map-btn-sm ${mode === 'explore' ? 'active' : ''}`} onClick={() => { setMode('explore'); handleReset(); }}>Explore</button>
                <button className={`map-btn-sm ${mode === 'practice' ? 'active' : ''}`} onClick={() => { setMode('practice'); handleReset(); resetQuiz(); }}>Practice</button>
                {attempts.length > 0 && <button className={`map-btn-sm ${mode === 'review' ? 'active' : ''}`} onClick={startReview}>Review</button>}

                <div style={{ flex: 1 }}></div>
                {mode === 'practice' && (
                    <button
                        className={`map-btn-sm ${isHardcore ? 'active' : ''}`}
                        onClick={() => setIsHardcore(!isHardcore)}
                        title="Blind Map, Double Points"
                    >
                        ☠️ Hardcore
                    </button>
                )}
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
                            <span className="hud-value" style={{ color: totalMarks < 0 ? '#f85149' : '#3fb950' }}>
                                {totalMarks > 0 ? '+' : ''}{totalMarks}
                            </span>
                        </div>
                    </div>

                    {!showResult && quizIndex < locations.length && (
                        <div className="timer-bar-container">
                            <div
                                className={`timer-bar-fill ${timeLeft < 5 ? 'critical' : ''}`}
                                style={{ width: `${(timeLeft / 20) * 100}%` }}
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
                                <div style={{ display: 'flex', gap: 10, justifyContent: 'center', marginTop: 10 }}>
                                    <button onClick={handleHint} className="give-up-btn" style={{ background: '#0d1117', border: '1px solid #30363d' }}>
                                        💡 Hint (-1.0)
                                    </button>
                                    <button onClick={handleGiveUp} className="give-up-btn">
                                        🏳️ Give Up
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="completion-box">
                            <div>Session Complete!</div>
                            <div style={{ fontSize: '1.5rem', margin: '10px 0', color: totalMarks >= 0 ? '#3fb950' : '#f85149' }}>
                                Final Score: {totalMarks}
                            </div>
                            <div className="completion-actions">
                                <button onClick={resetQuiz} className="retry-btn">Restart</button>
                                <button onClick={startReview} className="next-btn" style={{ marginLeft: 10 }}>Review Mistakes ➡️</button>
                            </div>
                        </div>
                    )}

                    {feedbackMsg && (
                        <div className={`feedback-box ${attempts[attempts.length - 1]?.correct ? 'success' : 'failure'}`}>
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
                    <div className="review-controls" style={{ marginTop: 10, display: 'flex', gap: 10, justifyContent: 'center' }}>
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
                    style={{ cursor: mode === 'practice' && !showResult ? 'crosshair' : 'default' }}
                >
                    <g ref={gRef}></g>
                </svg>


                {tooltip && (
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
