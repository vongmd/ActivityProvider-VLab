from abc import ABC, abstractmethod

# =================================================================
# DADOS MOCK (Configurações e Protocolos)
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
# PADRÃO DE CRIAÇÃO: FACTORY METHOD
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
# ENGINE (Motor de Processamento)
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
    
    # Getters para os dados Mock (para o Facade usar)
    def get_activity_config(self):
        return PROTOCOL_CONFIG_JSON
        
    def get_json_params(self):
        return JSON_PARAMS_URL

    def get_analytics_list(self):
        return ANALYTICS_LIST_JSON