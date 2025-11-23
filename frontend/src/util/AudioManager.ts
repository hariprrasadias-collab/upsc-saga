// /frontend/src/utils/AudioManager.ts

class AudioManager {
    private static instance: AudioManager;
    private isMuted: boolean = false;
    private sounds: Record<string, HTMLAudioElement> = {};

private constructor() {
        this.loadSound('click', '/sounds/click.wav');
        this.loadSound('success', '/sounds/success.wav');
        this.loadSound('levelup', '/sounds/levelup.wav');
        this.loadSound('rage', '/sounds/rage.wav');
        
        // FIX: Set Volume to 1.0 (Max) for testing
        if (this.sounds['click']) this.sounds['click'].volume = 1.0;
        if (this.sounds['success']) this.sounds['success'].volume = 1.0;
        
        // Rage usually needs to be lower because it's background noise
        if (this.sounds['rage']) {
            this.sounds['rage'].loop = true;
            this.sounds['rage'].volume = 0.5; 
        }
    }

    // Helper to load and debug sounds
    private loadSound(key: string, path: string) {
        const audio = new Audio(path);
        
        // Add Error Listener to catch 404s or Corrupt files
        audio.addEventListener('error', (e) => {
            console.error(`❌ FAILED TO LOAD SOUND: ${key}`, e);
            console.error(`   Path tried: ${path}`);
            console.error(`   Check if file exists in /public/sounds/ and name matches exactly.`);
        });

        // Add Success Listener (Optional, for debugging)
        audio.addEventListener('canplaythrough', () => {
            console.log(`✅ Sound loaded: ${key}`);
        });

        this.sounds[key] = audio;
    }

    public static getInstance(): AudioManager {
        if (!AudioManager.instance) {
            AudioManager.instance = new AudioManager();
        }
        return AudioManager.instance;
    }

public play(soundName: string): void {
        if (this.isMuted) return;
        
        const original = this.sounds[soundName];
        if (original) {
            // CRITICAL FIX: Clone the node so we can play it repeatedly/rapidly
            const soundClone = original.cloneNode() as HTMLAudioElement;
            
            // Force volume to max just to be sure
            soundClone.volume = 1.0; 
            
            soundClone.play()
                .then(() => {
                    console.log(`🔊 Playing: ${soundName}`);
                })
                .catch(e => {
                    console.error(`❌ Play failed for ${soundName}:`, e);
                });
        } else {
            console.warn(`⚠️ Sound not found: ${soundName}`);
        }
    }

    public startLoop(soundName: string): void {
        if (this.isMuted) return;
        const audio = this.sounds[soundName];
        if (audio) audio.play().catch(e => console.warn("Loop failed", e));
    }

    public stopLoop(soundName: string): void {
        const audio = this.sounds[soundName];
        if (audio) {
            audio.pause();
            audio.currentTime = 0;
        }
    }

    public toggleMute(): boolean {
        this.isMuted = !this.isMuted;
        if (this.isMuted) {
            Object.values(this.sounds).forEach(s => s.pause());
        }
        return this.isMuted;
    }

    public getMuteStatus(): boolean {
        return this.isMuted;
    }
}

export const audioManager = AudioManager.getInstance();