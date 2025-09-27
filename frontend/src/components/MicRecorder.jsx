import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import React, { useEffect, useState } from 'react';

export default function MicRecorder() {
    const [message, setMessage] = useState("Waiting for Audio")

    const commands = [
        {
        command: 'pay',
        callback: () => setMessage('Hi there!')
        }
    ]

    const {
        transcript,
        interimTranscript,
        finalTranscript,
        resetTranscript,
        listening,
        browserSupportsSpeechRecognition,
    } = useSpeechRecognition({ commands })

    useEffect(() => {
        if (finalTranscript !== '') {
            console.log('Got final result:', finalTranscript);
        }
    }, [interimTranscript, finalTranscript]);

    useEffect(() => {
        if (browserSupportsSpeechRecognition && !listening) {
            SpeechRecognition.startListening({ continuous: true });
        }
    }, [browserSupportsSpeechRecognition, listening]);

    return (
        <div>
            <p>Microphone: {listening ? 'on' : 'off'}</p>
                <div className="flex gap-x-2 p-2 rounded">
                    <button onClick={() => SpeechRecognition.startListening({ continuous:true})} className="w-48 p-3 bg-purple-600 rounded-lg shadow hover:bg-purple-500 transition">
                        Start
                    </button>
                    <button onClick={SpeechRecognition.stopListening} className="w-48 p-3 bg-purple-600 rounded-lg shadow hover:bg-purple-500 transition">
                        Stop
                    </button>
                    <button onClick={resetTranscript} className="w-48 p-3 bg-purple-600 rounded-lg shadow hover:bg-purple-500 transition">
                        Reset
                    </button>
                </div>
            <p>{"Waiting for Pay Command"}</p>
        </div>
    )
}
