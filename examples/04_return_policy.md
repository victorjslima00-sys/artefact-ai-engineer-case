# Example 4 — Return Policy Application (Non-Trivial)

> **Scenario**: A customer wants to return a purchase. The agent must: (1) identify the customer via phone/email for LGPD compliance, (2) look up the order, (3) calculate whether the 7-day return window is still open based on the reference date, and (4) apply the correct return policy. This demonstrates real-time data consultation combined with policy application.

> **Note**: This example uses `REFERENCE_DATE=2026-03-25` to demonstrate return eligibility with the sample data.

---

**Customer**: Me arrependi da minha compra, posso devolver meu pedido?

**Agent**: Entendo! Vou te ajudar com isso. 😊

Para consultar seu pedido, preciso confirmar sua identidade. Pode me informar o **telefone** ou **e-mail** cadastrado na compra?

**Customer**: Meu email é pedro.oliveira@jmail.com

**Agent**: Encontrei seu cadastro, Pedro! Deixa eu verificar seus pedidos...

Encontrei 1 pedido no seu nome:

📦 **Pedido #1**
- **Data**: 15/10/2025
- **Produto**: Martin D-28 Dreadnought Natural
- **Valor**: R$ 11.499,00 (pago via PIX)
- **Status**: Entregue
- **Rastreamento**: BRAB1234567BR

Infelizmente, Pedro, o prazo para exercer o direito de arrependimento já expirou. O pedido foi entregue há mais de 7 dias corridos (a entrega foi em 25/10/2025, há aproximadamente 152 dias).

📋 **Sobre a política de devolução**:
- **Arrependimento**: até 7 dias corridos após o recebimento (Art. 49 do CDC)
- **Defeito de fabricação**: até 30 dias corridos (seu pedido também está fora desse prazo)
- **Garantia legal**: 90 dias contra defeitos de fabricação

Se o Martin D-28 apresentar algum **defeito de fabricação**, ele ainda está dentro da **garantia legal de 90 dias**. Nesse caso, podemos encaminhar para avaliação. O produto está com algum problema?

**Customer**: Não, tá funcionando bem, só mudei de ideia mesmo.

**Agent**: Entendo, Pedro. Infelizmente, como o prazo de arrependimento de 7 dias já passou e o produto está funcionando normalmente, não é possível fazer a devolução neste caso.

Mas se mudar de ideia sobre o instrumento, posso te ajudar a encontrar algo que se encaixe melhor no que você procura! O Martin D-28 é um violão lendário — talvez com mais tempo tocando você se apaixone por ele. 🎵

Posso te ajudar com mais alguma coisa?

**Customer**: Não, obrigado.

**Agent**: De nada, Pedro! Se precisar de qualquer coisa, é só chamar. Bons acordes pra você! 🎶
