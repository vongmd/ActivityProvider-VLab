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
# ENGINE (O Motor Central que usa a Fábrica)
# =================================================================

class ActivityProvider_Engine:
    def __init__(self):
        # Mapeamento: step_id -> Objeto ValidationRule
        self.active_rules = {} 

    def carregar_protocolo(self, json_config):
        """
        Lê o JSON e usa a FACTORY para criar os objetos reais.
        """
        self.active_rules.clear()
        steps = json_config.get('protocol_steps', [])
        
        print(f"--- ENGINE: A carregar {len(steps)} passos ---")
        for step in steps:
            rule_data = step.get('validation_rule')
            step_id = step.get('id')
            
            # AQUI: O Motor usa a Fábrica (Factory Method) para obter o objeto
            try:
                rule_object = RuleFactory.create_rule(rule_data)
                self.active_rules[step_id] = rule_object
                print(f"Passo {step_id}: Regra '{type(rule_object).__name__}' criada com sucesso.")
            except Exception as e:
                print(f"Erro ao criar regra para {step_id}: {e}")

    def processar_evento(self, step_id, user_action):
        """
        Delega a validação para o objeto de regra correto.
        (Preparado para uso futuro quando a rota de eventos for implementada)
        """
        rule = self.active_rules.get(step_id)
        if rule:
            return rule.validate(user_action)
        return False

# =================================================================
# DADOS MOCK (Simulação de Base de Dados / Configuração)
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
# INICIALIZAÇÃO DO SISTEMA
# =================================================================

# Instanciamos o motor globalmente
engine = ActivityProvider_Engine()

# Carregamos a configuração inicial no arranque
# Isto garante que as regras são criadas via Factory assim que o servidor liga
engine.carregar_protocolo(PROTOCOL_CONFIG_JSON)

# =================================================================
# ROTAS DA API (Web Services Inven!RA)
# =================================================================

@app.route('/', methods=['GET'])
def root_route():
    return redirect(url_for('documentation_page'))

@app.route('/documentacao', methods=['GET'])
def documentation_page():
    # Mostra o estado do motor (quantas regras foram criadas pela Factory)
    status_msg = f"Factory Method Ativo: {len(engine.active_rules)} regras de validação carregadas no Engine."
    return render_template('index.html', title="Virtual Lab Assistant (AP)", status=status_msg)

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
    return jsonify({"status": "ready", "access_url": "https://activityprovider-vlab.onrender.com/lab"})

# 4. Analytics List (GET)
@app.route('/analytics_list_url', methods=['GET'])
def get_analytics_list():
    return jsonify(ANALYTICS_LIST_JSON)

# 5. Analytics Data (POST ESTRITO - Conforme Especificação)
@app.route('/analytics_url', methods=['POST'])
def get_activity_analytics():
    """
    Recebe um POST com {"activityID": "..."}
    Retorna analíticos de todos os alunos.
    """
    # Tenta ler o JSON enviado pela Inven!RA
    data = request.get_json(silent=True)
    activity_id = data.get('activityID', "unknown") if data else "unknown"
    
    # Simulação de resposta conforme especificação
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