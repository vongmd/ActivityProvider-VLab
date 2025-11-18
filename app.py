from flask import Flask, jsonify

app = Flask(__name__)

# =================================================================
# DADOS DE EXEMPLO DO ACTIVITY PROVIDER: "Virtual Lab Assistant"
# =================================================================

# 1. Endpoint: /json_params_url (Parâmetros de Configuração)
# Formato que a Inven!RA espera para listar os parâmetros configuráveis.
JSON_PARAMS_URL = [
    {
        "name": "protocolo_config_json", 
        "type": "application/json"      
    }
]

# 2. Endpoint: /configuracao (Conteúdo de 'protocolo_config_json')
# Simula o JSON que o Formador usa para definir o protocolo laboratorial.
PROTOCOL_CONFIG_JSON = {
    "activity_title": "Titulacao de NaOH com HC1",
    "virtual_equipment": [
        "pipette_25ml",
        "burette_50ml",
        "erlenmeyer_flask"
    ],
    "protocol_steps": [
        {
            "id": "step1",
            "description": "Lavar a bureta com a solucao titulante.",
            "validation_rule": {
                "action": "rinse",
                "with": "titrant_solution"
            }
        },
        {
            "id": "step2",
            "description": "Pipetor 25ml da solucao titulada.",
            "validation_rule": {
                "action": "transfer_volume",
                "equipment": "pipette_25ml",
                "volume_ml": 25.0,
                "tolerance": 0.5
            }
        }
    ],
    "final_evaluation": {
        "target_analytic": "final_measurement_value",
        "expected_value": 22.5,
        "tolerance_percent": 2.0
    }
}

# 3. Endpoint: /analytics_list_url (Analytics Disponíveis)
# Lista dos dados analíticos que o seu módulo é capaz de fornecer (quantitativos e qualitativos).
ANALYTICS_LIST_JSON = {
    "quantAnalytics": [
        {"name": "protocol_errors_count", "type": "integer"},
        {"name": "steps_completed_in_order", "type": "integer"},
        {"name": "time_elapsed_seconds", "type": "integer"},
        {"name": "final_measurement_value", "type": "number"},
        {"name": "measurement_accuracy_error_percent", "type": "percentage"}
    ],
    "qualAnalytics": [
        {"name": "current_step_id", "type": "text/plain"},
        {"name": "last_error_code", "type": "text/plain"}
    ]
}

# 4. JSON de Dados Analíticos Atuais (Resposta de /analytics_url - GET)
# Simula um estado atual da atividade para a Inven!RA puxar (pull).
CURRENT_ANALYTICS_DATA = {
    "activity_instance_id": "INST_001",
    "data": {
        "protocol_errors_count": 3,
        "steps_completed_in_order": 1,
        "time_elapsed_seconds": 185,
        "current_step_id": "step2",
        "last_error_code": "WRONG_CHEMICAL_TRANSFER"
    }
}

# =================================================================
# IMPLEMENTAÇÃO DOS 5 WEB SERVICES RESTFUL (Endpoints)
# =================================================================

# 1. Parâmetros de Configuração (URL Fixo: json_params_url)
@app.route('/json_params_url', methods=['GET'])
def get_config_params():
    return jsonify(JSON_PARAMS_URL)

# 2. Configuração da Atividade (URL Fixo: configuracao)
@app.route('/configuracao', methods=['GET'])
def get_activity_config():
    return jsonify(PROTOCOL_CONFIG_JSON)

# 3. Analytics Disponíveis (URL Fixo: analytics_list_url)
@app.route('/analytics_list_url', methods=['GET'])
def get_analytics_list():
    return jsonify(ANALYTICS_LIST_JSON)

# 4. Pedido de Analytics (URL Fixo: analytics_url - GET)
@app.route('/analytics_url', methods=['GET'])
def get_current_analytics():
    return jsonify(CURRENT_ANALYTICS_DATA)

# 5. Deploy (URL Fixo: deploy_url)
@app.route('/deploy_url', methods=['GET'])
def deploy_status():
    return jsonify({"status": "ready", "module_name": "Virtual Lab Assistant", "api_version": "1.0"})


if __name__ == '__main__':
    # Execução local na porta padrão 5000.
    app.run(debug=True, port=5000)