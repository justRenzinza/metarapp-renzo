# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import re
import math
from decimal import Decimal, ROUND_DOWN
from datetime import datetime

# FIX WINDOWS: Force UTF-8 no stdout
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# CHECK netCDF4
try:
    import netCDF4
    from netCDF4 import Dataset
except ImportError:
    print("[ERRO] netCDF4 nao instalado!")
    print("Instale com: pip install netCDF4")
    sys.exit(1)

# =========================================================
# CONSTANTES
# =========================================================

COLUNAS_SBVT = [
    'station', 'valid', 'tmpc', 'dwpc', 'relh', 'drct', 'sknt',
    'vsby', 'skyc1', 'skyl1', 'metar',
    'Coluna L(null)', 'Coluna M (null)', 'Coluna N (null)',
    'Coluna O (null)', 'Coluna P (null)',
    'velocidade', 'cobertura nuvens', 'visibilidade (null)',
    'pressao', 'altura nuvens'
]

CLOUD_COVERAGE_MAP = {
    "M - DADOS FALTANTES": 0,
    "M": 0,
    "FEW": 2,
    "SCT": 4,
    "BKN": 6,
    "OVC": 8
}

CODIGO_ESTACAO = "00083649"  # Código fixo da estação

# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def extrair_pressao(metar_str):
    match = re.search(r"Q(\d{4})", str(metar_str))
    if match:
        valor = Decimal(match.group(1)) / Decimal("1000")
        valor_formatado = valor.quantize(Decimal(".001"), rounding=ROUND_DOWN)
        return str(valor_formatado).replace(".", ",")
    return "0,000"

# =========================================================
# PROCESSAMENTO INMET
# =========================================================

def processar_inmet(caminho_inmet, pasta_destino):
    try:
        df = pd.read_csv(caminho_inmet, sep=";", skiprows=10, encoding="latin1")
        df = df.loc[:, ~df.columns.str.contains("Unnamed")]
        print("[INMET] Carregado com sucesso")
    except Exception as e:
        print(f"[ERRO INMET] {e}")
        raise

    mapeamento = {
        "Data Medicao": "Data",
        "Hora Medicao": "Hora (UTC)",
        "PRECIPITACAO TOTAL, HORARIO(mm)": "Chuva (mm)",
        "TEMPERATURA DO AR - BULBO SECO, HORARIA(Â°C)": "Temp. Ins. (C)",
        "TEMPERATURA MAXIMA NA HORA ANT. (AUT)(Â°C)": "Temp. Max. (C)",
        "TEMPERATURA MINIMA NA HORA ANT. (AUT)(Â°C)": "Temp. Min. (C)",
        "TEMPERATURA DO PONTO DE ORVALHO(Â°C)": "Pto Orvalho Ins. (C)",
        "TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT)(Â°C)": "Pto Orvalho Max. (C)",
        "TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT)(Â°C)": "Pto Orvalho Min. (C)",
        "VENTO, DIRECAO HORARIA (gr)(Â° (gr))": "Dir. Vento (m/s)",
        "RADIACAO GLOBAL(Kj/mÂ²)": "RADIACAO_GLOBAL"
    }

    df = df.rename(columns=mapeamento)
    df = df[list(mapeamento.values())]

    df["RADIACAO_GLOBAL"] = (
        df["RADIACAO_GLOBAL"]
        .replace(r'^\s*$', '0', regex=True)
        .astype(str)
        .str.replace(',', '.', regex=False)
        .astype(float)
        .fillna(0)
        .apply(lambda x: 0 if x < 0 else math.ceil(x))
    )

    df["Radiacao (KJ/m²)"] = df["RADIACAO_GLOBAL"]

    df["Chuva (mm)"] = (
        df["Chuva (mm)"]
        .replace(r'^\s*$', '0', regex=True)
        .astype(float)
        .fillna(0)
    )

    radiacao = df.reset_index(drop=True)

    caminho_saida = os.path.join(pasta_destino, "radiacao_tratada.csv")
    df.to_csv(caminho_saida, sep=";", index=False, encoding="utf-8")
    print(f"[INMET OK] {len(df)} linhas -> radiacao_tratada.csv")

    return radiacao

# =========================================================
# PROCESSAMENTO SBVT
# =========================================================

def processar_sbvt(caminho_sbvt, radiacao):
    try:
        entrada = pd.read_csv(caminho_sbvt, header=None, names=COLUNAS_SBVT, 
                            encoding="latin1", on_bad_lines='skip', low_memory=False)
        print(f"[SBVT] Carregado: {len(entrada)} linhas brutas")
    except Exception as e:
        print(f"[ERRO SBVT 1] {e}")
        try:
            entrada = pd.read_csv(caminho_sbvt, header=None, names=COLUNAS_SBVT, 
                                encoding="utf-8", on_bad_lines='skip', low_memory=False)
            print(f"[SBVT UTF-8] {len(entrada)} linhas")
        except Exception as e2:
            print(f"[ERRO SBVT 2] {e2}")
            raise
    
    entrada['valid'] = pd.to_datetime(entrada['valid'], errors='coerce', utc=True)
    entrada = entrada.dropna(subset=['valid'])
    entrada = entrada.reset_index(drop=True)
    
    print(f"[SBVT VALIDO] {len(entrada)} linhas")

    linhas_formatadas = []

    for i, row in entrada.iterrows():
        try:
            data = row['valid']
            
            tmpc = float(row['tmpc']) if pd.notna(row['tmpc']) else 0.0
            dwpc = float(row['dwpc']) if pd.notna(row['dwpc']) else 0.0
            relh = float(row['relh']) if pd.notna(row['relh']) else 0.0

            pressao = extrair_pressao(row['metar'])

            drct = int(row['drct']) if pd.notna(row['drct']) and row['drct'] != 0 else 0
            sknt = float(row['sknt']) if pd.notna(row['sknt']) else 0.0
            velocidade = sknt * 0.514444

            radiacao_valor = 0
            if i < len(radiacao):
                try:
                    radiacao_valor = int(radiacao["Radiacao (KJ/m²)"].iloc[i])
                except:
                    radiacao_valor = 0

            skyc1 = str(row['skyc1']).strip().upper()
            cobertura = CLOUD_COVERAGE_MAP.get(skyc1, 0)

            vsby = float(row['vsby']) if pd.notna(row['vsby']) else 0.0
            visibilidade = round(vsby * 1609.34, 2) if vsby > 0 else 9999

            try:
                skyl1 = float(row['skyl1']) if pd.notna(row['skyl1']) else 0.0
                altura = math.ceil(skyl1 * 0.3048) if skyl1 > 0 else 9999
            except:
                altura = 9999

            linha = [
                str(data.year), data.month, data.day, data.hour, data.minute,
                9999, 9999, radiacao_valor, 9999, 9999,
                cobertura, cobertura,
                round(tmpc, 2), round(dwpc, 2),
                round(relh, 2),
                pressao,
                drct,
                round(velocidade, 2),
                visibilidade, altura,
                0, 9999, 99999, 9999, 999
            ]

            linhas_formatadas.append(linha)
            
        except Exception as e:
            print(f"[SKIP LINHA {i}] {e}")
            continue

    return linhas_formatadas

# =========================================================
# PROCESSAMENTO UPPERAIR (NetCDF)
# =========================================================

def processar_upperair(lista_arquivos_nc, pasta_destino):
    """
    Processa multiplos arquivos .grib2.nc (NetCDF) e gera CSV formatado.
    
    Args:
        lista_arquivos_nc: Lista com caminhos completos dos arquivos .grib2.nc
        pasta_destino: Pasta onde salvar o CSV final
    """
    
    if not lista_arquivos_nc:
        print("[AVISO] Nenhum arquivo UpperAir fornecido")
        return None
    
    saida_csv = os.path.join(pasta_destino, "upperair_tratado.csv")
    
    try:
        with open(saida_csv, mode='w', newline='', encoding='utf-8') as file:
            file.write('DATA,HORA,Pressao_hPa,Latitude,Longitude,Geopotential_Height_m,Temperatura_K,U_component_Wind_ms,V_component_Wind_ms\n')
            
            linhas_escritas = 0
            
            for caminho_arquivo in lista_arquivos_nc:
                if not os.path.exists(caminho_arquivo):
                    print(f"[AVISO] Arquivo nao encontrado: {caminho_arquivo}")
                    continue
                
                nome_arquivo = os.path.basename(caminho_arquivo)
                
                match = re.search(r'\.(\d{10})\.', nome_arquivo)
                if not match:
                    print(f"[AVISO] Data/hora nao encontrada em: {nome_arquivo}")
                    continue
                
                datahora_str = match.group(1)
                try:
                    datahora = datetime.strptime(datahora_str, "%Y%m%d%H")
                except ValueError:
                    print(f"[AVISO] Formato de data invalido em: {nome_arquivo}")
                    continue
                
                data_str = datahora.strftime("%Y-%m-%d")
                hora_str = datahora.strftime("%H:%M:%S")
                
                try:
                    nc = Dataset(caminho_arquivo, mode='r')
                except Exception as e:
                    print(f"[ERRO] Nao conseguiu abrir {nome_arquivo}: {e}")
                    continue
                
                try:
                    temperatura = nc.variables['TMP_L100'][0]
                    u = nc.variables['U_GRD_L100'][0]
                    v = nc.variables['V_GRD_L100'][0]
                    geopotencial = nc.variables['HGT_L100'][0]
                    pressao = nc.variables['level0'][:]
                    latitudes = nc.variables['lat'][:]
                    longitudes = nc.variables['lon'][:]
                except KeyError as e:
                    print(f"[ERRO] Variavel nao encontrada em {nome_arquivo}: {e}")
                    nc.close()
                    continue
                
                for nivel_idx, p in enumerate(pressao):
                    for lat_idx, lat in enumerate(latitudes):
                        for lon_idx, lon in enumerate(longitudes):
                            try:
                                linha = f"{data_str},{hora_str},{round(float(p), 2)},{round(float(lat), 4)},{round(float(lon), 4)},{round(float(geopotencial[nivel_idx, lat_idx, lon_idx]), 4)},{round(float(temperatura[nivel_idx, lat_idx, lon_idx]), 4)},{round(float(u[nivel_idx, lat_idx, lon_idx]), 4)},{round(float(v[nivel_idx, lat_idx, lon_idx]), 4)}\n"
                                file.write(linha)
                                linhas_escritas += 1
                            except Exception as e:
                                print(f"[SKIP] Erro em nivel {nivel_idx}, lat {lat_idx}, lon {lon_idx}: {e}")
                                continue
                
                nc.close()
                print(f"[UPPERAIR OK] {nome_arquivo} processado")
        
        print(f"[UPPERAIR FINAL] {linhas_escritas} linhas salvas em upperair_tratado.csv")
        return saida_csv
        
    except Exception as e:
        print(f"[ERRO FATAL] Nao conseguiu processar UpperAir: {e}")
        return None

# =========================================================
# PROCESSAMENTO UPPERAIR DAT (CALPUFF FORMAT - CORRETO)
# =========================================================

def gerar_upperair_dat(csv_upperair, pasta_destino):
    """
    Converte o CSV de UpperAir para formato DAT (CALPUFF) - FORMATO CORRETO
    Formato propriedade CALPUFF com cabeçalho e blocos de dados.
    """
    
    if not os.path.exists(csv_upperair):
        print(f"[AVISO] CSV UpperAir nao encontrado: {csv_upperair}")
        return None
    
    try:
        df = pd.read_csv(csv_upperair)
        print(f"[DAT] Carregado: {len(df)} linhas do CSV")
        
        # Cria coluna de data/hora para agrupamento
        df['DATAHORA'] = pd.to_datetime(df['DATA'] + " " + df['HORA'])
        
        # Extrai ano da primeira data
        primeira_data = df['DATAHORA'].iloc[0]
        ano = str(primeira_data.year)
        
        # Define caminho do DAT
        caminho_dat = os.path.join(pasta_destino, f"UpperAir_{ano}_Gerado.DAT")
        
        # Agrupa por DATA e HORA
        grupos = df.groupby(['DATAHORA'])
        
        with open(caminho_dat, "w", encoding="utf-8") as f_out:
            for _, grupo in grupos:
                linha_exemplo = grupo.iloc[0]
                data = linha_exemplo['DATAHORA']
                
                ano_bloco = data.year
                mes = data.month
                dia = data.day
                hora = data.hour
                minuto = data.minute
                
                # Cabeçalho do bloco
                f_out.write(f"   9999  {CODIGO_ESTACAO}    {ano_bloco:4d}  {mes:2d}  {dia:2d}  {hora:2d}    {minuto:1d}    "
                            f"{ano_bloco:4d}  {mes:2d}  {dia:2d}  {hora:2d}    {minuto:1d}   17       8\n")
                
                # Agora escreve as linhas com até 4 níveis por linha
                linhas_nivel = []
                for _, row in grupo.iterrows():
                    pressao = f"{row['Pressao_hPa']:.1f}"
                    altura = f"{row['Geopotential_Height_m']:.0f}."
                    temp = f"{row['Temperatura_K']:.1f}"
                    u = float(row['U_component_Wind_ms'])
                    v = float(row['V_component_Wind_ms'])
                    
                    # Calcula direção e velocidade do vento
                    direcao = (180 + (180 / 3.1415) * (v / (abs(u) + 0.0001))) % 360
                    velocidade = (u**2 + v**2) ** 0.5
                    
                    bloco = f"{pressao}\\ {altura}\\{temp}\\{int(direcao):3d}\\ {int(round(velocidade)):2d}"
                    linhas_nivel.append(bloco)
                
                # Divide em blocos de até 4 níveis por linha
                for i in range(0, len(linhas_nivel), 4):
                    f_out.write("    " + "    ".join(linhas_nivel[i:i+4]) + "\n")
        
        print(f"[DAT OK] {len(df)} linhas -> {caminho_dat}")
        return caminho_dat
        
    except Exception as e:
        print(f"[ERRO] Nao conseguiu gerar DAT: {e}")
        return None

# =========================================================
# MAIN
# =========================================================

def main():
    if len(sys.argv) != 5:
        print("Uso: script.py <SBVT.csv> <INMET.csv> <UPPERAIR_FILES> <PASTA_DESTINO>")
        print("  UPPERAIR_FILES: caminho1;caminho2;caminho3 (separados por ;)")
        sys.exit(1)

    caminho_sbvt = sys.argv[1]
    caminho_inmet = sys.argv[2]
    upperair_raw = sys.argv[3]
    pasta_destino = sys.argv[4]

    lista_upperair = [f.strip() for f in upperair_raw.split(';') if f.strip()]

    if not os.path.exists(caminho_sbvt):
        print(f"[ERRO] SBVT nao encontrado: {caminho_sbvt}")
        sys.exit(1)
    
    if not os.path.exists(caminho_inmet):
        print(f"[ERRO] INMET nao encontrado: {caminho_inmet}")
        sys.exit(1)
    
    if not lista_upperair:
        print(f"[ERRO] Nenhum arquivo UpperAir fornecido")
        sys.exit(1)
    
    for cam in lista_upperair:
        if not os.path.exists(cam):
            print(f"[ERRO] UpperAir nao encontrado: {cam}")
            sys.exit(1)

    os.makedirs(pasta_destino, exist_ok=True)

    print("[INICIO] Processamento...")
    
    print("[PROCESSANDO] INMET...")
    radiacao = processar_inmet(caminho_inmet, pasta_destino)
    
    print("[PROCESSANDO] SBVT...")
    linhas = processar_sbvt(caminho_sbvt, radiacao)
    df_saida = pd.DataFrame(linhas)
    caminho_csv_sbvt = os.path.join(pasta_destino, "teste2.csv")
    df_saida.to_csv(caminho_csv_sbvt, index=False, header=False)
    
    print("[PROCESSANDO] UpperAir...")
    csv_upperair = os.path.join(pasta_destino, "upperair_tratado.csv")
    processar_upperair(lista_upperair, pasta_destino)
    
    print("[GERANDO] UpperAir DAT (CALPUFF Format)...")
    gerar_upperair_dat(csv_upperair, pasta_destino)

    print(f"[OK] Concluido com sucesso!")
    print(f"[ARQUIVOS] radiacao_tratada.csv + teste2.csv ({len(linhas)} linhas) + upperair_tratado.csv + UpperAir_YYYY_Gerado.DAT")

if __name__ == "__main__":
    main()
