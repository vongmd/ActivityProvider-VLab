from flask import Flask, jsonify, render_template, redirect, url_for, request

# Importar as classes dos ficheiros que criaste
from app_engine import ActivityProvider_Engine
from app_facade import ActivityServiceFacade
from handlers import JSONSchemaHandler, AuthHandler, LogicHandler

app = Flask(__name__)

# =================================================================
# INICIALIZAÇÃO DO SISTEMA
# =================================================================

# 1. Instanciar Motor e Facade
engine = ActivityProvider_Engine()
facade = ActivityServiceFacade(engine)

# Inicializar dados do sistema (carregar protocolos)
facade.inicializar_sistema()

# 2. Configurar Chain of Responsibility (Os Seguranças)
schema_handler = JSONSchemaHandler()
auth_handler = AuthHandler()
logic_handler = LogicHandler(facade) # O último elo recebe o facade

# Ligar a corrente: Schema -> Auth -> Logic
schema_handler.set_next(auth_handler).set_next(logic_handler)

# Definir a entrada da corrente
validation_chain = schema_handler

# =================================================================
# ROTAS (CONTROLLERS)
# =================================================================

@app.route('/', methods=['GET'])
def root_route():
    return redirect(url_for('documentation_page'))

@app.route('/documentacao', methods=['GET'])
def documentation_page():
    # Podemos aceder ao engine via facade para mostrar status
    status_msg = "Sistema Ativo. Chain of Responsibility configurada."
    return render_template('index.html', title="Virtual Lab Assistant (AP)", status=status_msg)

@app.route('/configuracao', methods=['GET'])
def get_activity_config():
    """
    Retorna a página de configuração (Authoring Tool).
    """
    config_data = facade.get_config()
    return render_template('config.html', config=config_data)

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
def process_analytics():
    """
    Endpoint principal.
    Usa o CHAIN OF RESPONSIBILITY para validar e processar.
    """
    # 1. Recebe os dados
    data = request.get_json(silent=True) or {}
    
    # 2. Entrega à corrente de validação
    # O Controller não sabe validar, só sabe passar a batata quente.
    response_content, status_code = validation_chain.handle(data)
    
    # 3. Retorna o resultado
    return jsonify(response_content), status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)