from flask import Flask, jsonify, render_template, redirect, url_for, request
from abc import ABC, abstractmethod

app = Flask(__name__)

# =================================================================
# PADRÃO DE CRIAÇÃO: FACTORY METHOD (Semanas 2-3)
# =================================================================

# 1. Product Interface (A Abstração)
class ValidationRule(ABC):
    @abstractmethod
    def validate(self, user_action):
        """Valida a ação do utilizador contra a regra."""
        pass

# 2. Concrete Products (As Implementações Específicas)
class RinseRule(ValidationRule):
    def __init__(self, target_liquid):
        self.target_liquid = target_liquid

    def validate(self, user_action):
        # Lógica: Ação tem de ser 'rinse' e com o líquido correto
        return user_action.get('action') == 'rinse' and \
               user_action.get('with') == self.target_liquid

class TransferVolumeRule(ValidationRule):
    def __init__(self, equipment, volume, tolerance):
        self.equipment = equipment
        self.target_volume = volume
        self.tolerance = tolerance

    def validate(self, user_action):
        # Lógica: Equipamento certo, ação certa, volume dentro da tolerância
        if user_action.get('action') != 'transfer_volume':
            return False
        if user_action.get('equipment') != self.equipment:
            return False
        
        vol = user_action.get('volume_ml', 0)
        return abs(vol - self.target_volume) <= self.tolerance

# 3. Creator / Factory (A Fábrica)
class RuleFactory:
    @staticmethod
    def create_rule(rule_data):
        """
        Método Fábrica Parametrizado: Decide qual classe instanciar
        baseado no conteúdo do JSON (rule_data).
        """
        action_type = rule_data.get('action')
        
        if action_type == 'rinse':
            return RinseRule(rule_data.get('with'))
        
        elif action_type == 'transfer_volume':
            return TransferVolumeRule(
                equipment=rule_data.get('equipment'),
                volume=rule_data.get('volume_ml'),
                tolerance=rule_data.get('tolerance')
            )
        
        else:
            # Em produção, poderíamos logar um aviso ou levantar exceção
            raise ValueError(f"Tipo de regra desconhecido: {action_type}")

# =================================================================
# DADOS MOCK (Simulação de Base de Dados)
# =================================================================

JSON_PARAMS_URL = [ {"name": "protocolo_config_json", "type": "application/json"} ]

PROTOCOL_CONFIG_JSON = {
    "activity_title": "Titulacao de NaOH com HCl",
    "protocol_steps": [
        {
            "id": "step1", 
            "description": "Lavar a bureta", 
            "validation_rule": {"action": "rinse", "with": "titrant_solution"}
        },
        {
            "id": "step2", 
            "description": "Pipetar 25ml", 
            "validation_rule": {"action": "transfer_volume", "equipment": "pipette_25ml", "volume_ml": 25.0, "tolerance": 0.5}
        }
    ]
}

ANALYTICS_LIST_JSON = {
    "quantAnalytics": [
        {"name": "protocol_errors_count", "type": "integer"}, 
        {"name": "final_measurement_value", "type": "number"}
    ],
    "qualAnalytics": [
        {"name": "student_activity_profile", "type": "link"}
    ]
}

# =================================================================
# ROTAS DA API (Implementação dos Requisitos Inven!RA)
# =================================================================

@app.route('/', methods=['GET'])
def root_route():
    return redirect(url_for('documentation_page'))

@app.route('/documentacao', methods=['GET'])
def documentation_page():
    # Inicializa a Fábrica apenas para demonstrar no log/consola que está a funcionar
    print("--- VIRTUAL LAB: A carregar regras via Factory Method ---")
    try:
        for step in PROTOCOL_CONFIG_JSON['protocol_steps']:
            rule = RuleFactory.create_rule(step['validation_rule'])
            print(f"Regra criada: {type(rule).__name__}")
    except Exception as e:
        print(f"Erro na fábrica: {e}")
        
    return render_template('index.html', 
                           title="Virtual Lab Assistant (AP)", 
                           status="Factory Method Active & Ready")

# 1. Configuração (GET)
@app.route('/configuracao', methods=['GET'])
def get_activity_config():
    return jsonify(PROTOCOL_CONFIG_JSON)

# 2. Parâmetros (GET)
@app.route('/json_params_url', methods=['GET'])
def get_config_params():
    return jsonify(JSON_PARAMS_URL)

# 3. Deploy (GET)
@app.route('/deploy_url', methods=['GET'])
def deploy_status():
    # Recebe user_url?id=... (conforme requisito)
    return jsonify({"status": "ready", "access_url": "https://virtual-lab-assistant.herokuapp.com/lab"})

# 4. Analytics List (GET)
@app.route('/analytics_list_url', methods=['GET'])
def get_analytics_list():
    return jsonify(ANALYTICS_LIST_JSON)

# 5. Analytics Data (CORRIGIDO: POST em vez de GET)
@app.route('/analytics_url', methods=['POST'])
def get_activity_analytics():
    """
    Recebe um POST com {"activityID": "..."}
    Retorna analíticos de todos os alunos.
    """
    data = request.get_json()
    activity_id = data.get('activityID') if data else "unknown"
    
    # Simulação de resposta conforme especificação (ponto 4 do documento de requisitos)
    mock_analytics_response = [
        {
            "inveniraStdID": 1001,
            "quantAnalytics": [
                {"name": "protocol_errors_count", "value": 2},
                {"name": "final_measurement_value", "value": 22.4}
            ],
            "qualAnalytics": [
                {"student_activity_profile": f"https://meu-ap.com/report?user=1001&act={activity_id}"}
            ]
        },
        {
            "inveniraStdID": 1002,
            "quantAnalytics": [
                {"name": "protocol_errors_count", "value": 0},
                {"name": "final_measurement_value", "value": 22.5}
            ],
            "qualAnalytics": [
                {"student_activity_profile": f"https://meu-ap.com/report?user=1002&act={activity_id}"}
            ]
        }
    ]
    return jsonify(mock_analytics_response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)