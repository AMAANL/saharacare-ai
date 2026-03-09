const VOIC_API_URL = '';

const playVoiceBtn = document.getElementById('play-voice-btn');
const audioPlayer = document.getElementById('audio-player');

if (playVoiceBtn) {
    playVoiceBtn.addEventListener('click', () => {

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Your browser does not support Voice Recognition.");
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = 'en-IN'; // Listen for English/Indian English speech (better for bilingual)
        recognition.interimResults = false;

        recognition.onstart = function () {
            playVoiceBtn.innerText = 'Listening...';
        };

        recognition.onspeechend = function () {
            recognition.stop();
        };

        recognition.onresult = async function (event) {
            const transcript = event.results[0][0].transcript;
            console.log("User said:", transcript);
            playVoiceBtn.innerText = 'Processing...';

            try {
                const response = await fetch(`${VOIC_API_URL}/voice_command`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', "X-User-Id": localStorage.getItem("user_id") || "arthur" },
                    body: JSON.stringify({ text: transcript })
                });
                const data = await response.json();

                if (data.audio && data.audio.type === 'url') {
                    audioPlayer.src = data.audio.data;
                    audioPlayer.play().catch(e => console.error("Play error:", e));
                } else if (data.audio && data.audio.type === 'base64') {
                    audioPlayer.src = `data:audio/wav;base64,${data.audio.data}`;
                    audioPlayer.play().catch(e => console.error("Play error:", e));
                }

                if (data.redirect) {
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 2500); // Wait for speech to start/finish
                }
                playVoiceBtn.innerText = 'Speak Command';
            } catch (error) {
                console.error('Voice reminder error:', error);
                playVoiceBtn.innerText = 'Server Error';
                setTimeout(() => playVoiceBtn.innerText = 'Speak Command', 2000);
            }
        };

        recognition.onerror = function (event) {
            console.error("Speech Error:", event.error);
            // If it's a no-speech error, silently ignore
            if (event.error === 'no-speech') {
                playVoiceBtn.innerText = 'Speak Command';
            } else {
                playVoiceBtn.innerText = 'Mic Error';
                setTimeout(() => playVoiceBtn.innerText = 'Speak Command', 2000);
            }
        };

        recognition.start();
    });
}
