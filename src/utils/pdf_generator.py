from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os
from datetime import datetime

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
            val = p['valor']
            status = "PAGO" if p['status'] == 'paga' else "PENDENTE"
            if p['status'] == 'paga': total_rec += val
            else: total_pend += val
            
            data.append([
                datetime.strptime(p['data_vencimento'], '%Y-%m-%d').strftime('%d/%m/%Y'),
                p['cliente'],
                f"R$ {val:.2f}",
                status
            ])
            
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Total Recebido:</b> R$ {total_rec:,.2f}", styles['Normal']))
        elements.append(Paragraph(f"<b>Total Pendente:</b> R$ {total_pend:,.2f}", styles['Normal']))
        
        doc.build(elements)
        return True, os.path.abspath(filename)
    except Exception as e:
        return False, str(e)