// Flow State Audio Engine - Bio-Adaptive Binaural Beats

export class FlowAudioEngine {
    private audioCtx: AudioContext | null = null;
    private leftOsc: OscillatorNode | null = null;
    private rightOsc: OscillatorNode | null = null;
    private gainNode: GainNode | null = null;
    private isPlaying: boolean = false;
    private baseFreq: number = 200; // Carrier frequency

    constructor() { }

    public start() {
        if (this.isPlaying) return;

        // Initialize Audio Context (must be after user interaction)
        if (!this.audioCtx) {
            this.audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
        }

        // Create Nodes
        this.leftOsc = this.audioCtx.createOscillator();
        this.rightOsc = this.audioCtx.createOscillator();
        this.gainNode = this.audioCtx.createGain();

        // Binaural Beat Setup (Gamma 40Hz)
        // Left Ear: 200Hz
        // Right Ear: 240Hz
        // Difference: 40Hz (Gamma - Peak Focus)
        this.leftOsc.frequency.value = this.baseFreq;
        this.rightOsc.frequency.value = this.baseFreq + 40;

        // Stereo Panning (Essential for Binaural Beats)
        const leftPanner = this.audioCtx.createStereoPanner();
        leftPanner.pan.value = -1; // Full Left
        const rightPanner = this.audioCtx.createStereoPanner();
        rightPanner.pan.value = 1; // Full Right

        // Connect Graph
        this.leftOsc.connect(leftPanner);
        leftPanner.connect(this.gainNode);

        this.rightOsc.connect(rightPanner);
        rightPanner.connect(this.gainNode);

        this.gainNode.connect(this.audioCtx.destination);

        // Start
        this.leftOsc.start();
        this.rightOsc.start();

        // Fade In
        this.gainNode.gain.setValueAtTime(0, this.audioCtx.currentTime);
        this.gainNode.gain.linearRampToValueAtTime(0.1, this.audioCtx.currentTime + 2); // Low volume start

        this.isPlaying = true;
    }

    public stop() {
        if (!this.isPlaying || !this.audioCtx || !this.gainNode) return;

        // Fade Out
        this.gainNode.gain.linearRampToValueAtTime(0, this.audioCtx.currentTime + 1);

        setTimeout(() => {
            if (this.leftOsc) { this.leftOsc.stop(); this.leftOsc.disconnect(); }
            if (this.rightOsc) { this.rightOsc.stop(); this.rightOsc.disconnect(); }
            this.isPlaying = false;
        }, 1000);
    }

    public updateIntensity(activityLevel: number) {
        // activityLevel: 0 to 1 (0 = idle, 1 = intense work)
        if (!this.gainNode || !this.leftOsc || !this.rightOsc || !this.audioCtx) return;

        // Adaptive Volume: Increase slightly during high activity to mask distractions
        const targetGain = 0.05 + (activityLevel * 0.1); // Min 0.05, Max 0.15
        this.gainNode.gain.setTargetAtTime(targetGain, this.audioCtx.currentTime, 0.5);

        // Adaptive Frequency: Shift slightly to keep brain engaged
        // Base freq wobbles between 200Hz and 210Hz based on activity
        const targetFreq = this.baseFreq + (activityLevel * 10);
        this.leftOsc.frequency.setTargetAtTime(targetFreq, this.audioCtx.currentTime, 1);
        this.rightOsc.frequency.setTargetAtTime(targetFreq + 40, this.audioCtx.currentTime, 1);
    }
}
