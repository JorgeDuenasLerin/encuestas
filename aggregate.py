#!/usr/bin/env python3

import os
import pandas as pd
import numpy as np
import re
import csv

def extract_professor_data(csv_file_path):
    """
    Extrae los datos de profesores de un archivo CSV de encuesta
    Retorna un diccionario con las 12 preguntas (excluyendo 13 y 14)
    """
    result = {
        'archivo': os.path.basename(csv_file_path),
        'grado': os.path.basename(csv_file_path).replace('.csv', ''),
        'pregunta_1': np.nan,
        'pregunta_2': np.nan,
        'pregunta_3': np.nan,
        'pregunta_4': np.nan,
        'pregunta_5': np.nan,
        'pregunta_6': np.nan,
        'pregunta_7': np.nan,
        'pregunta_8': np.nan,
        'pregunta_9': np.nan,
        'pregunta_10': np.nan,
        'pregunta_11': np.nan,
        'pregunta_12': np.nan
    }
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar la sección "Datos sobre los profesores"
        if "Datos sobre los profesores" not in content:
            print(f"    No hay datos de profesores en {os.path.basename(csv_file_path)}")
            return result
        
        lines = content.split('\n')
        in_professor_section = False
        
        for line in lines:
            line = line.strip()
            
            if "Datos sobre los profesores" in line:
                in_professor_section = True
                continue
            
            if in_professor_section and line.startswith('Pregunta '):
                # Buscar preguntas del 1 al 12 usando regex
                match = re.match(r'Pregunta (\d+),"[^"]*",([^,]*),', line)
                if match:
                    q_num = int(match.group(1))
                    media = match.group(2).strip()
                    
                    if 1 <= q_num <= 12:
                        # Solo guardar si es un número válido
                        try:
                            float(media)  # Verificar que es un número
                            result[f'pregunta_{q_num}'] = float(media)
                        except ValueError:
                            # Si no es un número, dejar como NaN
                            result[f'pregunta_{q_num}'] = np.nan
        
        return result
        
    except Exception as e:
        print(f"Error procesando {csv_file_path}: {e}")
        return result

def process_subject_folder(subject_path):
    """
    Procesa todos los archivos CSV de una asignatura y genera el archivo agregado
    """
    subject_name = os.path.basename(subject_path)
    print(f"\nProcesando asignatura: {subject_name}")
    
    csv_files = [f for f in os.listdir(subject_path) 
                if f.endswith('.csv') and f != 'agg.csv']
    
    if not csv_files:
        print(f"  No se encontraron archivos CSV en {subject_path}")
        return
    
    all_data = []
    
    for csv_file in csv_files:
        csv_path = os.path.join(subject_path, csv_file)
        print(f"  Procesando: {csv_file}")
        
        data = extract_professor_data(csv_path)
        all_data.append(data)
    
    # Generar archivo agregado
    output_file = os.path.join(subject_path, 'agg.csv')
    
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Convertir las columnas de preguntas a numéricas, manteniendo NaN
        pregunta_cols = [f'pregunta_{i}' for i in range(1, 13)]
        for col in pregunta_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calcular la media de cada fila (solo preguntas numéricas, ignorando NaN)
        df['media_fila'] = df[pregunta_cols].mean(axis=1)
        
        # Añadir fila con medias de las medias (ignorando NaN)
        media_row = {'archivo': 'MEDIA_GENERAL', 'grado': ''}
        for col in pregunta_cols:
            media_row[col] = df[col].mean()
        media_row['media_fila'] = df['media_fila'].mean()
        
        # Convertir a DataFrame y concatenar
        media_df = pd.DataFrame([media_row])
        df = pd.concat([df, media_df], ignore_index=True)
        
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"  Generado: {output_file} con {len(all_data)} archivos + 1 fila de medias")

def main():
    data_dir = 'data'
    
    if not os.path.exists(data_dir):
        print("No se encontró el directorio 'data'")
        return
    
    subject_folders = [d for d in os.listdir(data_dir) 
                      if os.path.isdir(os.path.join(data_dir, d))]
    
    print(f"Encontradas {len(subject_folders)} asignaturas: {subject_folders}")
    
    for subject_folder in subject_folders:
        subject_path = os.path.join(data_dir, subject_folder)
        process_subject_folder(subject_path)
    
    print("\n¡Procesamiento completado!")

if __name__ == "__main__":
    main()
