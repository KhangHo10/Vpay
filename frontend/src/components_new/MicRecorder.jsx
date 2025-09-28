import React, { useState, useRef, useCallback, useEffect } from 'react';

export default function MicRecorder() {
    const [isRecording, setIsRecording] = useState(false);
    const [audioUrl, setAudioUrl] = useState(null);
    const [transcript, setTranscript] = useState('');
    const [paymentAnalysis, setPaymentAnalysis] = useState(null);
    const [voiceAuthentication, setVoiceAuthentication] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [currentStep, setCurrentStep] = useState('payment'); // 'payment' or 'auth'
    const [stepMessage, setStepMessage] = useState('');

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const streamRef = useRef(null);

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        return <div className="p-4 bg-red-100 text-red-800 rounded-lg">"getUserMedia is not supported in this browser."</div>;
    }
    
    const startRecording = useCallback(async () => {
        try {
            if (audioUrl) {
                URL.revokeObjectURL(audioUrl);
                setAudioUrl(null);
            }

            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            streamRef.current = stream;
            audioChunksRef.current = [];

            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            mediaRecorderRef.current = mediaRecorder;

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { 
                    type: 'audio/webm;codecs=opus' 
                });
                
                if (audioUrl) {
                    URL.revokeObjectURL(audioUrl);
                }

                const url = URL.createObjectURL(audioBlob);
                setAudioUrl(url);
                
                await processAudio(audioBlob);
            };

            mediaRecorder.start(100);
            setIsRecording(true);
            
            // Clear previous results when starting new recording
            if (currentStep === 'payment') {
                setTranscript('');
                setPaymentAnalysis(null);
                setVoiceAuthentication(null);
                setStepMessage('');
            }
            
        } catch (error) {
            console.error('Error starting recording:', error);
            alert('Error accessing microphone: ' + error.message);
        }
    }, [audioUrl, currentStep]);

    const stopRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        }
    }, [isRecording]);

    const processAudio = async (audioBlob) => {
        setIsProcessing(true);

        try {
            const arrayBuffer = await audioBlob.arrayBuffer();
            const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
            
            const response = await fetch('http://localhost:8000/process_voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    audio_data: base64Audio,
                    audio_format: 'webm',
                    sample_rate: 16000,
                    step: currentStep
                })
            });

            if (!response.ok) {
                throw new Error('Failed to process audio');
            }

            const result = await response.json();
            console.log('Processing result:', result);

            // Handle results based on current step
            if (currentStep === 'payment') {
                if (result.transcript) {
                    setTranscript(result.transcript);
                }
                
                if (result.payment_analysis) {
                    setPaymentAnalysis(result.payment_analysis);
                }
                
                setStepMessage(result.message);
                
                // Check if we need to proceed to authentication step
                if (result.next_step === 'auth') {
                    setCurrentStep('auth');
                } else if (result.next_step === 'complete') {
                    // Payment command not detected, stay on payment step
                    setCurrentStep('payment');
                }
                
            } else if (currentStep === 'auth') {
                if (result.voice_authentication) {
                    setVoiceAuthentication(result.voice_authentication);
                }
                
                setStepMessage(result.message);
                
                // Reset to payment step for next transaction
                setTimeout(() => {
                    setCurrentStep('payment');
                    setTranscript('');
                    setPaymentAnalysis(null);
                    setVoiceAuthentication(null);
                    setStepMessage('');
                }, 5000); // Reset after 5 seconds
            }

        } catch (error) {
            console.error('Error processing audio:', error);
            setStepMessage('Error: ' + error.message);
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

    const resetToPaymentStep = () => {
        setCurrentStep('payment');
        setTranscript('');
        setPaymentAnalysis(null);
        setVoiceAuthentication(null);
        setStepMessage('');
        if (audioUrl) {
            URL.revokeObjectURL(audioUrl);
            setAudioUrl(null);
        }
    };

    useEffect(() => {
        return () => {
            if (audioUrl) {
                URL.revokeObjectURL(audioUrl);
            }
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, [audioUrl]);

    // Determine button text and style based on current step
    const getButtonConfig = () => {
        if (isProcessing) {
            return {
                text: 'Processing...',
                style: 'bg-gray-500',
                disabled: true
            };
        }
        
        if (isRecording) {
            return {
                text: currentStep === 'payment' ? 'STOP (Payment)' : 'STOP (PIN)',
                style: 'bg-red-500 hover:bg-red-600 animate-pulse',
                disabled: false
            };
        }
        
        if (currentStep === 'payment') {
            return {
                text: 'Record Payment Command',
                style: 'bg-blue-500 hover:bg-blue-600',
                disabled: false
            };
        } else {
            return {
                text: 'Record 5-Digit PIN',
                style: 'bg-green-500 hover:bg-green-600',
                disabled: false
            };
        }
    };

    const buttonConfig = getButtonConfig();

    return (
        <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg">
            <h2 className="text-2xl font-bold text-center mb-6">Voice Payment System</h2>

            {/* Step Indicator */}
            <div className="flex justify-center mb-4">
                <div className="flex items-center space-x-4">
                    <div className={`flex items-center space-x-2 ${currentStep === 'payment' ? 'text-blue-600 font-semibold' : 'text-gray-400'}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep === 'payment' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}>
                            1
                        </div>
                        <span>Payment</span>
                    </div>
                    <div className="w-8 h-px bg-gray-300"></div>
                    <div className={`flex items-center space-x-2 ${currentStep === 'auth' ? 'text-green-600 font-semibold' : 'text-gray-400'}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep === 'auth' ? 'bg-green-500 text-white' : 'bg-gray-200'}`}>
                            2
                        </div>
                        <span>PIN</span>
                    </div>
                </div>
            </div>

            {/* Current Step Instructions */}
            <div className="text-center mb-4 p-3 bg-gray-50 rounded-lg">
                {currentStep === 'payment' ? (
                    <p className="text-sm text-gray-700">
                        <strong>Step 1:</strong> Say your payment command<br/>
                        (e.g., "Pay 20 dollars to Starbucks")
                    </p>
                ) : (
                    <p className="text-sm text-gray-700">
                        <strong>Step 2:</strong> Say your 5-digit PIN<br/>
                        (e.g., "1 2 3 4 5")
                    </p>
                )}
            </div>

            {/* Recording Button */}
            <div className="text-center mb-6">
                <button 
                    onClick={toggleRecording}
                    disabled={buttonConfig.disabled}
                    className={`w-full p-4 rounded-lg text-white font-semibold transition ${buttonConfig.style} ${
                        buttonConfig.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'
                    }`}
                > 
                    {buttonConfig.text}
                </button>
            </div>

            {/* Status Indicator */}
            {isRecording && (
                <div className="text-center mb-4">
                    <div className="inline-flex items-center px-3 py-1 rounded-full bg-red-100 text-red-800">
                        <div className="w-2 h-2 bg-red-500 rounded-full mr-2 animate-pulse"></div>
                        Recording {currentStep === 'payment' ? 'payment command' : '5-digit PIN'}...
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

            {/* Step Message */}
            {stepMessage && (
                <div className={`mb-4 p-3 rounded-lg ${
                    stepMessage.includes('✅') ? 'bg-green-100 text-green-800' :
                    stepMessage.includes('❌') ? 'bg-red-100 text-red-800' :
                    'bg-blue-100 text-blue-800'
                }`}>
                    <p className="font-medium">{stepMessage}</p>
                </div>
            )}

            {/* Transcript Display */}
            {transcript && currentStep === 'payment' && (
                <div className="mb-4 p-3 bg-gray-100 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Transcript:
                    </label>
                    <p className="text-gray-800">{transcript}</p>
                </div>
            )}

            {/* Payment Analysis Display */}
            {paymentAnalysis && paymentAnalysis.has_payment_command && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                    <label className="block text-sm font-medium text-blue-700 mb-1">
                        Payment Details Detected:
                    </label>
                    <div className="text-blue-800 text-sm space-y-1">
                        {paymentAnalysis.payment_details?.action && (
                            <p><strong>Action:</strong> {paymentAnalysis.payment_details.action}</p>
                        )}
                        {paymentAnalysis.payment_details?.amount && (
                            <p><strong>Amount:</strong> ${(paymentAnalysis.payment_details.amount / 100).toFixed(2)}</p>
                        )}
                        {paymentAnalysis.payment_details?.recipient && (
                            <p><strong>Recipient:</strong> {paymentAnalysis.payment_details.recipient}</p>
                        )}
                        {paymentAnalysis.payment_details?.confidence && (
                            <p><strong>Confidence:</strong> {(paymentAnalysis.payment_details.confidence * 100).toFixed(0)}%</p>
                        )}
                    </div>
                </div>
            )}

            {/* Voice Authentication Result */}
            {voiceAuthentication && (
                <div className={`mb-4 p-3 rounded-lg ${
                    voiceAuthentication.authenticated 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                }`}>
                    <label className="block text-sm font-medium mb-1">
                        Authentication Result:
                    </label>
                    <div className="text-sm space-y-1">
                        <p className="font-semibold">
                            {voiceAuthentication.authenticated ? 'Authentication Successful!' : 'Authentication Failed'}
                        </p>
                        {voiceAuthentication.user_card_id && voiceAuthentication.user_card_id !== "0" && (
                            <p><strong>User ID:</strong> {voiceAuthentication.user_card_id}</p>
                        )}
                        {voiceAuthentication.similarity_score && (
                            <p><strong>Voice Match:</strong> {(voiceAuthentication.similarity_score * 100).toFixed(1)}%</p>
                        )}
                        {voiceAuthentication.message && (
                            <p className="mt-2 text-xs">{voiceAuthentication.message}</p>
                        )}
                    </div>
                </div>
            )}

            {/* Reset Button */}
            {(currentStep === 'auth' || voiceAuthentication) && (
                <div className="text-center mb-4">
                    <button 
                        onClick={resetToPaymentStep}
                        className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
                    >
                        Start New Transaction
                    </button>
                </div>
            )}

            {/* Instructions */}
            <div className="mt-6 p-3 bg-yellow-50 rounded-lg">
                <p className="text-sm text-yellow-800">
                    <strong>How it works:</strong>
                </p>
                <ol className="text-sm text-yellow-800 mt-2 space-y-1">
                    <li>1. Record payment command: "Pay 20 dollars to Starbucks"</li>
                    <li>2. If payment detected, record your 5-digit PIN: "1 2 3 4 5"</li>
                    <li>3. System will authenticate your voice and PIN</li>
                </ol>
            </div>

            {/* Current Status Summary */}
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-600">
                    <strong>Status:</strong> {
                        currentStep === 'payment' ? 'Waiting for payment command' :
                        currentStep === 'auth' ? 'Waiting for authentication PIN' :
                        'Ready for new transaction'
                    }
                </p>
                {paymentAnalysis?.has_payment_command && (
                    <p className="text-xs text-gray-600 mt-1">
                        Payment detected: {paymentAnalysis.payment_details?.action || 'Unknown'} 
                        {paymentAnalysis.payment_details?.amount && 
                            ` ${(paymentAnalysis.payment_details.amount / 100).toFixed(2)}`
                        }
                        {paymentAnalysis.payment_details?.recipient && 
                            ` to ${paymentAnalysis.payment_details.recipient}`
                        }
                    </p>
                )}
                {voiceAuthentication?.authenticated && (
                    <p className="text-xs text-green-600 mt-1">
                        Transaction completed successfully!
                    </p>
                )}
            </div>
        </div>
    )
}