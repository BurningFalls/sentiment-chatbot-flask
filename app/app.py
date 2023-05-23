from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import re
import KEY # mykey.py에 openai api key를 입력 후, (import KEY => import mykey)로 변경
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from transformers import TextClassificationPipeline

app = Flask(__name__)
CORS(app)

MODEL_PATH = "burningfalls/my-fine-tuned-bert"

Feel = [
    {"label": "가난한, 불우한", "index": 0},
    {"label": "감사하는", "index": 1},
    {"label": "걱정스러운", "index": 2},
    {"label": "고립된", "index": 3},
    {"label": "괴로워하는", "index": 4},
    {"label": "구역질 나는", "index": 5},
    {"label": "기쁨", "index": 6},
    {"label": "낙담한", "index": 7},
    {"label": "남의 시선을 의식하는", "index": 8},
    {"label": "노여워하는", "index": 9},
    {"label": "눈물이 나는", "index": 10},
    {"label": "느긋", "index": 11},
    {"label": "당혹스러운", "index": 12},
    {"label": "당황", "index": 13},
    {"label": "두려운", "index": 14},
    {"label": "마비된", "index": 15},
    {"label": "만족스러운", "index": 16},
    {"label": "방어적인", "index": 17},
    {"label": "배신당한", "index": 18},
    {"label": "버려진", "index": 19},
    {"label": "부끄러운", "index": 20},
    {"label": "분노", "index": 21},
    {"label": "불안", "index": 22},
    {"label": "비통한", "index": 23},
    {"label": "상처", "index": 24},
    {"label": "성가신", "index": 25},
    {"label": "스트레스 받는", "index": 26},
    {"label": "슬픔", "index": 27},
    {"label": "신뢰하는", "index": 28},
    {"label": "신이 난", "index": 29},
    {"label": "실망한", "index": 30},
    {"label": "악의적인", "index": 31},
    {"label": "안달하는", "index": 32},
    {"label": "안도", "index": 33},
    {"label": "억울한", "index": 34},
    {"label": "열등감", "index": 35},
    {"label": "염세적인", "index": 36},
    {"label": "외로운", "index": 37},
    {"label": "우울한", "index": 38},
    {"label": "자신하는", "index": 39},
    {"label": "조심스러운", "index": 40},
    {"label": "좌절한", "index": 41},
    {"label": "죄책감의", "index": 42},
    {"label": "질투하는", "index": 43},
    {"label": "짜증내는", "index": 44},
    {"label": "초조한", "index": 45},
    {"label": "충격 받은", "index": 46},
    {"label": "취약한", "index": 47},
    {"label": "툴툴대는", "index": 48},
    {"label": "편안한", "index": 49},
    {"label": "한심한", "index": 50},
    {"label": "혐오스러운", "index": 51},
    {"label": "혼란스러운", "index": 52},
    {"label": "환멸을 느끼는", "index": 53},
    {"label": "회의적인", "index": 54},
    {"label": "후회되는", "index": 55},
    {"label": "흥분", "index": 56},
    {"label": "희생된", "index": 57},
]

global text_classifier

model = "gpt-3.5-turbo"
messages = []
messages.append({"role": "system", "content": "친구, 일상대화, 반말"})


# BERT 모델 load
def load_model():
    global text_classifier

    loaded_tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    loaded_model = TFAutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

    text_classifier = TextClassificationPipeline(
        tokenizer=loaded_tokenizer,
        model=loaded_model,
        framework='tf',
        top_k=1
    )


# 서버에서 받은 텍스트 데이터를 BERT 모델로 예측하는 함수
def predict_sentiment(text):
    global text_classifier

    pred = text_classifier(text)[0]
    predicted_label = int(re.sub(r'[^0-9]', '', pred[0]['label']))

    return predicted_label


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    content = data['text']
    feel_idx = predict_sentiment(content)  # bert출력

    # gpt+bert
    feel = Feel[feel_idx]["label"]
    messages.append({"role": "user", "content": content + feel})

    # 감정 문장 생성
    completion = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    chat_response = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": chat_response})

    return jsonify({'result': chat_response})


if __name__ == '__main__':
    load_model()
    app.run()