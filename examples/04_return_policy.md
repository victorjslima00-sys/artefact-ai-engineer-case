# Example 4 — Return Policy Application (Non-Trivial)

> **Scenario**: A customer wants to return a purchase. The agent must: (1) identify the customer via phone/email for LGPD compliance, (2) look up the order, (3) acknowledge that return eligibility is marked as `provisional` based on the estimated delivery date and ask to confirm the actual delivery date, and (4) properly apply the CDC 7-day return policy once the actual date is confirmed.

> **Note**: This example uses `REFERENCE_DATE=2026-03-25` to demonstrate return eligibility with the sample data.

---

**Customer**: Me arrependi da minha compra, posso devolver meu pedido?

**Agent**: Olá! Claro, posso te ajudar com isso. 

Para verificar a elegibilidade da devolução por arrependimento, por favor, me informe o seu **telefone ou e-mail cadastrado** e a **data em que você recebeu o produto** (ou o número do pedido, se lembrar). 

Assim que você me passar esses dados, confiro tudo para você! 😊

**Customer**: Meu email é leticia.rocha@jmail.com

**Agent**: Olá, Letícia! Vi aqui que o seu pedido do **Ukulele Shelby SU-21S Soprano Sunburst** foi entregue. 

Como a nossa regra de arrependimento permite a devolução em até **7 dias corridos após o recebimento**, e o cálculo aproximado com base na data de entrega estimada (17/02/2026) indica que esse prazo já passou, a princípio o pedido consta como não elegível por prazo (`provisional`). 

Para termos certeza absoluta: você lembra exatamente em qual data recebeu o pacote em sua casa? Se a entrega aconteceu recentemente (dentro dos últimos 7 dias corridos), me avise para eu verificar se conseguimos abrir uma exceção ou ajustar a data real no sistema para você! 😊

**Customer**: Recebi no dia 22/03/2026!

**Agent**: Ah, perfeito, Letícia! Muito obrigado por confirmar a data. 

Como você recebeu o produto no dia **22/03/2026** (domingo passado) e hoje é dia 25/03/2026, você está super dentro do prazo de **7 dias corridos** do direito de arrependimento da compra online! 🎉

Para realizarmos a devolução, o instrumento precisa estar na embalagem original e sem nenhum sinal de uso, combinado? O frete de devolução fica por nossa conta e, assim que o produto chegar e passar pela nossa conferência, o reembolso é feito em até 10 dias úteis na mesma forma de pagamento da compra.

Você quer que eu inicie o processo de solicitação da devolução agora mesmo para você? 😊
