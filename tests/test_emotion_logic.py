import unittest

from src.emotion.emotion_logic import EmotionLogic, Emotion, FacialFeatures


class EmotionLogicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logic = EmotionLogic()

    def test_happy_vs_neutral(self):
        happy_features = FacialFeatures(
            mouth_openness=0.02,
            eye_openness=0.03,
            eyebrow_raise=0.0,
            smile_lift=0.02,
        )
        neutral_features = FacialFeatures(
            mouth_openness=0.01,
            eye_openness=0.02,
            eyebrow_raise=0.0,
            smile_lift=0.0,
        )
        self.assertEqual(self.logic.infer_emotion(happy_features), Emotion.HAPPY)
        self.assertEqual(self.logic.infer_emotion(neutral_features), Emotion.NEUTRAL)

    def test_surprised_vs_fear(self):
        surprised_features = FacialFeatures(
            mouth_openness=0.10,
            eye_openness=0.05,
            eyebrow_raise=0.02,
            smile_lift=0.0,
        )
        fear_features = FacialFeatures(
            mouth_openness=0.055,
            eye_openness=0.04,
            eyebrow_raise=0.006,
            smile_lift=0.0,
        )
        self.assertEqual(self.logic.infer_emotion(surprised_features), Emotion.SURPRISED)
        self.assertEqual(self.logic.infer_emotion(fear_features), Emotion.FEAR)

    def test_angry_vs_disgust(self):
        angry_features = FacialFeatures(
            mouth_openness=0.01,
            eye_openness=0.01,
            eyebrow_raise=-0.02,
            smile_lift=0.0,
        )
        disgust_features = FacialFeatures(
            mouth_openness=0.02,
            eye_openness=0.015,
            eyebrow_raise=-0.006,
            smile_lift=0.0,
        )
        self.assertEqual(self.logic.infer_emotion(angry_features), Emotion.ANGRY)
        self.assertEqual(self.logic.infer_emotion(disgust_features), Emotion.DISGUST)

    def test_edge_speech_guard_stays_neutral(self):
        # Mouth is open but no smile lift → should stay NEUTRAL due to speech guard
        speech_like = FacialFeatures(
            mouth_openness=self.logic._mouth_open_happy * 1.3,
            eye_openness=self.logic._eye_open_neutral * 0.9,
            eyebrow_raise=0.0,
            smile_lift=0.0,
        )
        self.assertEqual(self.logic.infer_emotion(speech_like), Emotion.NEUTRAL)


if __name__ == "__main__":
    unittest.main()
