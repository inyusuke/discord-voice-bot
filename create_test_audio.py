import wave
import struct
import math

# 簡単なテスト用WAVファイルを作成
def create_test_wav(filename="test_audio.wav", duration=2, frequency=440):
    """
    テスト用のWAVファイル（A音 440Hz）を作成
    """
    sample_rate = 44100
    num_samples = duration * sample_rate
    
    with wave.open(filename, 'w') as wav_file:
        # WAVファイルのパラメータを設定
        wav_file.setnchannels(1)  # モノラル
        wav_file.setsampwidth(2)   # 16ビット
        wav_file.setframerate(sample_rate)
        
        # サイン波を生成
        for i in range(num_samples):
            # A音（440Hz）のサイン波
            value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            # 16ビット整数として書き込み
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)
    
    print(f"テスト用音声ファイル '{filename}' を作成しました（{duration}秒、{frequency}Hz）")
    return filename

if __name__ == "__main__":
    create_test_wav()