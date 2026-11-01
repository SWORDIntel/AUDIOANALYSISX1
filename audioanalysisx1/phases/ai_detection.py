"""
PHASE 5: AI VOICE DETECTION (DEEPFAKE & SYNTHETIC VOICE DETECTION)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objective: Detect AI-generated voices from TTS, voice cloning, and deepfakes
"""

import math
from numbers import Real

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
        Analyze the first five seconds of audio for AI voice artifacts.

        Only a five-second source prefix is resampled to the feature extractor's
        expected rate, then trimmed to its exact sample limit. This is not a
        whole-recording scan.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            dict: AI detection results
        """
        if isinstance(sr, bool) or not isinstance(sr, Real) or not math.isfinite(sr) or sr <= 0:
            raise ValueError("sr must be a finite, positive sample rate")

        target_sr = getattr(self.feature_extractor, "sampling_rate", 16000)
        if (isinstance(target_sr, bool) or not isinstance(target_sr, Real)
                or not math.isfinite(target_sr) or target_sr <= 0
                or not float(target_sr).is_integer()):
            raise ValueError("Feature extractor sampling_rate must be a positive integer")
        target_sr = int(target_sr)

        # Bound resampling work even when the input recording is very long.
        # Round up for fractional source rates, then enforce the target limit.
        y = y[:math.ceil(5 * sr)]
        if sr != target_sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)

        max_samples = 5 * target_sr
        y = y[:max_samples]
        inputs = self.feature_extractor(
            y, sampling_rate=target_sr, return_tensors="pt", padding=True,
            truncation=True, max_length=max_samples
        )

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

