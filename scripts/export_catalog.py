import sys, os
sys.path.insert(0, r'.')
from src.data_loader import DataStore

store = DataStore()
df = store.products.copy()

output_path = r'.\docs\relacao_instrumentos.md'

with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# Relação Completa de Instrumentos — Empório da Música\n\n")
    f.write(f"Total de itens cadastrados no acervo: **{len(df)} instrumentos**.\n\n")
    
    for cat_id in sorted(store.categories['category_id']):
        cat_name = store.get_category_name(cat_id)
        sub = df[df['category_id'] == cat_id].sort_values(by='price_brl')
        if sub.empty:
            continue
        f.write(f"## {cat_name} ({len(sub)} itens)\n\n")
        f.write("| ID | Nome do Instrumento | Preço Tabela | Estoque | Status | Promoção Ativa |\n")
        f.write("| :---: | :--- | :---: | :---: | :---: | :--- |\n")
        
        for _, r in sub.iterrows():
            p_id = int(r['product_id'])
            promo = store.get_active_promotion(p_id)
            if promo:
                final_p = r['price_brl'] * (1 - promo['discount_percent'] / 100)
                promo_str = f"**{promo['discount_percent']:.0f}% OFF** (R$ {final_p:,.2f}) — *{promo['description']}*"
            else:
                promo_str = "-"
            
            price_str = f"R$ {r['price_brl']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            promo_str = promo_str.replace(',', 'X').replace('.', ',').replace('X', '.')
            
            status_map = {
                'active': '🟢 Ativo',
                'discontinued': '🔴 Descontinuado',
                'coming_soon': '🟡 Em Breve'
            }
            st = status_map.get(r['status'], r['status'])
            if r['status'] == 'active' and r['stock_quantity'] == 0:
                st = '⚪ Esgotado'
                
            f.write(f"| {p_id} | {r['name']} | {price_str} | {r['stock_quantity']} | {st} | {promo_str} |\n")
        f.write("\n")

print("File generated successfully at:", output_path)
