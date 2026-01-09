from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from datetime import datetime
from collections import defaultdict

def _create_table_style():
    return TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ])

def gerar_relatorio_fluxo(parcelas, filename="relatorio_fluxo.pdf"):
    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        title = Paragraph(f"Relatório Financeiro - {datetime.now().strftime('%d/%m/%Y')}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        data = [['Vencimento', 'Cliente', 'Valor', 'Status']]
        total_rec = 0
        total_pend = 0
        
        for p in parcelas:
            val = float(p.get('valor', 0))
            status = "PAGO" if p.get('status') == 'paga' else "PENDENTE"
            if p.get('status') == 'paga': total_rec += val
            else: total_pend += val
            
            data.append([
                datetime.strptime(p['data_vencimento'], '%Y-%m-%d').strftime('%d/%m/%Y'),
                p['cliente'],
                f"R$ {val:,.2f}",
                status
            ])
            
        t = Table(data)
        t.setStyle(_create_table_style())
        elements.append(t)
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Total Recebido:</b> R$ {total_rec:,.2f}", styles['Normal']))
        elements.append(Paragraph(f"<b>Total Pendente:</b> R$ {total_pend:,.2f}", styles['Normal']))
        
        doc.build(elements)
        return True, os.path.abspath(filename)
    except Exception as e:
        return False, str(e)

def gerar_relatorio_inadimplencia(parcelas, filename="relatorio_inadimplencia.pdf"):
    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph(f"Relatório de Inadimplência", styles['Title']))
        elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        data = [['Vencimento', 'Cliente', 'Valor', 'Dias Atraso']]
        total_devido = 0
        hoje = datetime.now().date()
        
        count = 0
        for p in parcelas:
            try:
                venc_str = p.get('data_vencimento')
                if not venc_str: continue
                
                venc = datetime.strptime(venc_str, '%Y-%m-%d').date()
                if venc < hoje and p.get('status') != 'paga':
                    atraso = (hoje - venc).days
                    val = float(p.get('valor', 0))
                    total_devido += val
                    
                    data.append([
                        venc.strftime('%d/%m/%Y'),
                        p.get('cliente', '-'),
                        f"R$ {val:,.2f}",
                        f"{atraso} dias"
                    ])
                    count += 1
            except:
                continue
                
        if count == 0:
            elements.append(Paragraph("Nenhuma inadimplência encontrada. Parabéns!", styles['Normal']))
        else:
            t = Table(data)
            t.setStyle(_create_table_style())
            elements.append(t)
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"<b>Total Inadimplente:</b> R$ {total_devido:,.2f}", styles['Normal']))
            
        doc.build(elements)
        return True, os.path.abspath(filename)
    except Exception as e:
        return False, str(e)

def gerar_extrato_ir(parcelas, ano, filename="extrato_ir.pdf"):
    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph(f"Extrato para Imposto de Renda - Ano Base {ano}", styles['Title']))
        elements.append(Spacer(1, 20))
        
        data = [['Data', 'Cliente', 'Serviço', 'Valor Recebido']]
        total_ano = 0
        
        parcelas_ano = []
        for p in parcelas:
            if p.get('status') == 'paga':
                dt_str = p.get('data_vencimento', '')
                try:
                    dt = datetime.strptime(dt_str, '%Y-%m-%d')
                    if dt.year == int(ano):
                        parcelas_ano.append(p)
                except:
                    continue
        
        # Ordenar por data
        parcelas_ano.sort(key=lambda x: x.get('data_vencimento'))
        
        for p in parcelas_ano:
            val = float(p.get('valor', 0))
            total_ano += val
            dt = datetime.strptime(p['data_vencimento'], '%Y-%m-%d')
            
            data.append([
                dt.strftime('%d/%m/%Y'),
                p.get('cliente', '-'),
                "Honorários Advocatícios",
                f"R$ {val:,.2f}"
            ])
            
        if len(parcelas_ano) == 0:
             elements.append(Paragraph(f"Nenhum recebimento registrado em {ano}.", styles['Normal']))
        else:
            t = Table(data)
            t.setStyle(_create_table_style())
            elements.append(t)
            
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"<b>Total Recebido em {ano}:</b> R$ {total_ano:,.2f}", styles['Normal']))
        
        doc.build(elements)
        return True, os.path.abspath(filename)
    except Exception as e:
        return False, str(e)

def gerar_dre(receitas, despesas, ano, filename="dre_gerencial.pdf"):
    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph(f"DRE Gerencial - {ano}", styles['Title']))
        elements.append(Spacer(1, 20))
        
        data = [['Mês', 'Receita Bruta', 'Despesas', 'Resultado Líquido']]
        
        resumo = defaultdict(lambda: {'rec': 0.0, 'desp': 0.0})
        
        # Processar Receitas
        for r in receitas:
             if r.get('status') == 'paga':
                try:
                    dt = datetime.strptime(r.get('data_vencimento'), '%Y-%m-%d')
                    if dt.year == int(ano):
                        resumo[dt.month]['rec'] += float(r.get('valor', 0))
                except: continue

        # Processar Despesas
        for d in despesas:
            try:
                dt = datetime.strptime(d.get('data'), '%Y-%m-%d')
                if dt.year == int(ano):
                    resumo[dt.month]['desp'] += float(d.get('valor', 0))
            except: continue
            
        tot_rec = 0
        tot_desp = 0
        tot_res = 0
        
        nomes_meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        
        for m in range(1, 13):
            rec = resumo[m]['rec']
            desp = resumo[m]['desp']
            res = rec - desp
            
            tot_rec += rec
            tot_desp += desp
            tot_res += res
            
            data.append([
                nomes_meses[m],
                f"R$ {rec:,.2f}",
                f"R$ {desp:,.2f}",
                f"R$ {res:,.2f}"
            ])
            
        # Linha de Totais
        data.append(['TOTAL ANUAL', f"R$ {tot_rec:,.2f}", f"R$ {tot_desp:,.2f}", f"R$ {tot_res:,.2f}"])
            
        t = Table(data)
        style = _create_table_style()
        # Destacar linha de total
        style.add('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold')
        style.add('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey)
        
        t.setStyle(style)
        elements.append(t)
        
        doc.build(elements)
        return True, os.path.abspath(filename)
    except Exception as e:
        return False, str(e)
