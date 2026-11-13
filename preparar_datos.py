"""
preparar_datos.py
Inicializa la base de datos SQLite del Observatorio de Educación Superior (OES).
Práctica Guiada N.° 08 — Prototipo académico de monitoreo institucional.
"""

import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("oes.db")

with sqlite3.connect(DB) as con:
    # ── Crear tabla principal (desnormalizada para el laboratorio) ──────────
    con.execute("""
        CREATE TABLE IF NOT EXISTS noticias (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo      TEXT NOT NULL,
            institucion TEXT NOT NULL,
            categoria   TEXT NOT NULL,
            fuente      TEXT NOT NULL,
            fecha       TEXT NOT NULL,
            url         TEXT NOT NULL UNIQUE,
            resumen     TEXT NOT NULL
        )
    """)

    # ── Datos demostrativos (NO son noticias verificadas) ───────────────────
    datos = [
        (
            "PRONABEC lanza convocatoria de becas de pregrado 2027",
            "PRONABEC",
            "Ente rector",
            "Portal institucional (ejemplo)",
            "2026-11-06",
            "https://www.pronabec.gob.pe/",
            "Registro didáctico: verificar la nota original en el portal antes de usar institucionalmente.",
        ),
        (
            "UNMSM presenta resultados de investigación en congreso internacional",
            "UNMSM",
            "Universidad pública",
            "Portal institucional (ejemplo)",
            "2026-11-06",
            "https://www.unmsm.edu.pe/",
            "Registro didáctico: verificar noticia original en el portal de la universidad.",
        ),
        (
            "PUCP incorpora nuevo programa de Inteligencia Artificial",
            "PUCP",
            "Universidad privada",
            "Portal institucional (ejemplo)",
            "2026-11-05",
            "https://www.pucp.edu.pe/",
            "Registro didáctico: verificar noticia original en el portal de la universidad.",
        ),
        (
            "SUNEDU publica ranking de universidades licenciadas 2026",
            "SUNEDU",
            "Ente rector",
            "Portal institucional (ejemplo)",
            "2026-11-07",
            "https://www.sunedu.gob.pe/",
            "Registro didáctico: verificar la resolución original en el portal de SUNEDU.",
        ),
        (
            "CONCYTEC financia 50 proyectos de ciencia básica para universidades regionales",
            "CONCYTEC",
            "Ente rector",
            "Portal institucional (ejemplo)",
            "2026-11-04",
            "https://www.concytec.gob.pe/",
            "Registro didáctico: verificar la convocatoria original en el portal de CONCYTEC.",
        ),
        (
            "MINEDU aprueba nuevo reglamento de educación superior tecnológica",
            "MINEDU",
            "Ente rector",
            "Portal institucional (ejemplo)",
            "2026-11-03",
            "https://www.minedu.gob.pe/",
            "Registro didáctico: verificar resolución en el Diario Oficial El Peruano.",
        ),
        (
            "Universidad de Lima anuncia doble titulación con institución europea",
            "Universidad de Lima",
            "Universidad privada",
            "Portal institucional (ejemplo)",
            "2026-11-02",
            "https://www.ulima.edu.pe/",
            "Registro didáctico: verificar noticia original en el portal de la universidad.",
        ),
        (
            "UNSA lidera producción científica en universidades del sur del Perú",
            "UNSA",
            "Universidad pública",
            "Portal institucional (ejemplo)",
            "2026-11-01",
            "https://www.unsa.edu.pe/",
            "Registro didáctico: verificar artículo original en el repositorio institucional.",
        ),
    ]

    con.executemany(
        """
        INSERT OR IGNORE INTO noticias
            (titulo, institucion, categoria, fuente, fecha, url, resumen)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        datos,
    )

    total = con.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]

print(f"✓ Base de datos creada/actualizada: {DB}")
print(f"  Registros en tabla noticias: {total}")
print()
print("AVISO: Los registros son DEMOSTRATIVOS.")
print("Las URLs apuntan a portales institucionales, no a artículos específicos.")
print("Reemplázalos con noticias reales verificadas para uso institucional.")

