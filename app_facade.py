from dataclasses import dataclass

# =================================================================
# ESTRUTURAS AUXILIARES
# =================================================================

@dataclass
class DeployStatus:
    status: str
    access_url: str

class ResponseBuilder:
    """Helper para formatar respostas complexas de Analytics"""
    @staticmethod
    def build_analytics(activity_id: str, student_id: str):
        # Gera uma resposta simulada baseada no ID da atividade e do aluno
        return {
             "inveniraStdID": student_id,
             "qualAnalytics": [
                 {"student_activity_profile": f"https://meu-ap.com/report?user={student_id}&act={activity_id}"}
             ],
             "quantAnalytics": [
                 {"name": "protocol_errors_count", "value": 0},
                 {"name": "final_measurement_value", "value": 22.5}
             ]
        }

# =================================================================
# FACADE
# =================================================================

class ActivityServiceFacade:
    """
    FACADE: Interface unificada para o Activity Provider.
    """
    def __init__(self, engine):
        self.engine = engine

    # --- Métodos de Leitura (Delegam no Engine) ---
    def get_config(self):
        return self.engine.get_activity_config()

    def get_json_params(self):
        return self.engine.get_json_params()

    def get_deploy_status(self) -> DeployStatus:
        return DeployStatus(status="ready", access_url="https://activityprovider-vlab.onrender.com/lab")

    def get_analytics_list(self):
        return self.engine.get_analytics_list()

    def inicializar_sistema(self):
        # Carrega a configuração inicial no motor
        config = self.engine.get_activity_config()
        self.engine.carregar_protocolo(config)

    # --- MÉTODO USADO PELO CHAIN OF RESPONSIBILITY ---
    def process_activity(self, request_data):
        """
        Recebe os dados validados pelos Handlers e coordena a resposta.
        """
        activity_id = request_data.get('activityID', 'unknown')
        student_id = request_data.get('Inven!RAstdID', 'unknown')
        
        # Aqui poderias chamar self.engine.processar_evento() se quisesses validar regras reais.
        # Para cumprir o requisito de devolver o JSON de analytics:
        return ResponseBuilder.build_analytics(activity_id, student_id)