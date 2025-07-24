#!/usr/bin/env python3

import sys
import re
import pandas as pd
import os
from bs4 import BeautifulSoup

def get_first_letters(text):
    words = text.split()
    return ''.join([word[0].upper() for word in words if word])

def extract_ids(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    for title_element in soup.find_all('div', class_='title'):
        title_text = title_element.get_text().strip()
        
        if 'GRADO' in title_text:
            grado_abbrev = get_first_letters(title_text)
            content_element = title_element.find_next_sibling('div', class_='content')
            
            if content_element:
                links = content_element.find_all('a', href=re.compile(r'/encuestas/statistics/subject/\d+/groups'))
                
                for link in links:
                    href = link.get('href', '')
                    match = re.search(r'/subject/(\d+)/groups', href)
                    if match:
                        subject_id = match.group(1)
                        asignatura = link.get('title', '').strip()
                        asignatura_abbrev = get_first_letters(asignatura)
                        
                        results.append({
                            'ID': subject_id,
                            'ASIGNATURA': asignatura_abbrev,
                            'GRADO': grado_abbrev,
                            'FILE_ID': ''
                        })
    
    return results

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 extract-ids.py <archivo_html>")
        sys.exit(1)
    
    archivo_html = sys.argv[1]
    
    if not os.path.exists(archivo_html):
        print(f"Error: No se encontro el archivo '{archivo_html}'")
        sys.exit(1)
    
    try:
        with open(archivo_html, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"Procesando {archivo_html}...")
        
        results = extract_ids(html_content)
        
        if results:
            os.makedirs('data', exist_ok=True)
            df = pd.DataFrame(results)
            output_file = 'data/id.csv'
            
            # Verificar si el archivo ya existe
            if os.path.exists(output_file):
                response = input(f"El archivo {output_file} ya existe. ¿Sobrescribir? (s/N): ")
                if response.lower() not in ['s', 'si', 'y', 'yes']:
                    print("Operación cancelada.")
                    sys.exit(0)
            
            df.to_csv(output_file, index=False, encoding='utf-8')
            
            print(f"Extraidos {len(results)} elementos")
            print(f"Guardado en: {output_file}")
            
            for i, result in enumerate(results[:5]):
                print(f"  {i+1}. ID: {result['ID']} | {result['ASIGNATURA']} | {result['GRADO']}")
            
            if len(results) > 5:
                print(f"  ... y {len(results) - 5} mas")
        else:
            print("No se encontraron elementos")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
