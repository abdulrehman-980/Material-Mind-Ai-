"""
MaterialMind API — Phase 1 MVP

An AI-powered engineering material selection and comparison service.
Combines a verified 72-material database with Gemini-powered reasoning,
falling back to deterministic scoring or clearly-labeled AI estimates
whenever a verified match or the AI itself is unavailable.
"""

import io
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import google.generativeai as genai
import pandas as pd
import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("materialmind")


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

class Config:
    """Centralized environment configuration."""

    PROJECT_ID = os.getenv("PROJECT_ID", "material-ai")
    BUCKET_NAME = os.getenv("BUCKET_NAME", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    GEMINI_MODEL_NAME = "gemini-flash-latest"


if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(Config.GEMINI_MODEL_NAME)
    GEMINI_AVAILABLE = True
    logger.info("Gemini configured successfully with model '%s'.", Config.GEMINI_MODEL_NAME)
else:
    GEMINI_AVAILABLE = False
    gemini_model = None
    logger.warning("GEMINI_API_KEY not set — running in fallback mode without AI features.")


# --------------------------------------------------------------------------
# Request/response schemas
# --------------------------------------------------------------------------

class MaterialSearch(BaseModel):
    query: str
    category: Optional[str] = None
    min_tensile_strength: Optional[int] = None
    max_density: Optional[float] = None
    application: Optional[str] = None
    limit: int = 20


class MaterialComparison(BaseModel):
    material_ids: List[int]
    focus: Optional[str] = "all"


class RecommendationRequest(BaseModel):
    application: str
    requirements: Dict[str, str]
    budget: Optional[str] = None
    sustainability_priority: bool = False


class ManufacturingRequest(BaseModel):
    material_id: int
    quantity: Optional[int] = 100
    desired_processes: Optional[List[str]] = None
    budget_priority: Optional[str] = "balanced"


class PDFReportRequest(BaseModel):
    material_ids: List[int]
    report_title: Optional[str] = "Material Comparison Report"
    include_gemini_analysis: bool = True


# --------------------------------------------------------------------------
# Material database
# --------------------------------------------------------------------------

NUMERIC_COLUMNS = [
    "density_g_cm3",
    "yield_strength_mpa",
    "tensile_strength_mpa",
    "youngs_modulus_gpa",
    "fatigue_strength_mpa",
    "elongation_%",
    "thermal_cond_w_m_k",
    "electrical_cond_ms_m",
    "specific_heat_j_kg_k",
    "melting_point_c",
    "max_service_temp_c",
]

CANDIDATE_CSV_PATHS = [
    "MaterialMind_Engineering_Database_72_verified-2.csv",
    "materials.csv",
    "./data/materials.csv",
    "../MaterialMind_Engineering_Database_72_verified-2.csv",
]


class MaterialDatabase:
    """Loads and queries the verified engineering material dataset."""

    def __init__(self) -> None:
        self.materials: List[Dict[str, Any]] = []
        self.df: Optional[pd.DataFrame] = None
        self.load_materials()

    def load_materials(self) -> None:
        for path in CANDIDATE_CSV_PATHS:
            if not os.path.exists(path):
                continue
            try:
                self._load_csv(path)
                logger.info("Loaded %d materials from '%s'.", len(self.materials), path)
                return
            except Exception:
                logger.exception("Failed to load materials from '%s'.", path)

        logger.warning("No material CSV found — falling back to sample dataset.")
        self.create_sample_data()

    def _load_csv(self, path: str) -> None:
        df = pd.read_csv(path)
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("(", "", regex=False)
            .str.replace(")", "", regex=False)
            .str.replace("Â°", "", regex=False)
            .str.replace("°", "", regex=False)
            .str.replace("·", "_", regex=False)
        )

        for col in NUMERIC_COLUMNS:
            if col in df.columns:
                df[col] = df[col].astype(str).str.extract(r"(\d+\.?\d*)", expand=False)
                df[col] = pd.to_numeric(df[col], errors="coerce")

        self.df = df
        self.materials = json.loads(df.to_json(orient="records"))

    def create_sample_data(self) -> None:
        """Minimal fallback dataset so the app remains functional without a CSV."""
        self.materials = [
            {
                "id": 1,
                "material_name": "Aluminium Alloy 6061",
                "category": "Aluminium Alloy",
                "density_g_cm3": 2.7,
                "tensile_strength_mpa": 310,
                "yield_strength_mpa": 276,
                "youngs_modulus_gpa": 68.9,
                "max_service_temp_c": 150,
                "cost": "Medium",
                "advantages": "Good balance of strength, weldability, corrosion resistance",
                "limitations": "Lower strength than 7xxx/2xxx series",
                "common_applications": "Structural frames, automotive/aerospace parts",
                "manufacturing_methods": "Extrusion, Forging, CNC, Welding",
            },
            {
                "id": 2,
                "material_name": "Carbon Steel 1018",
                "category": "Carbon/Alloy Steel",
                "density_g_cm3": 7.87,
                "tensile_strength_mpa": 440,
                "yield_strength_mpa": 370,
                "youngs_modulus_gpa": 200,
                "max_service_temp_c": 400,
                "cost": "Low",
                "advantages": "Easy to machine and weld, low cost",
                "limitations": "Poor corrosion resistance, low hardenability",
                "common_applications": "Shafts, pins, low-stress machine parts",
                "manufacturing_methods": "Machining, Forging, Welding",
            },
            {
                "id": 3,
                "material_name": "Stainless Steel 304",
                "category": "Stainless Steel",
                "density_g_cm3": 8.0,
                "tensile_strength_mpa": 505,
                "yield_strength_mpa": 215,
                "youngs_modulus_gpa": 193,
                "max_service_temp_c": 870,
                "cost": "Medium",
                "advantages": "Excellent corrosion resistance, good formability/weldability",
                "limitations": "Susceptible to chloride pitting/stress corrosion cracking",
                "common_applications": "Kitchen equipment, piping, architectural trim",
                "manufacturing_methods": "Forming, Welding, CNC",
            },
        ]
        self.df = pd.DataFrame(self.materials)
        logger.info("Created %d sample materials.", len(self.materials))

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        min_strength: Optional[int] = None,
        max_density: Optional[float] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        results = self.materials

        if query:
            q = query.lower()
            results = [
                m
                for m in results
                if q in str(m.get("material_name", "")).lower()
                or q in str(m.get("category", "")).lower()
                or q in str(m.get("common_applications", "")).lower()
                or q in str(m.get("advantages", "")).lower()
            ]

        if category:
            results = [m for m in results if m.get("category") == category]

        if min_strength:
            results = [m for m in results if m.get("tensile_strength_mpa", 0) >= min_strength]

        if max_density:
            results = [m for m in results if m.get("density_g_cm3", float("inf")) <= max_density]

        return results[:limit]

    def get_by_ids(self, ids: List[int]) -> List[Dict[str, Any]]:
        id_set = set(ids)
        return [m for m in self.materials if m.get("id") in id_set]

    def get_categories(self) -> List[str]:
        if self.df is not None and "category" in self.df.columns:
            return sorted(self.df["category"].dropna().unique().tolist())
        return sorted({m.get("category") for m in self.materials if m.get("category")})

    def get_stats(self) -> Dict[str, Any]:
        if not self.materials:
            return {"total": 0}

        df = pd.DataFrame(self.materials)
        stats: Dict[str, Any] = {
            "total": len(self.materials),
            "categories": len(self.get_categories()),
        }

        for col in ("tensile_strength_mpa", "density_g_cm3", "max_service_temp_c"):
            if col in df.columns:
                stats[f"avg_{col}"] = None if pd.isna(df[col].mean()) else round(float(df[col].mean()), 2)
                stats[f"max_{col}"] = None if pd.isna(df[col].max()) else round(float(df[col].max()), 2)
                stats[f"min_{col}"] = None if pd.isna(df[col].min()) else round(float(df[col].min()), 2)

        return stats


# --------------------------------------------------------------------------
# Gemini AI service
# --------------------------------------------------------------------------

MAX_CANDIDATES_IN_PROMPT = 10


def _format_candidates(materials: List[Dict[str, Any]]) -> str:
    """Render a compact, prompt-friendly summary of candidate materials."""
    return "\n".join(
        f"- {m['material_name']} ({m.get('category', 'N/A')}): "
        f"Strength {m.get('tensile_strength_mpa', 'N/A')} MPa, "
        f"Density {m.get('density_g_cm3', 'N/A')} g/cm3, "
        f"Cost {m.get('cost', 'N/A')}"
        for m in materials[:MAX_CANDIDATES_IN_PROMPT]
    )


class GeminiService:
    """Wraps all Gemini-powered reasoning: recommendations, comparisons, and manufacturing advice."""

    def __init__(self) -> None:
        self.available = GEMINI_AVAILABLE
        self.model = gemini_model

    def get_recommendation(self, requirements: Dict[str, Any], candidates: List[Dict[str, Any]]) -> str:
        """Generate a comparative recommendation from verified database candidates."""
        if not self.available or not self.model:
            return self._fallback_recommendation(requirements, candidates)

        candidates_text = _format_candidates(candidates)

        prompt = f"""You are a senior materials engineer writing a recommendation memo for a colleague. Write in natural, complete sentences, the way an experienced engineer would explain their reasoning out loud, not as a spec-sheet dump of fragments.

Requirements:
Application: {requirements.get('application', 'Not specified')}
Required Properties: {requirements.get('requirements', 'Not specified')}
Budget: {requirements.get('budget', 'Not specified')}
Sustainability Priority: {requirements.get('sustainability_priority', False)}

Verified candidate materials from our database:
{candidates_text}

Write a comparative recommendation with these sections, using ## headers:

## Top Pick
Name the material and explain in 2-3 full sentences why it fits. Then explicitly state one real weakness or limitation, a genuine trade-off an engineer would need to plan around.

## Runner-Up
Name the alternative and explain in 2-3 sentences when you'd choose it instead of the top pick.

## Key Trade-offs
A short paragraph, not a bullet list, comparing the top candidates directly on the properties that matter most for this application.

## Manufacturing Considerations
1-2 sentences on how each would actually be produced and any practical constraints.

## Sustainability Impact
1-2 sentences, be honest if a material has a poor sustainability profile rather than glossing over it.

## Bottom Line
A short closing paragraph giving your actual recommendation as if advising a colleague directly, referencing the specific numbers or constraints that drove the decision.

Writing rules:
- Use full grammatically correct sentences throughout, not sentence fragments.
- Do not use identical sentence structure across sections. Vary your phrasing.
- Avoid bullet points except where genuinely listing 3+ discrete items.
- Never present the top pick as a flawless winner. Every material has a real limitation, name it directly.
- Keep the whole response under 400 words."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception:
            logger.exception("Gemini recommendation generation failed.")
            return self._fallback_recommendation(requirements, candidates)

    def get_open_recommendation(self, requirements: Dict[str, Any]) -> str:
        """Generate an AI-only estimate when no verified database match exists."""
        if not self.available or not self.model:
            return "No matching materials in our verified database, and AI is currently unavailable to suggest alternatives."

        prompt = f"""You are a senior materials engineer. No material in our internal verified database matched this application:

Application: {requirements.get('application', 'Not specified')}
Required Properties: {requirements.get('requirements', 'Not specified')}
Budget: {requirements.get('budget', 'Not specified')}
Sustainability Priority: {requirements.get('sustainability_priority', False)}

Using your own general materials engineering knowledge, recommend 2-3 suitable materials. For each, give real trade-offs, manufacturing considerations, and note this is a general estimate, not a verified database match. Write in full, natural sentences rather than sentence fragments, and vary phrasing between materials rather than repeating the same template three times.

Start your response with exactly: "AI ESTIMATE (not from verified database):\""""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception:
            logger.exception("Gemini open-recommendation generation failed.")
            return "No matching materials in our verified database, and the AI recommendation failed. Please try rephrasing your application."

    def _fallback_recommendation(
        self, requirements: Dict[str, Any], candidates: List[Dict[str, Any]]
    ) -> str:
        """Deterministic, non-AI scoring fallback used when Gemini is unavailable."""
        if not candidates:
            return "No materials found matching your criteria."

        req_fields = requirements.get("requirements", {})

        scored = []
        for m in candidates:
            score = 0
            if "strength" in req_fields and m.get("tensile_strength_mpa", 0) > 500:
                score += 3
            if "weight" in req_fields and m.get("density_g_cm3", 10) < 3:
                score += 3
            if requirements.get("sustainability_priority", False) and m.get("recyclability") == "High":
                score += 2
            scored.append((m, score))

        scored.sort(key=lambda pair: pair[1], reverse=True)

        lines = ["MATERIAL RECOMMENDATIONS (AI Mode: Fallback)", "=" * 50, ""]
        for i, (m, score) in enumerate(scored[:3], 1):
            lines.append(f"{i}. {m.get('material_name')} (Score: {score})")
            lines.append(f"   Category: {m.get('category', 'N/A')}")
            lines.append(f"   Tensile Strength: {m.get('tensile_strength_mpa', 'N/A')} MPa")
            lines.append(f"   Density: {m.get('density_g_cm3', 'N/A')} g/cm3")
            lines.append(f"   Cost: {m.get('cost', 'N/A')}")
            lines.append(f"   Advantages: {m.get('advantages', 'N/A')}")
            lines.append("")

        return "\n".join(lines)

    def get_manufacturing_advice(self, material: Dict[str, Any], query: Dict[str, Any]) -> str:
        if not self.available or not self.model:
            return self._fallback_manufacturing_advice(material, query)

        prompt = f"""You are a senior manufacturing engineer advising on production of the following material.

Material: {material.get('material_name')} ({material.get('category')})
Recommended methods: {material.get('manufacturing_methods', 'Not specified')}
Quantity: {query.get('quantity', 100)}
Budget Priority: {query.get('budget_priority', 'balanced')}

Provide practical manufacturing guidance covering:
1. Best manufacturing processes for this quantity and material
2. Process considerations specific to this material
3. Cost implications
4. Quality control measures
5. Common challenges and how to address them

Write in full sentences suitable for an engineering guide, not fragments. Keep it practical and specific to the material and quantity given."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception:
            logger.exception("Gemini manufacturing advice generation failed.")
            return self._fallback_manufacturing_advice(material, query)

    def _fallback_manufacturing_advice(self, material: Dict[str, Any], query: Dict[str, Any]) -> str:
        methods = material.get("manufacturing_methods", "Various methods available")
        quantity = query.get("quantity", 100)

        lines = [
            "MANUFACTURING ADVICE (AI Mode: Fallback)",
            "=" * 50,
            "",
            f"Material: {material.get('material_name')}",
            f"Quantity: {quantity} units",
            "",
            "Recommended Processes:",
            f"  - {methods}",
            "",
        ]

        if quantity < 100:
            lines.append("For small quantities: consider CNC machining or 3D printing.")
        elif quantity < 1000:
            lines.append("For medium quantities: consider casting or forging.")
        else:
            lines.append("For large quantities: consider injection molding or extrusion.")

        return "\n".join(lines)

    def estimate_missing_properties(
        self, material: Dict[str, Any], missing_keys: List[str]
    ) -> Dict[str, str]:
        """Ask Gemini for a best-effort estimate of properties absent from the
        verified database. Every returned value is tagged '(AI est.)' so it can
        never be mistaken for a verified database figure downstream."""
        if not self.available or not self.model or not missing_keys:
            return {}

        keys_text = ", ".join(missing_keys)
        prompt = f"""You are a senior materials engineer. For the material below, give your best professional estimate for ONLY these properties: {keys_text}

Material: {material.get('material_name')} ({material.get('category', 'N/A')})
Known properties: density {material.get('density_g_cm3', 'N/A')} g/cm3, tensile strength {material.get('tensile_strength_mpa', 'N/A')} MPa, cost {material.get('cost', 'N/A')}

Respond with ONLY a valid JSON object mapping each property name to a short value (a qualitative rating like "Good", "Fair", or "Excellent" for qualitative properties, or a number with units for quantitative ones). No explanation, no markdown formatting, no code fences, just the raw JSON object. Example: {{"weldability": "Good", "machinability": "Fair"}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            if text.startswith("```"):
                text = text.strip("`")
                if "\n" in text:
                    first_line, rest = text.split("\n", 1)
                    text = rest if first_line.strip().lower() in ("json", "") else text

            estimates = json.loads(text)
            return {k: f"{v} (AI est.)" for k, v in estimates.items() if k in missing_keys}
        except Exception:
            logger.exception("Gemini property estimation failed for '%s'.", material.get("material_name"))
            return {}

    def compare_materials(self, materials: List[Dict[str, Any]]) -> str:
        if not self.available or not self.model:
            return "AI analysis unavailable (Gemini not configured). Showing verified database properties only."

        materials_text = "\n".join(
            f"- {m.get('material_name')} ({m.get('category', 'N/A')}): "
            f"Strength {m.get('tensile_strength_mpa', 'N/A')} MPa, "
            f"Density {m.get('density_g_cm3', 'N/A')} g/cm3, "
            f"Cost {m.get('cost', 'N/A')}, "
            f"Advantages: {m.get('advantages', 'N/A')}, "
            f"Limitations: {m.get('limitations', 'N/A')}"
            for m in materials
        )

        prompt = f"""You are a senior materials engineer writing a comparison section for a formal report.

Materials being compared:
{materials_text}

Write a comparative analysis covering:
1. Which material suits which use case, and why
2. Key trade-offs between them (never declare one an unqualified winner)
3. Manufacturing and cost implications
4. A final recommendation with reasoning

Write in full, natural sentences. Keep it concise and professional, suitable for an engineering report. Plain text, no markdown symbols."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception:
            logger.exception("Gemini comparison generation failed.")
            return "AI analysis unavailable due to an error. Showing verified database properties only."


# --------------------------------------------------------------------------
# PDF report generation
# --------------------------------------------------------------------------

PDF_PROPERTIES = [
    ("Density (g/cm3)", "density_g_cm3"),
    ("Tensile Strength (MPa)", "tensile_strength_mpa"),
    ("Yield Strength (MPa)", "yield_strength_mpa"),
    ("Young's Modulus (GPa)", "youngs_modulus_gpa"),
    ("Max Service Temp (C)", "max_service_temp_c"),
    ("Cost", "cost"),
    ("Corrosion Resistance", "corrosion_resistance"),
    ("Weldability", "weldability"),
    ("Machinability", "machinability"),
]


class PDFReportGenerator:
    """Builds a formatted PDF comparison report using ReportLab."""

    def generate_comparison_report(
        self,
        materials: List[Dict[str, Any]],
        comparison_data: Dict[str, Any],
        gemini_analysis: Optional[str] = None,
    ) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor("#1a5276"),
        )

        header_style = ParagraphStyle(
            "CustomHeader",
            parent=styles["Heading2"],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor("#2c3e50"),
        )

        story: List[Any] = [
            Paragraph("Material Comparison Report", title_style),
            Spacer(1, 0.25 * inch),
            Paragraph(
                f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                styles["Normal"],
            ),
            Spacer(1, 0.5 * inch),
            Paragraph("Materials Compared", header_style),
            Spacer(1, 0.1 * inch),
        ]

        for i, material in enumerate(materials, 1):
            story.append(Paragraph(f"<b>{i}. {material.get('material_name')}</b>", styles["Normal"]))
            story.append(Paragraph(f"Category: {material.get('category', 'N/A')}", styles["Normal"]))
            story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph("Key Properties Comparison", header_style))
        story.append(Spacer(1, 0.1 * inch))

        table_data = [["Property"] + [m.get("material_name") for m in materials]]
        for prop_name, prop_key in PDF_PROPERTIES:
            row = [prop_name] + [str(m.get(prop_key, "N/A")) for m in materials]
            table_data.append(row)

        table = Table(table_data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                ]
            )
        )

        story.append(table)
        story.append(Spacer(1, 0.5 * inch))

        if gemini_analysis:
            story.append(Paragraph("AI Analysis & Recommendations", header_style))
            story.append(Spacer(1, 0.1 * inch))

            for paragraph in gemini_analysis.split("\n\n"):
                if paragraph.strip():
                    clean = (
                        paragraph.strip()
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                    )
                    story.append(Paragraph(clean, styles["Normal"]))
                    story.append(Spacer(1, 0.1 * inch))

        doc.build(story)
        buffer.seek(0)
        return buffer


# --------------------------------------------------------------------------
# Shared enrichment helper
# --------------------------------------------------------------------------

def _is_missing(value: Any) -> bool:
    return value is None or value == "N/A" or value == "" or (isinstance(value, float) and pd.isna(value))


def enrich_materials_with_estimates(
    materials: List[Dict[str, Any]],
    property_keys: List[str],
    gemini_service: "GeminiService",
) -> List[Dict[str, Any]]:
    """Return copies of the given materials with any missing property_keys
    filled in via Gemini estimates. Verified values already present are never
    overwritten. Materials are left unmodified if Gemini is unavailable."""
    enriched = []
    for material in materials:
        material_copy = dict(material)
        missing_keys = [k for k in property_keys if _is_missing(material_copy.get(k))]

        if missing_keys:
            estimates = gemini_service.estimate_missing_properties(material_copy, missing_keys)
            material_copy.update(estimates)

        enriched.append(material_copy)

    return enriched


# --------------------------------------------------------------------------
# FastAPI application
# --------------------------------------------------------------------------

app = FastAPI(
    title="MaterialMind API",
    description="AI-Powered Material Selection and Comparison Engine",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = MaterialDatabase()
gemini = GeminiService()
pdf_generator = PDFReportGenerator()


@app.get("/")
async def root():
    return {
        "service": "MaterialMind API",
        "version": "2.0.0",
        "status": "operational",
        "features": {
            "material_database": True,
            "gemini_integration": GEMINI_AVAILABLE,
            "recommendation_agent": True,
            "material_comparison": True,
            "manufacturing_advisor": True,
            "pdf_report_generator": True,
            "deployed_on_cloud_run": True,
        },
        "materials_loaded": len(db.materials),
        "endpoints": [
            "/docs - API Documentation",
            "/health - Health Check",
            "/categories - All Categories",
            "/materials/search - Search Materials",
            "/materials/recommend - AI Recommendations",
            "/materials/compare - Compare Materials",
            "/materials/manufacturing - Manufacturing Advice",
            "/materials/report - PDF Report",
            "/materials/stats - Database Statistics",
        ],
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MaterialMind API",
        "version": "2.0.0",
        "materials_loaded": len(db.materials),
        "gemini_available": GEMINI_AVAILABLE,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/categories")
async def get_categories():
    return {
        "categories": db.get_categories(),
        "count": len(db.get_categories()),
    }


@app.post("/materials/search")
async def search_materials(request: MaterialSearch):
    results = db.search(
        query=request.query,
        category=request.category,
        min_strength=request.min_tensile_strength,
        max_density=request.max_density,
        limit=request.limit,
    )

    return {
        "count": len(results),
        "results": results,
    }


@app.post("/materials/recommend")
async def recommend_material(request: RecommendationRequest):
    candidates = db.search(query=request.application, limit=20)

    if not candidates:
        recommendation = gemini.get_open_recommendation(request.dict())
        return {
            "status": "success",
            "gemini_available": GEMINI_AVAILABLE,
            "source": "ai_estimate",
            "candidates": [],
            "recommendation": recommendation,
            "total_candidates": 0,
            "note": "No verified match in our database. This is an AI estimate - verify before use.",
        }

    recommendation = gemini.get_recommendation(request.dict(), candidates[:10])

    return {
        "status": "success",
        "gemini_available": GEMINI_AVAILABLE,
        "source": "verified_database",
        "candidates": candidates[:5],
        "recommendation": recommendation,
        "total_candidates": len(candidates),
    }


@app.post("/materials/compare")
async def compare_materials(request: MaterialComparison):
    materials = db.get_by_ids(request.material_ids)

    if len(materials) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 materials to compare")

    properties = [
        "material_name",
        "category",
        "density_g_cm3",
        "tensile_strength_mpa",
        "yield_strength_mpa",
        "youngs_modulus_gpa",
        "max_service_temp_c",
        "cost",
        "advantages",
        "limitations",
        "corrosion_resistance",
        "weldability",
        "machinability",
    ]

    if GEMINI_AVAILABLE:
        materials = enrich_materials_with_estimates(materials, properties, gemini)

    comparison_table = []
    for prop in properties:
        row = {"property": prop.replace("_", " ").title()}
        for m in materials:
            row[m.get("material_name")] = m.get(prop, "N/A")
        comparison_table.append(row)

    return {
        "materials": materials,
        "comparison_table": comparison_table,
        "count": len(materials),
    }


@app.post("/materials/manufacturing")
async def manufacturing_advice(request: ManufacturingRequest):
    material = next((m for m in db.materials if m.get("id") == request.material_id), None)

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    advice = gemini.get_manufacturing_advice(material, request.dict())

    return {
        "material": material,
        "gemini_available": GEMINI_AVAILABLE,
        "advice": advice,
        "recommended_methods": material.get("manufacturing_methods", "Not specified"),
    }


@app.post("/materials/report")
async def generate_report(request: PDFReportRequest):
    materials = db.get_by_ids(request.material_ids)

    if len(materials) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 materials to generate report")

    if GEMINI_AVAILABLE:
        pdf_property_keys = [key for _, key in PDF_PROPERTIES]
        materials = enrich_materials_with_estimates(materials, pdf_property_keys, gemini)

    if request.include_gemini_analysis and GEMINI_AVAILABLE:
        gemini_analysis = gemini.compare_materials(materials)
    else:
        gemini_analysis = "AI analysis not requested or Gemini unavailable."

    pdf_buffer = pdf_generator.generate_comparison_report(
        materials=materials,
        comparison_data={"focus": request.report_title},
        gemini_analysis=gemini_analysis,
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f"attachment; filename=material_comparison_{datetime.now().strftime('%Y%m%d')}.pdf"
            )
        },
    )


@app.get("/materials/stats")
async def get_stats():
    stats = db.get_stats()

    if db.df is not None and "category" in db.df.columns:
        counts = db.df["category"].value_counts().to_dict()
        stats["materials_by_category"] = {str(k): int(v) for k, v in counts.items()}

    return stats


@app.get("/materials/{material_id}")
async def get_material(material_id: int):
    for m in db.materials:
        if m.get("id") == material_id:
            return m
    raise HTTPException(status_code=404, detail="Material not found")


if __name__ == "__main__":
    print("=" * 60)
    print("MATERIALMIND API - PHASE 1 MVP")
    print("=" * 60)
    print(f"Materials Loaded: {len(db.materials)}")
    print(f"Gemini Integration: {'Enabled' if GEMINI_AVAILABLE else 'Disabled (API key needed)'}")
    print("PDF Report Generator: Enabled")
    print("Manufacturing Advisor: Enabled")
    print("Server: http://localhost:8080")
    print("API Docs: http://localhost:8080/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8080)
