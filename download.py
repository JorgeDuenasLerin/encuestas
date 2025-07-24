#!/usr/bin/env python3

import sys
import requests
import os
import pandas as pd

def read_cookies_from_file(cookie_file):
    try:
        with open(cookie_file, 'r') as f:
            cookie_line = f.read().strip()
            
        if cookie_line.startswith('Cookie: '):
            cookie_line = cookie_line[8:]
            
        cookies = {}
        for cookie in cookie_line.split('; '):
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key] = value
                
        return cookies
    except Exception as e:
        print(f"Error leyendo cookies: {e}")
        return {}

def download_file(url, file_path, cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/csv,application/pdf,*/*',
    }
    
    try:
        response = requests.get(url, cookies=cookies, headers=headers)
        
        if response.status_code == 200 and len(response.content) > 100:
            if file_path.endswith('.csv'):
                # Para archivos CSV, convertir de ISO-8859-3 a UTF-8
                text_content = response.content.decode('iso-8859-3')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
            else:
                # Para archivos PDF y otros, usar binario
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            
            print(f"    OK {file_path} ({len(response.content)} bytes)")
            return True
        else:
            print(f"    Error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"    Error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 download.py data/id.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    cookie_file = 'cookie.txt'
    
    if not os.path.exists(csv_file):
        print(f"No se encontro {csv_file}")
        sys.exit(1)
    
    cookies = read_cookies_from_file(cookie_file)
    if not cookies:
        print("No se pudieron leer las cookies")
        sys.exit(1)
    
    print(f"Cookies: {list(cookies.keys())}")
    
    df = pd.read_csv(csv_file)
    print(f"Procesando {len(df)} asignaturas")
    
    success_count = 0
    
    for index, row in df.iterrows():
        subject_id = str(row['ID'])
        asignatura = row['ASIGNATURA']
        grado = row['GRADO']
        file_id = str(row['FILE_ID'])
        
        print(f"\n[{index+1}/{len(df)}] {asignatura} (FILE_ID: {file_id})")
        
        output_dir = os.path.join('data', asignatura)
        os.makedirs(output_dir, exist_ok=True)
        
        csv_url = f"https://servicios.upm.es/encuestas/api/group/{file_id}/stats?format=csv"
        pdf_url = f"https://servicios.upm.es/encuestas/api/group/{file_id}/stats?format=pdf"
        
        csv_file_path = os.path.join(output_dir, f"{grado}.csv")
        pdf_file_path = os.path.join(output_dir, f"{grado}.pdf")

        print(f"  Descargando CSV desde: {csv_url}")
        print(f"  Descargando PDF desde: {pdf_url}")
        
        csv_ok = download_file(csv_url, csv_file_path, cookies)
        pdf_ok = download_file(pdf_url, pdf_file_path, cookies)
        
        if csv_ok or pdf_ok:
            success_count += 1
    
    print(f"\nCompletado: {success_count}/{len(df)} exitosos")

if __name__ == "__main__":
    main()
