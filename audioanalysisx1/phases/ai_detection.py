"""
PHASE 5: AI VOICE DETECTION (DEEPFAKE & SYNTHETIC VOICE DETECTION)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objective: Detect AI-generated voices from TTS, voice cloning, and deepfakes
"""

import librosa
import numpy as np
from scipy import stats, signal
from scipy.fft import fft


from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import torch
import numpy as np

class AIVoiceDetector:
    """
    Detects AI-generated voices using a pre-trained model from Hugging Face.
    """

    def __init__(self):
        self.model = AutoModelForAudioClassification.from_pretrained("mo-thecreator/Deepfake-audio-detection")
        self.feature_extractor = AutoFeatureExtractor.from_pretrained("mo-thecreator/Deepfake-audio-detection")

    def analyze(self, y, sr):
        """
        Comprehensive AI voice detection analysis.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            dict: AI detection results
        """
        inputs = self.feature_extractor(y, sampling_rate=16000, return_tensors="pt", padding=True, truncation=True, max_length=5 * 16000)

        with torch.no_grad():
            logits = self.model(**inputs).logits

        scores = torch.nn.functional.softmax(logits, dim=1).tolist()[0]

        predicted_class_id = np.argmax(scores)
        confidence = scores[predicted_class_id]

        ai_detected = self.model.config.id2label[predicted_class_id] == "FAKE"

        return {
            'ai_detected': ai_detected,
            'confidence': float(confidence),
            'ai_type': 'Wav2Vec2' if ai_detected else 'None (Human Voice)'
        }
