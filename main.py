import json

from flask import Flask, jsonify, request
from services.OpenAIService import OpenAIService
from services.SerAPIService import SerpAPIService

app = Flask(__name__)

openAiService = OpenAIService()
serpService = SerpAPIService()

@app.route('/', methods=['POST'])
def question_process():
    if request.is_json:
      data = request.get_json()
      question = data.get('question')
      print(f"User Question: {question}")
      if not question:
       return jsonify({'response': 'Lack of question'}), 400

      try:
        response = openAiService.send_message_to_llm_with_return_json_object(question)
        system_prompt="""
          Behave like a categorizer which split information into two categories.
          Always return in json property "type" with value "question" or "information" depend on the user message.
          If user ask question then return type "question" if user pass information the return "information"
          never answer on question!

          ###Example
          User: "Powiedz mi jak to jest być LLMem, dobrze czy nie dobrze"
          Answer: {"type": "question"}
          User: "Kocham grać w nogę po pracy w piątek"
          Answer: {"type": "information"}
        """
        response_type = openAiService.send_message_to_llm_with_return_json_object(question, system_prompt)
        question_content = json.loads(response_type).get("type", "")
        if question_content:
           openAiService.extend_system_prompt_context(question)
      except Exception as ex:
         return jsonify({'response','Error with processing LLM requests'}), 400

      print(f"RESPONSE FOR USER: {response}\nRESPONSE FOR CONTENT: {question_content}")
      return jsonify(json.loads(response)), 200   
    
    return jsonify({'response': 'Request is not JSON'}), 400

@app.route('/google', methods=['POST'])
def find_url():
  if request.is_json:
    data = request.get_json()
    question = data.get('question')
    print(f"User Question: {question}")
    if not question:
      return jsonify({'response': 'Lack of question'}), 400

    try:
      system_prompt="""
        Do not ANSWER user question, data! Transfer user prompt into webbrowser search input question! 
      """
      transfered_question = openAiService.send_message_to_llm(question, system_prompt)
      
      url = serpService.get_google_data(transfered_question)
      response = {"reply": url}
    except Exception as ex:
        return jsonify({'response','Error with processing LLM requests'}), 400

    print(f"RESPONSE FOR USER: {response}\n, QUESTION TO ASK: {question}. RESPONSE FOR CONTENT: {url}")
    return jsonify(response), 200   
  
  return jsonify({'response': 'Request is not JSON'}), 400
        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
