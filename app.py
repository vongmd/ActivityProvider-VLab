from flask import Flask, jsonify, render_template, redirect, url_for, request
from abc import ABC, abstractmethod
from dataclasses import dataclass

app = Flask(__name__)

# =================================================================
# PADRÃO DE CRIAÇÃO: FACTORY METHOD (Mantido igual)
# =================================================================

class ValidationRule(ABC):
    @abstractmethod
    def validate(self, user_action):
        pass

class RinseRule(ValidationRule):
    def __init__(self, target_liquid):
        self.target_liquid = target_liquid

    def validate(self, user_action):
        return user_action.get('action') == 'rinse' and \
               user_action.get('with') == self.target_liquid

class TransferVolumeRule(ValidationRule):
    def __init__(self, equipment, volume, tolerance):
        self.equipment = equipment
        self.target_volume = volume
        self.tolerance = tolerance

    def validate(self, user_action):
        if user_action.get('action') != 'transfer_volume':
            return False
        if user_action.get('equipment') != self.equipment:
            return False
        vol = user_action.get('volume_ml', 0)
        return abs(vol - self.target_volume) <= self.tolerance

class RuleFactory:
    @staticmethod
    def create_rule(rule_data):
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
            raise ValueError(f"Tipo de regra desconhecido: {action_type}")

# =================================================================
# ENGINE (Mantido igual)
# =================================================================

class ActivityProvider_Engine:
    def __init__(self):
        self.active_rules = {} 

    def carregar_protocolo(self, json_config):
        self.active_rules.clear()
        steps = json_config.get('protocol_steps', [])
        print(f"--- ENGINE: A carregar {len(steps)} passos ---")
        for step in steps:
            rule_data = step.get('validation_rule')
            step_id = step.get('id')
            try:
                rule_object = RuleFactory.create_rule(rule_data)
                self.active_rules[step_id] = rule_object
                print(f"Passo {step_id}: Regra '{type(rule_object).__name__}' criada com sucesso.")
            except Exception as e:
                print(f"Erro ao criar regra para {step_id}: {e}")

    def processar_evento(self, step_id, user_action):
        rule = self.active_rules.get(step_id)
        if rule:
            return rule.validate(user_action)
        return False

# =================================================================
# DADOS MOCK (Mantido igual)
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
# NOVO PADRÃO: FACADE (Mantido igual)
# =================================================================

@dataclass
class DeployStatus:
    status: str
    access_url: str

class ResponseBuilder:
    """Helper para formatar respostas complexas de Analytics"""
    @staticmethod
    def build_analytics(activity_id: str):
        return [
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

class ActivityServiceFacade:
    """
    FACADE: Interface unificada para o Activity Provider.
    """
    def __init__(self, engine: ActivityProvider_Engine):
        self.engine = engine

    def get_config(self):
        return PROTOCOL_CONFIG_JSON

    def get_json_params(self):
        return JSON_PARAMS_URL

    def get_deploy_status(self) -> DeployStatus:
        return DeployStatus(status="ready", access_url="https://activityprovider-vlab.onrender.com/lab")

    def get_analytics_list(self):
        return ANALYTICS_LIST_JSON

    def get_analytics_data(self, activity_id: str):
        return ResponseBuilder.build_analytics(activity_id)

    def inicializar_sistema(self):
        self.engine.carregar_protocolo(PROTOCOL_CONFIG_JSON)

# =================================================================
# INICIALIZAÇÃO
# =================================================================

engine = ActivityProvider_Engine()
facade = ActivityServiceFacade(engine)
facade.inicializar_sistema()

# =================================================================
# ROTAS FLASK
# =================================================================

@app.route('/', methods=['GET'])
def root_route():
    return redirect(url_for('documentation_page'))

@app.route('/documentacao', methods=['GET'])
def documentation_page():
    status_msg = f"Factory Method & Facade Ativos. Regras carregadas: {len(engine.active_rules)}"
    return render_template('index.html', title="Virtual Lab Assistant (AP)", status=status_msg)

# --- AQUI ESTÁ A CORREÇÃO SOLICITADA PELO PROFESSOR ---
@app.route('/configuracao', methods=['GET'])
def get_activity_config():
    """
    Retorna uma PÁGINA HTML (Authoring Tool) em vez de JSON cru.
    O Facade fornece os dados, o Flask renderiza o HTML.
    """
    config_data = facade.get_config()
    return render_template('config.html', config=config_data)
# ------------------------------------------------------

@app.route('/json_params_url', methods=['GET'])
def get_config_params():
    return jsonify(facade.get_json_params())

@app.route('/deploy_url', methods=['GET'])
def deploy_status():
    ds = facade.get_deploy_status()
    return jsonify({"status": ds.status, "access_url": ds.access_url})

@app.route('/analytics_list_url', methods=['GET'])
def get_analytics_list():
    return jsonify(facade.get_analytics_list())

@app.route('/analytics_url', methods=['POST'])
def get_activity_analytics():
    data = request.get_json(silent=True)
    activity_id = data.get('activityID', "unknown") if data else "unknown"
    result = facade.get_analytics_data(activity_id)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)