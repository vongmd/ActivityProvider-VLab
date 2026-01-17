from abc import ABC, abstractmethod

# =================================================================
# PADRÃO COMPORTAMENTAL: CHAIN OF RESPONSIBILITY
# =================================================================

class Handler(ABC):
    """
    Interface (Handler) que define o comportamento da corrente.
    """
    _next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler 

    @abstractmethod
    def handle(self, request_data):
        if self._next_handler:
            return self._next_handler.handle(request_data)
        
        # SEGURANÇA: Se chegámos ao fim da linha e ninguém tratou o pedido,
        # retornamos um erro 500 explícito para não quebrar o 'unpack' no controller.
        return {
            "status": "error", 
            "message": "Server Configuration Error: Request fell off the chain."
        }, 500

# --- ELO 1: Validação Técnica ---
class JSONSchemaHandler(Handler):
    def handle(self, request_data):
        # Validação: Campos obrigatórios
        required_fields = ['activityID', 'Inven!RAstdID', 'json_params']
        
        for field in required_fields:
            if field not in request_data:
                return {
                    "status": "error", 
                    "message": f"Bad Request: Missing field '{field}'"
                }, 400
        
        return super().handle(request_data)

# --- ELO 2: Validação de Segurança ---
class AuthHandler(Handler): 
    # Nome 'AuthHandler' corresponde ao Diagrama
    def handle(self, request_data):
        user_id = request_data.get('Inven!RAstdID', '')
        
        # Validação simples
        if not user_id or len(user_id) < 3:
            return {
                "status": "error", 
                "message": "Unauthorized: Invalid Student ID"
            }, 401
            
        return super().handle(request_data)

# --- ELO 3: Lógica de Negócio ---
class LogicHandler(Handler): 
    # Nome 'LogicHandler' corresponde ao Diagrama
    def __init__(self, facade_instance):
        self.facade = facade_instance

    def handle(self, request_data):
        # Agora chama o método process_activity que acabámos de criar no Facade
        result = self.facade.process_activity(request_data)
        
        # Retorna sempre 200 se a lógica passar (requisito Inven!RA)
        return result, 200