from record_voc import record_and_recognize

if __name__ == '__main__':
    text = record_and_recognize(duration=5)
    print("最终识别内容：", text)