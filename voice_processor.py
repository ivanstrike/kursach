import speech_recognition as sr
import pydub
from gtts import gTTS
import io
import os
import tempfile
from typing import Optional, Tuple

class VoiceProcessor:
    def __init__(self, language='ru'):
        self.language = language
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

    def recognize_speech_from_audio(self, audio_data: bytes, input_format: str = 'ogg') -> Tuple[Optional[str], str]:
        try:
            if input_format != 'wav':
                wav_data = self.convert_audio_format(audio_data, input_format, 'wav')
                if not wav_data:
                    return None, "Ошибка конвертации аудио в WAV. Проверьте формат файла."
            else:
                wav_data = audio_data

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(wav_data)
                tmp_file_path = tmp_file.name

            try:
                with sr.AudioFile(tmp_file_path) as source:
                    audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language=self.language)
                return text, "success"
            except sr.UnknownValueError:
                return None, "Не удалось распознать речь"
            except sr.RequestError as e:
                return None, f"Ошибка сервиса распознавания речи: {e}"
            finally:
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
        except Exception as e:
            return None, f"Ошибка обработки аудио: {e}"


    def text_to_speech(self, text: str) -> Tuple[Optional[bytes], str]:
        """Преобразование текста в речь"""
        if not text or not text.strip():
            return None, "Пустой текст"

        try:
            tts = gTTS(text=text, lang=self.language, slow=False)

            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)

            return mp3_fp.read(), "success"

        except Exception as e:
            return None, f"Ошибка синтеза речи: {e}"

    def convert_audio_format(self, audio_data: bytes, input_format: str, output_format: str = 'wav') -> Optional[bytes]:
        try:
            with tempfile.NamedTemporaryFile(suffix=f'.{input_format}', delete=False) as input_file:
                input_file.write(audio_data)
                input_file_path = input_file.name

            audio = pydub.AudioSegment.from_file(input_file_path, format=input_format)

            with tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False) as output_file:
                output_file_path = output_file.name

            audio.export(output_file_path, format=output_format)

            with open(output_file_path, 'rb') as f:
                result = f.read()

            os.unlink(input_file_path)
            os.unlink(output_file_path)

            return result

        except Exception as e:
            print(f"Ошибка конвертации аудио: {e}")
            return None

    def save_audio_to_file(self, audio_data: bytes, filename: str, format: str = 'mp3') -> bool:
        try:
            with open(filename, 'wb') as f:
                f.write(audio_data)
            return True
        except Exception as e:
            print(f"Ошибка сохранения аудио: {e}")
            return False

    def get_audio_duration(self, audio_data: bytes, format: str = 'mp3') -> Optional[float]:
        try:
            with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name

            try:
                audio = pydub.AudioSegment.from_file(tmp_file_path, format=format)
                duration = len(audio) / 1000.0
                return duration
            finally:
                os.unlink(tmp_file_path)

        except Exception as e:
            print(f"Ошибка получения длительности аудио: {e}")
            return None
