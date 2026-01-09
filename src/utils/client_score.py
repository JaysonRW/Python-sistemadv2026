from datetime import datetime

def parse_date(date_str):
    if not date_str: return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

def calcular_score_cliente(cliente_nome, contratos, parcelas):
    """
    Calcula o score do cliente de 0 a 100 e retorna as estrelas e detalhes.
    """
    # Filtrar dados do cliente
    contratos_cli = [c for c in contratos if c.get('cliente') == cliente_nome]
    parcelas_cli = [p for p in parcelas if p.get('cliente') == cliente_nome]
    
    if not contratos_cli:
        return {"score": 0, "estrelas": "☆☆☆☆☆", "texto": "Novo ou sem dados", "cor": "gray"}

    hoje = datetime.now().date()
    pontos = 0
    detalhes = []
    
    # --- 1. PONTUALIDADE (Máx 50 pontos) ---
    # Analisar histórico de pagamentos e pendências
    parcelas_pagas = [p for p in parcelas_cli if p.get('status') == 'paga']
    parcelas_atrasadas_aberto = [
        p for p in parcelas_cli 
        if p.get('status') == 'em_aberto' 
        and parse_date(p.get('data_vencimento')) 
        and parse_date(p.get('data_vencimento')) < hoje
    ]
    
    total_devido = len(parcelas_pagas) + len(parcelas_atrasadas_aberto)
    
    if total_devido == 0:
        pontos += 50 # Benefício da dúvida se não tem nada vencido/pago ainda
        detalhes.append("Sem histórico de cobrança")
    else:
        # Penalidade grave por estar devendo AGORA
        qtd_atraso_atual = len(parcelas_atrasadas_aberto)
        if qtd_atraso_atual > 0:
            penalidade = min(40, qtd_atraso_atual * 15)
            pontos += max(0, 30 - penalidade) # Começa com 30 e perde
            detalhes.append(f"⚠️ {qtd_atraso_atual} parcelas em atraso hoje")
        else:
            # Analisar pagamentos passados
            pagas_em_dia = 0
            for p in parcelas_pagas:
                dt_venc = parse_date(p.get('data_vencimento'))
                dt_pag = parse_date(p.get('data_pagamento'))
                if dt_venc and dt_pag and dt_pag <= dt_venc:
                    pagas_em_dia += 1
            
            taxa_pontualidade = pagas_em_dia / len(parcelas_pagas) if parcelas_pagas else 1.0
            pts_pontualidade = int(50 * taxa_pontualidade)
            pontos += pts_pontualidade
            
            if taxa_pontualidade == 1.0:
                detalhes.append("💎 Pagamentos 100% em dia")
            elif taxa_pontualidade > 0.8:
                detalhes.append("✅ Maioria dos pagamentos em dia")
            else:
                detalhes.append("⚠️ Histórico de atrasos")

    # --- 2. VOLUME FINANCEIRO (Máx 30 pontos) ---
    total_pago = sum(p.get('valor', 0) for p in parcelas_pagas)
    
    if total_pago > 15000:
        pontos += 30
        detalhes.append("💰 Cliente High Ticket (>15k)")
    elif total_pago > 5000:
        pontos += 20
        detalhes.append("💲 Bom volume financeiro")
    elif total_pago > 1000:
        pontos += 10
    else:
        pontos += 5
        
    # --- 3. RELACIONAMENTO (Máx 20 pontos) ---
    # Data do contrato mais antigo
    datas_inicio = [parse_date(c.get('data_inicio')) for c in contratos_cli if parse_date(c.get('data_inicio'))]
    if datas_inicio:
        primeira_data = min(datas_inicio)
        meses_casa = (hoje.year - primeira_data.year) * 12 + (hoje.month - primeira_data.month)
        
        if meses_casa >= 24:
            pontos += 20
            detalhes.append("🏆 Cliente Antigo (+2 anos)")
        elif meses_casa >= 12:
            pontos += 15
            detalhes.append("📅 Cliente (+1 ano)")
        elif meses_casa >= 6:
            pontos += 10
        else:
            pontos += 5
            detalhes.append("🆕 Cliente Recente")

    # --- GERAÇÃO DE ESTRELAS ---
    # Normalizar max 100
    pontos = min(100, max(0, pontos))
    
    if pontos >= 90:
        estrelas = "⭐⭐⭐⭐⭐"
        cor = "#2ecc71" # Verde
        nivel = "Excelente"
    elif pontos >= 70:
        estrelas = "⭐⭐⭐⭐"
        cor = "#3498db" # Azul
        nivel = "Muito Bom"
    elif pontos >= 50:
        estrelas = "⭐⭐⭐"
        cor = "#f1c40f" # Amarelo
        nivel = "Regular"
    elif pontos >= 30:
        estrelas = "⭐⭐"
        cor = "#e67e22" # Laranja
        nivel = "Atenção"
    else:
        estrelas = "⭐"
        cor = "#e74c3c" # Vermelho
        nivel = "Crítico"

    return {
        "score": pontos,
        "estrelas": estrelas,
        "nivel": nivel,
        "cor": cor,
        "detalhes": detalhes,
        "total_pago": total_pago
    }
