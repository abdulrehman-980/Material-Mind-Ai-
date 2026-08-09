"""
MaterialMind - Complete Phase 1 MVP
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import os
import json
import io
from datetime import datetime
import google.generativeai as genai
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import uvicorn

class Config:
    PROJECT_ID = os.getenv('PROJECT_ID', 'material-ai')
    BUCKET_NAME = os.getenv('BUCKET_NAME', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./test.db')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

if Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-flash-latest')
    GEMINI_AVAILABLE = True
else:
    GEMINI_AVAILABLE = False
    gemini_model = None

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

class MaterialDatabase:
    def __init__(self):
        self.materials = []
        self.df = None
        self.load_materials()

    def load_materials(self):
        possible_paths = [
            'MaterialMind_Engineering_Database_72_verified-2.csv',
            'materials.csv',
            './data/materials.csv',
            '../MaterialMind_Engineering_Database_72_verified-2.csv',
        ]

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    self.df = pd.read_csv(path)
                    self.df.columns = self.df.columns.str.strip().str.lower().str.replace(' ', '_')
                    self.df.columns = self.df.columns.str.replace('(', '').str.replace(')', '')
                    self.df.columns = self.df.columns.str.replace('Â°', '').str.replace('°', '')
                    self.df.columns = self.df.columns.str.replace('·', '_')

                    numeric_cols = ['density_g_cm3', 'yield_strength_mpa', 'tensile_strength_mpa',
                                   'youngs_modulus_gpa', 'fatigue_strength_mpa', 'elongation_%',
                                   'thermal_cond_w_m_k', 'electrical_cond_ms_m',
                                   'specific_heat_j_kg_k', 'melting_point_c', 'max_service_temp_c']

                    for col in numeric_cols:
                        if col in self.df.columns:
                            self.df[col] = self.df[col].astype(str).str.extract(r'(\d+\.?\d*)', expand=False)
                            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

                    self.materials = json.loads(self.df.to_json(orient='records'))
                    print(f"Loaded {len(self.materials)} materials from {path}")
                    return
                except Exception as e:
                    print(f"Error loading {path}: {e}")

        self.create_sample_data()

    def create_sample_data(self):
        self.materials = [
            {"id": 1, "material_name": "Aluminium Alloy 6061", "category": "Aluminium Alloy",
             "density_g_cm3": 2.7, "tensile_strength_mpa": 310, "yield_strength_mpa": 276,
             "youngs_modulus_gpa": 68.9, "max_service_temp_c": 150, "cost": "Medium",
             "advantages": "Good balance of strength, weldability, corrosion resistance",
             "limitations": "Lower strength than 7xxx/2xxx",
             "common_applications": "Structural frames, automotive/aerospace parts",
             "manufacturing_methods": "Extrusion, Forging, CNC, Welding"},
            {"id": 2, "material_name": "Carbon Steel 1018", "category": "Carbon/Alloy Steel",
             "density_g_cm3": 7.87, "tensile_strength_mpa": 440, "yield_strength_mpa": 370,
             "youngs_modulus_gpa": 200, "max_service_temp_c": 400, "cost": "Low",
             "advantages": "Easy to machine and weld, low cost",
             "limitations": "Poor corrosion resistance, low hardenability",
             "common_applications": "Shafts, pins, low-stress machine parts",
             "manufacturing_methods": "Machining, Forging, Welding"},
            {"id": 3, "material_name": "Stainless Steel 304", "category": "Stainless Steel",
             "density_g_cm3": 8.0, "tensile_strength_mpa": 505, "yield_strength_mpa": 215,
             "youngs_modulus_gpa": 193, "max_service_temp_c": 870, "cost": "Medium",
             "advantages": "Excellent corrosion resistance, good formability/weldability",
             "limitations": "Susceptible to chloride pitting/SCC",
             "common_applications": "Kitchen equipment, piping, architectural trim",
             "manufacturing_methods": "Forming, Welding, CNC"},
        ]
        self.df = pd.DataFrame(self.materials)
        print(f"Created {len(self.materials)} sample materials")

    def search(self, query: str, category: str = None, min_strength: int = None,
               max_density: float = None, limit: int = 20) -> List[Dict]:
        results = self.materials.copy()

        if query:
            query_lower = query.lower()
            results = [
                m for m in results
                if query_lower in str(m.get('material_name', '')).lower()
                or query_lower in str(m.get('category', '')).lower()
                or query_lower in str(m.get('common_applications', '')).lower()
                or query_lower in str(m.get('advantages', '')).lower()
            ]

        if category:
            results = [m for m in results if m.get('category') == category]

        if min_strength:
            results = [
                m for m in results
                if m.get('tensile_strength_mpa', 0) >= min_strength
            ]

        if max_density:
            results = [
                m for m in results
                if m.get('density_g_cm3', float('inf')) <= max_density
            ]

        return results[:limit]

    def get_by_ids(self, ids: List[int]) -> List[Dict]:
        id_set = set(ids)
        return [m for m in self.materials if m.get('id') in id_set]

    def get_categories(self) -> List[str]:
        if self.df is not None and 'category' in self.df.columns:
            return sorted(self.df['category'].dropna().unique().tolist())
        return sorted(list(set([m.get('category') for m in self.materials if m.get('category')])))

    def get_stats(self) -> Dict:
        if not self.materials:
            return {"total": 0}

        df = pd.DataFrame(self.materials)
        stats = {
            "total": len(self.materials),
            "categories": len(self.get_categories()),
        }

        numeric_cols = ['tensile_strength_mpa', 'density_g_cm3', 'max_service_temp_c']
        for col in numeric_cols:
            if col in df.columns:
                stats[f'avg_{col}'] = None if pd.isna(df[col].mean()) else round(float(df[col].mean()), 2)
                stats[f'max_{col}'] = None if pd.isna(df[col].max()) else round(float(df[col].max()), 2)
                stats[f'min_{col}'] = None if pd.isna(df[col].min()) else round(float(df[col].min()), 2)

        return stats

class GeminiService:
    def __init__(self):
        self.available = GEMINI_AVAILABLE
        self.model = gemini_model

    def get_recommendation(self, requirements: Dict, candidates: List[Dict]) -> str:
        if not self.available or not self.model:
            return self._fallback_recommendation(requirements, candidates)

        try:
            candidates_text = "\n".join([
                f"- {m['material_name']} ({m.get('category', 'N/A')}): "
                f"Strength {m.get('tensile_strength_mpa', 'N/A')} MPa, "
                f"Density {m.get('density_g_cm3', 'N/A')} g/cm3, "
                f"Cost {m.get('cost', 'N/A')}"
                for m in candidates[:10]
            ])
prompt = f"""
You are a senior materials engineer writing a recommendation memo for a colleague. Write in natural, complete sentences, the way an experienced engineer would explain their reasoning out loud, not as a spec-sheet dump of fragments.

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
- Keep the whole response under 400 words.
"""
        
            You are a senior materials engineer. No material in our internal verified database matched this application:

            Application: {requirements.get('application', 'Not specified')}
            Required Properties: {requirements.get('requirements', 'Not specified')}
            Budget: {requirements.get('budget', 'Not specified')}
            Sustainability Priority: {requirements.get('sustainability_priority', False)}

            Using your own general materials engineering knowledge, recommend 2-3 suitable materials.
            For each, give real trade-offs, manufacturing considerations, and note this is a general
            estimate, not a verified database match.

            Start your response with exactly: "AI ESTIMATE (not from verified database):"
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"Gemini open-recommendation error: {e}")
            return "No matching materials in our verified database, and the AI recommendation failed. Please try rephrasing your application."

    def _fallback_recommendation(self, requirements: Dict, candidates: List[Dict]) -> str:
        if not candidates:
            return "No materials found matching your criteria."

        scored = []
        for m in candidates:
            score = 0
            if 'strength' in requirements.get('requirements', {}):
                if m.get('tensile_strength_mpa', 0) > 500:
                    score += 3
            if 'weight' in requirements.get('requirements', {}):
                if m.get('density_g_cm3', 10) < 3:
                    score += 3
            if requirements.get('sustainability_priority', False):
                if m.get('recyclability') == 'High':
                    score += 2
            scored.append((m, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        result = "MATERIAL RECOMMENDATIONS (AI Mode: Fallback)\n"
        result += "=" * 50 + "\n\n"

        for i, (m, score) in enumerate(scored[:3], 1):
            result += f"{i}. {m.get('material_name')} (Score: {score})\n"
            result += f"   Category: {m.get('category', 'N/A')}\n"
            result += f"   Tensile Strength: {m.get('tensile_strength_mpa', 'N/A')} MPa\n"
            result += f"   Density: {m.get('density_g_cm3', 'N/A')} g/cm3\n"
            result += f"   Cost: {m.get('cost', 'N/A')}\n"
            result += f"   Advantages: {m.get('advantages', 'N/A')}\n\n"

        return result

    def get_manufacturing_advice(self, material: Dict, query: Dict) -> str:
        if not self.available or not self.model:
            return self._fallback_manufacturing_advice(material, query)

        try:
            prompt = f"""
            Material: {material.get('material_name')} ({material.get('category')})

            Recommended methods: {material.get('manufacturing_methods', 'Not specified')}
            Quantity: {query.get('quantity', 100)}
            Budget Priority: {query.get('budget_priority', 'balanced')}

            Provide manufacturing advice:
            1. Best manufacturing processes
            2. Process considerations
            3. Cost implications
            4. Quality control measures
            5. Common challenges and solutions

            Format as practical engineering guide.
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"Gemini error: {e}")
            return self._fallback_manufacturing_advice(material, query)

    def _fallback_manufacturing_advice(self, material: Dict, query: Dict) -> str:
        methods = material.get('manufacturing_methods', 'Various methods available')
        quantity = query.get('quantity', 100)

        result = "MANUFACTURING ADVICE (AI Mode: Fallback)\n"
        result += "=" * 50 + "\n\n"
        result += f"Material: {material.get('material_name')}\n"
        result += f"Quantity: {quantity} units\n\n"
        result += "Recommended Processes:\n"
        result += f"  - {methods}\n\n"

        if quantity < 100:
            result += "For small quantities: Consider CNC machining or 3D printing\n"
        elif quantity < 1000:
            result += "For medium quantities: Consider casting or forging\n"
        else:
            result += "For large quantities: Consider injection molding or extrusion\n"

        return result

    def compare_materials(self, materials: List[Dict]) -> str:
        if not self.available or not self.model:
            return "AI analysis unavailable (Gemini not configured). Showing verified database properties only."

        try:
            materials_text = "\n".join([
                f"- {m.get('material_name')} ({m.get('category', 'N/A')}): "
                f"Strength {m.get('tensile_strength_mpa', 'N/A')} MPa, "
                f"Density {m.get('density_g_cm3', 'N/A')} g/cm3, "
                f"Cost {m.get('cost', 'N/A')}, "
                f"Advantages: {m.get('advantages', 'N/A')}, "
                f"Limitations: {m.get('limitations', 'N/A')}"
                for m in materials
            ])

            prompt = f"""
            You are a senior materials engineer writing a comparison section for a formal report.

            Materials being compared:
            {materials_text}

            Write a comparative analysis covering:
            1. Which material suits which use case, and why
            2. Key trade-offs between them (never declare one an unqualified winner)
            3. Manufacturing and cost implications
            4. A final recommendation with reasoning

            Keep it concise and professional, suitable for an engineering report. Plain text, no markdown symbols."""
            

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"Gemini compare error: {e}")
            return "AI analysis unavailable due to an error. Showing verified database properties only."

class PDFReportGenerator:
    def generate_comparison_report(self, materials: List[Dict], comparison_data: Dict,
                                  gemini_analysis: str = None) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a5276')
        )

        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#2c3e50')
        )

        story = []

        story.append(Paragraph("Material Comparison Report", title_style))
        story.append(Spacer(1, 0.25*inch))

        date = Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                        styles['Normal'])
        story.append(date)
        story.append(Spacer(1, 0.5*inch))

        story.append(Paragraph("Materials Compared", header_style))
        story.append(Spacer(1, 0.1*inch))

        for i, material in enumerate(materials, 1):
            story.append(Paragraph(f"<b>{i}. {material.get('material_name')}</b>",
                                  styles['Normal']))
            story.append(Paragraph(f"Category: {material.get('category', 'N/A')}",
                                  styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

        story.append(Paragraph("Key Properties Comparison", header_style))
        story.append(Spacer(1, 0.1*inch))

        table_data = [
            ['Property'] + [m.get('material_name') for m in materials]
        ]

        properties = [
            ('Density (g/cm3)', 'density_g_cm3'),
            ('Tensile Strength (MPa)', 'tensile_strength_mpa'),
            ('Yield Strength (MPa)', 'yield_strength_mpa'),
            ("Young's Modulus (GPa)", 'youngs_modulus_gpa'),
            ('Max Service Temp (C)', 'max_service_temp_c'),
            ('Cost', 'cost'),
            ('Corrosion Resistance', 'corrosion_resistance'),
            ('Weldability', 'weldability'),
            ('Machinability', 'machinability'),
        ]

        for prop_name, prop_key in properties:
            row = [prop_name]
            for m in materials:
                value = m.get(prop_key, 'N/A')
                row.append(str(value))
            table_data.append(row)

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))

        story.append(table)
        story.append(Spacer(1, 0.5*inch))

        if gemini_analysis:
            story.append(Paragraph("AI Analysis & Recommendations", header_style))
            story.append(Spacer(1, 0.1*inch))

            for paragraph in gemini_analysis.split('\n\n'):
                if paragraph.strip():
                    clean = paragraph.strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(clean, styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))

        doc.build(story)
        buffer.seek(0)
        return buffer

app = FastAPI(
    title="MaterialMind API",
    description="AI-Powered Material Selection and Comparison Engine",
    version="2.0.0"
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
            "deployed_on_cloud_run": True
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
            "/materials/stats - Database Statistics"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MaterialMind API",
        "version": "2.0.0",
        "materials_loaded": len(db.materials),
        "gemini_available": GEMINI_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/categories")
async def get_categories():
    return {
        "categories": db.get_categories(),
        "count": len(db.get_categories())
    }

@app.post("/materials/search")
async def search_materials(request: MaterialSearch):
    results = db.search(
        query=request.query,
        category=request.category,
        min_strength=request.min_tensile_strength,
        max_density=request.max_density,
        limit=request.limit
    )

    return {
        "count": len(results),
        "results": results
    }

@app.post("/materials/recommend")
async def recommend_material(request: RecommendationRequest):
    candidates = db.search(
        query=request.application,
        limit=20
    )

    if not candidates:
        recommendation = gemini.get_open_recommendation(request.dict())
        return {
            "status": "success",
            "gemini_available": GEMINI_AVAILABLE,
            "source": "ai_estimate",
            "candidates": [],
            "recommendation": recommendation,
            "total_candidates": 0,
            "note": "No verified match in our database. This is an AI estimate - verify before use."
        }

    recommendation = gemini.get_recommendation(
        request.dict(),
        candidates[:10]
    )

    return {
        "status": "success",
        "gemini_available": GEMINI_AVAILABLE,
        "source": "verified_database",
        "candidates": candidates[:5],
        "recommendation": recommendation,
        "total_candidates": len(candidates)
    }

@app.post("/materials/compare")
async def compare_materials(request: MaterialComparison):
    materials = db.get_by_ids(request.material_ids)

    if len(materials) < 2:
        raise HTTPException(
            status_code=400,
            detail="Need at least 2 materials to compare"
        )

    properties = ["material_name", "category", "density_g_cm3", "tensile_strength_mpa",
                  "yield_strength_mpa", "youngs_modulus_gpa", "max_service_temp_c",
                  "cost", "advantages", "limitations"]

    comparison_table = []
    for prop in properties:
        row = {"property": prop.replace('_', ' ').title()}
        for m in materials:
            row[m.get('material_name')] = m.get(prop, "N/A")
        comparison_table.append(row)

    return {
        "materials": materials,
        "comparison_table": comparison_table,
        "count": len(materials)
    }

@app.post("/materials/manufacturing")
async def manufacturing_advice(request: ManufacturingRequest):
    material = None
    for m in db.materials:
        if m.get('id') == request.material_id:
            material = m
            break

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    advice = gemini.get_manufacturing_advice(material, request.dict())

    return {
        "material": material,
        "gemini_available": GEMINI_AVAILABLE,
        "advice": advice,
        "recommended_methods": material.get('manufacturing_methods', 'Not specified')
    }

@app.post("/materials/report")
async def generate_report(request: PDFReportRequest):
    materials = db.get_by_ids(request.material_ids)

    if len(materials) < 2:
        raise HTTPException(
            status_code=400,
            detail="Need at least 2 materials to generate report"
        )

    gemini_analysis = None
    if request.include_gemini_analysis and GEMINI_AVAILABLE:
        gemini_analysis = gemini.compare_materials(materials)
    else:
        gemini_analysis = "AI analysis not requested or Gemini unavailable."

    pdf_buffer = pdf_generator.generate_comparison_report(
        materials=materials,
        comparison_data={"focus": request.report_title},
        gemini_analysis=gemini_analysis
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=material_comparison_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    )

@app.get("/materials/stats")
async def get_stats():
    stats = db.get_stats()

    if db.df is not None and 'category' in db.df.columns:
        counts = db.df['category'].value_counts().to_dict()
        stats["materials_by_category"] = {str(k): int(v) for k, v in counts.items()}

    return stats

@app.get("/materials/{material_id}")
async def get_material(material_id: int):
    for m in db.materials:
        if m.get('id') == material_id:
            return m
    raise HTTPException(status_code=404, detail="Material not found")

if __name__ == "__main__":
    print("=" * 60)
    print("MATERIALMIND API - PHASE 1 MVP")
    print("=" * 60)
    print(f"Materials Loaded: {len(db.materials)}")
    print(f"Gemini Integration: {'Enabled' if GEMINI_AVAILABLE else 'Disabled (API key needed)'}")
    print(f"PDF Report Generator: Enabled")
    print(f"Manufacturing Advisor: Enabled")
    print(f"Server: http://localhost:8080")
    print(f"API Docs: http://localhost:8080/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8080)
