#!/usr/bin/env python3
"""
Genera un informe PDF con tabla de encuestas por año y asignatura.
Uso: python3 report.py [output.pdf]
"""

import os, sys, subprocess, tempfile
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))

PREGUNTAS_TEXTO = {
    1:  "El profesor cumple con su horario de clase establecido.",
    2:  "El profesor asiste regularmente a clase.",
    3:  "El profesor está accesible para tutorías o consultas por parte de los estudiantes en su horario establecido.",
    4:  "El profesor prepara, organiza y estructura bien las actividades o tareas que se realizan en la clase.",
    5:  "El profesor explica de forma clara y comprensible los contenidos de la asignatura.",
    6:  "El profesor ha cumplido con lo planificado en la guía de aprendizaje.",
    7:  "El profesor resuelve las dudas y orienta a los alumnos en el desarrollo de las tareas.",
    8:  "Los materiales docentes utilizados y/o recomendados son útiles para cursar la asignatura y se encuentran disponibles.",
    9:  "El profesor utiliza las Tecnologías de Información y Comunicación (TIC) y técnicas docentes innovadoras de forma adecuada.",
    10: "El profesor despierta mi interés por esta asignatura.",
    11: "El profesor ha contribuido en mi adquisición de competencias y destrezas al cursar esta asignatura.",
    12: "En general, estoy satisfecho con la labor docente del profesor.",
}

def load_data():
    rows = []
    for year in sorted(os.listdir(os.path.join(BASE, 'data'))):
        year_path = os.path.join(BASE, 'data', year)
        if not os.path.isdir(year_path):
            continue
        for asig in sorted(os.listdir(year_path)):
            agg = os.path.join(year_path, asig, 'agg.csv')
            if not os.path.exists(agg):
                continue
            df = pd.read_csv(agg)
            m = df[df['archivo'] == 'MEDIA_GENERAL']
            if m.empty:
                continue
            r = m.iloc[0]
            row = {'año': year, 'asignatura': asig}
            for i in range(1, 13):
                v = r.get(f'pregunta_{i}')
                row[f'p{i}'] = round(float(v), 2) if pd.notna(v) else None
            mf = r.get('media_fila')
            row['media'] = round(float(mf), 2) if pd.notna(mf) else None
            rows.append(row)
    return rows


def year_label(y):
    return f"20{y[:2]}-{y[2:]}"  # 2526 → 2025-26


def bg(v):
    if v is None: return '#f0f0f0'
    if v >= 8:    return '#c8e6c9'
    if v >= 6:    return '#fff9c4'
    return '#ffcdd2'


def build_html(data):
    years = sorted(set(r['año'] for r in data))
    sections = ''
    for year in years:
        yr = [r for r in data if r['año'] == year]
        rows = ''
        for r in yr:
            cells = f'<td class="asig">{r["asignatura"]}</td>'
            for i in range(1, 13):
                v = r[f'p{i}']
                cells += f'<td style="background:{bg(v)}">{v if v is not None else "-"}</td>'
            m = r['media']
            cells += f'<td class="med" style="background:{bg(m)}">{m if m is not None else "-"}</td>'
            rows += f'<tr>{cells}</tr>\n'
        headers = ''.join(f'<th>P{i}</th>' for i in range(1, 13))
        sections += f'<h2>Curso {year_label(year)}</h2>\n<table>\n<tr><th>Asignatura</th>{headers}<th>Media</th></tr>\n{rows}</table>\n'

    legend_items = '\n'.join(
        f'<li><b>P{n}.</b> {texto}</li>' for n, texto in PREGUNTAS_TEXTO.items()
    )

    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  @page {{ size: A4 landscape; margin: 1.5cm; }}
  body {{ font-family: Arial, sans-serif; font-size: 10px; }}
  h1 {{ font-size: 15px; }}
  h2 {{ font-size: 12px; margin-top: 20px; color: #1565c0; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 16px; }}
  th {{ background: #1565c0; color: white; padding: 4px 6px; text-align: center; }}
  td {{ padding: 3px 6px; border: 1px solid #ccc; text-align: center; }}
  td.asig {{ text-align: left; font-weight: bold; }}
  td.med {{ font-weight: bold; }}
  .legend {{ margin-top: 24px; border-top: 1px solid #ccc; padding-top: 12px; }}
  .legend h3 {{ font-size: 11px; color: #1565c0; margin-bottom: 6px; }}
  .legend ol {{ columns: 2; column-gap: 2em; padding-left: 1.2em; margin: 0; }}
  .legend li {{ margin-bottom: 4px; break-inside: avoid; }}
  .footer {{ margin-top: 20px; border-top: 1px solid #ccc; padding-top: 8px; font-size: 9px; color: #888; text-align: center; }}
  .footer a {{ color: #1565c0; }}
</style></head><body>
<h1>Encuestas de satisfacción docente - UPM</h1>
{sections}
<div class="legend">
  <h3>Preguntas sobre el profesorado</h3>
  <ol>{legend_items}</ol>
</div>
<div class="footer">
  Desarrollado por Jorge Due&ntilde;as Ler&iacute;n &mdash;
  <a href="https://github.com/JorgeDuenasLerin/encuestas">github.com/JorgeDuenasLerin/encuestas</a>
</div>
</body></html>'''


def to_pdf(html, output):
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
        f.write(html)
        tmp = f.name

    abs_output = os.path.abspath(output)
    for cmd in ['chromium', 'chromium-browser', 'google-chrome']:
        try:
            r = subprocess.run(
                [cmd, '--headless', '--no-sandbox', '--disable-gpu',
                 '--no-pdf-header-footer',
                 f'--print-to-pdf={abs_output}', f'file://{tmp}'],
                capture_output=True, timeout=30
            )
            if r.returncode == 0:
                os.unlink(tmp)
                print(f"OK: {output}")
                return
        except FileNotFoundError:
            continue

    try:
        r = subprocess.run(
            ['wkhtmltopdf', '--orientation', 'Landscape', tmp, abs_output],
            capture_output=True, timeout=30
        )
        if r.returncode == 0:
            os.unlink(tmp)
            print(f"OK: {output}")
            return
    except FileNotFoundError:
        pass

    print(f"Sin herramienta de conversión. HTML en: {tmp}")
    print("Instala: sudo apt install chromium  o  sudo apt install wkhtmltopdf")


def main():
    output = sys.argv[1] if len(sys.argv) > 1 else 'informe.pdf'
    data = load_data()
    if not data:
        print("No hay datos en data/")
        sys.exit(1)
    print(f"Cargadas {len(data)} filas de datos")
    to_pdf(build_html(data), output)


if __name__ == '__main__':
    main()
