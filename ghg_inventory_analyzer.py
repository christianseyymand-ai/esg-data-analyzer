"""
GHG Inventory Analyzer

Portfolio project for ESG / carbon accounting workflows.

What it does:
- Calculates Scope 1 emissions from fuel consumption.
- Calculates Scope 2 emissions from electricity consumption.
- Calculates selected Scope 3 categories:
  - Category 1: Purchased goods and services
  - Category 4: Upstream transportation and distribution
  - Category 6: Business travel
  - Category 7: Employee commuting
- Exports a complete emissions inventory as CSV.
- Optionally generates an AI-assisted ESG report using Anthropic Claude.

Before running the AI report:
1. Create a .env file.
2. Add: ANTHROPIC_API_KEY=your_api_key_here

Run:
    python ghg_inventory_analyzer.py

Optional:
    python ghg_inventory_analyzer.py --no-ai
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv

try:
    import anthropic
except ImportError:  # Allows the calculator to run even if Anthropic is not installed.
    anthropic = None


# =============================================================================
# EMISSION FACTORS
# =============================================================================

# Grid emission factors in kgCO2e per kWh.
FACTORES_GRID = {
    "argentina": 0.321,
    "chile": 0.295,
    "peru": 0.247,
    "brasil": 0.075,
    "colombia": 0.126,
    "mexico": 0.454,
    "promedio_latam": 0.270,
}

# Fuel emission factors in kgCO2e per liter.
FACTORES_COMBUSTIBLE = {
    "gasoil": 2.68,
    "diesel": 2.68,
    "nafta": 2.31,
    "gnc": 0.00202,
    "glp": 1.51,
}

# Scope 3 Category 1 — purchased goods and services.
# Spend-based factors in kgCO2e per USD spent.
# Portfolio assumption: EEIO-style factors adapted for a LatAm case study.
FACTORES_SCOPE3_CAT1 = {
    "manufactura": 0.45,
    "servicios": 0.18,
    "tecnologia": 0.22,
    "construccion": 0.38,
    "alimentos": 0.52,
    "transporte": 0.41,
    "energia": 0.68,
    "quimica": 0.61,
    "retail": 0.25,
    "otro": 0.30,
}

# Scope 3 Category 4 — upstream transportation and distribution.
# Factors in kgCO2e per ton-km.
FACTORES_TRANSPORTE = {
    "camion": 0.062,
    "tren": 0.022,
    "barco": 0.008,
    "avion_carga": 0.602,
}

# Scope 3 Category 6 — business travel.
# Factors in kgCO2e per passenger-km.
FACTORES_VIAJES = {
    "avion_corto": 0.255,
    "avion_largo": 0.195,
    "auto": 0.171,
    "taxi_remis": 0.171,
    "bus": 0.027,
    "tren_viaje": 0.041,
}

# Scope 3 Category 7 — employee commuting.
# Factors in kgCO2e per employee-km.
FACTORES_COMMUTING = {
    "auto_solo": 0.171,
    "auto_compartido": 0.085,
    "bus_publico": 0.027,
    "subte_metro": 0.011,
    "moto": 0.103,
    "bicicleta": 0.000,
    "caminando": 0.000,
}


# =============================================================================
# UNIT CONVERSIONS
# =============================================================================

CONVERSIONES = {
    "kwh": {"factor": 1, "base": "kWh"},
    "mwh": {"factor": 1000, "base": "kWh"},
    "gj": {"factor": 277.78, "base": "kWh"},
    "litros": {"factor": 1, "base": "litros"},
    "m3": {"factor": 1000, "base": "litros"},
    "galones": {"factor": 3.785, "base": "litros"},
    "toneladas": {"factor": 1, "base": "toneladas"},
    "kg": {"factor": 0.001, "base": "toneladas"},
}


def convertir(valor: float, unidad: str) -> tuple[float, str]:
    """Convert an input value into the calculator's base unit."""
    unidad_normalizada = unidad.lower().strip()

    if unidad_normalizada in CONVERSIONES:
        conversion = CONVERSIONES[unidad_normalizada]
        return valor * conversion["factor"], conversion["base"]

    return valor, unidad


# =============================================================================
# SCOPE 1 AND SCOPE 2 CALCULATIONS
# =============================================================================

def calcular_scope1(litros: float, combustible: str) -> float:
    """Calculate Scope 1 emissions from fuel consumption."""
    factor = FACTORES_COMBUSTIBLE.get(
        combustible.lower(),
        FACTORES_COMBUSTIBLE["diesel"],
    )
    return round((litros * factor) / 1000, 2)


def calcular_scope2(kwh: float, pais: str) -> float:
    """Calculate Scope 2 emissions from electricity consumption."""
    factor = FACTORES_GRID.get(
        pais.lower(),
        FACTORES_GRID["promedio_latam"],
    )
    return round((kwh * factor) / 1000, 2)


# =============================================================================
# SCOPE 3 CALCULATIONS
# =============================================================================

def calcular_scope3_cat1(gastos_por_sector: dict[str, float]) -> tuple[float, dict[str, float]]:
    """
    Scope 3 Category 1 — Purchased goods and services.

    Method: spend-based.
    Input example:
        {"manufactura": 500000, "servicios": 200000}
    """
    total = 0.0
    detalle = {}

    for sector, monto in gastos_por_sector.items():
        factor = FACTORES_SCOPE3_CAT1.get(
            sector.lower(),
            FACTORES_SCOPE3_CAT1["otro"],
        )
        tco2e = round((monto * factor) / 1000, 2)
        detalle[sector] = tco2e
        total += tco2e

    return round(total, 2), detalle


def calcular_scope3_cat4(envios: list[dict[str, Any]]) -> float:
    """
    Scope 3 Category 4 — Upstream transportation and distribution.

    Method: distance-based, using ton-km.
    Input example:
        [{"medio": "camion", "toneladas": 500, "km": 800}]
    """
    total = 0.0

    for envio in envios:
        factor = FACTORES_TRANSPORTE.get(
            envio["medio"].lower(),
            FACTORES_TRANSPORTE["camion"],
        )
        tco2e = (envio["toneladas"] * envio["km"] * factor) / 1000
        total += tco2e

    return round(total, 2)


def calcular_scope3_cat6(viajes: list[dict[str, Any]]) -> float:
    """
    Scope 3 Category 6 — Business travel.

    Method: distance-based, using passenger-km.
    Input example:
        [{"tipo": "avion_corto", "cantidad_viajes": 50, "km_promedio": 800}]
    """
    total = 0.0

    for viaje in viajes:
        factor = FACTORES_VIAJES.get(
            viaje["tipo"].lower(),
            FACTORES_VIAJES["auto"],
        )
        tco2e = (
            viaje["cantidad_viajes"]
            * viaje["km_promedio"]
            * factor
        ) / 1000
        total += tco2e

    return round(total, 2)


def calcular_scope3_cat7(empleados: int, modos_transporte: dict[str, float]) -> float:
    """
    Scope 3 Category 7 — Employee commuting.

    Method: distance-based.
    Portfolio assumptions:
    - 220 working days per year.
    - 25 km per day round trip average.
    - Transport mode split provided as percentages.
    """
    dias_laborales = 220
    km_promedio_diario = 25
    total = 0.0

    for modo, porcentaje in modos_transporte.items():
        factor = FACTORES_COMMUTING.get(
            modo.lower(),
            FACTORES_COMMUTING["auto_solo"],
        )
        empleados_modo = empleados * porcentaje
        tco2e = (
            empleados_modo
            * km_promedio_diario
            * dias_laborales
            * factor
        ) / 1000
        total += tco2e

    return round(total, 2)


# =============================================================================
# SAMPLE COMPANY DATA
# =============================================================================

EMPRESAS = [
    {
        "nombre": "Acme Manufacturing",
        "pais": "argentina",
        "empleados": 320,
        "electricidad": {"valor": 8200, "unidad": "MWh"},
        "combustible": {"valor": 45000, "unidad": "litros", "tipo": "gasoil"},
        "gastos_proveedores": {
            "manufactura": 8500000,
            "energia": 1200000,
            "transporte": 950000,
            "servicios": 600000,
        },
        "fletes": [
            {"medio": "camion", "toneladas": 1200, "km": 600},
            {"medio": "tren", "toneladas": 800, "km": 1200},
        ],
        "viajes_negocio": [
            {"tipo": "avion_corto", "cantidad_viajes": 80, "km_promedio": 900},
            {"tipo": "auto", "cantidad_viajes": 200, "km_promedio": 150},
        ],
        "commuting": {
            "auto_solo": 0.55,
            "bus_publico": 0.30,
            "moto": 0.10,
            "bicicleta": 0.05,
        },
    },
    {
        "nombre": "GreenTech Ltd",
        "pais": "chile",
        "empleados": 95,
        "electricidad": {"valor": 2800, "unidad": "MWh"},
        "combustible": {"valor": 12000, "unidad": "galones", "tipo": "diesel"},
        "gastos_proveedores": {
            "tecnologia": 3200000,
            "servicios": 1800000,
            "otro": 400000,
        },
        "fletes": [
            {"medio": "camion", "toneladas": 200, "km": 400},
        ],
        "viajes_negocio": [
            {"tipo": "avion_largo", "cantidad_viajes": 30, "km_promedio": 3500},
            {"tipo": "avion_corto", "cantidad_viajes": 45, "km_promedio": 700},
        ],
        "commuting": {
            "auto_solo": 0.40,
            "subte_metro": 0.35,
            "bus_publico": 0.20,
            "bicicleta": 0.05,
        },
    },
    {
        "nombre": "RetailCo",
        "pais": "peru",
        "empleados": 1200,
        "electricidad": {"valor": 12240, "unidad": "GJ"},
        "combustible": {"valor": 8500, "unidad": "litros", "tipo": "nafta"},
        "gastos_proveedores": {
            "retail": 22000000,
            "transporte": 4500000,
            "servicios": 2000000,
            "alimentos": 1500000,
        },
        "fletes": [
            {"medio": "camion", "toneladas": 5000, "km": 300},
            {"medio": "barco", "toneladas": 2000, "km": 8000},
        ],
        "viajes_negocio": [
            {"tipo": "avion_corto", "cantidad_viajes": 120, "km_promedio": 600},
            {"tipo": "auto", "cantidad_viajes": 800, "km_promedio": 80},
        ],
        "commuting": {
            "bus_publico": 0.50,
            "auto_solo": 0.25,
            "moto": 0.15,
            "caminando": 0.10,
        },
    },
]


# =============================================================================
# PROCESSING
# =============================================================================

def construir_inventario(empresas: list[dict[str, Any]]) -> pd.DataFrame:
    """Build a complete GHG inventory DataFrame from company activity data."""
    registros = []

    print("=== ESG Data Analyzer — Scope 1, 2 and 3 ===\n")

    for empresa in empresas:
        print(f"Processing: {empresa['nombre']} ({empresa['pais'].upper()})")

        electricidad_kwh, _ = convertir(
            empresa["electricidad"]["valor"],
            empresa["electricidad"]["unidad"],
        )
        combustible_litros, _ = convertir(
            empresa["combustible"]["valor"],
            empresa["combustible"]["unidad"],
        )

        scope1 = calcular_scope1(
            combustible_litros,
            empresa["combustible"]["tipo"],
        )
        scope2 = calcular_scope2(electricidad_kwh, empresa["pais"])

        scope3_cat1, _ = calcular_scope3_cat1(empresa["gastos_proveedores"])
        scope3_cat4 = calcular_scope3_cat4(empresa["fletes"])
        scope3_cat6 = calcular_scope3_cat6(empresa["viajes_negocio"])
        scope3_cat7 = calcular_scope3_cat7(
            empresa["empleados"],
            empresa["commuting"],
        )

        scope3_total = round(
            scope3_cat1 + scope3_cat4 + scope3_cat6 + scope3_cat7,
            2,
        )
        total = round(scope1 + scope2 + scope3_total, 2)
        scope3_pct = round((scope3_total / total) * 100, 1) if total else 0

        print(f"  Scope 1: {scope1} tCO2e")
        print(f"  Scope 2: {scope2} tCO2e")
        print(f"  Scope 3 Cat. 1 - Purchased goods and services: {scope3_cat1} tCO2e")
        print(f"  Scope 3 Cat. 4 - Upstream transportation:     {scope3_cat4} tCO2e")
        print(f"  Scope 3 Cat. 6 - Business travel:             {scope3_cat6} tCO2e")
        print(f"  Scope 3 Cat. 7 - Employee commuting:          {scope3_cat7} tCO2e")
        print(f"  Total: {total} tCO2e | Scope 3 share: {scope3_pct}%\n")

        registros.append(
            {
                "company": empresa["nombre"],
                "country": empresa["pais"],
                "employees": empresa["empleados"],
                "scope1_tco2e": scope1,
                "scope2_tco2e": scope2,
                "scope3_cat1_purchased_goods_services_tco2e": scope3_cat1,
                "scope3_cat4_upstream_transport_tco2e": scope3_cat4,
                "scope3_cat6_business_travel_tco2e": scope3_cat6,
                "scope3_cat7_employee_commuting_tco2e": scope3_cat7,
                "scope3_total_tco2e": scope3_total,
                "total_tco2e": total,
                "scope3_share_pct": scope3_pct,
                "emissions_intensity_tco2e_per_employee": round(
                    total / empresa["empleados"],
                    2,
                ),
            }
        )

    return pd.DataFrame(registros)


def generar_prompt_reporte(df: pd.DataFrame) -> str:
    """Create the prompt used for the AI-assisted ESG report."""
    columnas = [
        "company",
        "scope1_tco2e",
        "scope2_tco2e",
        "scope3_cat1_purchased_goods_services_tco2e",
        "scope3_cat4_upstream_transport_tco2e",
        "scope3_cat6_business_travel_tco2e",
        "scope3_cat7_employee_commuting_tco2e",
        "scope3_total_tco2e",
        "total_tco2e",
        "scope3_share_pct",
        "emissions_intensity_tco2e_per_employee",
    ]
    tabla = df[columnas].to_string(index=False)

    return f"""You are an ESG analyst specialized in the GHG Protocol Corporate Standard.
Analyze this Scope 1, Scope 2 and Scope 3 emissions inventory for three companies in Latin America.

GHG INVENTORY, in tCO2e:
{tabla}

Scope 3 calculation methods:
- Category 1: spend-based method
- Category 4: distance-based method using ton-km
- Category 6: distance-based method using passenger-km
- Category 7: distance-based method using employee-km

Your report must include:
1. Ranking by total emissions and emissions intensity.
2. Analysis of the Scope 3 structure: which category dominates and why.
3. Which company has the best profile for an SBTi-style decarbonization strategy.
4. The three highest-impact reduction measures for each company, prioritized by reducible tCO2e.
5. Methodological limitations of this inventory.

Be technical, clear and concise. Maximum 500 words."""


def generar_reporte_con_claude(df: pd.DataFrame) -> str | None:
    """Generate an AI-assisted ESG report with Anthropic Claude, if configured."""
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    if not api_key:
        print("No ANTHROPIC_API_KEY found. Skipping AI report generation.")
        return None

    if anthropic is None:
        print("The 'anthropic' package is not installed. Skipping AI report generation.")
        return None

    print("--- Sending inventory to Claude for ESG analysis ---")

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=1200,
        messages=[
            {
                "role": "user",
                "content": generar_prompt_reporte(df),
            }
        ],
    )

    return response.content[0].text


def supuestos_metodologicos() -> str:
    """Return methodological assumptions for the exported report."""
    return """
METHODOLOGICAL ASSUMPTIONS

- Scope 1: calculated from fuel consumption using fuel-specific emission factors.
- Scope 2: location-based method using country-level grid emission factors.
- Scope 3 Category 1: spend-based method using EEIO-style sector factors.
- Scope 3 Category 4: distance-based method by transport mode, using ton-km.
- Scope 3 Category 6: distance-based method by travel type, using passenger-km.
- Scope 3 Category 7: distance-based method using employee commuting assumptions.
- Employee commuting assumption: 220 working days per year and 25 km/day round trip.
- Grid factors used in this case study:
  AR=0.321 | CL=0.295 | PE=0.247 kgCO2e/kWh.
- Fuel factors used in this case study:
  diesel/gasoil=2.68 | gasoline/nafta=2.31 kgCO2e/liter.

Note: This is a portfolio case study. For production use, factors should be replaced
with verified, source-specific and year-specific emission factors.
""".strip()


def exportar_resultados(
    df: pd.DataFrame,
    output_dir: Path,
    reporte: str | None,
) -> None:
    """Export the inventory and ESG report to the outputs folder."""
    output_dir.mkdir(parents=True, exist_ok=True)

    inventory_path = output_dir / "ghg_inventory_complete.csv"
    report_path = output_dir / "esg_report_ai_assisted.txt"

    df.to_csv(inventory_path, index=False)

    if reporte:
        report_body = reporte
    else:
        report_body = (
            "AI-assisted report was not generated because ANTHROPIC_API_KEY "
            "was not configured.\n\n"
            "The emissions inventory CSV was still generated successfully."
        )

    with report_path.open("w", encoding="utf-8") as file:
        file.write("ESG REPORT — COMPLETE GHG INVENTORY SCOPE 1, 2 AND 3\n")
        file.write("=" * 64 + "\n\n")
        file.write(supuestos_metodologicos())
        file.write("\n\n" + "=" * 64 + "\n\n")
        file.write(report_body)

    print("=" * 50)
    print("Generated files:")
    print(f"  - {inventory_path}")
    print(f"  - {report_path}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate a Scope 1, 2 and 3 GHG inventory and generate ESG outputs.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Folder where generated outputs will be saved. Default: outputs",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip the AI-assisted report generation.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the ESG Data Analyzer workflow."""
    args = parse_args()

    inventory_df = construir_inventario(EMPRESAS)
    reporte = None if args.no_ai else generar_reporte_con_claude(inventory_df)

    if reporte:
        print("\n" + "=" * 50)
        print("AI-ASSISTED ESG REPORT")
        print("=" * 50)
        print(reporte)
        print()

    exportar_resultados(
        df=inventory_df,
        output_dir=Path(args.output_dir),
        reporte=reporte,
    )


if __name__ == "__main__":
    main()
