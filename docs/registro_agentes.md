# Registro de agentes — Empório da Música

Este arquivo registra a atuação dos agentes de IA no projeto com escopo, justificativas técnicas resumidas, arquivos tocados e verificações. Não registra cadeia de raciocínio privada; registra decisões auditáveis para evitar sobreposição com o Antigravity.

## 2026-11-01 — Hermes — em andamento

**Solicitação:** continuar a validação do protótipo e corrigir os pontos identificados na revisão anterior, deixando o trabalho visível para o Antigravity.

**Estado de partida observado:**
- O projeto contém a UI Streamlit, integração Gemini, ferramentas de catálogo/pedidos/promoções e dados CSV.
- Não há repositório Git nem testes automatizados visíveis nesta pasta.
- A verificação de execução anterior foi bloqueada por ausência de `pandas` no Python ativo; a compilação sintática de `app.py` e `src/` passou.
- `orders.csv` contém `order_date` e `estimated_delivery`, mas não uma data de entrega efetiva (`delivery_date`). Para pedidos entregues, a documentação de exemplo usa `estimated_delivery` como a data de entrega.
- O código atual calcula os 7 dias desde `order_date`, incompatível com a política de arrependimento após o recebimento.

**Decisões e justificativas registradas:**
1. Corrigir a contagem para usar a data de entrega disponível (`estimated_delivery`) somente em pedidos marcados como entregues; identificar esse campo como estimativa/proxy, pois o CSV não fornece a data efetiva. Se a data estiver ausente, inválida ou no futuro em relação à referência, não afirmar elegibilidade como fato.
2. Criar testes de regressão antes da alteração de produção e executar testes locais das ferramentas sem chamar a API Gemini nem ler/imprimir `.env`.
3. Instalar dependências de teste em ambiente temporário fora da pasta do projeto, para não criar `.venv` nem alterar o setup do Antigravity.
4. Não editar `app.py` nesta etapa; a inconsistência do indicador de horário da loja fica registrada para decisão futura.
5. Atualizar este registro ao concluir cada mudança, anotando arquivos, motivo, comandos e resultados. Não criar commits: esta pasta não tem Git inicializado.

**Escopo reservado durante esta tarefa:**
- Hermes: `src/tools.py`, `src/agent.py`, `tests/` e este registro. `src/agent.py` foi incluído antes da edição porque a ferramenta passará a marcar a elegibilidade calculada com data estimada como provisória; o prompt precisa instruir o chatbot a não apresentá-la como certeza. Qualquer outro arquivo só será tocado se ficar indispensável e será anotado antes.
- Antigravity: evitar sobrescrever esses arquivos durante esta validação; ao retomar, ler este registro e comparar o estado atual antes de editar.

**Progresso:** concluído em 2026-11-01.

**Arquivos alterados:**
- `src/tools.py`: o cálculo agora parte de `estimated_delivery` (não `order_date`), limita a janela a 0–7 dias e marca o resultado como provisório por ser uma estimativa. Data ausente, inválida ou futura retorna elegibilidade desconhecida.
- `src/agent.py`: orienta o chatbot a explicar a aproximação e confirmar a data efetiva antes de afirmar ou negar elegibilidade.
- `tests/test_order_return_eligibility.py`: cinco testes cobrindo data de entrega, limite de 7 dias, 8º dia, estimativa ausente e estimativa futura.
- `README.md`: registra Hermes e direciona agentes ao presente log.
- `docs/registro_agentes.md`: este histórico e o escopo de coordenação.

**Verificações executadas:**
- RED antes da correção: `test_return_window_starts_from_delivery_date` falhou como esperado (o código antigo retornava `False` usando `order_date`).
- GREEN/regressão: `python -m unittest discover -s tests -v` — 5 testes passaram.
- `python -m compileall -q app.py src tests` — passou.
- Dependências de `requirements.txt` instaladas apenas em ambiente virtual temporário fora do repositório; `pip check` reportou `No broken requirements found`.
- Smoke test local: catálogo (12 violões até R$1.000), detalhes do Takamine GD20, 4 promoções e consulta de pedidos executaram com dados locais.
- Streamlit `AppTest`: execução sem exceções. Chave temporária fictícia usada somente para inicializar o cliente; nenhuma chamada à API Gemini foi feita.

**Limites mantidos:** não li nem imprimi `.env`; não fiz chamada externa ao Gemini; não alterei `app.py`; não inicializei Git nem criei commits. A data real de entrega ainda não existe no CSV, portanto o cálculo permanece explicitamente provisório até a fonte de dados registrar essa data. A inconsistência do horário da loja fica para uma tarefa separada.

