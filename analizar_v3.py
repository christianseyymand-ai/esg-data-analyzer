import anthropic
import pandas as pd

API_KEY = "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"  # reemplazá con tu key

# ══════════════════════════════════════════════
# FACTORES DE EMISION
# ══════════════════════════════════════════════

FACTORES_GRID = {
    "argentina": 0.321,
    "chile":     0.295,
    "peru":      0.247,
    "brasil":    0.075,
    "colombia":  0.126,
    "mexico":    0.454,
    "promedio_latam": 0.270,
}

FACTORES_COMBUSTIBLE = {
    "gasoil":  2.68,
    "diesel":  2.68,
    "nafta":   2.31,
    "gnc":     0.00202,
    "glp":     1.51,
}

# Scope 3 Cat 1 — factores por sector (kgCO2e por USD gastado)
# Fuente: EEIO US EPA adaptado a LatAm
FACTORES_SCOPE3_CAT1 = {
    "manufactura":       0.45,
    "servicios":         0.18,
    "tecnologia":        0.22,
    "construccion":      0.38,
    "alimentos":         0.52,
    "transporte":        0.41,
    "energia":           0.68,
    "quimica":           0.61,
    "retail":            0.25,
    "otro":              0.30,
}

# Scope 3 Cat 4 — transporte upstream (kgCO2e por ton-km)
FACTORES_TRANSPORTE = {
    "camion":      0.062,
    "tren":        0.022,
    "barco":       0.008,
    "avion_carga": 0.602,
}

# Scope 3 Cat 6 — viajes de negocio (kgCO2e por km por pasajero)
FACTORES_VIAJES = {
    "avion_corto":  0.255,   # < 3hs
    "avion_largo":  0.195,   # > 3hs (más eficiente por km)
    "auto":         0.171,
    "taxi_remis":   0.171,
    "bus":          0.027,
    "tren_viaje":   0.041,
}

# Scope 3 Cat 7 — transporte empleados (kgCO2e por km por empleado)
FACTORES_COMMUTING = {
    "auto_solo":    0.171,
    "auto_compartido": 0.085,
    "bus_publico":  0.027,
    "subte_metro":  0.011,
    "moto":         0.103,
    "bicicleta":    0.000,
    "caminando":    0.000,
}

# ══════════════════════════════════════════════
# CONVERSIONES
# ══════════════════════════════════════════════

CONVERSIONES = {
    "kwh":       {"factor": 1,        "base": "kWh"},
    "mwh":       {"factor": 1000,     "base": "kWh"},
    "gj":        {"factor": 277.78,   "base": "kWh"},
    "litros":    {"factor": 1,        "base": "litros"},
    "m3":        {"factor": 1000,     "base": "litros"},
    "galones":   {"factor": 3.785,    "base": "litros"},
    "toneladas": {"factor": 1,        "base": "toneladas"},
    "kg":        {"factor": 0.001,    "base": "toneladas"},
}

def convertir(valor, unidad):
    u = unidad.lower().strip()
    if u in CONVERSIONES:
        return valor * CONVERSIONES[u]["factor"], CONVERSIONES[u]["base"]
    return valor, unidad

# ══════════════════════════════════════════════
# CALCULOS SCOPE 1 y 2
# ══════════════════════════════════════════════

def scope1(litros, combustible):
    factor = FACTORES_COMBUSTIBLE.get(combustible.lower(), 2.68)
    return round((litros * factor) / 1000, 2)

def scope2(kwh, pais):
    factor = FACTORES_GRID.get(pais.lower(), FACTORES_GRID["promedio_latam"])
    return round((kwh * factor) / 1000, 2)

# ══════════════════════════════════════════════
# CALCULOS SCOPE 3
# ══════════════════════════════════════════════

def scope3_cat1(gastos_por_sector):
    """
    Cat 1 — Bienes y servicios comprados (spend-based)
    Input: dict con {sector: monto_usd}
    Ej: {"manufactura": 500000, "servicios": 200000}
    """
    total = 0
    detalle = {}
    for sector, monto in gastos_por_sector.items():
        factor = FACTORES_SCOPE3_CAT1.get(sector.lower(), FACTORES_SCOPE3_CAT1["otro"])
        tco2e = round((monto * factor) / 1000, 2)
        detalle[sector] = tco2e
        total += tco2e
    return round(total, 2), detalle

def scope3_cat4(envios):
    """
    Cat 4 — Transporte upstream
    Input: lista de dicts [{medio, toneladas, km}]
    Ej: [{"medio": "camion", "toneladas": 500, "km": 800}]
    """
    total = 0
    for e in envios:
        factor = FACTORES_TRANSPORTE.get(e["medio"].lower(), 0.062)
        tco2e = (e["toneladas"] * e["km"] * factor) / 1000
        total += tco2e
    return round(total, 2)

def scope3_cat6(viajes):
    """
    Cat 6 — Viajes de negocio
    Input: lista de dicts [{tipo, cantidad_viajes, km_promedio}]
    Ej: [{"tipo": "avion_corto", "cantidad_viajes": 50, "km_promedio": 800}]
    """
    total = 0
    for v in viajes:
        factor = FACTORES_VIAJES.get(v["tipo"].lower(), 0.171)
        tco2e = (v["cantidad_viajes"] * v["km_promedio"] * factor) / 1000
        total += tco2e
    return round(total, 2)

def scope3_cat7(empleados, modos_transporte):
    """
    Cat 7 — Transporte empleados (commuting)
    Input: cantidad empleados, dict {modo: porcentaje}
    Ej: {"auto_solo": 0.6, "bus_publico": 0.3, "bicicleta": 0.1}
    dias_laborales: dias al año que viajan
    """
    dias = 220  # dias laborales promedio por año
    km_promedio_diario = 25  # km ida y vuelta promedio
    total = 0
    for modo, porcentaje in modos_transporte.items():
        factor = FACTORES_COMMUTING.get(modo.lower(), 0.171)
        empleados_modo = empleados * porcentaje
        tco2e = (empleados_modo * km_promedio_diario * dias * factor) / 1000
        total += tco2e
    return round(total, 2)

# ══════════════════════════════════════════════
# DATOS DE EMPRESAS — como llegarian de un cliente real
# ══════════════════════════════════════════════

empresas = [
    {
        "nombre": "Acme Manufacturing",
        "pais": "argentina",
        "empleados": 320,
        # Scope 1 y 2
        "electricidad": {"valor": 8200, "unidad": "MWh"},
        "combustible":  {"valor": 45000, "unidad": "litros", "tipo": "gasoil"},
        # Scope 3 Cat 1 — gastos por sector de proveedor
        "gastos_proveedores": {
            "manufactura": 8500000,
            "energia":      1200000,
            "transporte":   950000,
            "servicios":    600000,
        },
        # Scope 3 Cat 4 — fletes recibidos
        "fletes": [
            {"medio": "camion", "toneladas": 1200, "km": 600},
            {"medio": "tren",   "toneladas": 800,  "km": 1200},
        ],
        # Scope 3 Cat 6 — viajes de negocio
        "viajes_negocio": [
            {"tipo": "avion_corto", "cantidad_viajes": 80,  "km_promedio": 900},
            {"tipo": "auto",        "cantidad_viajes": 200, "km_promedio": 150},
        ],
        # Scope 3 Cat 7 — commuting
        "commuting": {
            "auto_solo":     0.55,
            "bus_publico":   0.30,
            "moto":          0.10,
            "bicicleta":     0.05,
        },
    },
    {
        "nombre": "GreenTech Ltd",
        "pais": "chile",
        "empleados": 95,
        "electricidad": {"valor": 2800, "unidad": "MWh"},
        "combustible":  {"valor": 12000, "unidad": "galones", "tipo": "diesel"},
        "gastos_proveedores": {
            "tecnologia": 3200000,
            "servicios":  1800000,
            "otro":        400000,
        },
        "fletes": [
            {"medio": "camion", "toneladas": 200, "km": 400},
        ],
        "viajes_negocio": [
            {"tipo": "avion_largo", "cantidad_viajes": 30, "km_promedio": 3500},
            {"tipo": "avion_corto", "cantidad_viajes": 45, "km_promedio": 700},
        ],
        "commuting": {
            "auto_solo":      0.40,
            "subte_metro":    0.35,
            "bus_publico":    0.20,
            "bicicleta":      0.05,
        },
    },
    {
        "nombre": "RetailCo",
        "pais": "peru",
        "empleados": 1200,
        "electricidad": {"valor": 12240, "unidad": "GJ"},
        "combustible":  {"valor": 8500, "unidad": "litros", "tipo": "nafta"},
        "gastos_proveedores": {
            "retail":        22000000,
            "transporte":     4500000,
            "servicios":      2000000,
            "alimentos":      1500000,
        },
        "fletes": [
            {"medio": "camion", "toneladas": 5000, "km": 300},
            {"medio": "barco",  "toneladas": 2000, "km": 8000},
        ],
        "viajes_negocio": [
            {"tipo": "avion_corto", "cantidad_viajes": 120, "km_promedio": 600},
            {"tipo": "auto",        "cantidad_viajes": 800, "km_promedio": 80},
        ],
        "commuting": {
            "bus_publico":   0.50,
            "auto_solo":     0.25,
            "moto":          0.15,
            "caminando":     0.10,
        },
    },
]

# ══════════════════════════════════════════════
# PROCESAMIENTO
# ══════════════════════════════════════════════

print("=== ESG ANALYZER v3 — SCOPE 1 + 2 + 3 ===\n")

registros = []

for e in empresas:
    print(f"Procesando: {e['nombre']} ({e['pais'].upper()})")

    # Scope 1 y 2
    elec_kwh, _ = convertir(e["electricidad"]["valor"], e["electricidad"]["unidad"])
    comb_litros, _ = convertir(e["combustible"]["valor"], e["combustible"]["unidad"])

    s1 = scope1(comb_litros, e["combustible"]["tipo"])
    s2 = scope2(elec_kwh, e["pais"])

    # Scope 3
    s3_cat1, detalle_cat1 = scope3_cat1(e["gastos_proveedores"])
    s3_cat4 = scope3_cat4(e["fletes"])
    s3_cat6 = scope3_cat6(e["viajes_negocio"])
    s3_cat7 = scope3_cat7(e["empleados"], e["commuting"])
    s3_total = round(s3_cat1 + s3_cat4 + s3_cat6 + s3_cat7, 2)

    total = round(s1 + s2 + s3_total, 2)
    s3_pct = round((s3_total / total) * 100, 1)

    print(f"  Scope 1: {s1} tCO2e")
    print(f"  Scope 2: {s2} tCO2e")
    print(f"  Scope 3 Cat1 (proveedores): {s3_cat1} tCO2e")
    print(f"  Scope 3 Cat4 (flete):       {s3_cat4} tCO2e")
    print(f"  Scope 3 Cat6 (viajes):      {s3_cat6} tCO2e")
    print(f"  Scope 3 Cat7 (commuting):   {s3_cat7} tCO2e")
    print(f"  TOTAL: {total} tCO2e — Scope 3 representa {s3_pct}%\n")

    registros.append({
        "empresa":        e["nombre"],
        "pais":           e["pais"],
        "empleados":      e["empleados"],
        "scope1_tco2e":   s1,
        "scope2_tco2e":   s2,
        "s3_cat1_proveedores": s3_cat1,
        "s3_cat4_flete":       s3_cat4,
        "s3_cat6_viajes":      s3_cat6,
        "s3_cat7_commuting":   s3_cat7,
        "scope3_total":   s3_total,
        "total_tco2e":    total,
        "scope3_pct":     s3_pct,
    })

df = pd.DataFrame(registros)
df.to_csv("esg_inventario_completo.csv", index=False)
print("Dataset guardado como 'esg_inventario_completo.csv'\n")

# ══════════════════════════════════════════════
# ANALISIS CON CLAUDE
# ══════════════════════════════════════════════

print("--- MANDANDO A CLAUDE PARA ANALISIS ---")

tabla = df[["empresa", "scope1_tco2e", "scope2_tco2e",
            "s3_cat1_proveedores", "s3_cat4_flete",
            "s3_cat6_viajes", "s3_cat7_commuting",
            "scope3_total", "total_tco2e", "scope3_pct"]].to_string(index=False)

prompt = f"""Sos un analista ESG experto en GHG Protocol Corporate Standard.
Analizá este inventario completo de emisiones Scope 1, 2 y 3 de 3 empresas en LatAm.

INVENTARIO GHG COMPLETO (tCO2e):
{tabla}

Scope 3 calculado con:
- Cat 1: método spend-based (EEIO)
- Cat 4: método distancia (ton-km)
- Cat 6: método distancia (pasajero-km)
- Cat 7: método distancia (empleado-km)

Tu reporte debe incluir:
1. Ranking por emisiones totales y por intensidad
2. Análisis de la estructura de Scope 3 — qué categoría domina y por qué
3. Qué empresa tiene mejor perfil para una estrategia SBTi
4. Las 3 medidas de mayor impacto por empresa (priorizadas por tCO2e reducible)
5. Limitaciones metodológicas de este inventario

Sé técnico. Máximo 500 palabras."""

client = anthropic.Anthropic(api_key=API_KEY)

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1200,
    messages=[{"role": "user", "content": prompt}]
)

reporte = response.content[0].text

print("\n" + "="*50)
print("REPORTE ESG — INVENTARIO COMPLETO SCOPE 1+2+3")
print("="*50)
print(reporte)

supuestos = f"""
SUPUESTOS METODOLOGICOS:
- Scope 3 Cat 1: método spend-based con factores EEIO adaptados a LatAm
- Scope 3 Cat 4: factor por modo de transporte (ton-km)
- Scope 3 Cat 6: factor por tipo de vuelo/transporte (pasajero-km)
- Scope 3 Cat 7: 220 días laborales, 25 km/día promedio ida y vuelta
- Factores de grid: AR=0.321 | CL=0.295 | PE=0.247 kgCO2e/kWh (fuente: IEA 2023)
- Factores combustible: diesel/gasoil=2.68 | nafta=2.31 kgCO2e/litro (fuente: IPCC AR6)
"""

with open("reporte_esg_v3.txt", "w", encoding="utf-8") as f:
    f.write("REPORTE ESG v3 — INVENTARIO COMPLETO SCOPE 1+2+3\n")
    f.write("="*50 + "\n")
    f.write(supuestos + "\n")
    f.write("="*50 + "\n\n")
    f.write(reporte)

print("\n" + "="*50)
print("Archivos generados:")
print("  - esg_inventario_completo.csv")
print("  - reporte_esg_v3.txt")
