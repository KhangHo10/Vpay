// import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
// import React, { useEffect, useState } from 'react';

// export default function MicRecorder() {
//     const [message, setMessage] = useState("Waiting for Audio")

//     const commands = [
//         {
//         command: 'pay',
//         callback: () => setMessage('Hi there!')
//         }
//     ]

//     const {
//         transcript,
//         interimTranscript,
//         finalTranscript,
//         resetTranscript,
//         listening,
//         browserSupportsSpeechRecognition,
//     } = useSpeechRecognition({ commands })

//     useEffect(() => {
//         if (finalTranscript !== '') {
//             console.log('Got final result:', finalTranscript);
//         }
//     }, [interimTranscript, finalTranscript]);

//     useEffect(() => {
//         if (browserSupportsSpeechRecognition && !listening) {
//             SpeechRecognition.startListening({ continuous: true });
//         }
//     }, [browserSupportsSpeechRecognition, listening]);

//     return (
//         <div>
//             <p>Microphone: {listening ? 'on' : 'off'}</p>
//                 <div className="flex gap-x-2 p-2 rounded">
//                     <button onClick={() => SpeechRecognition.startListening({ continuous:true})} className="w-48 p-3 bg-purple-600 rounded-lg shadow hover:bg-purple-500 transition">
//                         Start
//                     </button>
//                     <button onClick={SpeechRecognition.stopListening} className="w-48 p-3 bg-purple-600 rounded-lg shadow hover:bg-purple-500 transition">
//                         Stop
//                     </button>
//                     <button onClick={resetTranscript} className="w-48 p-3 bg-purple-600 rounded-lg shadow hover:bg-purple-500 transition">
//                         Reset
//                     </button>
//                 </div>
//             <p>{transcript}</p>
//         </div>
//     )
// }

import React, { useState, useRef, useCallback, useEffect } from 'react';

export default function MicRecorder() {
    const [isRecording, setIsRecording] = useState(false); // Checks if the browser is recording or not
    const [audioUrl, setAudioUrl] = useState(null); // Stores URL for playback when we stop obtaining audio
    const [transcript, setTranscript] = useState(''); // use to show feedback back to the frontend for transcripts
    const [paymentResult, setPaymentResult] = useState(null); // Showcases whether the payment was successful or not 
    const [isProcessing, setIsProcessing] = useState(false); // Used to disable the record button while audio is being processed

    const mediaRecorderRef = useRef(null); // ALlows tro record audio
    const audioChunksRef = useRef([]); // Stores audio data chunks as they're recorded
    const streamRef = useRef(null); // Stores the media stream so we can stop it later

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        return <div className="p-4 bg-red-100 text-red-800 rounded-lg">"getUserMedia is not supported in this browser."</div>;
    }
    
    const startRecording = useCallback(async () => {
        try {
            // Cleans up the previous audio file
            if (audioUrl) {
                URL.revokeObjectURL(audioUrl);
                setAudioUrl(null);
            }
            // Get audio stream with specific constraints for better STT
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: 16000,  // Google STT prefers 16kHz
                    channelCount: 1,    // Mono
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            streamRef.current = stream;
            audioChunksRef.current = [];

            // Create MediaRecorder with specific options for LINEAR16 compatibility
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'  // Most widely supported
            });

            mediaRecorderRef.current = mediaRecorder;

            // Continuously adds the audio chunks to the array for check
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            // When the audio stops recording it creates a blob
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { 
                    type: 'audio/webm;codecs=opus' 
                });
                
                if (audioUrl) {
                    URL.revokeObjectURL(audioUrl);
                }

                // Create URL for playback
                const url = URL.createObjectURL(audioBlob);
                setAudioUrl(url);
                
                // Process the audio
                await processAudio(audioBlob);
            };

            mediaRecorder.start(100); // Collect data every 100ms
            setIsRecording(true);
            setTranscript('');
            setPaymentResult(null);
        }catch (error) {
            console.error('Error starting recording:', error);
            alert('Error accessing microphone: ' + error.message);
        }
    }, [audioUrl])

    // Creates call for stop recording and resets everything
    const stopRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            
            // Stop all tracks
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        }
    }, [isRecording]);

    const processAudio = async (audioBlob) => {
        setIsProcessing(true);

        try {
            // Convert blob to base64 for sending to backend in order to be able to be 
            // converted to text
            const arrayBuffer = await audioBlob.arrayBuffer();
            const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer))); // Convert binary to base64 text
            
            // Send to your FastAPI backend
            const response = await fetch('/api/voice-payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    audio_data: base64Audio,
                    audio_format: 'webm',
                    sample_rate: 16000
                })
            });

            if (!response.ok) {
                throw new Error('Failed to process audio');
            }

            const result = await response.json();

            if (result.transcript) {
                setTranscript(result.transcript);
            }
                
            if (result.payment_result) {
                setPaymentResult(result.payment_result);
            }

        } catch (error) {
            console.error('Error processing audio:', error);
            setTranscript('Error: ' + error.message);
        } finally {
            setIsProcessing(false);
        }        
    };

    const toggleRecording = () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    };


    useEffect(() => {
        return () => {
            if (audioUrl) {
                URL.revokeObjectURL(audioUrl);  // Clean up CURRENT audio
            }
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, [audioUrl]);

    return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold text-center mb-6">Voice Payment</h2>

        {/* Recording Button */}
        <div className="text-center mb-6">
            <button 
                onClick={toggleRecording}
                disabled={isProcessing}
                className={`w-48 p-3 bg-purple-600 rounded-lg shadow hover:bg-purple-500 transition ${
                        isRecording ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                        : 'bg-blue-500 hover:bg-blue-600'
                } ${isProcessing ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}`}
            > 
                {isProcessing ? '...' : isRecording ? 'STOP' : 'REC'}
            </button>
        </div>

        {/* Status Indicator */}
        {isRecording && (
            <div className="text-center mb-4">
                <div className="inline-flex items-center px-3 py-1 rounded-full bg-red-100 text-red-800">
                    <div className="w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse"></div>
                    Recording...
                </div>
            </div>
        )}

        {/* Audio Playback */}
        {audioUrl && !isRecording && (
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Recorded Audio:
                </label>
                <audio controls className="w-full">
                    <source src={audioUrl} type="audio/webm" />
                    Your browser does not support audio playback.
                </audio>
            </div>
        )}

        {/* Transcript Display */}
        {transcript && (
            <div className="mb-4 p-3 bg-gray-100 rounded-lg">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    Transcript:
                </label>
                <p className="text-gray-800">{transcript}</p>
            </div>
        )}

        {/* Payment Result */}
        {paymentResult && (
            <div className={`p-3 rounded-lg ${
                paymentResult.status === 'success' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
            }`}>
                <label className="block text-sm font-medium mb-1">
                    Payment Result:
                </label>
                <p className="font-semibold">
                    {paymentResult.status === 'success' ? 'Successful' : 'Failed'} 
                </p>
                {paymentResult.amount && (
                    <p>Amount: ${(paymentResult.amount / 100).toFixed(2)}</p>
                )}
                {paymentResult.recipient && (
                    <p>To: {paymentResult.recipient}</p>
                )}
            </div>
        )}

        {/* Instructions */}
        <div className="mt-6 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
                💡 Try saying: "Pay 20 dollars to Starbucks" or "Send 5 dollars to Bob"
            </p>
        </div>
    </div>
    )
}
