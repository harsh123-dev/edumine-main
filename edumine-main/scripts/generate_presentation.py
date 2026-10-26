import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path="EduMine_Project_Review.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme Colors
    COLOR_BG_DARK = RGBColor(15, 23, 42)       # #0F172A Slate 900
    COLOR_BG_LIGHT = RGBColor(248, 250, 252)   # #F8FAFC Slate 50
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_PRIMARY = RGBColor(37, 99, 235)      # #2563EB Royal Blue
    COLOR_SECONDARY = RGBColor(14, 165, 233)   # #0EA5E9 Sky Blue
    COLOR_TEAL = RGBColor(13, 148, 136)        # #0D9488 Teal
    COLOR_CARD_BG = RGBColor(255, 255, 255)
    COLOR_CARD_BORDER = RGBColor(226, 232, 240)# #E2E8F0 Slate 200
    COLOR_TEXT_MAIN = RGBColor(30, 41, 59)     # #1E293B Slate 800
    COLOR_TEXT_MUTED = RGBColor(100, 116, 139) # #64748B Slate 500
    COLOR_ACCENT_WARN = RGBColor(245, 158, 11) # #F59E0B Amber
    COLOR_ACCENT_DANGER = RGBColor(239, 68, 68)# #EF4444 Red
    COLOR_ACCENT_SUCCESS = RGBColor(16, 185, 129)# #10B981 Emerald
    COLOR_VIT_GOLD = RGBColor(217, 119, 6)     # #D97706 Warm Gold

    FONT_MAIN = "Calibri"
    FONT_HEAD = "Segoe UI"

    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title, subtitle, slide_num):
        # Top banner line
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.12))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = COLOR_PRIMARY
        top_bar.line.fill.background()

        # Title text
        txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.5), Inches(0.85))
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEAD
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_MAIN

        if subtitle:
            p2 = tf.add_paragraph()
            p2.text = subtitle
            p2.font.name = FONT_MAIN
            p2.font.size = Pt(13)
            p2.font.color.rgb = COLOR_TEXT_MUTED

        # Slide Number Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.8), Inches(0.45), Inches(0.8), Inches(0.38))
        badge.fill.solid()
        badge.fill.fore_color.rgb = RGBColor(238, 242, 255)
        badge.line.color.rgb = COLOR_PRIMARY
        badge.line.width = Pt(1)
        tf_b = badge.text_frame
        tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_b = tf_b.paragraphs[0]
        p_b.text = f"{slide_num:02d}"
        p_b.alignment = PP_ALIGN.CENTER
        p_b.font.name = FONT_HEAD
        p_b.font.size = Pt(12)
        p_b.font.bold = True
        p_b.font.color.rgb = COLOR_PRIMARY

        # Footer institution watermark
        footerBox = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.35))
        tf_f = footerBox.text_frame
        tf_f.margin_left = tf_f.margin_top = tf_f.margin_right = tf_f.margin_bottom = 0
        p_f = tf_f.paragraphs[0]
        p_f.text = "EduMine: Integrated Educational Data Mining Framework | Vellore Institute of Technology"
        p_f.font.name = FONT_MAIN
        p_f.font.size = Pt(10)
        p_f.font.color.rgb = RGBColor(148, 163, 184)

    def add_card(slide, left, top, width, height, bg_color=COLOR_WHITE, border_color=COLOR_CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    # ==========================================
    # SLIDE 1: TITLE SLIDE (Dark Luxury Theme)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, COLOR_BG_DARK)

    # Decorative accent card in background
    accent_bar = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = RGBColor(30, 41, 59)
    accent_bar.line.color.rgb = RGBColor(51, 65, 85)
    accent_bar.line.width = Pt(1.5)

    # Top Pill Tag
    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.15), Inches(4.0), Inches(0.42))
    pill.fill.solid()
    pill.fill.fore_color.rgb = RGBColor(37, 99, 235)
    pill.line.fill.background()
    p_p = pill.text_frame.paragraphs[0]
    p_p.text = "ACADEMIC CAPSTONE PROJECT REVIEW"
    p_p.alignment = PP_ALIGN.CENTER
    p_p.font.name = FONT_HEAD
    p_p.font.size = Pt(11)
    p_p.font.bold = True
    p_p.font.color.rgb = COLOR_WHITE

    # Title & Subtitle Box
    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.75), Inches(11.0), Inches(2.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p_t1 = tf1.paragraphs[0]
    p_t1.text = "EduMine: Integrated Educational Data Mining Framework"
    p_t1.font.name = FONT_HEAD
    p_t1.font.size = Pt(32)
    p_t1.font.bold = True
    p_t1.font.color.rgb = COLOR_WHITE

    p_t2 = tf1.add_paragraph()
    p_t2.text = "An Intelligent Student Performance Analysis, Academic Risk Prediction & Early Intervention System"
    p_t2.font.name = FONT_MAIN
    p_t2.font.size = Pt(17)
    p_t2.font.color.rgb = COLOR_SECONDARY
    p_t2.space_before = Pt(8)

    p_t3 = tf1.add_paragraph()
    p_t3.text = "End-to-End Supervised & Unsupervised Machine Learning Web Architecture"
    p_t3.font.name = FONT_MAIN
    p_t3.font.size = Pt(13)
    p_t3.font.color.rgb = RGBColor(148, 163, 184)
    p_t3.space_before = Pt(6)

    # Meta Cards Row (Student & Project Guide Info)
    # Card 1: Presented By
    c1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(4.3), Inches(4.5), Inches(2.0))
    c1.fill.solid()
    c1.fill.fore_color.rgb = RGBColor(15, 23, 42)
    c1.line.color.rgb = RGBColor(71, 85, 105)
    tf_c1 = c1.text_frame
    tf_c1.margin_left = Inches(0.25)
    tf_c1.margin_top = Inches(0.2)
    p_c1_h = tf_c1.paragraphs[0]
    p_c1_h.text = "PRESENTED BY"
    p_c1_h.font.name = FONT_HEAD
    p_c1_h.font.size = Pt(11)
    p_c1_h.font.bold = True
    p_c1_h.font.color.rgb = COLOR_SECONDARY

    p_c1_b = tf_c1.add_paragraph()
    p_c1_b.text = "Student Name: Animesh B Labh\nReg. Number: [Your Registration Number]\nDepartment: Computer Science & Engineering\nInstitution: Vellore Institute of Technology (VIT)"
    p_c1_b.font.name = FONT_MAIN
    p_c1_b.font.size = Pt(12)
    p_c1_b.font.color.rgb = COLOR_WHITE
    p_c1_b.space_before = Pt(6)

    # Card 2: Guided By
    c2 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.0), Inches(4.3), Inches(4.5), Inches(2.0))
    c2.fill.solid()
    c2.fill.fore_color.rgb = RGBColor(15, 23, 42)
    c2.line.color.rgb = RGBColor(71, 85, 105)
    tf_c2 = c2.text_frame
    tf_c2.margin_left = Inches(0.25)
    tf_c2.margin_top = Inches(0.2)
    p_c2_h = tf_c2.paragraphs[0]
    p_c2_h.text = "PROJECT GUIDANCE"
    p_c2_h.font.name = FONT_HEAD
    p_c2_h.font.size = Pt(11)
    p_c2_h.font.bold = True
    p_c2_h.font.color.rgb = COLOR_SECONDARY

    p_c2_b = tf_c2.add_paragraph()
    p_c2_b.text = "Project Guide: [Faculty Name]\nDesignation: Associate Professor / Guide\nSchool: School of Computer Science & Engineering (SCOPE)\nRepository: github.com/animeshlabh57-rgb/edumine"
    p_c2_b.font.name = FONT_MAIN
    p_c2_b.font.size = Pt(12)
    p_c2_b.font.color.rgb = COLOR_WHITE
    p_c2_b.space_before = Pt(6)

    # ==========================================
    # SLIDE 2: INTRODUCTION
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, COLOR_BG_LIGHT)
    add_header(s2, "Introduction", "Context, Motivation and the Role of Educational Data Mining (EDM)", 2)

    # 4 Cards Layout
    cards_data_s2 = [
        ("Institutional Data Explosion", "Higher educational institutions continuously record massive academic and behavioral data footprints, including continuous assessments, portal logons, assignment submissions, and attendance.", COLOR_PRIMARY),
        ("Traditional Evaluation Blindspots", "Conventional academic monitoring strictly relies on final marks and examinations post-facto. Vital behavioral precursors like weekly study drop-offs and low portal engagement are completely ignored.", COLOR_ACCENT_WARN),
        ("The Power of Educational Data Mining", "EDM applies specialized machine learning, statistical patterns, and association algorithms to uncover hidden multi-dimensional dependencies between behavior and success.", COLOR_TEAL),
        ("The EduMine Solution", "EduMine consolidates data cleaning, association mining, cohort clustering, risk classification, grade regression, and prescriptive what-if intervention into an interactive web platform.", COLOR_SECONDARY)
    ]

    for idx, (head, body, col) in enumerate(cards_data_s2):
        row = idx // 2
        col_idx = idx % 2
        x = Inches(0.8 + col_idx * 5.95)
        y = Inches(1.5 + row * 2.65)
        add_card(s2, x, y, Inches(5.75), Inches(2.45))

        # Color Accent Strip on card left
        strip = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(0.18), Inches(2.45))
        strip.fill.solid()
        strip.fill.fore_color.rgb = col
        strip.line.fill.background()

        tb = s2.shapes.add_textbox(x + Inches(0.35), y + Inches(0.2), Inches(5.15), Inches(2.05))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"{idx+1}. {head}"
        p1.font.name = FONT_HEAD
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_MAIN

        p2 = tf.add_paragraph()
        p2.text = body
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(13)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(8)

    # ==========================================
    # SLIDE 3: PROBLEM STATEMENT
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, COLOR_BG_LIGHT)
    add_header(s3, "Problem Statement", "Critical Gaps in Current Academic Monitoring Systems", 3)

    # Left Column: Big Problem Callout Card
    add_card(s3, Inches(0.8), Inches(1.5), Inches(4.5), Inches(5.3))
    strip_p = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(4.5), Inches(0.15))
    strip_p.fill.solid()
    strip_p.fill.fore_color.rgb = COLOR_ACCENT_DANGER
    strip_p.line.fill.background()

    tb_p = s3.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(3.9), Inches(4.7))
    tf_p = tb_p.text_frame
    tf_p.word_wrap = True
    p = tf_p.paragraphs[0]
    p.text = "CORE CHALLENGE"
    p.font.name = FONT_HEAD
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_DANGER

    p2 = tf_p.add_paragraph()
    p2.text = "Academic failure is typically diagnosed after semester-end exams, rendering remedial counseling ineffective and too late."
    p2.font.name = FONT_HEAD
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_TEXT_MAIN
    p2.space_before = Pt(12)

    p3 = tf_p.add_paragraph()
    p3.text = "Higher education lacks an automated, unified system capable of bridging behavioral metrics with predictive performance models to provide proactive, personalized interventions before exams occur."
    p3.font.name = FONT_MAIN
    p3.font.size = Pt(13)
    p3.font.color.rgb = COLOR_TEXT_MUTED
    p3.space_before = Pt(14)

    # Right Column: 4 Pain Points Cards
    pain_points = [
        ("Delayed Post-Mortem Diagnosis", "Risk is realized only after poor grades or semester failure occurs. No real-time alerts exist during the active semester."),
        ("Manual & Fragmented Analysis", "Advisors spend excessive hours cross-referencing disconnected spreadsheets containing attendance, quiz scores, and LMS logs."),
        ("Hidden Multi-Factor Dependencies", "Simple threshold rules fail to reveal intricate correlations—e.g., how low study hours combined with high absenteeism compound failure risk."),
        ("One-Size-Fits-All Interventions", "Institutions prescribe generic extra classes rather than tailored interventions targeting specific behavioral root-causes.")
    ]

    for idx, (h, b) in enumerate(pain_points):
        y = Inches(1.5 + idx * 1.33)
        add_card(s3, Inches(5.6), y, Inches(6.9), Inches(1.18))
        # icon square
        sq = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.8), y + Inches(0.2), Inches(0.78), Inches(0.78))
        sq.fill.solid()
        sq.fill.fore_color.rgb = RGBColor(254, 226, 226)
        sq.line.fill.background()
        sq_tf = sq.text_frame
        sq_tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        sq_p = sq_tf.paragraphs[0]
        sq_p.text = f"!{idx+1}"
        sq_p.alignment = PP_ALIGN.CENTER
        sq_p.font.name = FONT_HEAD
        sq_p.font.size = Pt(14)
        sq_p.font.bold = True
        sq_p.font.color.rgb = COLOR_ACCENT_DANGER

        tb_pt = s3.shapes.add_textbox(Inches(6.75), y + Inches(0.12), Inches(5.5), Inches(0.95))
        tf_pt = tb_pt.text_frame
        tf_pt.word_wrap = True
        p_pt1 = tf_pt.paragraphs[0]
        p_pt1.text = h
        p_pt1.font.name = FONT_HEAD
        p_pt1.font.size = Pt(14)
        p_pt1.font.bold = True
        p_pt1.font.color.rgb = COLOR_TEXT_MAIN

        p_pt2 = tf_pt.add_paragraph()
        p_pt2.text = b
        p_pt2.font.name = FONT_MAIN
        p_pt2.font.size = Pt(11)
        p_pt2.font.color.rgb = COLOR_TEXT_MUTED
        p_pt2.space_before = Pt(3)

    # ==========================================
    # SLIDE 4: OBJECTIVES
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, COLOR_BG_LIGHT)
    add_header(s4, "Project Objectives", "Concrete Goals and Deliverables of the EduMine Framework", 4)

    objectives = [
        ("Unified Mining Platform", "Develop a centralized, web-based educational data mining architecture accepting raw institutional CSV, Excel, or JSON records.", COLOR_PRIMARY),
        ("Association Rule Discovery", "Implement Apriori association algorithms to identify hidden behavioral combinations leading to examination success or failure.", COLOR_TEAL),
        ("Unsupervised Student Segmentation", "Cluster students into behavioral and academic personas using K-Means, Hierarchical, and DBSCAN with 2D PCA projections.", COLOR_SECONDARY),
        ("Early Risk Classification", "Train and benchmark supervised classifiers (Random Forest, Gradient Boosting, SVM, etc.) to predict at-risk students with >95% accuracy.", COLOR_ACCENT_WARN),
        ("Continuous Grade Regression", "Estimate precise expected final marks and GPA using ensemble regressors (Gradient Boosting, Ridge, SVR) with low error bounds.", COLOR_PRIMARY),
        ("Diagnostic Anomaly Detection", "Detect counter-intuitive academic profiles using Isolation Forests and generate actionable what-if intervention simulations.", COLOR_ACCENT_SUCCESS)
    ]

    for idx, (title, desc, col) in enumerate(objectives):
        row = idx // 3
        col_i = idx % 3
        x = Inches(0.8 + col_i * 3.95)
        y = Inches(1.5 + row * 2.65)
        add_card(s4, x, y, Inches(3.75), Inches(2.45))

        top_strip = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.75), Inches(0.12))
        top_strip.fill.solid()
        top_strip.fill.fore_color.rgb = col
        top_strip.line.fill.background()

        tb = s4.shapes.add_textbox(x + Inches(0.25), y + Inches(0.25), Inches(3.25), Inches(2.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"Objective {idx+1}\n{title}"
        p1.font.name = FONT_HEAD
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_MAIN

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(12)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(8)

    # ==========================================
    # SLIDE 5: EXISTING VS PROPOSED SYSTEM
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, COLOR_BG_LIGHT)
    add_header(s5, "Existing System vs. Proposed EduMine System", "Comparative Paradigm Shift in Educational Analytics", 5)

    # Create Styled Comparison Table
    rows = 7
    cols = 3
    left = Inches(0.8)
    top = Inches(1.5)
    width = Inches(11.733)
    height = Inches(5.2)

    table_shape = s5.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(3.0)
    table.columns[1].width = Inches(4.366)
    table.columns[2].width = Inches(4.366)

    table_data = [
        ["Comparison Dimension", "Traditional Institutional System", "Proposed EduMine Framework"],
        ["Analysis Workflow", "Manual spreadsheets, fragmented records, and delayed offline review", "Automated, asynchronous web pipeline processing records in seconds"],
        ["Data Scope", "Narrowly restricted to exam scores and final semester grades", "Holistic: combines study hours, attendance, assignments, and LMS engagement"],
        ["Detection Timing", "Reactive post-mortem (after exams are concluded)", "Proactive early-warning during active semester for timely remediation"],
        ["Analytical Depth", "Basic averages, summary histograms, and static tables", "Advanced ML: Association Rules, Clustering, Classification, Regression & Anomalies"],
        ["Student Segmentation", "Simple arbitrary mark-cutoffs (e.g. >75% Distinction)", "Unsupervised ML clustering (K-Means, DBSCAN, PCA 2D cohort personas)"],
        ["Remediation Action", "Generic non-specific advice ('Work harder in all subjects')", "Targeted what-if simulation sandbox with tailored action prescriptions"]
    ]

    for r_idx, row_data in enumerate(table_data):
        for c_idx, cell_text in enumerate(row_data):
            cell = table.cell(r_idx, c_idx)
            cell.text = cell_text
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_MAIN

            if r_idx == 0:
                cell.fill.solid()
                if c_idx == 0:
                    cell.fill.fore_color.rgb = COLOR_BG_DARK
                elif c_idx == 1:
                    cell.fill.fore_color.rgb = RGBColor(71, 85, 105)
                else:
                    cell.fill.fore_color.rgb = COLOR_PRIMARY
                p.font.bold = True
                p.font.size = Pt(13)
                p.font.color.rgb = COLOR_WHITE
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if r_idx % 2 == 1 else COLOR_WHITE
                p.font.size = Pt(11)
                if c_idx == 0:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_TEXT_MAIN
                elif c_idx == 1:
                    p.font.color.rgb = RGBColor(100, 116, 139)
                else:
                    p.font.bold = True
                    p.font.color.rgb = COLOR_PRIMARY

    # ==========================================
    # SLIDE 6: SYSTEM ARCHITECTURE
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, COLOR_BG_LIGHT)
    add_header(s6, "System Architecture", "End-to-End Pipeline from Raw Ingestion to Interactive Visualization", 6)

    # 4 Flow Steps Architecture Diagram
    flow_steps = [
        ("Layer 1: Data Ingestion", "Raw Dataset Loader\n• CSV / XLSX / JSON formats\n• Synthetic (600 records)\n• UCI Student Performance\n• Intelligent Auto-Detector", COLOR_BG_DARK),
        ("Layer 2: Preprocessing", "Data Engine & Scaler\n• Missing Value Imputation\n• Target & Feature Segregation\n• Standard & MinMax Scaling\n• One-Hot Categorical Encoding", COLOR_PRIMARY),
        ("Layer 3: Analytics Engine", "Data Mining Core\n• Apriori Association Rules\n• K-Means & DBSCAN Clusters\n• Supervised Risk Classifiers\n• Grade Regression Ensembles\n• Isolation Forest Outliers", COLOR_TEAL),
        ("Layer 4: Presentation & UI", "Interactive Dashboard\n• FastAPI RESTful Web Endpoints\n• Glassmorphic CSS3 & Chart.js\n• Real-Time What-If Sandbox\n• Actionable Intervention Plans", COLOR_SECONDARY)
    ]

    for idx, (title, desc, col) in enumerate(flow_steps):
        x = Inches(0.8 + idx * 2.95)
        y = Inches(1.6)
        card = add_card(s6, x, y, Inches(2.75), Inches(4.2))

        # Top banner for card
        top_b = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(2.75), Inches(0.7))
        top_b.fill.solid()
        top_b.fill.fore_color.rgb = col
        top_b.line.fill.background()
        tf_b = top_b.text_frame
        tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_b = tf_b.paragraphs[0]
        p_b.text = title
        p_b.alignment = PP_ALIGN.CENTER
        p_b.font.name = FONT_HEAD
        p_b.font.size = Pt(13)
        p_b.font.bold = True
        p_b.font.color.rgb = COLOR_WHITE

        # Body
        tb = s6.shapes.add_textbox(x + Inches(0.15), y + Inches(0.85), Inches(2.45), Inches(3.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p_desc = tf.paragraphs[0]
        p_desc.text = desc
        p_desc.font.name = FONT_MAIN
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_TEXT_MAIN
        p_desc.line_spacing = 1.3

        # Connective arrows
        if idx < 3:
            arrow = s6.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + Inches(2.77), Inches(3.4), Inches(0.17), Inches(0.3))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = COLOR_PRIMARY
            arrow.line.fill.background()

    # Bottom Architecture Summary Note
    note_card = add_card(s6, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.85), bg_color=RGBColor(238, 242, 255), border_color=COLOR_PRIMARY)
    tb_n = s6.shapes.add_textbox(Inches(1.0), Inches(6.05), Inches(11.3), Inches(0.75))
    tf_n = tb_n.text_frame
    p_n = tf_n.paragraphs[0]
    p_n.text = "Key Architectural Strength: Decoupled Modular Design"
    p_n.font.name = FONT_HEAD
    p_n.font.size = Pt(13)
    p_n.font.bold = True
    p_n.font.color.rgb = COLOR_PRIMARY
    p_n2 = tf_n.add_paragraph()
    p_n2.text = "Each mining engine functions independently via standardized APIs, enabling institutions to plug in custom data models without redesigning the UI or preprocessing pipeline."
    p_n2.font.name = FONT_MAIN
    p_n2.font.size = Pt(11)
    p_n2.font.color.rgb = COLOR_TEXT_MAIN

    # ==========================================
    # SLIDE 7: TECHNOLOGY STACK
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, COLOR_BG_LIGHT)
    add_header(s7, "Technology Stack", "Robust, High-Performance Software Framework Specifications", 7)

    # 8 Tech Cards in 2x4 grid
    tech_stack = [
        ("Core Language", "Python 3.10+", "Powers high-throughput data processing, machine learning model training, and analytical computation."),
        ("Backend Web API", "FastAPI & Uvicorn", "Asynchronous, production-grade REST API with auto-generated Swagger/OpenAPI documentation."),
        ("Machine Learning", "Scikit-Learn", "Standardized framework for supervised classifiers, regressors, K-Means clustering, and Isolation Forests."),
        ("Data Processing", "Pandas & NumPy", "High-performance vectorized data manipulation, missing value imputation, and correlation calculations."),
        ("Pattern Mining", "MLxtend & Native Apriori", "Vectorized frequent itemset extraction with support, confidence, lift, and leverage metrics."),
        ("Frontend UI", "HTML5 & Vanilla CSS3", "Ultra-responsive glassmorphism layout, dynamic light/dark theming, and zero bloated frameworks."),
        ("Data Visualizations", "Chart.js & HTML5 Canvas", "Interactive radar plots, scatter charts, confusion matrix heatmaps, and rule network dependency graphs."),
        ("File Ingestion", "OpenPyXL & CSV Parsers", "Instant multi-format parser supporting institutional XLSX, CSV, and JSON student records.")
    ]

    for idx, (comp, tech, role) in enumerate(tech_stack):
        r = idx // 4
        c = idx % 4
        x = Inches(0.8 + c * 2.95)
        y = Inches(1.5 + r * 2.65)
        add_card(s7, x, y, Inches(2.75), Inches(2.45))

        top_strip = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(2.75), Inches(0.12))
        top_strip.fill.solid()
        top_strip.fill.fore_color.rgb = COLOR_PRIMARY if r == 0 else COLOR_TEAL
        top_strip.line.fill.background()

        tb = s7.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), Inches(2.35), Inches(2.05))
        tf = tb.text_frame
        tf.word_wrap = True
        p_c = tf.paragraphs[0]
        p_c.text = comp.upper()
        p_c.font.name = FONT_HEAD
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = COLOR_TEXT_MUTED

        p_t = tf.add_paragraph()
        p_t.text = tech
        p_t.font.name = FONT_HEAD
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_TEXT_MAIN
        p_t.space_before = Pt(3)

        p_r = tf.add_paragraph()
        p_r.text = role
        p_r.font.name = FONT_MAIN
        p_r.font.size = Pt(11)
        p_r.font.color.rgb = COLOR_TEXT_MUTED
        p_r.space_before = Pt(6)

    # ==========================================
    # SLIDE 8: DATASET DESCRIPTION & PREPROCESSING
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, COLOR_BG_LIGHT)
    add_header(s8, "Dataset Description & Preprocessing Pipeline", "Multi-Source Student Behavioral & Academic Attributes", 8)

    # Left Card: Datasets Overview
    add_card(s8, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.3))
    tb_d = s8.shapes.add_textbox(Inches(1.05), Inches(1.7), Inches(5.2), Inches(4.9))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    p = tf_d.paragraphs[0]
    p.text = "DATASET SPECIFICATIONS"
    p.font.name = FONT_HEAD
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    bullets_d = [
        ("Synthetic Cohort Dataset", "600 realistic student academic and engagement records generated with realistic latent student profiles (Disengaged, Average, Diligent)."),
        ("UCI Student Performance Dataset", "649 secondary school student records (student-por.csv) from Portuguese secondary schools with 33 academic and socio-economic attributes."),
        ("Key Analyzed Features", "Attendance Percentage (%), Study Hours/Week, LMS Portal Activity, Assignment Completion Rate, Midterm Examination Scores, and Past Failures."),
        ("Target Outcomes", "Academic Risk Status (At-Risk vs Safe) and Final Examination Grade / GPA.")
    ]
    for h, b in bullets_d:
        p_b = tf_d.add_paragraph()
        p_b.text = f"• {h}: {b}"
        p_b.font.name = FONT_MAIN
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = COLOR_TEXT_MAIN
        p_b.space_before = Pt(8)

    # Right Card: Preprocessing Pipeline
    add_card(s8, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    tb_pr = s8.shapes.add_textbox(Inches(7.05), Inches(1.7), Inches(5.2), Inches(4.9))
    tf_pr = tb_pr.text_frame
    tf_pr.word_wrap = True
    p_pr = tf_pr.paragraphs[0]
    p_pr.text = "DATA PREPROCESSING WORKFLOW"
    p_pr.font.name = FONT_HEAD
    p_pr.font.size = Pt(15)
    p_pr.font.bold = True
    p_pr.font.color.rgb = COLOR_TEAL

    prep_steps = [
        ("Intelligent Column Detection", "Automatically detects identifiers (Student_ID), regression targets (Final_Exam, G3), and classification labels without manual configuration."),
        ("Missing Value Imputation", "Fills missing continuous metrics using median imputation and categorical variables using mode/unknown categorization."),
        ("Categorical Transformation", "Applies One-Hot Encoding (OHE) for algorithms requiring numerical vectors (Regression, SVM, Neural Nets)."),
        ("Feature Normalization & Scaling", "Utilizes StandardScaler (mean=0, std=1) for distance-sensitive algorithms (KNN, SVR, K-Means) and MinMaxScaler for itemsets."),
        ("Train/Test Partitioning", "Executes 75/25 stratified train-test splits and 5-fold cross-validation to prevent data leakage and overfitting.")
    ]
    for h, b in prep_steps:
        p_b = tf_pr.add_paragraph()
        p_b.text = f"✔ {h}: {b}"
        p_b.font.name = FONT_MAIN
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = COLOR_TEXT_MAIN
        p_b.space_before = Pt(8)

    # ==========================================
    # SLIDE 9: ASSOCIATION RULE MINING
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, COLOR_BG_LIGHT)
    add_header(s9, "Association Rule Mining", "Uncovering Latent Academic Patterns using the Apriori Algorithm", 9)

    # Top Cards: Mathematical Foundations
    add_card(s9, Inches(0.8), Inches(1.5), Inches(5.7), Inches(2.55))
    tb_m = s9.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.2), Inches(2.2))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    p = tf_m.paragraphs[0]
    p.text = "MATHEMATICAL EVALUATION MEASURES"
    p.font.name = FONT_HEAD
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    formulas = [
        ("Support", "Support(A → B) = P(A ∩ B)", "Frequency of itemset A and B co-occurring across all students."),
        ("Confidence", "Confidence(A → B) = P(B | A) = Support(A ∩ B) / Support(A)", "Conditional probability that B occurs given A."),
        ("Lift", "Lift(A → B) = Support(A ∩ B) / [Support(A) × Support(B)]", "Strength of rule over random co-occurrence (>1 = positive association).")
    ]
    for name, f_str, desc in formulas:
        p_f = tf_m.add_paragraph()
        p_f.text = f"• {name}: {f_str} — {desc}"
        p_f.font.name = FONT_MAIN
        p_f.font.size = Pt(11)
        p_f.font.color.rgb = COLOR_TEXT_MAIN
        p_f.space_before = Pt(4)

    # Top Right Card: Discretization Strategy
    add_card(s9, Inches(6.8), Inches(1.5), Inches(5.7), Inches(2.55))
    tb_disc = s9.shapes.add_textbox(Inches(7.05), Inches(1.65), Inches(5.2), Inches(2.2))
    tf_disc = tb_disc.text_frame
    tf_disc.word_wrap = True
    p = tf_disc.paragraphs[0]
    p.text = "CONTINUOUS-TO-CATEGORICAL DISCRETIZATION"
    p.font.name = FONT_HEAD
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL

    p2 = tf_disc.add_paragraph()
    p2.text = "Continuous behavioral variables are mapped into educational quintiles before mining:\n• Attendance: Low (<70%), Moderate (70-85%), High (>85%)\n• Study Hours: Low (<8 hrs/wk), Moderate (8-18 hrs), Diligent (>18 hrs)\n• Assignment Scores: Incomplete (<60%), Average (60-80%), High (>80%)\n• Academic Outcome: At-Risk vs Safe / Distinction"
    p2.font.name = FONT_MAIN
    p2.font.size = Pt(11.5)
    p2.font.color.rgb = COLOR_TEXT_MAIN
    p2.space_before = Pt(6)

    # Bottom Full Card: Example Discovered Rules
    add_card(s9, Inches(0.8), Inches(4.3), Inches(11.733), Inches(2.5))
    tb_rules = s9.shapes.add_textbox(Inches(1.05), Inches(4.45), Inches(11.2), Inches(2.2))
    tf_rules = tb_rules.text_frame
    tf_rules.word_wrap = True
    p_rh = tf_rules.paragraphs[0]
    p_rh.text = "HIGH-IMPACT DISCOVERED ASSOCIATION RULES (SAMPLE EXTRACT FROM EDUMINE)"
    p_rh.font.name = FONT_HEAD
    p_rh.font.size = Pt(14)
    p_rh.font.bold = True
    p_rh.font.color.rgb = COLOR_TEXT_MAIN

    rules_table = [
        ("Rule 1 (Critical Risk):", "Low Attendance (<70%) ∧ Low Study Hours (<8 hrs) → Academic Risk", "Support: 0.16 (16%) | Confidence: 0.92 (92%) | Lift: 3.32x"),
        ("Rule 2 (Intervention Gap):", "Low Midterm (<55) ∧ Incomplete Assignments (<60%) → Final Failure", "Support: 0.14 (14%) | Confidence: 0.88 (88%) | Lift: 2.85x"),
        ("Rule 3 (Excellence Pattern):", "High Attendance (>90%) ∧ LMS Engagement (>14 hrs) → Grade A / Safe", "Support: 0.28 (28%) | Confidence: 0.95 (95%) | Lift: 1.45x")
    ]
    for r_title, r_body, r_meta in rules_table:
        p_r = tf_rules.add_paragraph()
        p_r.text = f"{r_title}  {r_body}   [{r_meta}]"
        p_r.font.name = FONT_MAIN
        p_r.font.size = Pt(12)
        p_r.font.color.rgb = COLOR_PRIMARY
        p_r.space_before = Pt(6)

    # ==========================================
    # SLIDE 10: STUDENT CLUSTERING
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, COLOR_BG_LIGHT)
    add_header(s10, "Student Clustering & Cohort Segmentation", "Unsupervised Persona Profiling with K-Means, DBSCAN & 2D PCA", 10)

    # 3 Persona Cards Layout
    personas = [
        ("Cluster 1: High-Flying Diligent Achievers", "Size: ~30% of Cohort", "• Average Study Hours: 24.2 hrs/week\n• Average Attendance: 92.5%\n• Assignment Completion: 89.2%\n• Final Exam Average: 84.8 / 100\n• Academic Risk: 0% (Safe)\n• Action: Advanced research projects, honors mentorship, and peer tutor roles.", COLOR_ACCENT_SUCCESS),
        ("Cluster 2: Consistent Moderate Performers", "Size: ~45% of Cohort", "• Average Study Hours: 14.1 hrs/week\n• Average Attendance: 81.3%\n• Assignment Completion: 73.8%\n• Final Exam Average: 68.4 / 100\n• Academic Risk: 4.8% (Minor)\n• Action: Targeted concept-strengthening and motivational study groups.", COLOR_PRIMARY),
        ("Cluster 3: Disengaged / At-Risk Cohort", "Size: ~25% of Cohort", "• Average Study Hours: 6.2 hrs/week\n• Average Attendance: 64.1%\n• Assignment Completion: 52.4%\n• Final Exam Average: 44.6 / 100\n• Academic Risk: 88.5% (High)\n• Action: Mandatory academic counselor check-ins, attendance warnings, remedial clinics.", COLOR_ACCENT_DANGER)
    ]

    for idx, (title, size, desc, col) in enumerate(personas):
        x = Inches(0.8 + idx * 3.95)
        y = Inches(1.5)
        add_card(s10, x, y, Inches(3.75), Inches(4.3))

        top_strip = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.75), Inches(0.7))
        top_strip.fill.solid()
        top_strip.fill.fore_color.rgb = col
        top_strip.line.fill.background()
        tf_s = top_strip.text_frame
        tf_s.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_s = tf_s.paragraphs[0]
        p_s.text = title
        p_s.alignment = PP_ALIGN.CENTER
        p_s.font.name = FONT_HEAD
        p_s.font.size = Pt(11)
        p_s.font.bold = True
        p_s.font.color.rgb = COLOR_WHITE

        tb = s10.shapes.add_textbox(x + Inches(0.2), y + Inches(0.8), Inches(3.35), Inches(3.35))
        tf = tb.text_frame
        tf.word_wrap = True
        p_sz = tf.paragraphs[0]
        p_sz.text = size
        p_sz.font.name = FONT_HEAD
        p_sz.font.size = Pt(13)
        p_sz.font.bold = True
        p_sz.font.color.rgb = col

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_MAIN
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_TEXT_MAIN
        p_d.line_spacing = 1.3
        p_d.space_before = Pt(6)

    # Bottom Banner: Cluster Validation Metrics
    bot_card = add_card(s10, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.85), bg_color=RGBColor(241, 245, 249))
    tb_b = s10.shapes.add_textbox(Inches(1.0), Inches(6.05), Inches(11.3), Inches(0.75))
    tf_b = tb_b.text_frame
    p_b1 = tf_b.paragraphs[0]
    p_b1.text = "Clustering Diagnostics & Dimensionality Reduction"
    p_b1.font.name = FONT_HEAD
    p_b1.font.size = Pt(12)
    p_b1.font.bold = True
    p_b1.font.color.rgb = COLOR_TEXT_MAIN
    p_b2 = tf_b.add_paragraph()
    p_b2.text = "Optimal cluster count (k=3) validated via the Elbow Method (Sum of Squared Errors) and Silhouette Score (0.42). Principal Component Analysis (PCA) projects high-dimensional metrics onto a 2D interactive coordinate plane."
    p_b2.font.name = FONT_MAIN
    p_b2.font.size = Pt(11)
    p_b2.font.color.rgb = COLOR_TEXT_MUTED

    # ==========================================
    # SLIDE 11: ACADEMIC RISK CLASSIFICATION
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, COLOR_BG_LIGHT)
    add_header(s11, "Academic Risk Classification", "Benchmarking Supervised Learning Models for Proactive Alerting", 11)

    # Table on Left Side
    table_shape_s11 = s11.shapes.add_table(7, 5, Inches(0.8), Inches(1.5), Inches(7.5), Inches(4.3))
    t11 = table_shape_s11.table
    t11.columns[0].width = Inches(2.5)
    t11.columns[1].width = Inches(1.25)
    t11.columns[2].width = Inches(1.25)
    t11.columns[3].width = Inches(1.25)
    t11.columns[4].width = Inches(1.25)

    clf_metrics = [
        ["Model Name", "Accuracy", "F1-Score", "ROC-AUC", "CV-Mean"],
        ["Logistic Regression", "97.33%", "95.12%", "0.987", "96.4%"],
        ["Random Forest", "97.33%", "95.00%", "0.989", "96.9%"],
        ["Support Vector Machine", "97.33%", "95.00%", "0.975", "96.2%"],
        ["Gradient Boosting", "95.33%", "91.36%", "0.989", "95.8%"],
        ["K-Nearest Neighbors", "95.33%", "91.36%", "0.979", "94.7%"],
        ["Decision Tree", "92.00%", "86.05%", "0.923", "91.1%"]
    ]

    for r_i, r_data in enumerate(clf_metrics):
        for c_i, val in enumerate(r_data):
            cell = t11.cell(r_i, c_i)
            cell.text = val
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_MAIN
            if r_i == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_PRIMARY
                p.font.bold = True
                p.font.size = Pt(12)
                p.font.color.rgb = COLOR_WHITE
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(241, 245, 249) if r_i % 2 == 1 else COLOR_WHITE
                p.font.size = Pt(11)
                p.font.color.rgb = COLOR_TEXT_MAIN
                if c_i == 0:
                    p.font.bold = True

    # Right Side: Feature Importance Card & Notes
    add_card(s11, Inches(8.55), Inches(1.5), Inches(3.98), Inches(4.3))
    tb_fi = s11.shapes.add_textbox(Inches(8.75), Inches(1.65), Inches(3.6), Inches(4.0))
    tf_fi = tb_fi.text_frame
    tf_fi.word_wrap = True
    p = tf_fi.paragraphs[0]
    p.text = "FEATURE IMPORTANCE HIERARCHY"
    p.font.name = FONT_HEAD
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    p_body = tf_fi.add_paragraph()
    p_body.text = "Random Forest Gini Impurity reduction identifies the most influential predictors of academic failure:\n\n1. Attendance % (34.2%)\n   Strongest single predictor of student completion.\n2. Midterm Score (26.5%)\n   Early exam gap compounds into final risk.\n3. Assignment Rate (18.7%)\n   Continuous engagement buffer.\n4. Study Hours (12.4%)\n   Weekly effort foundation.\n5. Past Failures (8.2%)\n   Historical academic friction."
    p_body.font.name = FONT_MAIN
    p_body.font.size = Pt(11)
    p_body.font.color.rgb = COLOR_TEXT_MAIN
    p_body.space_before = Pt(6)

    # Bottom Validation Pill
    b_pill = add_card(s11, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.85), bg_color=RGBColor(238, 242, 255), border_color=COLOR_PRIMARY)
    tb_val = s11.shapes.add_textbox(Inches(1.0), Inches(6.05), Inches(11.3), Inches(0.75))
    tf_val = tb_val.text_frame
    p_val1 = tf_val.paragraphs[0]
    p_val1.text = "Evaluation Summary: Outstanding Predictive Reliability"
    p_val1.font.name = FONT_HEAD
    p_val1.font.size = Pt(12)
    p_val1.font.bold = True
    p_val1.font.color.rgb = COLOR_PRIMARY
    p_val2 = tf_val.add_paragraph()
    p_val2.text = "Classifiers attain up to 97.33% testing accuracy and 0.989 ROC-AUC. 5-fold cross-validation verifies that predictions do not suffer from synthetic dataset overfitting or data leakage."
    p_val2.font.name = FONT_MAIN
    p_val2.font.size = Pt(11)
    p_val2.font.color.rgb = COLOR_TEXT_MAIN

    # ==========================================
    # SLIDE 12: GRADE PREDICTION & ANOMALY DETECTION
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, COLOR_BG_LIGHT)
    add_header(s12, "Grade Prediction & Anomaly Detection", "Continuous Marks Estimation (Regression) & Outlier Identification", 12)

    # Left Card: Regression Ensembles
    add_card(s12, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.3))
    tb_reg = s12.shapes.add_textbox(Inches(1.05), Inches(1.7), Inches(5.2), Inches(4.9))
    tf_reg = tb_reg.text_frame
    tf_reg.word_wrap = True
    p = tf_reg.paragraphs[0]
    p.text = "CONTINUOUS GRADE REGRESSION"
    p.font.name = FONT_HEAD
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    reg_content = (
        "Estimates exact expected final marks (0-100) and GPA (0-4.0 scale):\n\n"
        "• Lasso Regression: R² = 0.9165 (91.7% variance), RMSE = 4.80, MAE = 3.96\n"
        "• Ridge Regression: R² = 0.9125 (91.3% variance), RMSE = 4.91, MAE = 4.06\n"
        "• Random Forest Regressor: R² = 0.8983 (89.8%), RMSE = 5.29, MAE = 4.16\n"
        "• Gradient Boosting Regressor: R² = 0.8968 (89.7%), RMSE = 5.34, MAE = 4.32\n"
        "• Support Vector Regressor: R² = 0.8344 (83.4%), RMSE = 6.76, MAE = 5.01\n\n"
        "Significance: Enables fine-grained grade letter forecasting (O, A+, A, B, C, F) rather than crude binary pass/fail classification."
    )
    p_rb = tf_reg.add_paragraph()
    p_rb.text = reg_content
    p_rb.font.name = FONT_MAIN
    p_rb.font.size = Pt(11.5)
    p_rb.font.color.rgb = COLOR_TEXT_MAIN
    p_rb.space_before = Pt(8)

    # Right Card: Anomaly Detection
    add_card(s12, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    tb_ano = s12.shapes.add_textbox(Inches(7.05), Inches(1.7), Inches(5.2), Inches(4.9))
    tf_ano = tb_ano.text_frame
    tf_ano.word_wrap = True
    p = tf_ano.paragraphs[0]
    p.text = "ISOLATION FOREST ANOMALY DETECTION"
    p.font.name = FONT_HEAD
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT_WARN

    ano_content = (
        "Isolates counter-intuitive or abnormal student behaviors:\n\n"
        "• Contamination Factor: Tunable threshold (default 5.0% of cohort)\n"
        "• Mechanism: Builds tree partitions to isolate anomalous records in few splits\n\n"
        "Diagnostic Anomaly Profiles Detected:\n"
        "1. High Attendance with Unexpected Failure:\n"
        "   Student attends 95% of classes but scores <40% on examinations. Points to test anxiety or fundamental comprehension barriers.\n\n"
        "2. High Exam Marks with Zero Engagement:\n"
        "   Student has <50% attendance and low LMS hours yet achieves 90%+. Points to external tutoring, exam malpractice, or prior mastery.\n\n"
        "Benefit: Flags unique cases that standard linear models fail to explain."
    )
    p_ab = tf_ano.add_paragraph()
    p_ab.text = ano_content
    p_ab.font.name = FONT_MAIN
    p_ab.font.size = Pt(11.5)
    p_ab.font.color.rgb = COLOR_TEXT_MAIN
    p_ab.space_before = Pt(8)

    # ==========================================
    # SLIDE 13: EARLY INTERVENTION & SIMULATOR
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13, COLOR_BG_LIGHT)
    add_header(s13, "Early Intervention & What-If Simulation", "Prescriptive Counseling Automation and Scenario Modeling Sandbox", 13)

    # Left: Prescriptive Action Cards
    add_card(s13, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.3))
    tb_int = s13.shapes.add_textbox(Inches(1.05), Inches(1.7), Inches(5.2), Inches(4.9))
    tf_int = tb_int.text_frame
    tf_int.word_wrap = True
    p = tf_int.paragraphs[0]
    p.text = "TARGETED REMEDIATION ENGINE"
    p.font.name = FONT_HEAD
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL

    interventions_list = [
        ("Attendance Deficit (<72%)", "Triggers automated official attendance alert and schedules mandatory session with faculty mentor."),
        ("Assignment Friction (<65%)", "Automatically enrolls student in homework coaching clinics and assigns collaborative peer group."),
        ("Midterm Examination Gap (<55)", "Mandates diagnostic 1-on-1 problem-solving tutorial review to address syllabus misunderstandings."),
        ("Low Study Hours (<8 hrs/wk)", "Pairs student with high-achieving peer study buddy targeting a minimum 14 hrs/week study regimen.")
    ]
    for h, b in interventions_list:
        p_b = tf_int.add_paragraph()
        p_b.text = f"• {h}:\n  {b}"
        p_b.font.name = FONT_MAIN
        p_b.font.size = Pt(11.5)
        p_b.font.color.rgb = COLOR_TEXT_MAIN
        p_b.space_before = Pt(8)

    # Right: What-If Simulation Sandbox
    add_card(s13, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    tb_sim = s13.shapes.add_textbox(Inches(7.05), Inches(1.7), Inches(5.2), Inches(4.9))
    tf_sim = tb_sim.text_frame
    tf_sim.word_wrap = True
    p = tf_sim.paragraphs[0]
    p.text = "LIVE WHAT-IF SIMULATION SANDBOX"
    p.font.name = FONT_HEAD
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    sim_text = (
        "The web dashboard enables faculty and academic advisors to dynamically slide behavioral levers and observe real-time model re-estimation:\n\n"
        "Baseline Profile (STU-1042):\n"
        "• Attendance: 62% | Study: 5 hrs/wk | Midterm: 48\n"
        "• Model Output: 88.4% Risk Probability (Grade F / 42.1 marks)\n\n"
        "Simulated Intervention Adjustments:\n"
        "• Boost Attendance: 62% → 85% (+23%)\n"
        "• Increase Study Time: 5 → 14 hrs/wk (+9 hrs)\n"
        "• Complete Assignments: 50% → 80% (+30%)\n\n"
        "Simulated Real-Time Outcome:\n"
        "• Risk Probability Drops: 88.4% → 11.2% (-77.2% Risk Reduction!)\n"
        "• Projected Grade: 42.1 (F) → 71.5 (A - Very Good)"
    )
    p_sb = tf_sim.add_paragraph()
    p_sb.text = sim_text
    p_sb.font.name = FONT_MAIN
    p_sb.font.size = Pt(11)
    p_sb.font.color.rgb = COLOR_TEXT_MAIN
    p_sb.space_before = Pt(6)

    # ==========================================
    # SLIDE 14: RESULTS & DISCUSSION
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14, COLOR_BG_LIGHT)
    add_header(s14, "Results & Discussion", "Summary of Verified Empirical Outputs & Web Dashboard Modules", 14)

    # 4 Cards Layout showing actual results
    res_cards = [
        ("Dashboard & Data Explorer", "• 600 records loaded with dynamic KPIs.\n• Real-time at-risk rate: 27.7% baseline.\n• Searchable, paginated student table with color-coded risk flags.\n• One-click institutional CSV/Excel file uploader.", COLOR_PRIMARY),
        ("Apriori Association Mining", "• Generated 24 high-confidence educational rules.\n• Strongest risk rule: Low Attendance + Low Study → Risk (Lift 3.32x, Conf 92%).\n• Dynamic interactive network canvas graph visualizing rule antecedents & consequents.", COLOR_TEAL),
        ("Multi-Model Risk Benchmark", "• Logistic Regression & Random Forest achieved 97.33% accuracy.\n• ROC-AUC of 0.989 confirms pristine discriminatory power.\n• 5-fold cross-validation standard deviation < 1.2% across folds.", COLOR_ACCENT_SUCCESS),
        ("Grade Regression & Simulator", "• Lasso and Ridge regression explain 91.65% and 91.25% variance (R²).\n• Average prediction error constrained within ±3.96 marks (MAE).\n• Interactive what-if sandbox proves actionable remediation roadmap.", COLOR_SECONDARY)
    ]

    for idx, (title, body, col) in enumerate(res_cards):
        r = idx // 2
        c = idx % 2
        x = Inches(0.8 + c * 5.95)
        y = Inches(1.5 + r * 2.65)
        add_card(s14, x, y, Inches(5.75), Inches(2.45))

        top_strip = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.75), Inches(0.12))
        top_strip.fill.solid()
        top_strip.fill.fore_color.rgb = col
        top_strip.line.fill.background()

        tb = s14.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), Inches(5.25), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEAD
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_MAIN

        p2 = tf.add_paragraph()
        p2.text = body
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(12)
        p2.font.color.rgb = COLOR_TEXT_MUTED
        p2.space_before = Pt(8)

    # ==========================================
    # SLIDE 15: CONCLUSION & FUTURE SCOPE
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15, COLOR_BG_LIGHT)
    add_header(s15, "Conclusion & Future Scope", "Research Takeaways and Roadmaps for Institutional Deployment", 15)

    # Left: Conclusion
    add_card(s15, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.3))
    tb_c = s15.shapes.add_textbox(Inches(1.05), Inches(1.7), Inches(5.2), Inches(4.9))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    p.text = "RESEARCH CONCLUSIONS"
    p.font.name = FONT_HEAD
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY

    conclusions = [
        ("Unified Educational Platform", "EduMine successfully brings together preprocessing, association rules, clustering, classification, regression, and anomaly detection into one cohesive web suite."),
        ("Proactive vs Reactive Shift", "Shifts the academic paradigm from post-failure reaction to early mid-semester identification, granting faculty crucial time to intervene."),
        ("Empirical Superiority", "Supervised classifiers achieve 97.33% accuracy, while regression models explain over 91.6% of grade variance with low error (MAE 3.96)."),
        ("Actionable Insights", "What-if simulation bridges machine learning predictions directly with practical counseling prescriptions.")
    ]
    for h, b in conclusions:
        p_b = tf_c.add_paragraph()
        p_b.text = f"✔ {h}:\n  {b}"
        p_b.font.name = FONT_MAIN
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = COLOR_TEXT_MAIN
        p_b.space_before = Pt(8)

    # Right: Future Scope
    add_card(s15, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    tb_f = s15.shapes.add_textbox(Inches(7.05), Inches(1.7), Inches(5.2), Inches(4.9))
    tf_f = tb_f.text_frame
    tf_f.word_wrap = True
    p = tf_f.paragraphs[0]
    p.text = "FUTURE RESEARCH & EXTENSIONS"
    p.font.name = FONT_HEAD
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_TEAL

    future = [
        ("Institutional LMS Integration", "Direct API webhooks connecting with Canvas, Moodle, and Blackboard for automated nightly sync of student portal telemetry."),
        ("Explainable AI (XAI)", "Embedding SHAP (SHapley Additive exPlanations) and LIME to generate individualized, feature-by-feature rationale for counselor audits."),
        ("Deep Learning Sequential Models", "Deploying LSTM / GRU recurrent architectures to analyze time-series clickstream trajectories over 4-year degree programs."),
        ("Multi-Institutional Validation", "Expanding benchmarking across diverse university disciplines and demographics to validate cross-domain generalizability.")
    ]
    for h, b in future:
        p_b = tf_f.add_paragraph()
        p_b.text = f"🚀 {h}:\n  {b}"
        p_b.font.name = FONT_MAIN
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = COLOR_TEXT_MAIN
        p_b.space_before = Pt(8)

    prs.save(output_path)
    print(f"Successfully generated 15-slide PowerPoint deck at: {output_path}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "EduMine_Project_Review.pptx"
    create_deck(out_file)
