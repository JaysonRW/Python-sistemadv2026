from datetime import datetime

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def gerar_timeline_cliente(cliente_nome, contratos, parcelas):
    """
    Gera uma lista de eventos cronológicos para o cliente.
    Retorna lista de dicts ordenados por data (mais recente primeiro).
    """
    events = []
    
    # Filtrar dados
    contratos_cli = [c for c in contratos if c.get('cliente') == cliente_nome]
    parcelas_cli = [p for p in parcelas if p.get('cliente') == cliente_nome]
    
    hoje = datetime.now().date()
    
    # Eventos de Contrato
    for c in contratos_cli:
        dt_inicio = parse_date(c.get('data_inicio'))
        if dt_inicio:
            # Evento: Contrato Criado
            events.append({
                'data': dt_inicio,
                'tipo': 'contrato',
                'titulo': 'Contrato Iniciado',
                'descricao': f"{c.get('tipo_honorario')} - {c.get('area_direito')} (R$ {c.get('valor_total', 0):,.2f})",
                'icone': '📝',
                'cor': '#3498db' # Blue
            })
            
            # Evento: Parcelas Geradas
            num_p = c.get('num_parcelas', 0)
            if num_p > 0:
                events.append({
                    'data': dt_inicio,
                    'tipo': 'sistema',
                    'titulo': 'Parcelamento Definido',
                    'descricao': f"{num_p} parcelas geradas",
                    'icone': '⚙️',
                    'cor': '#95a5a6' # Gray
                })

    # Eventos de Parcelas
    for p in parcelas_cli:
        dt_venc = parse_date(p.get('data_vencimento'))
        dt_pag = parse_date(p.get('data_pagamento'))
        status = p.get('status')
        num = p.get('numero')
        valor = p.get('valor', 0)
        
        # Pagamento Realizado
        if status == 'paga' and dt_pag:
            events.append({
                'data': dt_pag,
                'tipo': 'pagamento',
                'titulo': 'Pagamento Recebido',
                'descricao': f"Parcela {num} quitada (R$ {valor:,.2f})",
                'icone': '✅',
                'cor': '#2ecc71' # Green
            })
        
        # Atraso (Vencida e não paga)
        elif status == 'em_aberto' and dt_venc and dt_venc < hoje:
             events.append({
                'data': dt_venc,
                'tipo': 'atraso',
                'titulo': 'Atraso Registrado',
                'descricao': f"Parcela {num} venceu dia {dt_venc.strftime('%d/%m/%Y')}",
                'icone': '🚨',
                'cor': '#e74c3c' # Red
            })
             
        # Futuro (Vencimento próximo ou distante)
        elif status == 'em_aberto' and dt_venc and dt_venc >= hoje:
             events.append({
                'data': dt_venc,
                'tipo': 'futuro',
                'titulo': 'Agendamento',
                'descricao': f"Parcela {num} vence em {dt_venc.strftime('%d/%m/%Y')}",
                'icone': '📅',
                'cor': '#f1c40f' # Yellow/Orange
            })

    # Ordenação: Mais recente primeiro
    events.sort(key=lambda x: x['data'], reverse=True)
    
    return events
