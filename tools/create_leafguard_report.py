from __future__ import annotations

import html
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "LeafGuard_Project_Report.pdf"


class Rule(Flowable):
    def __init__(self, width=440, color=colors.HexColor("#2f6f3e")):
        super().__init__()
        self.width = width
        self.height = 8
        self.color = color

    def draw(self):
        return


def styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title",
            parent=base["Title"],
            fontName="Times-Bold",
            fontSize=16,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=10,
        ),
        "cover": ParagraphStyle(
            "cover",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=12,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Times-Bold",
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceBefore=6,
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=15.5,
            alignment=TA_JUSTIFY,
            firstLineIndent=18,
            spaceAfter=7,
        ),
        "body_no_indent": ParagraphStyle(
            "body_no_indent",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=15.5,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=15,
            leftIndent=20,
            bulletIndent=8,
            spaceAfter=5,
        ),
        "toc": ParagraphStyle(
            "toc",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=10.8,
            leading=16,
            leftIndent=15,
            spaceAfter=5,
        ),
        "code": ParagraphStyle(
            "code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.1,
            leading=8.8,
            leftIndent=0,
            rightIndent=0,
            spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "caption",
            parent=base["BodyText"],
            fontName="Times-Italic",
            fontSize=9.2,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=8,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            parent=base["BodyText"],
            fontName="Times-Roman",
            fontSize=8.6,
            leading=10.5,
        ),
        "table_head": ParagraphStyle(
            "table_head",
            parent=base["BodyText"],
            fontName="Times-Bold",
            fontSize=8.8,
            leading=10.5,
            textColor=colors.black,
            alignment=TA_CENTER,
        ),
    }


S = styles()


def p(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    flow = []
    for item in items:
        flow.append(Paragraph(item, S["bullet"], bulletText="•"))
    return flow


def chapter(title):
    return [PageBreak(), Spacer(1, 6), p(title, "h1"), Spacer(1, 4)]


def section(title, paragraphs):
    flow = [p(title, "h2")]
    for para in paragraphs:
        if isinstance(para, list):
            flow.extend(bullets(para))
        else:
            flow.append(p(para))
    return flow


def on_page(canvas, doc):
    return


def clean_code(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    text = text.replace("\t", "    ")
    lines = text.splitlines()
    numbered = [f"{i:03d}  {line}" for i, line in enumerate(lines, 1)]
    return "\n".join(numbered)


def code_pages(title: str, path: Path, lines_per_page=48):
    lines = clean_code(path).splitlines()
    flow = [PageBreak(), p(title, "h1"), Spacer(1, 8)]
    for idx in range(0, len(lines), lines_per_page):
        if idx:
            flow.append(PageBreak())
            flow.append(p(f"{title} (continued)", "h1"))
            flow.append(Spacer(1, 8))
        chunk = "\n".join(lines[idx : idx + lines_per_page])
        flow.append(Preformatted(chunk, S["code"], maxLineLength=94))
    return flow


def table(data, widths):
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.white),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.white]),
            ]
        )
    )
    return t


def cover_pages():
    return [
        Spacer(1, 0.55 * inch),
        p("LEAFGUARD - PLANT DISEASE DETECTION SYSTEM", "cover_title"),
        Spacer(1, 0.2 * inch),
        p("Project Report Submitted in the partial fulfillment of the capstone project Of", "cover"),
        p("<b>Bachelor of Computer Application</b>", "cover"),
        Spacer(1, 0.35 * inch),
        p("By:", "cover"),
        p("<b>Abhay Chopra</b>", "cover"),
        p("Roll no: 2303004001", "cover"),
        Spacer(1, 0.25 * inch),
        p("Academic Session (2023-2026)", "cover"),
        Spacer(1, 0.35 * inch),
        p("Under the Guidance of", "cover"),
        p("<b>Adil Raja</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Archana Salaria</b>", "cover"),
        p("Assistant Professor &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Associate Professor", "cover"),
        Spacer(1, 0.35 * inch),
        p("Department Of Computer Science And Engineering", "cover"),
        p("Rayat Bahra University , Kharar", "cover"),
        p("Punjab, India", "cover"),
        PageBreak(),
        p("CERTIFICATE", "h1"),
        Rule(),
        p(
            "This is to certify that the project titled <b>“LeafGuard: Plant Disease Detection System”</b> has been completed and submitted in partial fulfillment of the requirements for the award of the degree of Bachelor of Computer Application. The project has been carried out with sincere effort and demonstrates practical application of computer vision, machine learning, database logging, and web application development.",
        ),
        p(
            "The work presented in this report is based on the implementation of a Flask-based application that accepts plant leaf images, preprocesses them, classifies plant diseases using an EfficientNetB0 deep learning model, and presents actionable treatment guidance to the user. The project is suitable for academic evaluation because it combines theoretical machine learning concepts with a working user-facing software system.",
        ),
        Spacer(1, 0.7 * inch),
        p("Project Guide Signature: __________________________", "body_no_indent"),
        p("Department Seal: _________________________________", "body_no_indent"),
        PageBreak(),
        p("ACKNOWLEDGEMENT", "h1"),
        Rule(),
        p(
            "I would like to express my sincere gratitude to my faculty guides, mentors, classmates, and all those who supported the completion of this project. Their guidance helped me understand the practical connection between programming, machine learning, image processing, and real-world agricultural problems.",
        ),
        p(
            "I am especially thankful for the academic environment that encouraged experimentation with image preprocessing, EfficientNetB0-based classification, Flask routing, SQLite storage, and responsive interface design. The project improved my understanding of how a machine learning model becomes useful only when it is connected to a complete workflow that ordinary users can access.",
        ),
        p(
            "I also acknowledge the importance of open learning resources and publicly available plant disease datasets that made it possible to study disease classes, symptoms, treatment recommendations, and model behavior. This report is the result of continuous learning, testing, documentation, and refinement.",
        ),
        PageBreak(),
        p("DECLARATION", "h1"),
        Rule(),
        p(
            "I hereby declare that the project titled <b>“LeafGuard: Plant Disease Detection System”</b> is an original academic project prepared as part of my capstone work. The design, implementation, analysis, and documentation have been completed with sincere effort and academic integrity.",
        ),
        p(
            "The system described in this report has been developed using Python, Flask, OpenCV, TensorFlow/Keras, EfficientNetB0, SQLite, HTML, CSS, and JavaScript. Wherever external libraries, datasets, or conceptual references have been used, they have been acknowledged appropriately in the report.",
        ),
        p(
            "I take responsibility for the correctness of the work described here and confirm that the project has not been submitted elsewhere for the award of any other degree, diploma, or certificate.",
        ),
        Spacer(1, 0.8 * inch),
        p("Student Signature: _______________________________", "body_no_indent"),
        p("Date: ___________________________________________", "body_no_indent"),
    ]


def toc_pages():
    items = [
        "Chapter 1: Introduction",
        "• Overview of LeafGuard",
        "• Background and Motivation",
        "• Importance of Plant Disease Detection",
        "• Problem Statement and Objectives",
        "Chapter 2: Project Plan and Requirements Analysis",
        "• Agile Planning and Development Phases",
        "• Functional and Non-Functional Requirements",
        "• Hardware, Software, and Dataset Requirements",
        "Chapter 3: System Design and Architecture",
        "• Overall Architecture",
        "• Data Flow and Module Design",
        "• Database Design",
        "• User Interface Design",
        "Chapter 4: Implementation and Results",
        "• OpenCV Preprocessing Pipeline",
        "• EfficientNetB0 Prediction Service",
        "• Flask API and Dashboard",
        "• Result Interpretation and Treatment Advice",
        "Chapter 5: Testing and Evaluation",
        "• Unit Testing, Integration Testing, and UI Testing",
        "• Model Testing and Error Handling",
        "• Evaluation Observations",
        "Chapter 6: Conclusion",
        "• Summary of Achievements",
        "• Skills Learned and Academic Impact",
        "Chapter 7: Future Scope",
        "• Deployment, Model Improvement, and Farmer-Focused Features",
        "Appendix A: Source Code",
        "References",
    ]
    flow = [PageBreak(), p("Index:", "h1"), Rule(), Spacer(1, 8)]
    for item in items:
        flow.append(p(html.escape(item), "toc"))
    return flow


def body_pages():
    flow = []
    flow += chapter("Chapter 1: INTRODUCTION")
    flow += section(
        "1.1 Overview of the Project",
        [
            "LeafGuard is a plant disease detection system designed to identify common crop diseases from leaf images. The application combines image preprocessing, deep learning classification, and a web-based interface so that users can upload a leaf image and receive disease information, confidence score, likely symptoms, severity status, and treatment guidance.",
            "The system uses a Flask backend to manage image upload, validation, preprocessing, prediction, and response generation. Image preprocessing is used to resize and prepare the leaf image before it is passed into an EfficientNetB0-based model. The prediction is then mapped to disease labels, symptom lists, and treatment advice stored in the application configuration.",
            "The project demonstrates how artificial intelligence can support agriculture by making early disease recognition more accessible. Although the system is academic in scale, its design follows a realistic workflow: input acquisition, image preparation, model inference, result explanation, and record keeping through a database-backed dashboard.",
        ],
    )
    flow += section(
        "1.2 Background and Motivation",
        [
            "Agriculture is one of the most important sectors for food security, rural employment, and economic stability. Plant diseases reduce crop yield, lower market quality, and increase the cost of cultivation. Many farmers identify diseases only after visible damage has spread, which makes treatment more expensive and less effective.",
            "Advances in computer vision and deep learning have made it possible to classify plant diseases from images with increasing accuracy. A smartphone or web-based upload interface can become a practical bridge between farmers and machine learning models. LeafGuard is motivated by this possibility: a simple tool that converts a leaf image into useful decision support.",
            "The project is also motivated by the need for students to understand complete software systems rather than isolated algorithms. A trained model alone is not enough. It must be connected to preprocessing, routing, validation, storage, interface design, and error handling before it can solve a real problem.",
        ],
    )
    flow += section(
        "1.3 Importance of Plant Disease Detection",
        [
            "Early disease detection helps reduce the spread of infection, protects crop productivity, and supports responsible use of pesticides and fungicides.",
            "Automated analysis can assist users in areas where expert plant pathologists or agricultural advisors are not immediately available.",
            "A digital record of predictions can help track disease patterns over time and support better field-level decision making.",
            "Computer vision systems create opportunities for scalable, low-cost agricultural advisory services.",
        ],
    )
    flow += section(
        "1.4 Problem Statement",
        [
            "The main problem addressed by LeafGuard is the difficulty of quickly identifying plant diseases from visible leaf symptoms. Manual identification requires experience, and incorrect diagnosis may lead to wrong treatment, crop loss, or unnecessary chemical use. The project therefore aims to provide an accessible image-based system for disease prediction and treatment guidance.",
            "The system accepts common image formats, applies preprocessing to make the input more suitable for classification, predicts the most likely class, and presents the output in a user-friendly format. The output is not intended to replace professional agricultural advice, but it provides a helpful first-level screening mechanism.",
        ],
    )
    flow += section(
        "1.5 Objectives",
        [
            [
                "To design and develop a web application for plant leaf image upload and disease prediction.",
                "To preprocess images using OpenCV operations such as resizing, denoising, color conversion, masking, and morphological filtering.",
                "To integrate an EfficientNetB0 deep learning model for multiclass plant disease classification.",
                "To provide confidence score, symptoms, severity label, and treatment advice with every prediction.",
                "To store prediction history in SQLite and display summary statistics through a dashboard.",
                "To create a responsive and visually clear interface for users.",
            ]
        ],
    )
    flow += section(
        "1.6 Scope of the Project",
        [
            "The project covers 38 PlantVillage-style classes across crops such as apple, corn, grape, potato, tomato, strawberry, pepper, peach, cherry, squash, orange, soybean, raspberry, and blueberry. It supports image upload through a browser interface and produces structured JSON responses for prediction results.",
            "The scope includes image preprocessing, backend inference, treatment mapping, symptom display, database logging, and dashboard reporting. It does not include real-time field camera integration, mobile app packaging, cloud deployment, or expert-verified diagnosis, which are discussed later under future scope.",
        ],
    )

    flow += chapter("Chapter 2: PROJECT PLAN & REQUIREMENTS ANALYSIS")
    flow += section(
        "2.1 Development Methodology",
        [
            "The project follows an incremental development approach. Each module was planned, implemented, tested, and connected to the next module. This approach made it easier to isolate errors and improve the system gradually.",
            "The first phase focused on understanding the problem domain and selecting the dataset and model architecture. The second phase implemented preprocessing and model service logic. The third phase connected the model to Flask routes. The fourth phase developed the user interface and dashboard. The final phase involved testing, documentation, and report preparation.",
        ],
    )
    flow += section(
        "2.2 Development Phases",
        [
            [
                "Phase 1: Dataset study and disease class identification.",
                "Phase 2: OpenCV preprocessing pipeline design.",
                "Phase 3: EfficientNetB0 training and model export.",
                "Phase 4: Flask application integration.",
                "Phase 5: SQLite prediction logging and dashboard creation.",
                "Phase 6: Interface polishing, testing, and documentation.",
            ]
        ],
    )
    flow += section(
        "2.3 Functional Requirements",
        [
            [
                "The user shall be able to upload a JPG, JPEG, or PNG leaf image.",
                "The system shall reject unsupported files with a clear error message.",
                "The system shall preprocess the uploaded image before model prediction.",
                "The system shall predict the disease class and confidence score.",
                "The system shall show symptoms, severity, model name, processing method, and dataset name.",
                "The system shall store each prediction in a database.",
                "The dashboard shall display prediction history and basic statistics.",
            ]
        ],
    )
    flow += section(
        "2.4 Non-Functional Requirements",
        [
            [
                "Usability: The interface must be simple enough for non-technical users.",
                "Reliability: The system must handle missing files, unsupported formats, and missing model files gracefully.",
                "Performance: Preprocessing and prediction should complete quickly for standard leaf images.",
                "Maintainability: Disease classes, symptoms, and treatments should be stored in configuration mappings.",
                "Scalability: The design should allow future deployment, model replacement, and additional disease classes.",
                "Security: Uploaded filenames should be sanitized before saving to the server.",
            ]
        ],
    )
    req_data = [
        [p("Requirement Area", "table_head"), p("Description", "table_head")],
        [p("Frontend", "table_cell"), p("HTML templates, CSS styling, upload form, prediction result panel, and dashboard screens.", "table_cell")],
        [p("Backend", "table_cell"), p("Flask routes for index, dashboard, uploads, and prediction API.", "table_cell")],
        [p("Image Processing", "table_cell"), p("OpenCV resizing, denoising, HSV masking, morphology, and RGB conversion.", "table_cell")],
        [p("Machine Learning", "table_cell"), p("TensorFlow/Keras EfficientNetB0 model for multiclass disease classification.", "table_cell")],
        [p("Database", "table_cell"), p("SQLite table for prediction logs containing image, disease, confidence, advice, and timestamp.", "table_cell")],
        [p("Dataset", "table_cell"), p("PlantVillage-style disease classes represented through the application class list.", "table_cell")],
    ]
    flow.append(table(req_data, [1.7 * inch, 4.6 * inch]))
    flow += section(
        "2.5 Software and Hardware Requirements",
        [
            "The software stack includes Python, Flask, OpenCV, NumPy, TensorFlow/Keras, SQLite, HTML, CSS, and JavaScript. The application can run on a standard development machine with sufficient memory to load the model and process images.",
            "Recommended hardware includes a modern multicore processor, 8 GB RAM, and optional GPU support for model training. For inference, CPU execution is acceptable for academic demonstration because EfficientNetB0 offers a practical balance between accuracy and model size.",
        ],
    )

    flow += chapter("Chapter 3: SYSTEM DESIGN & ARCHITECTURE")
    flow += section(
        "3.1 System Architecture",
        [
            "LeafGuard is organized into clear modules. The browser interface sends the uploaded image to the Flask backend. The backend validates and saves the file, passes it to the preprocessing pipeline, sends the processed image to the model service, maps the predicted class to symptoms and treatments, stores the prediction record, and returns a structured result to the frontend.",
            "This separation of concerns keeps the project maintainable. The preprocessing module does not know about Flask routes, the model service does not know about the database, and the database logger does not know about HTML templates. Each part performs a focused responsibility.",
        ],
    )
    flow += section(
        "3.2 Data Flow",
        [
            [
                "Step 1: User opens the web application and selects a leaf image.",
                "Step 2: The browser submits the image to the `/predict` route.",
                "Step 3: Flask validates the file extension and saves the upload.",
                "Step 4: OpenCV preprocessing resizes, denoises, masks, and converts the image.",
                "Step 5: EfficientNetB0 predicts the most probable disease class.",
                "Step 6: The application maps the class to symptoms, severity, and treatment advice.",
                "Step 7: SQLite stores the prediction record.",
                "Step 8: The frontend displays a user-friendly result.",
            ]
        ],
    )
    module_data = [
        [p("Module", "table_head"), p("Responsibility", "table_head"), p("Main File", "table_head")],
        [p("Flask App", "table_cell"), p("Routes, upload validation, prediction endpoint, response formatting.", "table_cell"), p("src/app.py", "table_cell")],
        [p("Preprocessing", "table_cell"), p("Image resizing, denoising, HSV mask generation, morphology, RGB conversion.", "table_cell"), p("src/preprocessing/pipeline.py", "table_cell")],
        [p("Inference", "table_cell"), p("Model loading, normalization, batch creation, probability interpretation.", "table_cell"), p("src/inference/model_service.py", "table_cell")],
        [p("Database", "table_cell"), p("Prediction storage and dashboard statistics.", "table_cell"), p("src/db/logger.py", "table_cell")],
        [p("Configuration", "table_cell"), p("Class names, symptom mapping, and treatment mapping.", "table_cell"), p("src/config.py", "table_cell")],
        [p("Interface", "table_cell"), p("Upload page, dashboard page, and styling.", "table_cell"), p("templates/, static/", "table_cell")],
    ]
    flow.append(table(module_data, [1.25 * inch, 3.35 * inch, 1.7 * inch]))
    flow += section(
        "3.3 Image Preprocessing Design",
        [
            "The preprocessing pipeline prepares uploaded leaf images for model inference. Every image is resized to 224 x 224 pixels because EfficientNetB0 commonly expects fixed-size input. The current training setup uses normalized color images so that training and prediction remain consistent.",
            "The pipeline converts the image into HSV color space and applies a green-range mask to isolate the leaf region. Morphological opening and closing help remove small noise and fill gaps in the mask. A Gaussian blur smooths the mask before bitwise masking is applied. Finally, the image is converted from BGR to RGB for compatibility with common deep learning workflows.",
        ],
    )
    flow += section(
        "3.4 Database Design",
        [
            "The SQLite database stores prediction logs in a single table named `prediction_logs`. Each row contains the uploaded image name, predicted disease name, confidence score, treatment advice, and timestamp. This structure is sufficient for the current academic version and can be extended later with user accounts, location, crop season, or field identifiers.",
        ],
    )
    db_data = [
        [p("Field", "table_head"), p("Type", "table_head"), p("Purpose", "table_head")],
        [p("id", "table_cell"), p("INTEGER PRIMARY KEY", "table_cell"), p("Unique identifier for every prediction.", "table_cell")],
        [p("image_name", "table_cell"), p("TEXT", "table_cell"), p("Stores uploaded image filename.", "table_cell")],
        [p("disease_name", "table_cell"), p("TEXT", "table_cell"), p("Stores predicted class label.", "table_cell")],
        [p("confidence", "table_cell"), p("REAL", "table_cell"), p("Stores confidence percentage.", "table_cell")],
        [p("treatment_advice", "table_cell"), p("TEXT", "table_cell"), p("Stores recommended treatment message.", "table_cell")],
        [p("created_at", "table_cell"), p("TIMESTAMP", "table_cell"), p("Records prediction time automatically.", "table_cell")],
    ]
    flow.append(table(db_data, [1.25 * inch, 1.6 * inch, 3.4 * inch]))
    flow += section(
        "3.5 User Interface Design",
        [
            "The interface is designed around a direct workflow: upload, analyze, view result, and inspect history. The upload page presents the core prediction experience, while the dashboard supports review of past predictions. CSS styling gives the project a coherent LeafGuard identity with plant-focused colors and clear result cards.",
            "The user interface avoids unnecessary technical complexity. Instead of exposing raw model probabilities for every class, the application shows the most important information: plant name, disease name, confidence, severity, symptoms, treatment advice, model, processing method, and dataset.",
        ],
    )

    flow += chapter("Chapter 4: IMPLEMENTATION & RESULTS")
    flow += section(
        "4.1 Backend Implementation",
        [
            "The backend is implemented in Flask. The application initializes upload paths, model paths, preprocessing service, prediction logger, and model service. If the trained model file exists, it is loaded through the PlantDiseaseModelService. If the model file is missing, the prediction endpoint returns a clear server-side error explaining the expected model path.",
            "The `/predict` route is the central backend route. It obtains the uploaded file, validates it, saves it securely, preprocesses the image, runs inference, logs the result, and returns a JSON object. This route demonstrates a complete request-response cycle for machine-learning-enabled web software.",
        ],
    )
    flow += section(
        "4.2 Preprocessing Implementation",
        [
            "The `LeafPreprocessor` class contains a configurable preprocessing pipeline. The use of a dataclass for preprocessing parameters makes the code readable and adjustable. Target image size, denoising strength, template window size, search window size, blur kernel, and morphology kernel can be modified without rewriting the processing logic.",
            "The segmentation logic uses HSV thresholds because color-based masking is often easier in HSV than in raw BGR. The selected green range captures leaf regions while excluding part of the background. This step helps the classifier focus more on leaf tissue and visible disease patterns.",
        ],
    )
    flow += section(
        "4.3 Model Service Implementation",
        [
            "The model service loads the trained Keras model and stores the class names and treatment map. During prediction, the preprocessed RGB image is converted to float values in the range 0 to 1 and expanded into a batch dimension. The model output is interpreted using `argmax`, and the highest-probability class becomes the prediction.",
            "The service returns a structured `PredictionResult` containing the disease name, confidence percentage, and treatment advice. This makes the calling Flask route cleaner because prediction details are encapsulated in one object.",
        ],
    )
    flow += section(
        "4.4 Frontend Implementation",
        [
            "The frontend includes an upload-focused index page and a dashboard page. The index page allows users to select a leaf image and view the prediction result without needing to understand the backend. The dashboard page presents stored prediction logs and basic statistics from the SQLite database.",
            "The CSS file provides visual polish through structured layout, result panels, buttons, and plant-themed styling. The interface is important because a disease detection system must be understandable to users who may not have a technical background.",
        ],
    )
    sample_paths = [
        ROOT / "static" / "samples" / "apple_scab.jpg",
        ROOT / "static" / "samples" / "corn_healthy.jpg",
        ROOT / "static" / "samples" / "potato_blight.jpg",
        ROOT / "static" / "samples" / "tomato_blight.jpg",
    ]
    imgs = []
    for path in sample_paths:
        if path.exists():
            imgs.append(Image(str(path), width=1.25 * inch, height=1.0 * inch))
    if imgs:
        flow.append(table([[*imgs]], [1.5 * inch] * len(imgs)))
        flow.append(p("Figure 4.1: Sample leaf images used for interface demonstration.", "caption"))
    flow += section(
        "4.5 Disease Class Coverage",
        [
            "The configuration contains 38 disease and healthy classes. A wide class list makes the system more useful because it is not limited to a single crop. The project includes healthy categories as well as disease categories, allowing the interface to return positive care messages when no disease is detected.",
        ],
    )
    classes = [
        "Apple scab", "Apple black rot", "Cedar apple rust", "Apple healthy",
        "Blueberry healthy", "Cherry healthy", "Cherry powdery mildew",
        "Corn gray leaf spot", "Corn common rust", "Corn healthy", "Corn northern leaf blight",
        "Grape black rot", "Grape esca", "Grape healthy", "Grape leaf blight",
        "Orange citrus greening", "Peach bacterial spot", "Peach healthy",
        "Bell pepper bacterial spot", "Bell pepper healthy", "Potato early blight",
        "Potato healthy", "Potato late blight", "Raspberry healthy", "Soybean healthy",
        "Squash powdery mildew", "Strawberry healthy", "Strawberry leaf scorch",
        "Tomato bacterial spot", "Tomato early blight", "Tomato healthy",
        "Tomato late blight", "Tomato leaf mold", "Tomato septoria leaf spot",
        "Tomato spider mites", "Tomato target spot", "Tomato mosaic virus",
        "Tomato yellow leaf curl virus",
    ]
    class_rows = [[p("S. No.", "table_head"), p("Disease / Health Class", "table_head")]]
    for i, cls in enumerate(classes, 1):
        class_rows.append([p(str(i), "table_cell"), p(cls, "table_cell")])
    flow.append(table(class_rows, [0.7 * inch, 5.5 * inch]))
    flow += section(
        "4.6 Result Format",
        [
            "A successful prediction returns a result object containing disease name, raw class name, plant name, confidence, severity, symptoms, treatment, model name, processing method, dataset name, and uploaded image name. This result format is useful because it is both human-readable and machine-readable.",
            "The system derives a plant name and a simplified disease name by splitting PlantVillage-style class labels around the triple underscore marker. This makes labels more readable on the frontend while still preserving the raw class name for debugging or record keeping.",
        ],
    )

    flow += chapter("Chapter 5: TESTING & EVALUATION")
    flow += section(
        "5.1 Testing Strategy",
        [
            "Testing was planned around the main risk points of the system: file upload validation, preprocessing correctness, model availability, prediction response structure, database logging, and dashboard display. Each risk point was evaluated from the perspective of both developer correctness and user experience.",
            "Because the system depends on a trained model file, backend error handling is important. The application explicitly checks for the model path and returns a meaningful message if the model is not present. This prevents silent failure and helps during setup.",
        ],
    )
    test_data = [
        [p("Test Area", "table_head"), p("Test Case", "table_head"), p("Expected Result", "table_head")],
        [p("Upload", "table_cell"), p("Submit without selecting a file.", "table_cell"), p("Application returns an error asking for a leaf image.", "table_cell")],
        [p("Upload", "table_cell"), p("Submit unsupported file extension.", "table_cell"), p("Application rejects the file.", "table_cell")],
        [p("Preprocessing", "table_cell"), p("Process valid JPG/PNG image.", "table_cell"), p("Image is resized, denoised, segmented, and converted to RGB.", "table_cell")],
        [p("Model", "table_cell"), p("Run prediction with valid model.", "table_cell"), p("System returns class and confidence.", "table_cell")],
        [p("Database", "table_cell"), p("Complete a prediction.", "table_cell"), p("Prediction row is inserted into SQLite table.", "table_cell")],
        [p("Dashboard", "table_cell"), p("Open dashboard after predictions.", "table_cell"), p("History and statistics are displayed.", "table_cell")],
    ]
    flow.append(table(test_data, [1.15 * inch, 2.35 * inch, 2.7 * inch]))
    flow += section(
        "5.2 Unit Testing Considerations",
        [
            "The preprocessing module can be tested by passing a valid NumPy image array and confirming that the output shape is 224 x 224 x 3. It can also be tested with invalid file paths to confirm that the correct exception is raised.",
            "The database logger can be tested by creating a temporary SQLite database, inserting sample predictions, and checking whether `get_all_predictions` and `get_stats` return the expected values. These tests are useful because they do not require a trained model.",
        ],
    )
    flow += section(
        "5.3 Integration Testing",
        [
            "Integration testing checks whether the upload route, preprocessing pipeline, model service, and database logger work together. The most important integration test is a complete prediction flow using a valid leaf image. The expected result is a JSON response with disease details and a corresponding record in the database.",
            "Another integration test is the dashboard route. After predictions are made, the dashboard should fetch all stored rows and show summary statistics. This confirms that backend data is visible through the frontend layer.",
        ],
    )
    flow += section(
        "5.4 Evaluation Observations",
        [
            "The system architecture is suitable for academic demonstration because the modules are readable and the workflow is complete. The preprocessing approach is lightweight and deterministic. The prediction service is simple, which makes it easy to replace the model file in future iterations.",
            "Accuracy depends on the trained EfficientNetB0 model, the quality of training data, and how closely uploaded real-world images match the dataset distribution. Field images may include complex backgrounds, lighting variation, occlusion, multiple leaves, soil, or shadows. These factors can reduce prediction reliability, so future versions should include stronger augmentation and real-field validation.",
        ],
    )
    flow += section(
        "5.5 Limitations",
        [
            [
                "The system requires a trained `.keras` model file before prediction can run.",
                "The HSV green mask may not perfectly segment leaves under all lighting conditions.",
                "The application does not yet support user authentication or farm-level record grouping.",
                "Treatment advice is rule-based and should be reviewed by agricultural experts before production use.",
                "The system is web-based and is not yet packaged as an offline mobile app.",
            ]
        ],
    )

    flow += chapter("Chapter 6: CONCLUSION")
    flow += section(
        "6.1 Summary of Achievements",
        [
            "LeafGuard successfully demonstrates an end-to-end plant disease detection workflow. The project accepts uploaded leaf images, preprocesses them, predicts disease classes using an EfficientNetB0 model, maps predictions to symptoms and treatment advice, stores prediction history in SQLite, and displays results through a Flask web interface.",
            "The project is meaningful because it connects artificial intelligence with agriculture, a domain where early detection and timely action can protect yield and reduce losses. It also shows how academic software projects can become practical when they are designed as complete systems rather than isolated code fragments.",
        ],
    )
    flow += section(
        "6.2 Academic Learning",
        [
            "The development of LeafGuard provided practical experience in Python programming, computer vision, machine learning integration, backend routing, database design, template rendering, and frontend styling. It also improved understanding of software modularity, configuration-driven design, and user-centered result presentation.",
            "The project bridges classroom concepts with real implementation. Concepts such as convolutional neural networks, image normalization, HTTP requests, database persistence, and error handling become clearer when they are implemented together in one working application.",
        ],
    )
    flow += section(
        "6.3 Final Conclusion",
        [
            "Overall, LeafGuard is a strong academic demonstration of machine-learning-assisted agricultural diagnosis. It is not a replacement for expert inspection, but it provides a useful first-level screening tool that can be expanded into a more advanced advisory platform. With further model improvement, field testing, mobile deployment, and expert-verified treatment recommendations, the system can become a practical tool for farmers, students, and agricultural support teams.",
        ],
    )

    flow += chapter("Chapter 7: FUTURE SCOPE")
    flow += section(
        "7.1 Improved Model Accuracy",
        [
            "Future versions can train the model with larger and more diverse datasets that include real field images, different lighting conditions, various camera qualities, and multiple disease stages. Stronger data augmentation can improve robustness.",
            "The system can also compare EfficientNetB0 with ResNet, DenseNet, Vision Transformers, or ensemble models. Evaluation metrics such as precision, recall, F1-score, confusion matrix, and class-wise accuracy should be included in future experiments.",
        ],
    )
    flow += section(
        "7.2 Mobile Application",
        [
            "A mobile app would make LeafGuard more accessible to farmers and field workers. The mobile version could support camera capture, offline image storage, GPS-based tagging, local language instructions, and simplified treatment workflows.",
        ],
    )
    flow += section(
        "7.3 Cloud Deployment",
        [
            "Deploying the application on cloud infrastructure would allow remote access, centralized model updates, and scalable usage. Cloud deployment can include Docker containers, API gateways, managed databases, monitoring, and automated backups.",
        ],
    )
    flow += section(
        "7.4 Expert Recommendation System",
        [
            "The current treatment map provides simple guidance. Future versions can include an expert-verified recommendation engine that considers crop type, disease stage, season, local climate, organic or chemical treatment preference, and severity level.",
        ],
    )
    flow += section(
        "7.5 Multilingual Support",
        [
            "Since the target users may include farmers from different regions, multilingual support would make the application more inclusive. Disease names, symptoms, and treatment advice can be translated into Hindi, Punjabi, and other regional languages.",
        ],
    )
    flow += section(
        "7.6 Analytics Dashboard",
        [
            "A more advanced dashboard can show disease trends, prediction counts by crop, high-risk disease categories, confidence distributions, and seasonal changes. If location data is added, the system could display heatmaps of common plant diseases.",
        ],
    )
    flow += section(
        "7.7 IoT and Field Monitoring",
        [
            "LeafGuard can be integrated with IoT sensors that monitor humidity, temperature, rainfall, and soil moisture. Combining image-based disease detection with environmental data can improve disease risk prediction and preventive recommendations.",
        ],
    )
    flow += section(
        "7.8 Production Security",
        [
            "Future production versions should include user authentication, file size limits, virus scanning, secure upload storage, role-based dashboards, HTTPS deployment, and database backup policies. These improvements are important if the system is made public.",
        ],
    )

    flow += chapter("REFERENCES")
    refs = [
        "TensorFlow and Keras documentation for model loading and inference workflows.",
        "OpenCV documentation for resizing, denoising, HSV conversion, masking, morphology, and image processing.",
        "Flask documentation for routing, request handling, templates, and static file serving.",
        "SQLite documentation for lightweight relational database storage.",
        "PlantVillage dataset references for plant disease image classification research.",
        "EfficientNetB0 research and transfer learning references for efficient convolutional neural networks.",
        "Python documentation for pathlib, dataclasses, JSON handling, and application structure.",
    ]
    flow.extend(bullets(refs))
    return flow


def appendices():
    flow = [PageBreak(), p("APPENDIX A: SOURCE CODE", "h1"), Rule(), Spacer(1, 8)]
    flow += section(
        "A.1 Appendix Overview",
        [
            "This appendix includes the major source files used in the LeafGuard project. The code is included to document the implementation details behind preprocessing, model inference, Flask routing, configuration mapping, database logging, and interface design.",
        ],
    )
    files = [
        ("A.2 Flask Application - src/app.py", ROOT / "src" / "app.py"),
        ("A.3 Preprocessing Pipeline - src/preprocessing/pipeline.py", ROOT / "src" / "preprocessing" / "pipeline.py"),
        ("A.4 Model Service - src/inference/model_service.py", ROOT / "src" / "inference" / "model_service.py"),
        ("A.5 Database Logger - src/db/logger.py", ROOT / "src" / "db" / "logger.py"),
        ("A.6 Configuration - src/config.py", ROOT / "src" / "config.py"),
        ("A.7 Upload Page Template - templates/index.html", ROOT / "templates" / "index.html"),
        ("A.8 Dashboard Template - templates/dashboard.html", ROOT / "templates" / "dashboard.html"),
        ("A.9 Stylesheet - static/style.css", ROOT / "static" / "style.css"),
        ("A.10 Training Script - train_efficientnet.py", ROOT / "train_efficientnet.py"),
    ]
    for title, path in files:
        if path.exists():
            flow += code_pages(title, path)
    return flow


def main():
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        rightMargin=0.82 * inch,
        leftMargin=0.82 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="LeafGuard Project Report",
        author="Abhay Chopra",
    )
    story = []
    story.extend(cover_pages())
    story.extend(toc_pages())
    story.extend(body_pages())
    story.extend(appendices())
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(OUT)


if __name__ == "__main__":
    main()
