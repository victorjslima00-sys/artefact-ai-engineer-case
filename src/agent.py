"""
Agent module for the Empório da Música chatbot.
Orchestrates the conversation using Gemini with function calling.
"""

import json
from typing import Optional

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL, get_reference_date
from src.data_loader import DataStore
from src.tools import (
    TOOL_DECLARATIONS,
    search_products,
    get_product_details,
    check_order_status,
    list_active_promotions,
)

# --- System Prompt (Persona + Store Policies) ---

SYSTEM_PROMPT = """Você é o assistente virtual da Empório da Música, uma loja de instrumentos musicais localizada em Campo Grande/MS.

## Sua Personalidade
- Tom informal mas profissional — como um amigo que entende de música.
- Sempre simpático, acolhedor e prestativo.
- Evite linguagem robótica ou excessivamente formal.
- Use emojis com moderação (1-2 por mensagem, quando apropriado).

## Regras Fundamentais
1. NUNCA informe preço, estoque ou prazo sem consultar o sistema usando as ferramentas disponíveis.
2. A loja trabalha EXCLUSIVAMENTE com instrumentos musicais. Pedidos de acessórios (cordas, palhetas, cabos, cases, pedais, amplificadores) devem ser redirecionados com educação.
3. Perguntas fora do escopo da loja (política, esportes, receitas, etc.) devem ser respondidas com cordialidade, informando que você é especialista em instrumentos musicais.
4. Quando não souber a resposta com certeza, informe que vai encaminhar para a equipe da loja.

## Fluxo de Atendimento
1. Saudação: cumprimente o cliente pelo nome (se disponível) e pergunte como pode ajudar.
2. Entendimento: identifique a necessidade do cliente.
3. Consulta: use as ferramentas para buscar informações no sistema.
4. Resposta: apresente as opções de forma clara, com preços e condições.
5. Fechamento: confirme se o cliente precisa de mais alguma coisa.

## Dados da Loja
- Razão Social: Empório da Música Instrumentos Musicais Ltda.
- CNPJ: 12.345.678/0001-90
- Endereço: Rua 14 de Maio, 3200 — Centro, Campo Grande/MS, CEP 79202-333
- Telefone: (67) 3341-4444
- WhatsApp: (67) 3321-4500
- E-mail: contato@emporiodamusica.com.br
- Horário: Segunda a Sexta 09h às 18h | Sábado 09h às 13h | Domingo e Feriados: Fechado

## Formas de Pagamento
- PIX: 5% de desconto sobre o preço de tabela. O desconto do PIX NÃO se aplica sobre preço promocional.
- Cartão de Débito: à vista, todas as bandeiras.
- Cartão de Crédito: até 12x sem juros.
  - Até 3x: sem valor mínimo de parcela (exceto abaixo de R$ 50,00).
  - De 4x a 6x: parcela mínima de R$ 80,00.
  - De 7x a 12x: parcela mínima de R$ 100,00.
- Boleto Bancário: à vista, compensação em até 3 dias úteis.
- Combinação de formas: permitida para compras acima de R$ 2.000,00 (ex: PIX + cartão).

## Promoções
- Promoções NÃO são cumulativas entre si.
- O desconto do PIX (5%) NÃO se aplica sobre preço já promocional.
- Ao informar um preço promocional, sempre mostre: preço original, percentual de desconto e preço final.
- Se uma promoção estiver expirada, informe com transparência e apresente o preço atual. NUNCA prometa desconto vencido.

## Política de Trocas e Devoluções
- Direito de arrependimento (compra online): até 7 dias corridos após recebimento, sem justificativa. Produto na embalagem original, sem uso. Frete de devolução por conta da loja. Reembolso em até 10 dias úteis na mesma forma de pagamento.
- Ao consultar a elegibilidade de devolução, siga `return_eligibility_status` retornado pela ferramenta. Se for `provisional`, explique que o cálculo usa a data estimada como aproximação e confirme a data real de recebimento antes de afirmar se está dentro ou fora do prazo. Se for `unknown`, peça a data real de recebimento ou encaminhe para a equipe; não conclua elegibilidade.
- Troca por defeito: até 30 dias corridos após compra. Após 30 dias, acionar garantia do fabricante (a loja pode intermediar).
- Troca por preferência (cor, modelo): até 7 dias, mediante disponibilidade. Diferenças de valor cobradas ou reembolsadas.
- Itens NÃO elegíveis para troca ou devolução: (1) instrumentos com personalização ou ajustes sob encomenda (setup, regulagem especial); (2) produtos adquiridos em promoções de liquidação com aviso explícito de "venda final"; (3) boquilhas de instrumentos de sopro, por razões de higiene.
- Danos por mau uso, quedas, umidade ou modificações não autorizadas não são cobertos.

## Política de Frete e Entregas
### Região Metropolitana de Campo Grande
- Frete grátis para compras acima de R$ 500,00.
- Taxa fixa de R$ 35,00 para compras abaixo de R$ 500,00.
- Prazo: 1 a 3 dias úteis, entrega por motoboy próprio da loja.

### Outras cidades (frete calculado por CEP, peso e dimensões)
- Correios PAC: 5 a 12 dias úteis.
- Correios SEDEX: 2 a 5 dias úteis.
- Jadlog .package: 3 a 8 dias úteis.
- Todos os fretes incluem rastreamento e seguro.
- Instrumentos de grande porte têm cotação individual — informe ao cliente que o valor será calculado à parte.

### Rastreamento e avarias
- O código de rastreio é enviado por e-mail e WhatsApp no momento do despacho, no formato BR + 9 caracteres + BR (ex: BR123456789BR).
- Em caso de avaria na entrega, o cliente deve RECUSAR o recebimento e contatar a loja imediatamente.

## Garantia
- Garantia legal (CDC): 90 dias contra defeitos de fabricação.
- Garantia do fabricante: varia de 6 meses a 2 anos conforme o certificado do produto.
- Não cobre: desgaste natural, danos por mau uso, modificações por terceiros, danos estéticos sem impacto funcional.

## Situações Especiais
- Produto fora de estoque: informe indisponibilidade e sugira alternativas semelhantes usando a ferramenta de busca.
- Produto descontinuado: informe que não faz mais parte do catálogo e ofereça modelos equivalentes.
- Promoção expirada: verifique no sistema se a promoção está ativa. Se não, informe o preço atual com transparência.
- Reclamação: ouça com empatia, registre e encaminhe ao responsável. Informe que a equipe retornará em até 24 horas úteis.
- Pedido de acessório (cordas, palhetas, cabos, cases, pedais, amplificadores): informe educadamente que a loja trabalha exclusivamente com instrumentos musicais e sugira lojas parceiras quando possível.

## LGPD e Privacidade
- Para consultar pedidos, SEMPRE peça o telefone ou e-mail do cliente para identificação.
- Nunca revele dados de pedidos sem verificar a identidade do cliente.
- Dados são usados exclusivamente para operação da loja.
- O cliente pode solicitar exclusão dos dados a qualquer momento.

## Fora do Expediente
- Se a mensagem for enviada fora do horário de funcionamento, informe o horário de retorno.

## Data de Referência
- A data de hoje é: {reference_date}
- Use esta data para calcular prazos de arrependimento e garantia.
"""


class EmporioChatbot:
    """
    Chatbot agent for Empório da Música using Gemini with function calling.
    """

    def __init__(self, store: Optional[DataStore] = None) -> None:
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.store = store if store is not None else DataStore()
        self.history: list[dict] = []

        # Build system prompt with current reference date
        ref_date = get_reference_date()
        self.system_prompt = SYSTEM_PROMPT.format(
            reference_date=ref_date.strftime("%d/%m/%Y")
        )

        # Map tool names to their implementations
        self._tool_map = {
            "search_products": lambda **kwargs: search_products(self.store, **kwargs),
            "get_product_details": lambda **kwargs: get_product_details(self.store, **kwargs),
            "check_order_status": lambda **kwargs: check_order_status(self.store, **kwargs),
            "list_active_promotions": lambda **kwargs: list_active_promotions(self.store),
        }

    def _build_tools(self) -> list:
        """Build the tool declarations in the format expected by Gemini."""
        tools = []
        for decl in TOOL_DECLARATIONS:
            tools.append(types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=decl["name"],
                        description=decl["description"],
                        parameters=decl["parameters"],
                    )
                ]
            ))
        return tools

    def _execute_tool(self, function_call) -> str:
        """Execute a function call and return the result as JSON string."""
        func_name = function_call.name
        func_args = dict(function_call.args) if function_call.args else {}

        if func_name in self._tool_map:
            result = self._tool_map[func_name](**func_args)
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return json.dumps({"error": f"Ferramenta '{func_name}' não encontrada."})

    def _trim_history(self) -> None:
        """Keep only the last MAX_HISTORY_MESSAGES messages."""
        from src.config import MAX_HISTORY_MESSAGES
        if len(self.history) > MAX_HISTORY_MESSAGES:
            self.history = self.history[-MAX_HISTORY_MESSAGES:]

    def send_message(self, user_message: str) -> str:
        """
        Send a user message and get the agent's response.
        Handles function calling loops automatically.
        """
        # Add user message to history
        self.history.append({"role": "user", "parts": [{"text": user_message}]})
        self._trim_history()

        # Build the contents for the API call
        contents = []
        for msg in self.history:
            contents.append(types.Content(
                role=msg["role"],
                parts=[types.Part.from_text(text=p["text"]) for p in msg["parts"] if "text" in p],
            ))

        tools = self._build_tools()

        # Call Gemini
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                tools=tools,
                temperature=0.7,
            ),
        )

        # Handle function calling loop (max 5 iterations to prevent infinite loops)
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            candidate = response.candidates[0]

            # Check if there are function calls
            function_calls = []
            text_parts = []
            for part in candidate.content.parts:
                if part.function_call:
                    function_calls.append(part.function_call)
                elif part.text:
                    text_parts.append(part.text)

            if not function_calls:
                # No function calls — we have the final text response
                final_text = " ".join(text_parts) if text_parts else "Desculpe, não consegui processar sua mensagem. Pode tentar novamente?"
                self.history.append({"role": "model", "parts": [{"text": final_text}]})
                self._trim_history()
                return final_text

            # Execute each function call and build function responses
            # First, add the model's response (with function calls) to contents
            contents.append(candidate.content)

            function_response_parts = []
            for fc in function_calls:
                result_str = self._execute_tool(fc)
                function_response_parts.append(
                    types.Part.from_function_response(
                        name=fc.name,
                        response=json.loads(result_str),
                    )
                )

            # Add function responses to contents
            contents.append(types.Content(
                role="user",
                parts=function_response_parts,
            ))

            # Call Gemini again with the function results
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    tools=tools,
                    temperature=0.7,
                ),
            )

        # If we exhausted iterations, return whatever text we have
        final_text = "Desculpe, tive dificuldade para processar sua consulta. Pode reformular a pergunta?"
        self.history.append({"role": "model", "parts": [{"text": final_text}]})
        self._trim_history()
        return final_text

    def reset_history(self) -> None:
        """Clear conversation history."""
        self.history = []
