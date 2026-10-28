# ============================================================
# AJTI LEARNING APP - VERSION 7.8
# Single-file, offline-first Kivy prototype for Android
#
# Run with a Python/Kivy environment (for example, Pydroid 3
# with its compatible Kivy support). Save as main.py.
#
# IMPORTANT:
# - Data is stored locally in Kivy's app user-data directory.
# - This is a learning prototype, not a production-secure school
#   system. Do not use real sensitive passwords or private data.
# - Online accounts, teacher synchronization and school-wide
#   registration require a trusted backend and HTTPS.
# ============================================================

import os
import json
import hashlib
import secrets
import re
from datetime import datetime
import math

from kivy.clock import Clock
from kivy.graphics import Rectangle, Ellipse, Rotate, PushMatrix, PopMatrix
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ListProperty, NumericProperty
from kivy.app import App
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


# ---------------- PROVISIONAL AJTI BRAND PALETTE ----------------
# Navy/blue/gold/green are temporary design choices, NOT verified official school colours.
# Replace them when the user supplies the real AJTI badge or official branding.
# ---------------- COLORS ----------------

NAVY = get_color_from_hex("#102A43")
BLUE = get_color_from_hex("#1769FF")
LIGHT_BLUE = get_color_from_hex("#E8F1FF")
WHITE = get_color_from_hex("#FFFFFF")
GOLD = get_color_from_hex("#FFD166")
DARK = get_color_from_hex("#172B4D")
GREEN = get_color_from_hex("#07865B")
RED = get_color_from_hex("#D92D20")
GREY = get_color_from_hex("#52647A")
PALE = get_color_from_hex("#F5F8FC")

Window.clearcolor = get_color_from_hex("#F3F7FF")
APP_NAME = "AJTI LEARNING APP"
APP_VERSION = "7.8"


# ---------------- DEPARTMENTS ----------------

COURSES = {
    "Electrical Engineering Technology": [
        "Basic Electricity", "Electrical Installation", "Electrical Measurement",
        "Electrical Machines", "Power Generation and Distribution",
        "Electrical Wiring and Regulations"
    ],
    "Building and Construction Technology": [
        "Technical Drawing", "Building Construction", "Building Materials",
        "Construction Technology", "Estimating and Costing", "Site Safety"
    ],
    "Fashion and Design": [
        "Fashion Illustration", "Textile Studies", "Pattern Drafting",
        "Garment Construction", "Clothing Design", "Fashion Entrepreneurship"
    ],
    "Catering and Hospitality": [
        "Food Preparation", "Food and Nutrition", "Food Hygiene and Safety",
        "Hospitality Management", "Food and Beverage Service", "Menu Planning"
    ],
    "Electronics Engineering": [
        "Electronic Components", "Analogue Electronics", "Digital Electronics",
        "Electronic Circuit Design", "Instrumentation and Measurement", "Electronic Troubleshooting"
    ],
    "Renewable Energy": [
        "Solar Energy Systems", "Energy Storage Systems", "Renewable Energy Installation",
        "Energy Efficiency", "Wind Energy", "Renewable Energy Maintenance"
    ]
}

COMMON_SUBJECTS = [
    "English Language", "Mathematics", "Integrated Science", "ICT",
    "Social Studies", "Entrepreneurship"
]


# ---------------- STUDY YEARS ----------------
STUDY_YEARS = ("Year 1", "Year 2", "Year 3")


def subjects_for_year(course, year):
    """Return a year-specific department list plus the shared common subjects.

    Department subject placement is a provisional learning-app sequence and must
    be checked against AJTI's current scheme of learning before official use.
    """
    subjects = COURSES.get(course, [])
    try:
        year_index = STUDY_YEARS.index(year)
    except ValueError:
        year_index = 0
    base, extra = divmod(len(subjects), len(STUDY_YEARS))
    start = year_index * base + min(year_index, extra)
    count = base + (1 if year_index < extra else 0)
    year_subjects = subjects[start:start + count]
    return year_subjects + COMMON_SUBJECTS


# ---------------- STARTER LESSONS ----------------
# Teachers can edit or replace these in the app.

STARTER_LESSONS = {
    "Basic Electricity": {
        "title": "Introduction to Basic Electricity",
        "notes": (
            "Electricity is associated with electric charge and its movement. "
            "Current (I) is measured in amperes (A), voltage (V) in volts (V), "
            "and resistance (R) in ohms (Ω).\n\n"
            "Ohm's law: V = I × R.\n"
            "Example: if a 12 V supply is connected across a 6 Ω resistor, "
            "the current is I = V/R = 12/6 = 2 A.\n\n"
            "SAFETY: Never experiment with mains electricity. Practical work "
            "should be supervised by a qualified teacher using suitable "
            "protective equipment."
        )
    },
    "Electrical Measurement": {
        "title": "Electrical Measuring Instruments",
        "notes": (
            "An ammeter measures current and is connected in series in a "
            "properly designed circuit. A voltmeter measures potential "
            "difference and is connected in parallel across the component.\n\n"
            "A multimeter may measure voltage, current, resistance and "
            "continuity. Select the correct mode and input socket before use. "
            "Never measure resistance on an energized circuit."
        )
    },
    "Electronic Components": {
        "title": "Introduction to Electronic Components",
        "notes": (
            "Resistors limit current and divide voltage. Capacitors store "
            "energy in an electric field. Diodes mainly allow current in one "
            "direction. LEDs emit light when correctly connected and supplied "
            "within their ratings. Transistors can act as switches or "
            "amplifiers.\n\n"
            "Check component markings and datasheets before building circuits."
        )
    },
    "Solar Energy Systems": {
        "title": "Introduction to Solar Energy",
        "notes": (
            "A photovoltaic panel converts sunlight into electrical energy. "
            "A basic standalone system may include a PV panel, charge "
            "controller, battery, wiring and a suitable load or inverter.\n\n"
            "Panel voltage/current, controller rating, battery chemistry and "
            "cable sizes must be compatible. Installation should follow local "
            "electrical regulations and be checked by a qualified person."
        )
    },
    "Technical Drawing": {
        "title": "Technical Drawing Basics",
        "notes": (
            "Technical drawing communicates the shape, size and construction "
            "of an object. Common tools include a ruler, set squares, compass, "
            "protractor, pencils and eraser.\n\n"
            "Use clear line types, suitable scale, dimensions and a title block. "
            "Keep construction lines light and final object lines distinct."
        )
    },
    "Food Hygiene and Safety": {
        "title": "Food Hygiene and Safety",
        "notes": (
            "Food hygiene helps prevent contamination and foodborne illness. "
            "Wash hands, clean equipment, separate raw and ready-to-eat food, "
            "cook food thoroughly and keep food at safe temperatures.\n\n"
            "Follow your school's practical-work instructions and local food "
            "safety requirements."
        )
    }
}



# ---------------- ROUNDED / CURVED UI COMPONENTS ----------------

class RoundedButton(Button):
    """Custom button with reliable rounded backgrounds and clear pressed states."""
    bg_color = ListProperty([0.10, 0.42, 0.72, 1])
    corner_radius = NumericProperty(999)

    def __init__(self, **kwargs):
        bg = kwargs.pop("bg_color", None)
        if bg is None:
            bg = kwargs.pop("background_color", [0.10, 0.42, 0.72, 1])
        text_color = kwargs.pop("color", [1, 1, 1, 1])
        self.bg_color = list(bg)
        kwargs["color"] = text_color
        kwargs["background_normal"] = ""
        kwargs["background_down"] = ""
        kwargs["background_color"] = [0, 0, 0, 0]
        kwargs.setdefault("font_size", "14sp")
        kwargs.setdefault("bold", True)
        super().__init__(**kwargs)
        with self.canvas.before:
            self._rounded_bg = Color(rgba=self.bg_color)
            self._rounded_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[min(self.height / 2, self.corner_radius)]
            )
        self.bind(pos=self._update_rounded, size=self._update_rounded,
                  bg_color=self._update_rounded, state=self._update_state,
                  disabled=self._update_disabled)

    def _update_rounded(self, *_):
        self._rounded_rect.pos = self.pos
        self._rounded_rect.size = self.size
        self._rounded_rect.radius = [min(self.height / 2, self.corner_radius)]
        self._update_state()

    def _update_state(self, *_):
        if not hasattr(self, "_rounded_bg"):
            return
        factor = 0.82 if self.state == "down" else 1.0
        self._rounded_bg.rgba = [min(1, c * factor) for c in self.bg_color[:3]] + [self.bg_color[3]]

    def _update_disabled(self, *_):
        if hasattr(self, "_rounded_bg"):
            self.opacity = 0.55 if self.disabled else 1.0


# ---------------- AJTI CUSTOM UI DESIGN SYSTEM ----------------
AJTI_BG = (0.025, 0.055, 0.12, 1)
AJTI_SURFACE = (0.065, 0.11, 0.20, 1)
AJTI_SURFACE_ALT = (0.09, 0.15, 0.27, 1)
AJTI_PRIMARY = (0.10, 0.39, 1.0, 1)
AJTI_ACCENT = (0.10, 0.88, 0.58, 1)
AJTI_TEXT = (0.97, 0.98, 1.0, 1)
AJTI_MUTED = (0.72, 0.79, 0.90, 1)

class AJTICard(BoxLayout):
    """Reusable curved panel for AJTI's custom dashboard and content screens."""
    fill_color = ListProperty(list(AJTI_SURFACE))
    radius_size = NumericProperty(28)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._card_color = Color(rgba=self.fill_color)
            self._card_shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius_size])
        self.bind(pos=self._redraw_card, size=self._redraw_card, fill_color=self._redraw_card)

    def _redraw_card(self, *_):
        self._card_shape.pos = self.pos
        self._card_shape.size = self.size
        self._card_shape.radius = [self.radius_size]
        self._card_color.rgba = self.fill_color


# ---------------- SUBJECT GUIDES & STUDY MODES ----------------
SUBJECT_GUIDES = {
    'Basic Electricity': {'overview': 'Electricity and circuits', 'topics': ['Electric charge, current, voltage and resistance', "Ohm's law: V = I × R", 'Electrical power: P = V × I', 'Series and parallel circuits', 'Conductors, insulators, fuses and circuit breakers'], 'objectives': ['Define current, voltage, resistance and power', "Use Ohm's law to find an unknown value", 'Explain the difference between series and parallel circuits'], 'glossary': ['Current — rate of flow of electric charge, measured in amperes', 'Voltage — electrical potential difference, measured in volts', 'Resistance — opposition to current, measured in ohms', 'Power — rate of electrical energy transfer, measured in watts'], 'activity': 'Use only approved low-voltage learning kits under teacher supervision. Never experiment with household mains electricity.'},
    'Electrical Installation': {'overview': 'Planning safe electrical installations', 'topics': ['Installation tools and materials', 'Cable types and current ratings', 'Switches, socket outlets and lighting points', 'Protective earthing and bonding', 'Circuit protection and inspection'], 'objectives': ['Identify common installation accessories', 'Explain why cable sizing and protection must match the circuit', 'Read a simple installation diagram'], 'glossary': ['Earthing — a protective connection intended to reduce electric-shock risk', 'Fuse — a device that interrupts excessive current', 'Circuit breaker — a resettable protective switching device', 'Conduit — a protective route for cables'], 'activity': 'Practical wiring must be de-energized, checked, and supervised by a qualified instructor. Do not work on live circuits.'},
    'Electrical Machines': {'overview': 'Motors, generators and transformers', 'topics': ['Magnetic fields and electromagnetic induction', 'Basic motor and generator principles', 'Transformers and turns ratio', 'Nameplates, ratings and efficiency', 'Common faults and maintenance principles'], 'objectives': ['Distinguish motors from generators', 'Describe how electromagnetic induction works', 'Read basic information from a machine nameplate'], 'glossary': ['Motor — converts electrical energy to mechanical energy', 'Generator — converts mechanical energy to electrical energy', 'Transformer — transfers AC energy between circuits by electromagnetic induction', 'Efficiency — useful output power divided by input power'], 'activity': 'Do not open, wire or test energized machines. Rotating equipment and high-current supplies require instructor supervision.'},
    'Electrical Measurement': {'overview': 'Measuring electrical quantities', 'topics': ['Analogue and digital meters', 'Voltage, current, resistance and continuity', 'Correct meter ranges and terminals', 'Measurement error and significant figures', 'Safe inspection before measurement'], 'objectives': ['Choose a suitable instrument for a quantity', 'Explain series and parallel meter connections', 'Record results with units'], 'glossary': ['Ammeter — measures current and is connected in series in an appropriate circuit', 'Voltmeter — measures potential difference across a component', 'Continuity — whether an electrical path is complete', 'Accuracy — closeness of a reading to the true value'], 'activity': "Never measure resistance or continuity on an energized circuit. Follow the instrument manual and teacher's instructions."},
    'Power Generation and Distribution': {'overview': 'How electricity reaches consumers', 'topics': ['Thermal, hydro, solar and wind generation', 'Transmission and distribution networks', 'Step-up and step-down transformers', 'Substations, feeders and service lines', 'Losses, reliability and energy conservation'], 'objectives': ['Trace the path from generation to a consumer', 'Explain why high voltage is used for transmission', 'Compare renewable and non-renewable sources'], 'glossary': ['Generation — production of electrical energy', 'Transmission — bulk transfer over high-voltage networks', 'Distribution — delivery through local networks', 'Substation — facility for switching, protection and voltage transformation'], 'activity': 'Treat all power lines and utility equipment as dangerous. Study diagrams and simulations, not live infrastructure.'},
    'Electrical Wiring and Regulations': {'overview': 'Wiring practice and safety rules', 'topics': ['Wiring diagrams and symbols', 'Cable identification and protection', 'Isolation, inspection and testing principles', 'Overcurrent protection and earthing', 'Local codes, standards and documentation'], 'objectives': ['Interpret simple wiring symbols', 'Explain why inspections and tests are necessary', 'Recognize unsafe wiring conditions'], 'glossary': ['Isolation — separating equipment from all relevant energy sources', 'Overcurrent — current above the intended circuit value', 'Protective device — equipment that disconnects a fault or overload', 'Compliance — meeting applicable standards and regulations'], 'activity': 'Always follow current Ghanaian requirements, school rules and qualified supervision. Never bypass protective devices.'},
    'Technical Drawing': {'overview': 'Communicating designs accurately', 'topics': ['Drawing instruments and care', 'Line types, lettering and dimensioning', 'Scales, orthographic views and isometric views', 'Geometrical construction', 'Title blocks and drawing layout'], 'objectives': ['Use drawing tools accurately', 'Distinguish visible, hidden and centre lines', 'Produce neat, dimensioned drawings'], 'glossary': ['Scale — ratio between drawing size and actual size', 'Orthographic projection — views showing faces from different directions', 'Isometric drawing — a pictorial view using three principal axes', 'Dimension — a stated measurement on a drawing'], 'activity': 'Check units and dimensions before finalizing a drawing.'},
    'Building Construction': {'overview': 'Principles of building work', 'topics': ['Site preparation and setting out', 'Foundations and ground conditions', 'Walls, floors, roofs and finishes', 'Sequence of construction', 'Quality checks and site safety'], 'objectives': ['Name major building components', 'Explain why foundations depend on ground conditions', 'Describe a basic construction sequence'], 'glossary': ['Foundation — transfers building loads to the ground', 'Lintel — supports masonry above an opening', 'Damp-proof course — helps prevent rising moisture', 'Setting out — transferring design positions to a site'], 'activity': 'Follow site safety rules and use protective equipment during supervised practical work.'},
    'Building Materials': {'overview': 'Selecting materials for construction', 'topics': ['Cement, aggregates and concrete', 'Bricks, blocks, timber and steel', 'Material properties and durability', 'Storage and handling', 'Sustainability and waste reduction'], 'objectives': ['Identify common materials and their uses', 'Relate strength and durability to material selection', 'Explain correct storage practices'], 'glossary': ['Aggregate — granular material used in concrete or mortar', 'Mortar — mixture used to bond masonry units', 'Concrete — cementitious binder, water and aggregates', 'Durability — ability to resist deterioration over time'], 'activity': 'Use materials according to product instructions and teacher guidance.'},
    'Construction Technology': {'overview': 'Methods and processes in construction', 'topics': ['Building sequence and site organization', 'Masonry and concrete work', 'Roofing and finishes', 'Basic building services', 'Inspection, quality and safety'], 'objectives': ['Describe common construction processes', 'Explain the purpose of quality control', 'Identify hazards that require controls'], 'glossary': ['Masonry — construction using units such as blocks or bricks', 'Formwork — temporary mould supporting fresh concrete', 'Curing — maintaining conditions for concrete to develop strength', 'Specification — stated requirements for a construction item'], 'activity': 'Never enter restricted work areas or operate site machinery without authorization.'},
    'Estimating and Costing': {'overview': 'Planning quantities and costs', 'topics': ['Reading drawings and specifications', 'Taking dimensions and calculating areas', 'Material quantities and waste allowance', 'Labour, plant and overhead costs', 'Bills of quantities and checking estimates'], 'objectives': ['Calculate simple lengths, areas and volumes', 'Organize a basic material estimate', 'Explain why estimates include labour and overheads'], 'glossary': ['Estimate — forecast of expected project cost', 'Quantity take-off — measuring work from drawings', 'Unit rate — cost per unit of work', 'Contingency — allowance for uncertainty'], 'activity': 'State assumptions clearly and check units and arithmetic.'},
    'Garment Construction': {'overview': 'Making garments step by step', 'topics': ['Tools, equipment and fabric preparation', 'Taking body measurements respectfully', 'Seams, hems and fastenings', 'Cutting layouts and sewing sequence', 'Fitting, pressing and finishing'], 'objectives': ['Identify garment-making tools', 'Explain common seam and hem types', 'Plan a safe construction sequence'], 'glossary': ['Seam allowance — extra fabric beyond the stitching line', 'Hem — finished edge of a garment', 'Grainline — direction of fabric threads', 'Fastening — closure such as a button or zip'], 'activity': 'Keep fingers away from moving machine parts and follow workshop safety rules.'},
    'Pattern Drafting': {'overview': 'Turning measurements into patterns', 'topics': ['Body measurements and ease', 'Pattern symbols and grainlines', 'Basic blocks and adaptation', 'Seam allowances and notches', 'Pattern checking and layout'], 'objectives': ['Read basic pattern markings', 'Explain ease and seam allowance', 'Check a pattern before cutting fabric'], 'glossary': ['Block — basic pattern used as a starting point', 'Ease — extra room added for movement or fit', 'Notch — small mark used to align pattern pieces', 'Dart — shaped fold or seam that creates contour'], 'activity': 'Confirm measurements and obtain permission before cutting shared materials.'},
    'Fashion Illustration': {'overview': 'Drawing fashion ideas', 'topics': ['Proportion and figure poses', 'Garment silhouettes', 'Fabric texture and folds', 'Colour and design details', 'Presentation and annotation'], 'objectives': ['Communicate a clothing idea visually', 'Show garment details clearly', 'Use labels and colour consistently'], 'glossary': ['Silhouette — overall outline of a garment', 'Texture — visual or tactile surface quality', 'Mood board — collection of visual references', 'Annotation — note explaining a design feature'], 'activity': 'Credit reference images and develop original design ideas.'},
    'Textile Studies': {'overview': 'Understanding fibres and fabrics', 'topics': ['Natural and manufactured fibres', 'Yarns, weaving and knitting', 'Fabric properties and uses', 'Dyeing, printing and finishing', 'Care labels and sustainability'], 'objectives': ['Compare common fibre types', 'Relate fabric properties to garment use', 'Interpret basic care symbols'], 'glossary': ['Fibre — fine material used to make yarn', 'Weaving — interlacing lengthwise and crosswise yarns', 'Knitting — forming fabric with interlocking loops', 'Finishing — treatment that changes fabric appearance or performance'], 'activity': 'Follow chemical and hot-equipment safety instructions during textile practicals.'},
    'Clothing Design': {'overview': 'Designing useful and attractive clothing', 'topics': ['Design brief and target user', 'Line, shape, colour and balance', 'Function, comfort and fit', 'Sketches, samples and feedback', 'Ethical sourcing and final presentation'], 'objectives': ['Develop a design from a brief', 'Explain how design choices affect function', 'Present and improve a design using feedback'], 'glossary': ['Design brief — statement of needs and constraints', 'Balance — visual distribution of design elements', 'Prototype — early version used for evaluation', 'Function — what an item is intended to do'], 'activity': 'Consider comfort, accessibility, cultural context and material waste.'},
    'Food Preparation': {'overview': 'Preparing food safely and consistently', 'topics': ['Kitchen tools and preparation methods', 'Ingredient measurement', 'Heat transfer and cooking methods', 'Recipe sequence and timing', 'Presentation and evaluation'], 'objectives': ['Choose suitable cooking methods', 'Follow a recipe in sequence', 'Explain how preparation affects quality'], 'glossary': ['Boiling — cooking in liquid at its boiling point', 'Steaming — cooking using water vapour', 'Sautéing — cooking quickly with a small amount of fat', 'Mise en place — preparing ingredients and tools before cooking'], 'activity': 'Use knives, hot surfaces and appliances only with proper supervision.'},
    'Food and Nutrition': {'overview': 'Food, nutrients and wellbeing', 'topics': ['Carbohydrates, proteins and fats', 'Vitamins, minerals and water', 'Balanced meals and dietary variety', 'Food labels and portion planning', 'Nutrition needs across life stages'], 'objectives': ['Name major nutrient groups', 'Explain the idea of a balanced diet', 'Identify sources of key nutrients'], 'glossary': ['Carbohydrate — major energy-providing nutrient', 'Protein — nutrient needed for growth and tissue repair', 'Vitamin — organic nutrient needed in small amounts', 'Fibre — part of plant foods supporting normal digestion'], 'activity': 'Nutrition needs differ between people; avoid treating one meal plan as suitable for everyone.'},
    'Food Hygiene and Safety': {'overview': 'Preventing contamination', 'topics': ['Handwashing and personal hygiene', 'Cleaning and sanitizing equipment', 'Separating raw and ready-to-eat food', 'Safe storage and temperature control', 'Allergens and waste management'], 'objectives': ['Identify contamination risks', 'Explain cross-contamination prevention', 'Apply a clean-as-you-go routine'], 'glossary': ['Contamination — unwanted harmful material in food', 'Cross-contamination — transfer of contaminants between items', 'Sanitizing — reducing microorganisms to an appropriate level', 'Allergen — substance that can trigger an allergic reaction'], 'activity': "Follow official food-safety guidance and your instructor's procedures."},
    'Hospitality Management': {'overview': 'Delivering quality hospitality services', 'topics': ['Guest needs and customer care', 'Front office and housekeeping roles', 'Reservations and service records', 'Team communication and complaints', 'Professional conduct and sustainability'], 'objectives': ['Describe key hospitality departments', 'Respond politely to guest needs', 'Explain why accurate records matter'], 'glossary': ['Hospitality — service that welcomes and supports guests', 'Reservation — advance arrangement for a service', 'Service recovery — steps taken to resolve a service problem', 'Confidentiality — protecting private guest information'], 'activity': 'Respect guests, privacy, and workplace policies.'},
    'Food and Beverage Service': {'overview': 'Serving food and beverages professionally', 'topics': ['Table setting and service equipment', 'Menu knowledge and order taking', 'Sequence of service', 'Customer communication', 'Hygiene, allergens and payment accuracy'], 'objectives': ['Identify common service equipment', 'Explain a basic service sequence', 'Communicate dietary requests accurately'], 'glossary': ['Cover — place setting for one guest', 'À la carte — menu where items are priced individually', 'Order docket — record of items ordered', 'Service sequence — planned order of service steps'], 'activity': 'Never guess about allergens; check with the kitchen or responsible supervisor.'},
    'Solar Energy Systems': {'overview': 'Design basics for photovoltaic systems', 'topics': ['Solar radiation and photovoltaic cells', 'Panel ratings and energy yield', 'Charge controllers and batteries', 'Inverters and loads', 'System maintenance and safety'], 'objectives': ['Explain the main parts of a solar system', 'Distinguish power in watts from energy in watt-hours', 'Identify factors that affect solar output'], 'glossary': ['PV module — converts light into electrical energy', 'Charge controller — regulates charging between panel and battery', 'Inverter — converts DC to AC', 'Watt-hour — unit of energy'], 'activity': 'PV wiring and batteries can deliver dangerous current. Installation must be designed and checked by a qualified person.'},
    'Wind Energy': {'overview': 'Converting wind into useful energy', 'topics': ['Wind as a renewable resource', 'Turbine blades, rotor and generator', 'Wind speed and site selection', 'Grid-connected and standalone systems', 'Environmental and maintenance considerations'], 'objectives': ['Describe the energy conversion process', 'Name major turbine components', 'Explain why location affects performance'], 'glossary': ['Rotor — rotating assembly driven by wind', 'Nacelle — housing containing key turbine machinery', 'Cut-in speed — wind speed at which generation begins', 'Capacity factor — actual output compared with maximum possible output over time'], 'activity': 'Do not climb or approach turbines; study through models, diagrams and supervised demonstrations.'},
    'Energy Storage Systems': {'overview': 'Storing energy for later use', 'topics': ['Battery types and ratings', 'Voltage, capacity and energy', 'Charge and discharge cycles', 'Battery management and protection', 'Recycling and safe storage'], 'objectives': ['Distinguish battery capacity from power', 'Explain why compatible chargers are important', 'Recognize safe storage practices'], 'glossary': ['Capacity — commonly expressed in ampere-hours', 'State of charge — estimated remaining battery charge', 'Cycle life — expected charge/discharge cycles under stated conditions', 'BMS — battery management system'], 'activity': 'Never puncture, short-circuit, open or improvise battery packs. Use approved chargers and supervision.'},
    'Renewable Energy Installation': {'overview': 'Planning renewable-energy installations', 'topics': ['Site survey and energy needs', 'System sizing and component compatibility', 'Mounting, cable routing and protection', 'Inspection and maintenance plans', 'Documentation and safety'], 'objectives': ['List information needed before system design', 'Explain why ratings must be compatible', 'Describe maintenance record keeping'], 'glossary': ['Load assessment — identifying energy needs', 'Array — group of connected PV modules', 'Protection — devices and measures that reduce fault risks', 'Commissioning — checks before a system enters service'], 'activity': 'All installation work must follow applicable standards and be performed or checked by qualified personnel.'},
    'Energy Efficiency': {'overview': 'Using energy wisely', 'topics': ['Power and energy consumption', 'Efficient lighting and appliances', 'Standby power and user habits', 'Insulation and heat transfer', 'Energy audits and simple savings estimates'], 'objectives': ['Calculate energy use from power and time', 'Identify practical efficiency improvements', 'Compare energy labels and operating costs'], 'glossary': ['Efficiency — useful output divided by input', 'Kilowatt-hour — common unit of electrical energy', 'Energy audit — review of energy use and saving opportunities', 'Standby power — energy used while equipment is not actively operating'], 'activity': 'Base savings claims on measurements or clear assumptions.'},
    'Electronic Components': {'overview': 'Identifying components and their functions', 'topics': ['Resistors, capacitors and inductors', 'Diodes, LEDs and rectification', 'Transistors and switching', 'Integrated circuits and connectors', 'Polarity, ratings and datasheets'], 'objectives': ['Recognize common components', 'Explain basic component functions', 'Check polarity and ratings before a low-voltage project'], 'glossary': ['Resistor — limits current or divides voltage', 'Capacitor — stores energy in an electric field', 'Diode — conducts preferentially in one direction', 'Transistor — can switch or amplify signals'], 'activity': 'Use current-limited low-voltage learning circuits under supervision.'},
    'Analogue Electronics': {'overview': 'Signals that vary continuously', 'topics': ['Voltage and current signals', 'Diode rectifiers and filtering', 'Transistor operation', 'Operational amplifier basics', 'Noise, gain and measurement'], 'objectives': ['Distinguish analogue from digital signals', 'Explain rectification and filtering', 'Describe gain in an amplifier'], 'glossary': ['Gain — ratio of output signal to input signal', 'Rectifier — converts AC to pulsating DC', 'Filter — passes some signal components more than others', "Bias — setting a component's operating condition"], 'activity': 'Check circuit ratings and use safe low-voltage supplies.'},
    'Digital Electronics': {'overview': 'Working with binary logic', 'topics': ['Binary numbers and logic levels', 'AND, OR and NOT gates', 'Truth tables', 'Flip-flops and counters', 'Combinational and sequential circuits'], 'objectives': ['Convert simple binary values', 'Construct truth tables', 'Explain the difference between combinational and sequential logic'], 'glossary': ['Bit — binary digit 0 or 1', 'Logic gate — performs a Boolean operation', 'Truth table — lists outputs for input combinations', 'Flip-flop — stores one bit of state'], 'activity': 'Avoid connecting logic ICs to supplies outside their specified ratings.'},
    'Electronic Circuit Design': {'overview': 'Turning a circuit idea into a working design', 'topics': ['Circuit diagrams and symbols', 'Component selection and tolerances', 'Series and parallel calculations', 'Prototyping and testing', 'Troubleshooting and documentation'], 'objectives': ['Read a simple schematic', 'Choose components with suitable ratings', 'Record test results and design changes'], 'glossary': ['Schematic — symbolic representation of a circuit', 'Tolerance — allowed variation from a nominal value', 'Prototype — early version used to test a design', 'Ground/reference — common voltage reference in a circuit'], 'activity': 'Begin with low-voltage circuits; disconnect power before changing wiring.'},
    'Instrumentation and Measurement': {'overview': 'Measuring and interpreting physical quantities', 'topics': ['Sensors and transducers', 'Measurement range and resolution', 'Calibration and uncertainty', 'Signal conditioning', 'Data recording and interpretation'], 'objectives': ['Distinguish sensor and transducer functions', 'Explain resolution and measurement error', 'Record data in tables with units'], 'glossary': ['Sensor — detects a physical quantity', 'Transducer — converts one form of energy or signal to another', 'Calibration — comparison with a reference', 'Resolution — smallest change an instrument can display'], 'activity': 'Use instruments within their rated limits and document uncertainty honestly.'},

    'English Language': {'overview': 'Communication for study and work', 'topics': ['Reading comprehension', 'Grammar and sentence structure', 'Vocabulary and spelling', 'Summary and report writing', 'Formal letters, emails and presentations'], 'objectives': ['Identify main ideas in a passage', 'Write clear and correctly structured sentences', 'Prepare a short formal report'], 'glossary': ['Grammar — rules for how words form sentences', 'Summary — a brief statement of main points', 'Formal register — language suited to professional situations', 'Comprehension — understanding what is read'], 'activity': 'Practise writing original answers and review them for clarity, spelling and grammar.'},
    'Mathematics': {'overview': 'Mathematical skills for technical learning', 'topics': ['Number operations and fractions', 'Ratio, proportion and percentages', 'Algebra and equations', 'Geometry and measurement', 'Statistics, graphs and practical calculations'], 'objectives': ['Show calculation steps clearly', 'Solve equations and percentage problems', 'Use units and interpret graphs'], 'glossary': ['Variable — a symbol representing a value', 'Ratio — comparison of quantities', 'Mean — arithmetic average', 'Perimeter — total distance around a shape'], 'activity': 'Show each step, include units where needed, and check whether the answer is reasonable.'},
    'Integrated Science': {'overview': 'Scientific ideas and evidence in everyday life', 'topics': ['Scientific investigation and measurement', 'Matter and materials', 'Energy and forces', 'Living things and health', 'Environment and sustainability'], 'objectives': ['Describe a fair investigation', 'Distinguish observation from explanation', 'Explain safe and responsible use of resources'], 'glossary': ['Hypothesis — a testable proposed explanation', 'Variable — a factor that can change', 'Evidence — information used to support a conclusion', 'Ecosystem — living things and their environment interacting'], 'activity': 'Follow teacher instructions and laboratory safety rules during practical activities.'},
    'ICT': {'overview': 'Digital skills for learning and work', 'topics': ['Computer and mobile device basics', 'Files, folders and file management', 'Word processing and spreadsheets', 'Internet research and source checking', 'Digital safety, privacy and responsible use'], 'objectives': ['Organise files and folders', 'Create a simple document and spreadsheet', 'Recognise unreliable information and protect accounts'], 'glossary': ['Hardware — physical computer components', 'Software — programs and applications', 'Spreadsheet — a grid for organising and calculating data', 'Phishing — a deceptive attempt to obtain private information'], 'activity': 'Use strong unique passwords, protect personal information, and ask a teacher before installing unknown files.'},
    'Social Studies': {'overview': 'People, citizenship and society', 'topics': ['Citizenship and civic responsibility', 'Culture and national identity', 'Governance and the rule of law', 'Population and social change', 'Environment, community and development'], 'objectives': ['Explain responsible citizenship', 'Discuss how communities respond to social change', 'Support opinions with relevant examples'], 'glossary': ['Citizen — a legally recognised member of a state', 'Constitution — the fundamental framework of government', 'Demography — the study of populations', 'Sustainability — meeting needs while protecting future resources'], 'activity': 'Discuss issues respectfully and distinguish evidence from personal opinion.'},
    'Entrepreneurship': {'overview': 'Identifying opportunities and planning a small business', 'topics': ['Entrepreneurial qualities and problem solving', 'Customer needs and market research', 'Business ideas and value propositions', 'Costs, pricing, sales and simple records', 'Ethics, customer care and business planning'], 'objectives': ['Identify a practical customer problem', 'Prepare a simple business idea', 'Estimate costs and explain a pricing decision'], 'glossary': ['Entrepreneur — a person who organises a venture', 'Customer — a person or organisation buying a product or service', 'Revenue — money earned from sales', 'Profit — revenue minus costs'], 'activity': 'Use realistic assumptions and keep clear records when preparing a sample business plan.'}

}

# ---------------- PRACTICE QUESTIONS ----------------

QUIZ_BANK = {
    "Basic Electricity": [
        {"q": "Which unit measures electric current?",
         "options": ["Volt", "Ampere", "Ohm", "Watt"], "answer": "Ampere",
         "why": "Current is measured in amperes (A)."},
        {"q": "Which formula represents Ohm's law?",
         "options": ["V = I × R", "P = m × g", "A = l × w", "F = m × a"],
         "answer": "V = I × R", "why": "Voltage equals current multiplied by resistance."},
        {"q": "What is the unit of resistance?",
         "options": ["Watt", "Volt", "Ohm", "Ampere"], "answer": "Ohm",
         "why": "Resistance is measured in ohms (Ω)."}
    ],
    "Electrical Measurement": [
        {"q": "Which instrument measures voltage?",
         "options": ["Ammeter", "Voltmeter", "Thermometer", "Ruler"],
         "answer": "Voltmeter", "why": "A voltmeter measures potential difference."},
        {"q": "Resistance should be measured on a circuit that is…",
         "options": ["Energized", "Switched off and isolated", "Wet", "Overloaded"],
         "answer": "Switched off and isolated",
         "why": "Resistance measurement must not be made on an energized circuit."}
    ],
    "Electronic Components": [
        {"q": "Which component mainly allows current in one direction?",
         "options": ["Diode", "Resistor", "Fuse holder", "Switch plate"],
         "answer": "Diode", "why": "A diode conducts preferentially in one direction."},
        {"q": "What does an LED produce when correctly powered?",
         "options": ["Light", "Sound only", "Water", "Mechanical pressure"],
         "answer": "Light", "why": "LED means light-emitting diode."}
    ],
    "Solar Energy Systems": [
        {"q": "What does a photovoltaic panel convert?",
         "options": ["Sunlight to electrical energy", "Sound to food",
                     "Wind to water", "Heat to paper"],
         "answer": "Sunlight to electrical energy",
         "why": "Photovoltaic cells convert light into electrical energy."}
    ],
    "Technical Drawing": [
        {"q": "Which tool is commonly used to draw a circle?",
         "options": ["Compass", "Pliers", "Soldering iron", "Spanner"],
         "answer": "Compass", "why": "A compass draws circles and arcs."}
    ],
    "Food Hygiene and Safety": [
        {"q": "What helps prevent cross-contamination?",
         "options": ["Mixing raw and cooked foods", "Separating raw and ready-to-eat food",
                     "Leaving food uncovered", "Using dirty tools"],
         "answer": "Separating raw and ready-to-eat food",
         "why": "Separating foods helps prevent harmful microorganisms spreading."}
    ]
}


# ---------------- UI HELPERS ----------------

def label_symbol(label):
    """Choose a small sign for short headings and labels without changing lesson paragraphs."""
    raw = str(label).strip()
    if not raw or len(raw) > 46 or raw[0] in "⌂▦☆●⌕⋮✓★⚡🧠🛠✍📘🔎🔒👤📚💾🎓↩←→＋✦•ⓘ⚙✎▤♙":
        return ""
    lower = raw.lower()
    rules = [
        (("ajti", "school", "dashboard", "home"), "⌂"),
        (("subject", "course", "learn", "lesson", "study"), "📘"),
        (("search", "find"), "⌕"), (("saved", "bookmark", "favourite", "favorite"), "☆"),
        (("profile", "account", "student details"), "♙"),
        (("quiz", "question", "practice test", "test", "answer"), "✎"),
        (("progress", "result", "score", "completed"), "▤"),
        (("password", "security", "login", "sign in"), "🔒"),
        (("register", "registration", "submit"), "＋"),
        (("teacher", "admin", "manage", "setting"), "⚙"),
        (("help", "about", "information", "hint"), "ⓘ"),
        (("saved", "save"), "✓"), (("warning", "error", "failed"), "⚠"),
        (("success", "welcome", "ready"), "✓"), (("back", "cancel", "close"), "←"),
        (("math", "electric", "circuit", "technical drawing"), "⚡"),
    ]
    for keywords, symbol in rules:
        if any(word in lower for word in keywords):
            return symbol
    # A subtle marker keeps short UI labels visually consistent.
    return "•"


def make_label(text, size=16, color=DARK, height=48, bold=False):
    raw_text = str(text)
    symbol = label_symbol(raw_text)
    display_text = (symbol + "  " + raw_text) if symbol else raw_text
    w = Label(
        text=display_text, font_size=dp(size), color=color,
        size_hint_y=None, height=dp(height),
        halign="left", valign="middle", bold=bold
    )
    w.bind(size=lambda obj, val: setattr(obj, "text_size", (val[0] - dp(12), None)))
    return w


def button_symbol(label):
    """Return a readable symbol for common actions; keep existing symbols intact."""
    raw = str(label).strip()
    if not raw:
        return "•"
    # Don't duplicate symbols already deliberately supplied by a screen.
    if raw[0] in "⌂▦☆●⌕⋮✓★⚡🧠🛠✍📘🔎🔒👤📚💾🎓↩←→＋✦":
        return ""
    lower = raw.lower()
    rules = [
        (("home", "dashboard"), "⌂"), (("search", "find"), "⌕"),
        (("course", "subject", "explore", "learn"), "▦"),
        (("saved", "bookmark", "favourite", "favorite"), "☆"),
        (("profile", "account", "student details"), "●"),
        (("sign in", "login", "log in"), "↪"),
        (("sign out", "logout", "log out"), "⇥"),
        (("register", "registration", "submit request"), "＋"),
        (("quiz", "practice test", "test"), "✎"),
        (("progress", "results", "score"), "▤"),
        (("lesson", "notes", "read"), "▤"),
        (("study", "flashcard", "revision", "learning mode"), "✦"),
        (("edit", "change", "update"), "✎"),
        (("save",), "✓"), (("back", "cancel", "close"), "←"),
        (("approve", "confirm", "done"), "✓"),
        (("teacher", "admin", "manage"), "⚙"),
        (("information", "about", "help"), "ⓘ"),
        (("password", "security"), "♙"),
        (("delete", "remove"), "×"), (("open", "view", "continue"), "›"),
    ]
    for keywords, symbol in rules:
        if any(word in lower for word in keywords):
            return symbol
    return "•"


def make_button(text, callback, color=BLUE, height=48):
    # Light-coloured buttons use dark text; saturated buttons use white text.
    light_colors = (LIGHT_BLUE, PALE, WHITE, GOLD)
    text_color = DARK if color in light_colors else WHITE
    raw_text = str(text)
    symbol = button_symbol(raw_text)
    display_text = (symbol + "  " + raw_text) if symbol else raw_text
    w = RoundedButton(
        text=display_text, size_hint_y=None, height=dp(height),
        bg_color=list(color), color=text_color, font_size=dp(14), bold=True
    )
    w.bind(on_release=callback)
    return w


class RoundedInput(TextInput):
    """Text field with a soft rounded capsule background."""
    fill_color = ListProperty([0.91, 0.96, 1.0, 1])
    corner_radius = NumericProperty(20)

    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_active", "")
        kwargs["background_color"] = [0, 0, 0, 0]
        super().__init__(**kwargs)
        with self.canvas.before:
            self._input_color = Color(rgba=self.fill_color)
            self._input_shape = RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[min(self.height / 2, self.corner_radius)]
            )
        self.bind(pos=self._sync_input_shape, size=self._sync_input_shape,
                  fill_color=self._sync_input_shape, focus=self._sync_input_color)
        self._sync_input_color()

    def _sync_input_shape(self, *_):
        self._input_shape.pos = self.pos
        self._input_shape.size = self.size
        self._input_shape.radius = [min(self.height / 2, self.corner_radius)]
        self._input_color.rgba = self.fill_color

    def _sync_input_color(self, *_):
        if hasattr(self, "_input_color"):
            self._input_color.rgba = ([0.96, 0.98, 1.0, 1] if self.focus else self.fill_color)


def input_symbol(hint):
    text = str(hint).lower()
    if any(k in text for k in ("password", "pin")): return "🔒"
    if any(k in text for k in ("email", "username", "name", "student id")): return "♙"
    if any(k in text for k in ("search", "find")): return "⌕"
    if any(k in text for k in ("phone", "mobile", "contact")): return "☎"
    if any(k in text for k in ("answer", "write", "type", "message", "notes")): return "✎"
    return "✦"


def make_input(hint, multiline=False, password=False, height=48):
    hint_text = str(hint).strip()
    if hint_text and hint_text[0] not in "🔒♙⌕☎✎✦•":
        hint_text = input_symbol(hint_text) + "  " + hint_text
    return RoundedInput(
        hint_text=hint_text, multiline=multiline, password=password,
        size_hint_y=None, height=dp(height), font_size=dp(15),
        padding=[dp(14), dp(10), dp(14), dp(10)],
        fill_color=list(LIGHT_BLUE), foreground_color=DARK,
        cursor_color=BLUE, corner_radius=dp(22)
    )


class BaseScreen(Screen):
    """Shared modern AJTI interface: compact toolbar, animated content and bottom navigation."""
    def __init__(self, title, subtitle="", **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = get_color_from_hex("#F2F6FC")

        main = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        with main.canvas.before:
            self._screen_bg_color = Color(*get_color_from_hex("#F2F6FC"))
            self._screen_bg = RoundedRectangle(pos=main.pos, size=main.size, radius=[dp(22)])
        main.bind(pos=self._sync_screen_bg, size=self._sync_screen_bg)

        # Compact branded toolbar with quick search and app menu.
        toolbar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))
        brand = AJTICard(orientation="vertical", size_hint_x=None, width=dp(44),
                         padding=dp(3), spacing=0, fill_color=list(AJTI_PRIMARY), radius_size=22)
        brand.add_widget(make_label("AJTI", 13, WHITE, 21, True))
        toolbar.add_widget(brand)
        brand_text = BoxLayout(orientation="vertical", spacing=0)
        brand_text.add_widget(make_label("AJTI LEARN", 14, NAVY, 23, True))
        brand_text.add_widget(make_label("LEARN • PRACTISE • GROW", 9, GREY, 18, True))
        toolbar.add_widget(brand_text)
        search_btn = make_button("⌕", lambda *_: self.open_global_search(), AJTI_SURFACE_ALT, 42)
        search_btn.size_hint_x = None
        search_btn.width = dp(44)
        search_btn.font_size = dp(22)
        toolbar.add_widget(search_btn)
        menu_btn = make_button("⋮", lambda *_: self.open_quick_menu(), AJTI_SURFACE_ALT, 42)
        menu_btn.size_hint_x = None
        menu_btn.width = dp(40)
        menu_btn.font_size = dp(22)
        toolbar.add_widget(menu_btn)
        main.add_widget(toolbar)

        heading = BoxLayout(
            orientation="vertical", size_hint_y=None, height=dp(68),
            padding=[dp(12), dp(5), dp(12), dp(3)], spacing=dp(0)
        )
        with heading.canvas.before:
            heading_color = Color(*get_color_from_hex("#FFFFFF"))
            heading_rect = RoundedRectangle(pos=heading.pos, size=heading.size, radius=[dp(26)])
        def sync_heading(*_):
            heading_rect.pos = heading.pos
            heading_rect.size = heading.size
        heading.bind(pos=sync_heading, size=sync_heading)
        heading.add_widget(make_label(title, 18, NAVY, 36, True))
        if subtitle:
            heading.add_widget(make_label(subtitle, 11, GREY, 22))
        main.add_widget(heading)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4),
                            bar_color=BLUE, bar_inactive_color=LIGHT_BLUE)
        self.body = BoxLayout(
            orientation="vertical", spacing=dp(9), opacity=1,
            padding=[dp(3), dp(7), dp(3), dp(12)], size_hint_y=None
        )
        self.body.bind(minimum_height=self.body.setter("height"))
        scroll.add_widget(self.body)
        main.add_widget(scroll)

        # Modern compact navigation bar. Labels remain clear if emoji fonts differ.
        nav = AJTICard(orientation="horizontal", size_hint_y=None, height=dp(60), spacing=dp(7),
                       padding=[dp(7), dp(7), dp(7), dp(7)], fill_color=list(AJTI_SURFACE), radius_size=32)
        for label, destination, fill in [
            ("⌂  HOME", "customhome", AJTI_SURFACE_ALT),
            ("▦  LEARN", "courses", AJTI_PRIMARY),
            ("☆  SAVED", "bookmarks", AJTI_ACCENT),
            ("♙  PROFILE", "profile", AJTI_SURFACE_ALT),
        ]:
            nav_button = make_button(
                label, lambda _btn, dest=destination: self.go_to(dest), fill, 42
            )
            nav_button.font_size = dp(9)
            nav_button.corner_radius = dp(26)
            nav_button.padding = [dp(2), dp(2)]
            nav.add_widget(nav_button)
        main.add_widget(nav)
        self.add_widget(main)

    def _sync_screen_bg(self, widget, *_):
        self._screen_bg.pos = widget.pos
        self._screen_bg.size = widget.size

    def go_to(self, destination):
        if self.manager:
            self.manager.current = destination

    def add_label(self, text, size=16, color=DARK, height=48, bold=False):
        self.body.add_widget(make_label(text, size, color, height, bold))

    def add_button(self, text, callback, color=BLUE, height=48):
        self.body.add_widget(make_button(text, callback, color, height))

    def add_input(self, widget):
        self.body.add_widget(widget)

    def back(self, destination):
        self.add_button("BACK", lambda *_: setattr(self.manager, "current", destination), NAVY)

    def open_global_search(self):
        app = App.get_running_app()
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(9))
        field = make_input("Search subjects or lesson titles…")
        box.add_widget(field)
        hint = make_label("Search your offline AJTI lesson library", 12, GREY, 30)
        box.add_widget(hint)
        controls = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        pop = Popup(title="Quick lesson search", content=box, size_hint=(0.92, None), height=dp(190))
        def search(*_):
            term = field.text.strip().lower()
            if not term:
                app.message("Search", "Type a subject or lesson keyword first.")
                return
            matches = []
            for subject, lesson in app.data.get("lessons", {}).items():
                if term in subject.lower() or term in lesson.get("title", "").lower() or term in lesson.get("notes", "").lower():
                    matches.append(subject)
            pop.dismiss()
            if not matches:
                app.message("No results", "No lesson matched that search. Try another keyword.")
                return
            result_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
            result_scroll = ScrollView(do_scroll_x=False)
            result_list = BoxLayout(orientation="vertical", spacing=dp(7), size_hint_y=None)
            result_list.bind(minimum_height=result_list.setter("height"))
            result_popup = Popup(title="Search results (" + str(len(matches)) + ")", content=result_box, size_hint=(0.94, 0.78))
            for subject_name in matches[:40]:
                lesson = app.data.get("lessons", {}).get(subject_name, {})
                label = subject_name + "\n" + lesson.get("title", "Lesson notes")
                def choose(_, selected=subject_name):
                    result_popup.dismiss()
                    app.current_subject = selected
                    self.manager.current = "lesson"
                result_list.add_widget(make_button(label, choose, LIGHT_BLUE, 56))
            result_scroll.add_widget(result_list)
            result_box.add_widget(result_scroll)
            result_popup.open()
        controls.add_widget(make_button("SEARCH", search, BLUE, 42))
        controls.add_widget(make_button("CANCEL", lambda *_: pop.dismiss(), GREY, 42))
        box.add_widget(controls)
        pop.open()

    def open_quick_menu(self):
        app = App.get_running_app()
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        pop = Popup(title="AJTI quick menu", content=box, size_hint=(0.88, None), height=dp(300))
        options = [
            ("Search lessons", self.open_global_search),
            ("My progress", lambda: self.go_to("progress")),
            ("Study tools & flashcards", lambda: self.go_to("studytools")),
            ("App information", lambda: app.message("AJTI Learning App v7.7", "Offline-first learning prototype. Lessons, bookmarks and quiz results are stored on this device. Official school colours and crest can be added when supplied.")),
        ]
        for label, action in options:
            def run_action(*_, callback=action):
                pop.dismiss()
                callback()
            box.add_widget(make_button(label, run_action, LIGHT_BLUE, 44))
        box.add_widget(make_button("CLOSE", lambda *_: pop.dismiss(), NAVY, 40))
        pop.open()

    def on_pre_enter(self, *args):
        self.refresh()
        # Fade in the content after the ScreenManager's slide transition.
        self.body.opacity = 0.72
        Animation(opacity=1, duration=0.22, transition="out_quad").start(self.body)

    def refresh(self):
        pass

# ---------------- ANIMATED APP-OPENING SPLASH ----------------

class SplashParticles(Widget):
    """Lightweight orbiting particles drawn with Kivy canvas."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elapsed = 0.0
        Clock.schedule_interval(self.redraw, 1 / 24)

    def redraw(self, dt):
        self.elapsed += dt
        self.canvas.clear()
        cx, cy = self.center
        # Draw a restrained ring of glowing dots around the AJTI mark.
        with self.canvas:
            for i in range(24):
                phase = (i / 24.0) * math.tau + self.elapsed * (0.8 if i % 2 else -0.55)
                radius = min(self.width, self.height) * (0.16 + 0.035 * math.sin(self.elapsed * 1.7 + i))
                x = cx + math.cos(phase) * radius
                y = cy + math.sin(phase) * radius
                alpha = 0.28 + 0.42 * (0.5 + 0.5 * math.sin(self.elapsed * 2.0 + i))
                Color(0.12, 0.72, 1.0, alpha)
                Ellipse(pos=(x - dp(2.4), y - dp(2.4)), size=(dp(4.8), dp(4.8)))
                if i % 4 == 0:
                    Color(0.25, 1.0, 0.65, alpha * 0.75)
                    Ellipse(pos=(x - dp(1.3), y - dp(1.3)), size=(dp(2.6), dp(2.6)))


class SplashScreen(Screen):
    """Short animated opening shown every time the app is launched."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._leave_event = None
        with self.canvas.before:
            Color(*get_color_from_hex("#061426"))
            self._background = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        layout = FloatLayout()
        particles = SplashParticles(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        layout.add_widget(particles)

        # A diamond plate behind the initials gives a dimensional, rotating emblem.
        self.emblem = Label(
            text="◆", font_name="Roboto", font_size=dp(108),
            color=(0.08, 0.46, 0.88, 0.22), size_hint=(None, None),
            size=(dp(220), dp(190)), pos_hint={"center_x": 0.5, "center_y": 0.58}
        )
        layout.add_widget(self.emblem)

        self.logo = Label(
            text="AJTI", font_size=dp(54), bold=True,
            color=(0.35, 0.88, 1, 1), outline_width=dp(1.3),
            outline_color=(0.04, 0.36, 0.75, 1),
            size_hint=(None, None), size=(dp(260), dp(92)),
            pos_hint={"center_x": 0.5, "center_y": 0.58}
        )
        with self.logo.canvas.before:
            PushMatrix()
            self._logo_spin = Rotate(angle=0, origin=self.logo.center)
        with self.logo.canvas.after:
            PopMatrix()
        self.logo.bind(center=lambda inst, val: setattr(self._logo_spin, "origin", val))
        layout.add_widget(self.logo)

        self.tagline = Label(
            text="LEARN TODAY. ENGINEER TOMORROW!", font_size=dp(12), bold=True,
            color=(0.91, 0.96, 1, 0), size_hint=(0.9, None), height=dp(32),
            pos_hint={"center_x": 0.5, "center_y": 0.405}
        )
        layout.add_widget(self.tagline)
        self.status = Label(
            text="PREPARING YOUR LEARNING SPACE", font_size=dp(9),
            color=(0.42, 0.72, 0.9, 0.0), size_hint=(0.9, None), height=dp(24),
            pos_hint={"center_x": 0.5, "center_y": 0.32}
        )
        layout.add_widget(self.status)
        self.add_widget(layout)

    def _sync_bg(self, *_):
        self._background.pos = self.pos
        self._background.size = self.size

    def on_enter(self, *_):
        # Restart all animations each time this screen is entered.
        self._logo_spin.angle = 0
        self.logo.opacity = 0.2
        self.logo.font_size = dp(43)
        self.tagline.color = (0.91, 0.96, 1, 0)
        self.status.color = (0.42, 0.72, 0.9, 0)
        self._spin_animation = Animation(angle=360, duration=2.2, transition="linear")
        self._spin_animation.repeat = True
        self._spin_animation.start(self._logo_spin)
        Animation(opacity=1, font_size=dp(54), duration=0.75, transition="out_back").start(self.logo)
        Animation(color=(0.91, 0.96, 1, 1), duration=0.65, transition="out_quad").start(self.tagline)
        Animation(color=(0.42, 0.72, 0.9, 1), duration=0.75, transition="out_quad").start(self.status)
        if self._leave_event is not None:
            self._leave_event.cancel()
        self._leave_event = Clock.schedule_once(self.open_dashboard, 10.0)

    def open_dashboard(self, *_):
        if hasattr(self, "_spin_animation"):
            self._spin_animation.cancel(self._logo_spin)
        if self.manager and self.manager.has_screen("customhome"):
            self.manager.transition = SlideTransition(duration=0.28, direction="up")
            self.manager.current = "customhome"
            self.manager.transition = SlideTransition(duration=0.18, direction="left")


# ---------------- APP ----------------

class AJTIApp(App):
    def build(self):
        self.title = APP_NAME + " v" + APP_VERSION
        self.data_file = os.path.join(self.user_data_dir, "ajti_learning_data_v3.json")
        self.data = self.load_data()
        self.ensure_subject_guides()
        self.current_user = None
        self.current_course = ""
        self.current_subject = ""
        self.registration_course = ""
        self.registration_year = ""
        self.login_year = "Year 1"
        self.quiz_subject = ""
        self.quiz_questions = []
        self.quiz_index = 0
        self.quiz_score = 0
        self.quiz_answers = []

        sm = ScreenManager(transition=SlideTransition(duration=0.18, direction="left"))
        for screen in [
            SplashScreen(name="splash"), WelcomeScreen(name="welcome"), CustomHomeScreen(name="customhome"), LoginScreen(name="login"),
            RegisterScreen(name="register"), StudentScreen(name="student"),
            CoursesScreen(name="courses"), SubjectsScreen(name="subjects"),
            LessonScreen(name="lesson"), StudyToolsScreen(name="studytools"), ProfileScreen(name="profile"),
            ProgressScreen(name="progress"), BookmarksScreen(name="bookmarks"), QuizScreen(name="quiz"),
            TeacherScreen(name="teacher"), TeacherEditorScreen(name="editor"),
            AdminScreen(name="admin"), ResultsScreen(name="results")
        ]:
            sm.add_widget(screen)
        sm.current = "splash"
        return sm

    def load_data(self):
        default = {"users": [], "requests": [], "lessons": {},
                   "progress": {}, "results": [], "bookmarks": {}}
        try:
            if os.path.isfile(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                if isinstance(saved, dict):
                    for k, v in default.items():
                        if k not in saved or not isinstance(saved[k], type(v)):
                            saved[k] = v
                    for subject, lesson in STARTER_LESSONS.items():
                        saved["lessons"].setdefault(subject, lesson)
                    return saved
        except (OSError, ValueError, TypeError):
            pass
        default["lessons"] = dict(STARTER_LESSONS)
        return default


    def ensure_subject_guides(self):
        """Add expanded starter notes for new subjects without overwriting teacher edits."""
        for subject, guide in SUBJECT_GUIDES.items():
            if subject not in self.data["lessons"]:
                topics = "\n".join("• " + item for item in guide["topics"])
                objectives = "\n".join("• " + item for item in guide["objectives"])
                glossary = "\n".join("• " + item for item in guide["glossary"])
                notes = (
                    guide["overview"] + "\n\nKEY TOPICS\n" + topics +
                    "\n\nLEARNING OBJECTIVES\n" + objectives +
                    "\n\nKEY TERMS\n" + glossary +
                    "\n\nPRACTICAL APPLICATION / SAFETY\n" + guide["activity"] +
                    "\n\nSTUDY TIP\nDefine important terms, make labelled diagrams where appropriate, "
                    "show calculations step by step, include units, and review mistakes after quizzes."
                )
                self.data["lessons"][subject] = {
                    "title": subject + " — Complete Study Notes",
                    "notes": notes,
                    "updated_at": "AJTI Learning Library v3.3"
                }
        self.save_data()

    def save_data(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            temp = self.data_file + ".tmp"
            with open(temp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            os.replace(temp, self.data_file)
            return True
        except (OSError, TypeError, ValueError) as exc:
            self.message("Storage Error", "Could not save data.\n" + str(exc))
            return False

    def message(self, title, message):
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        box.add_widget(make_label(message, 14, DARK, 150))
        pop = Popup(title=title, content=box, size_hint=(0.9, None), height=dp(270))
        box.add_widget(make_button("OK", lambda *_: pop.dismiss(), BLUE))
        pop.open()

    def confirm(self, title, message, yes_callback):
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        box.add_widget(make_label(message, 14, DARK, 100))
        pop = Popup(title=title, content=box, size_hint=(0.9, None), height=dp(230))
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        row.add_widget(make_button("CANCEL", lambda *_: pop.dismiss(), GREY))
        def yes(*_):
            pop.dismiss()
            yes_callback()
        row.add_widget(make_button("CONTINUE", yes, RED))
        box.add_widget(row)
        pop.open()

    @staticmethod
    def password_hash(password, salt=None):
        salt = salt or secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                     salt.encode("utf-8"), 120000).hex()
        return salt, digest

    def password_matches(self, user, password):
        # Upgrade legacy plaintext demo passwords when possible.
        if user.get("password_hash") and user.get("salt"):
            _, digest = self.password_hash(password, user["salt"])
            return secrets.compare_digest(digest, user["password_hash"])
        if user.get("password") == password:
            salt, digest = self.password_hash(password)
            user["salt"], user["password_hash"] = salt, digest
            user.pop("password", None)
            self.save_data()
            return True
        return False

    def login(self, identity, password, selected_year=None):
        identity = identity.strip().lower()
        if not identity or not password:
            self.message("Missing Information", "Enter your email/student ID and password.")
            return
        for user in self.data["users"]:
            if identity in (user.get("email", "").lower(),
                            user.get("student_id", "").lower()):
                if not self.password_matches(user, password):
                    break
                if user.get("status") != "Approved":
                    self.message("Account Pending", "Your account is awaiting approval.")
                    return
                stored_year = user.get("year", "Year 1")
                if user.get("role", "student") == "student" and selected_year and selected_year != stored_year:
                    self.message("Year Does Not Match", "This account is registered for " + stored_year + ". Select that year to sign in.")
                    return
                self.current_user = user
                self.current_course = user.get("course", "")
                role = user.get("role", "student")
                self.root.current = "admin" if role == "admin" else (
                    "teacher" if role == "teacher" else "student")
                return
        self.message("Login Failed", "Incorrect email/student ID or password.")

    def logout(self):
        self.current_user = None
        self.current_course = ""
        self.current_subject = ""
        self.root.current = "welcome"

    def change_password(self, old_password, new_password, confirm_password):
        user = self.current_user
        if not user:
            self.message("Sign In Required", "Sign in before changing your password.")
            return
        if not old_password or not new_password or not confirm_password:
            self.message("Missing Information", "Complete all password fields.")
            return
        if not self.password_matches(user, old_password):
            self.message("Incorrect Password", "Your current password is not correct.")
            return
        if len(new_password) < 8:
            self.message("Password Too Short", "Use at least 8 characters.")
            return
        if new_password != confirm_password:
            self.message("Passwords Do Not Match", "Retype the same new password in both fields.")
            return
        salt, digest = self.password_hash(new_password)
        user["salt"], user["password_hash"] = salt, digest
        user.pop("password", None)
        user.pop("must_change_password", None)
        if self.save_data():
            self.message("Password Updated", "Your new password is saved on this device.")

    def register_student(self, name, email, student_id):
        name, email, student_id = name.strip(), email.strip().lower(), student_id.strip()
        if not name or not email or not student_id or not self.registration_course or self.registration_year not in STUDY_YEARS:
            self.message("Missing Information", "Complete all fields and select your year and department.")
            return
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            self.message("Invalid Email", "Enter an email address in a valid format.")
            return
        for user in self.data["users"]:
            if user.get("email", "").lower() == email:
                self.message("Account Exists", "That email is already registered.")
                return
            if user.get("student_id", "").lower() == student_id.lower():
                self.message("Student ID Exists", "That student ID is already registered.")
                return
        for req in self.data["requests"]:
            if req.get("status") == "Pending" and (
                req.get("email", "").lower() == email or
                req.get("student_id", "").lower() == student_id.lower()
            ):
                self.message("Request Exists", "A pending request already uses that email or student ID.")
                return
        self.data["requests"].append({
            "name": name, "email": email, "student_id": student_id,
            "course": self.registration_course, "year": self.registration_year, "status": "Pending",
            "created_at": datetime.now().isoformat(timespec="minutes")
        })
        if self.save_data():
            self.registration_course = ""
            self.registration_year = ""
            self.message("Request Saved", "Saved on this phone only. It has not been sent to the school online.")
            self.root.current = "welcome"

    def create_demo_admin(self):
        if any(u.get("role") == "admin" for u in self.data["users"]):
            self.message("Administrator Exists",
                         "An administrator account already exists on this device. Sign in with its credentials.")
            return
        # Demo credentials are intentionally displayed and must be changed before any real deployment.
        password = "ChangeMe-Admin-30!"
        salt, digest = self.password_hash(password)
        self.data["users"].append({
            "name": "AJTI Demo Administrator", "email": "admin@ajti.local",
            "student_id": "ADMIN-DEMO", "course": "Administration",
            "salt": salt, "password_hash": digest, "role": "admin",
            "status": "Approved", "must_change_password": True
        })
        if self.save_data():
            self.message("Demo Administrator Created",
                         "Email: admin@ajti.local\nPassword: " + password +
                         "\n\nDemo use only. Do not use this setup for real school accounts.")

    def create_demo_teacher(self):
        if any(u.get("role") == "teacher" for u in self.data["users"]):
            self.message("Teacher Exists", "A teacher account already exists on this device.")
            return
        password = "ChangeMe-Teacher-30!"
        salt, digest = self.password_hash(password)
        self.data["users"].append({
            "name": "AJTI Demo Teacher", "email": "teacher@ajti.local",
            "student_id": "TEACHER-DEMO", "course": "All Departments",
            "salt": salt, "password_hash": digest, "role": "teacher",
            "status": "Approved"
        })
        if self.save_data():
            self.message("Demo Teacher Created",
                         "Email: teacher@ajti.local\nPassword: " + password +
                         "\n\nDemo use only. Share credentials carefully.")

    def approve_next_request(self):
        for req in self.data["requests"]:
            if req.get("status") == "Pending":
                # Random temporary password is stored as a hash, not plaintext.
                temp_password = "AJTI-" + secrets.token_hex(4).upper()
                salt, digest = self.password_hash(temp_password)
                self.data["users"].append({
                    "name": req["name"], "email": req["email"],
                    "student_id": req["student_id"], "course": req["course"],
                    "year": req.get("year", "Year 1"), "salt": salt, "password_hash": digest, "role": "student",
                    "status": "Approved"
                })
                req["status"] = "Approved"
                req["approved_at"] = datetime.now().isoformat(timespec="minutes")
                if self.save_data():
                    self.message("Student Approved",
                                 "Name: " + req["name"] + "\nStudent ID: " +
                                 req["student_id"] + "\nTemporary password: " +
                                 temp_password + "\n\nGive these details securely. "
                                 "This approval is stored on this phone only.")
                return
        self.message("No Pending Requests", "There are no requests waiting for approval.")

    def user_key(self):
        user = self.current_user or {}
        return user.get("student_id") or user.get("email") or "local-student"

    def is_bookmarked(self, subject):
        return subject in self.data.setdefault("bookmarks", {}).get(self.user_key(), [])

    def toggle_bookmark(self, subject):
        if not self.current_user:
            self.message("Sign In Required", "Sign in to save lessons to your personal list.")
            return
        all_bookmarks = self.data.setdefault("bookmarks", {})
        saved = all_bookmarks.setdefault(self.user_key(), [])
        if subject in saved:
            saved.remove(subject)
            message = "Lesson removed from your saved list."
        else:
            saved.append(subject)
            message = "Lesson saved for quick access."
        if self.save_data():
            self.message("Saved Lessons", message)
            if self.root.current == "bookmarks":
                self.root.get_screen("bookmarks").refresh()
            elif self.root.current == "lesson":
                self.root.get_screen("lesson").refresh()

    def save_lesson(self, subject, title, notes):
        subject, title, notes = subject.strip(), title.strip(), notes.strip()
        if not subject or not title or not notes:
            self.message("Missing Information", "Enter subject, lesson title and notes.")
            return
        self.data["lessons"][subject] = {
            "title": title, "notes": notes,
            "updated_at": datetime.now().isoformat(timespec="minutes"),
            "updated_by": (self.current_user or {}).get("name", "Local user")
        }
        if self.save_data():
            self.current_subject = subject
            self.message("Lesson Saved", "Lesson saved on this phone.")
            self.root.current = "teacher"

    def save_progress(self, subject):
        user = self.current_user or {}
        key = user.get("student_id") or user.get("email") or "local-student"
        progress = self.data["progress"].setdefault(key, {"completed": []})
        if subject not in progress.setdefault("completed", []):
            progress["completed"].append(subject)
        self.save_data()

    def start_quiz(self, subject):
        questions = QUIZ_BANK.get(subject)
        if not questions:
            questions = [
                {"q": "Which unit measures electric current?",
                 "options": ["Volt", "Ampere", "Ohm", "Watt"],
                 "answer": "Ampere", "why": "Current is measured in amperes."}
            ]
        self.quiz_subject = subject
        self.quiz_questions = [dict(q) for q in questions]
        self.quiz_index = 0
        self.quiz_score = 0
        self.quiz_answers = []
        self.root.current = "quiz"

    def record_quiz_result(self):
        user = self.current_user or {}
        total = len(self.quiz_questions)
        percent = round((self.quiz_score / total) * 100) if total else 0
        self.data["results"].append({
            "student_id": user.get("student_id", "GUEST"),
            "student_name": user.get("name", "Guest"),
            "subject": self.quiz_subject,
            "score": self.quiz_score, "total": total, "percent": percent,
            "date": datetime.now().isoformat(timespec="minutes"),
            "answers": self.quiz_answers
        })
        self.save_data()
        self.message("Quiz Complete",
                     "Subject: " + self.quiz_subject + "\nScore: " +
                     str(self.quiz_score) + "/" + str(total) +
                     "\nPercentage: " + str(percent) + "%")
        self.root.current = "progress" if self.current_user else "welcome"


# ---------------- WELCOME ----------------

class WelcomeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("AJTI LEARNING APP", "Learn Today. Engineer Tomorrow!", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        self.add_label("✦ WELCOME TO AJTI ✦", 25, BLUE, 58, True)
        self.add_label("Version 7.8 • Six departments • Year 1–3 learning • Colour-coded interface • Expanded subject library", 12, GREY, 30)
        self.add_label("Offline-first learning for technical and vocational students. Lessons, progress and quiz results are stored locally on this phone.", 15, DARK, 80)
        self.add_label("🎓 YEAR 1 • YEAR 2 • YEAR 3", 17, NAVY, 38, True)
        self.add_label("Choose your department to preview its year-based subjects, or register for your own year.", 13, GREY, 48)
        self.add_label("EXPLORE DEPARTMENTS", 17, NAVY, 38, True)
        for course in COURSES:
            self.add_button(course, lambda _, c=course: self.open_course(c), LIGHT_BLUE, 46)
        self.add_button("SIGN IN", lambda *_: setattr(self.manager, "current", "login"), BLUE, 52)
        self.add_button("STUDENT REGISTRATION", lambda *_: setattr(self.manager, "current", "register"), GREEN, 52)
        self.add_button("CREATE DEMO ADMIN (FIRST SETUP ONLY)", lambda *_: App.get_running_app().create_demo_admin(), NAVY)
        self.add_button("CREATE DEMO TEACHER (OPTIONAL)", lambda *_: App.get_running_app().create_demo_teacher(), GREY)
        self.add_label("Version 7.7 • Year-based learning and courses", 12, GREY, 32)

    def open_course(self, course):
        app = App.get_running_app()
        app.current_course = course
        self.manager.current = "subjects"


# ---------------- LOGIN ----------------

class LoginScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("🔐 SIGN IN", "Choose your registered year, then sign in.", **kwargs)
        self.identity = make_input("Email or student ID")
        self.password = make_input("Password", password=True)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        self.add_label("🎓 SELECT YOUR YEAR", 14, NAVY, 32, True)
        for year in STUDY_YEARS:
            chosen = app.login_year == year
            self.add_button(("✓ " if chosen else "○ ") + year,
                            lambda _, y=year: self.select_year(y),
                            GREEN if chosen else LIGHT_BLUE, 42)
        self.add_label("✉ EMAIL OR STUDENT ID", 13, NAVY, 30, True)
        self.add_input(self.identity)
        self.add_label("🔒 PASSWORD", 13, NAVY, 30, True)
        self.add_input(self.password)
        self.add_button("↪ SIGN IN", lambda *_: app.login(self.identity.text, self.password.text, app.login_year), GREEN, 52)
        self.add_button("＋ REGISTER FOR A YEAR", lambda *_: setattr(self.manager, "current", "register"), BLUE, 48)
        self.add_button("← BACK", lambda *_: setattr(self.manager, "current", "welcome"), NAVY)

    def select_year(self, year):
        App.get_running_app().login_year = year
        self.refresh()


# ---------------- REGISTRATION ----------------

class RegisterScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("📝 STUDENT REGISTRATION", "Create a registration request for your year and department.", **kwargs)
        self.name_field = make_input("Full name")
        self.email_field = make_input("Email address")
        self.id_field = make_input("Student ID")

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        for title, widget in [("👤 FULL NAME", self.name_field), ("✉ EMAIL", self.email_field), ("🪪 STUDENT ID", self.id_field)]:
            self.add_label(title, 13, NAVY, 30, True)
            self.add_input(widget)
        self.add_label("🎓 SELECT YOUR YEAR", 15, NAVY, 34, True)
        for year in STUDY_YEARS:
            chosen = app.registration_year == year
            self.add_button(("✓ " if chosen else "○ ") + year,
                            lambda _, y=year: self.select_year(y),
                            GREEN if chosen else LIGHT_BLUE, 43)
        self.add_label("🏫 SELECT DEPARTMENT", 15, NAVY, 34, True)
        for course in COURSES:
            chosen = app.registration_course == course
            self.add_button(("✓ " if chosen else "▦ ") + course,
                            lambda _, c=course: self.select_course(c),
                            GREEN if chosen else LIGHT_BLUE, 43)
        self.add_label("Selected year: " + (app.registration_year or "Not selected"), 13, BLUE, 30)
        self.add_label("Selected department: " + (app.registration_course or "Not selected"), 13, BLUE, 38)
        self.add_button("✓ SUBMIT REGISTRATION", self.submit, GREEN, 52)
        self.back("welcome")

    def select_year(self, year):
        App.get_running_app().registration_year = year
        self.refresh()

    def select_course(self, course):
        App.get_running_app().registration_course = course
        self.refresh()

    def submit(self, *_):
        app = App.get_running_app()
        app.register_student(self.name_field.text, self.email_field.text, self.id_field.text)


# ---------------- STUDENT DASHBOARD ----------------

class StudentScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("STUDENT DASHBOARD", "Your learning space.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        user = app.current_user or {}
        self.add_label("Welcome, " + user.get("name", "Student"), 21, BLUE, 52, True)
        self.add_label("🎓 Year: " + user.get("year", "Year 1"), 15, GREEN, 34, True)
        self.add_label("🏫 Department: " + user.get("course", ""), 14, DARK, 42)
        key = user.get("student_id") or user.get("email") or "local-student"
        completed = len(app.data.get("progress", {}).get(key, {}).get("completed", []))
        quiz_count = sum(1 for r in app.data.get("results", []) if r.get("student_id") == user.get("student_id"))
        self.add_label("Learning summary: " + str(completed) + " lessons completed • " + str(quiz_count) + " quizzes taken", 13, GREEN, 44)
        self.add_button("MY COURSES", lambda *_: setattr(self.manager, "current", "courses"))
        self.add_button("MY PROGRESS & RESULTS", lambda *_: setattr(self.manager, "current", "progress"), GREEN)
        self.add_button("SAVED LESSONS  ★", lambda *_: setattr(self.manager, "current", "bookmarks"), GOLD)
        self.add_button("MY PROFILE", lambda *_: setattr(self.manager, "current", "profile"), LIGHT_BLUE)
        self.add_button("SIGN OUT", lambda *_: app.logout(), RED)


# ---------------- COURSES ----------------

class CoursesScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("📚 MY COURSES", "Courses for your registered year.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        user = app.current_user or {}
        year = user.get("year", "Year 1")
        course = user.get("course", "")
        self.add_label("🎓 " + year + " CURRICULUM", 18, BLUE, 42, True)
        available = [course] if course in COURSES else list(COURSES.keys())
        for item in available:
            subjects = subjects_for_year(item, year)
            self.add_button("▦ " + item + "  •  " + str(len(subjects)) + " subjects",
                            lambda _, c=item: self.open_course(c), LIGHT_BLUE, 52)
        self.back("student")

    def open_course(self, course):
        app = App.get_running_app()
        app.current_course = course
        self.manager.current = "subjects"


# ---------------- SUBJECTS ----------------

class SubjectsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("SUBJECTS", "Choose a subject to study.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        year = (app.current_user or {}).get("year", app.login_year or "Year 1")
        self.add_label("🎓 " + year + " • " + (app.current_course or "Choose a department from Home"), 16, BLUE, 52, True)
        if app.current_course in COURSES:
            for subject in subjects_for_year(app.current_course, year):
                self.add_button("📘 " + subject, lambda _, s=subject: self.open_subject(s), LIGHT_BLUE)
        self.add_button("SEARCH ALL LESSONS", lambda *_: self.search_lessons(), GOLD)
        self.back("courses" if app.current_user and app.current_user.get("role") == "student" else "welcome")

    def open_subject(self, subject):
        app = App.get_running_app()
        app.current_subject = subject
        self.manager.current = "lesson"

    def search_lessons(self):
        app = App.get_running_app()
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        field = make_input("Type a subject or lesson title")
        box.add_widget(field)
        pop = Popup(title="Search Lessons", content=box, size_hint=(0.9, None), height=dp(180))
        def search(*_):
            term = field.text.strip().lower()
            pop.dismiss()
            matches = []
            for subject, lesson in app.data["lessons"].items():
                if term in subject.lower() or term in lesson.get("title", "").lower():
                    matches.append(subject)
            if not term:
                app.message("Search", "Enter a search word.")
            elif not matches:
                app.message("No Results", "No lesson matched that search.")
            else:
                result_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(6))
                result_popup = Popup(title="Choose a Lesson", content=result_box, size_hint=(0.92, 0.8))
                result_scroll = ScrollView(do_scroll_x=False)
                result_list = BoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None)
                result_list.bind(minimum_height=result_list.setter("height"))
                for subject_name in matches:
                    lesson_data = app.data["lessons"].get(subject_name, {})
                    label = subject_name + " — " + lesson_data.get("title", "Lesson")
                    def choose(_, selected=subject_name):
                        result_popup.dismiss()
                        app.current_subject = selected
                        self.manager.current = "lesson"
                    result_list.add_widget(make_button(label, choose, LIGHT_BLUE, 52))
                result_scroll.add_widget(result_list)
                result_box.add_widget(result_scroll)
                result_box.add_widget(make_button("CLOSE", lambda *_: result_popup.dismiss(), GREY))
                result_popup.open()
        box.add_widget(make_button("SEARCH", search, BLUE))
        pop.open()


# ---------------- LESSON VIEWER ----------------

class LessonScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("LESSON ROOM", "Read the lesson and mark it complete.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        subject = app.current_subject
        lesson = app.data["lessons"].get(subject)
        self.add_label(subject or "No subject selected", 20, BLUE, 54, True)
        if lesson:
            self.add_label(lesson.get("title", subject), 17, NAVY, 54, True)
            notes = lesson.get("notes", "")
            self.add_label(notes, 15, DARK, max(160, min(1200, len(notes) // 2 + 90)))
            self.add_label("Last updated: " + lesson.get("updated_at", "Starter lesson"), 11, GREY, 30)
        else:
            self.add_label("No lesson has been added for this subject yet.", 15, DARK, 80)
        if app.current_user and app.current_user.get("role") in ("teacher", "admin"):
            self.add_button("EDIT THIS LESSON", lambda *_: setattr(self.manager, "current", "editor"), BLUE)
        if app.current_user and app.current_user.get("role") == "student":
            saved_label = "★ REMOVE FROM SAVED LESSONS" if app.is_bookmarked(subject) else "☆ SAVE LESSON"
            self.add_button(saved_label, lambda *_: app.toggle_bookmark(subject), GOLD)
            self.add_button("MARK LESSON COMPLETE", lambda *_: self.mark_complete(), GREEN)
            self.add_button("PRACTICE QUIZ", lambda *_: app.start_quiz(subject), BLUE)
        destination = "subjects" if not app.current_user else ("courses" if app.current_user.get("role") == "student" else ("admin" if app.current_user.get("role") == "admin" else "teacher"))
        self.back(destination)

    def mark_complete(self):
        app = App.get_running_app()
        app.save_progress(app.current_subject)
        app.message("Progress Saved", "This lesson is marked complete on this device.")
        self.refresh()



# ---------------- STUDY MODES & SUBJECT GUIDE ----------------

class StudyToolsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("STUDY MODES", "Explore, revise and test your understanding.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        subject = app.current_subject or "Basic Electricity"
        guide = SUBJECT_GUIDES.get(subject)
        lesson = app.data.get("lessons", {}).get(subject, {})
        self.add_label(subject, 20, BLUE, 50, True)
        if not guide:
            self.add_label("A detailed guide for this subject is being prepared. Start with the lesson notes and quiz.", 14, GREY, 70)
            self.add_button("OPEN LESSON NOTES", lambda *_: setattr(self.manager, "current", "lesson"), GREEN)
            self.back("lesson")
            return
        self.add_label("Choose a mode", 15, NAVY, 35, True)
        self.add_button("📘 GUIDED STUDY — overview and learning objectives", lambda *_: self.show_mode("guided"), LIGHT_BLUE, 58)
        self.add_button("⚡ QUICK REVISION — key topics and reminders", lambda *_: self.show_mode("revision"), GOLD, 58)
        self.add_button("🧠 FLASHCARDS — terms and definitions", lambda *_: self.show_mode("flashcards"), LIGHT_BLUE, 58)
        self.add_button("🛠 PRACTICAL / APPLICATION TASK", lambda *_: self.show_mode("activity"), GREEN, 58)
        self.add_button("✍ PRACTICE QUIZ", lambda *_: app.start_quiz(subject), BLUE, 50)
        self.add_button("READ FULL LESSON NOTES", lambda *_: setattr(self.manager, "current", "lesson"), NAVY, 50)
        self.back("lesson")

    def show_mode(self, mode):
        app = App.get_running_app()
        subject = app.current_subject
        guide = SUBJECT_GUIDES.get(subject, {})
        if mode == "guided":
            content = "OVERVIEW\n" + guide.get("overview", "") + "\n\nLEARNING OBJECTIVES\n" + "\n".join("• " + x for x in guide.get("objectives", [])) + "\n\nTOPICS TO LEARN\n" + "\n".join("• " + x for x in guide.get("topics", []))
            app.message("Guided Study", content)
        elif mode == "revision":
            content = "QUICK REVISION — " + subject + "\n\n" + "\n".join("✓ " + x for x in guide.get("topics", [])) + "\n\nRemember: define terms, show working, include units, and explain why each answer is correct."
            app.message("Quick Revision", content)
        elif mode == "activity":
            app.message("Practical / Application Task", guide.get("activity", "Review the topic and ask your teacher for a supervised activity.") + "\n\nWrite down: aim, materials, method, observations, conclusion and safety precautions.")
        elif mode == "flashcards":
            cards = guide.get("glossary", [])
            if not cards:
                app.message("Flashcards", "No flashcards have been added for this subject yet.")
                return
            self.show_flashcard(cards, 0)

    def show_flashcard(self, cards, index):
        app = App.get_running_app()
        if index >= len(cards):
            app.message("Flashcards Complete", "You have reviewed all " + str(len(cards)) + " key terms. Try explaining each one without looking.")
            return
        item = cards[index]
        if " — " in item:
            term, definition = item.split(" — ", 1)
        else:
            term, definition = item, ""
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        box.add_widget(make_label("CARD " + str(index + 1) + " OF " + str(len(cards)), 13, BLUE, 32, True))
        box.add_widget(make_label(term, 20, NAVY, 55, True))
        box.add_widget(make_label(definition, 15, DARK, 100))
        controls = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        pop = Popup(title="Flashcard • " + App.get_running_app().current_subject, content=box, size_hint=(0.92, None), height=dp(300))
        next_btn = make_button("NEXT CARD", lambda *_: (pop.dismiss(), self.show_flashcard(cards, index + 1)), GREEN)
        close_btn = make_button("CLOSE", lambda *_: pop.dismiss(), NAVY)
        controls.add_widget(next_btn)
        controls.add_widget(close_btn)
        box.add_widget(controls)
        pop.open()



# ---------------- CUSTOM AJTI HOME SCREEN ----------------
class CustomHomeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("ASSIN JAKAI TECHNICAL INSTITUTE", "AJTI Learning App • Version 7.2", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()

        # Temporary text badge: this is NOT the official AJTI crest/logo.
        brand = AJTICard(
            orientation="horizontal", spacing=dp(12), padding=dp(14),
            size_hint_y=None, height=dp(112), fill_color=list(AJTI_SURFACE_ALT)
        )
        badge = AJTICard(
            orientation="vertical", size_hint_x=None, width=dp(78),
            padding=dp(6), spacing=dp(2), fill_color=list(AJTI_PRIMARY)
        )
        badge.add_widget(make_label("AJTI", 19, WHITE, 38, True))
        badge.add_widget(make_label("LEARN", 9, WHITE, 22, True))
        brand.add_widget(badge)
        school_text = BoxLayout(orientation="vertical", spacing=dp(2))
        school_text.add_widget(make_label("ASSIN JAKAI", 15, AJTI_TEXT, 26, True))
        school_text.add_widget(make_label("TECHNICAL INSTITUTE", 12, AJTI_TEXT, 24, True))
        school_text.add_widget(make_label("Nurture your Heart, Head and Hand.", 11, AJTI_MUTED, 34, False))
        brand.add_widget(school_text)
        self.body.add_widget(brand)
        self.add_label("WELCOME BACK", 13, GREY, 26, True)
        self.add_label("Learn Today.\nEngineer Tomorrow.", 27, BLUE, 88, True)
        self.add_label("Your technical learning space", 14, GREY, 30)

        stats = BoxLayout(size_hint_y=None, height=dp(92), spacing=dp(10))
        for heading, value in [
            ("SUBJECTS", str(len(SUBJECT_GUIDES))),
            ("SAVED", str(sum(len(v) for v in app.data.get("bookmarks", {}).values()))),
            ("MODE", "OFFLINE")
        ]:
            card = AJTICard(orientation="vertical", spacing=dp(4), padding=dp(12),
                            size_hint_x=1, fill_color=list(AJTI_SURFACE_ALT))
            card.add_widget(make_label(heading, 11, AJTI_MUTED, 20, True))
            card.add_widget(make_label(value, 19, AJTI_TEXT, 34, True))
            stats.add_widget(card)
        self.body.add_widget(stats)

        self.add_label("YOUR LEARNING SPACE", 13, GREY, 28, True)
        self.add_button("Explore subjects", lambda *_: setattr(self.manager, "current", "courses"), BLUE, 56)
        self.add_button("Study modes & flashcards", lambda *_: self.open_study(), GREEN, 56)
        self.add_button("Saved lessons", lambda *_: setattr(self.manager, "current", "bookmarks"), GOLD, 56)
        self.add_button("My profile", lambda *_: setattr(self.manager, "current", "profile"), NAVY, 56)
        self.add_label("AJTI • LEARN • PRACTISE • GROW", 11, GREY, 28)

    def open_study(self):
        app = App.get_running_app()
        if not app.current_subject:
            app.message("Choose a subject", "Open Explore subjects first, then select a subject to access its study modes.")
            self.manager.current = "courses"
        else:
            self.manager.current = "studytools"

# ---------------- PROFILE ----------------

class ProfileScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("MY PROFILE", "Your local account details.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        user = App.get_running_app().current_user or {}
        for text in [
            "Name: " + user.get("name", ""),
            "Email: " + user.get("email", ""),
            "Student ID: " + user.get("student_id", ""),
            "Year: " + user.get("year", "Year 1") + "\nDepartment: " + user.get("course", ""),
            "Role: " + user.get("role", "student").title(),
            "Status: " + user.get("status", "")
        ]:
            self.add_label(text, 14, DARK, 42)
        self.add_label("For safety, use a unique password. This local prototype has no online password recovery.", 12, GREY, 70)
        self.add_button("CHANGE PASSWORD", lambda *_: self.open_password_dialog(), GREEN)
        self.back("student")

    def open_password_dialog(self):
        app = App.get_running_app()
        box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(7))
        old = make_input("Current password", password=True)
        new = make_input("New password (at least 8 characters)", password=True)
        confirm = make_input("Confirm new password", password=True)
        box.add_widget(old)
        box.add_widget(new)
        box.add_widget(confirm)
        pop = Popup(title="Change Password", content=box, size_hint=(0.92, None), height=dp(300))
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(7))
        row.add_widget(make_button("CANCEL", lambda *_: pop.dismiss(), GREY))
        def submit(*_):
            pop.dismiss()
            app.change_password(old.text, new.text, confirm.text)
        row.add_widget(make_button("SAVE", submit, GREEN))
        box.add_widget(row)
        pop.open()


# ---------------- PROGRESS ----------------

class ProgressScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("MY PROGRESS", "Completed lessons and saved quiz results.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        user = app.current_user or {}
        key = user.get("student_id") or user.get("email") or "local-student"
        progress = app.data["progress"].get(key, {}).get("completed", [])
        self.add_label("Completed lessons: " + str(len(progress)), 17, GREEN, 42, True)
        if progress:
            for subject in progress:
                self.add_label("✓ " + subject, 14, DARK, 36)
        else:
            self.add_label("No completed lessons yet. Open a lesson and mark it complete.", 14, GREY, 60)
        self.add_label("QUIZ HISTORY", 16, NAVY, 40, True)
        results = [r for r in app.data["results"] if r.get("student_id") == user.get("student_id")]
        if results:
            for result in reversed(results[-20:]):
                self.add_label(
                    result.get("subject", "Quiz") + " — " +
                    str(result.get("score", 0)) + "/" + str(result.get("total", 0)) +
                    " (" + str(result.get("percent", 0)) + "%)\n" +
                    result.get("date", ""),
                    13, DARK, 55
                )
        else:
            self.add_label("No quiz results saved yet.", 13, GREY, 40)
        self.add_button("BACK TO DASHBOARD", lambda *_: setattr(self.manager, "current", "student"), NAVY)



# ---------------- SAVED LESSONS ----------------

class BookmarksScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("SAVED LESSONS", "Your personal quick-access study list.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        if not app.current_user:
            self.add_label("Sign in to save and view lessons.", 15, GREY, 60)
            self.back("welcome")
            return
        saved = app.data.setdefault("bookmarks", {}).get(app.user_key(), [])
        self.add_label("Saved lessons: " + str(len(saved)), 16, BLUE, 40, True)
        if not saved:
            self.add_label("Your list is empty. Open a subject and tap SAVE LESSON to add it here.", 14, GREY, 80)
        else:
            for subject in saved:
                lesson = app.data.get("lessons", {}).get(subject, {})
                title = lesson.get("title", "Lesson not added yet")
                self.add_button("★ " + subject + "\n" + title,
                                lambda _, item=subject: self.open_lesson(item), LIGHT_BLUE, 64)
                self.add_button("REMOVE: " + subject,
                                lambda _, item=subject: app.toggle_bookmark(item), GREY, 38)
        self.back("student")

    def open_lesson(self, subject):
        app = App.get_running_app()
        app.current_subject = subject
        self.manager.current = "lesson"


# ---------------- QUIZ ----------------

class QuizScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("PRACTICE QUIZ", "Choose the best answer.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        if not app.quiz_questions:
            self.add_label("No quiz is active.", 15, DARK, 50)
            self.back("student")
            return
        q = app.quiz_questions[app.quiz_index]
        self.add_label("Subject: " + app.quiz_subject, 13, BLUE, 35)
        self.add_label("Question " + str(app.quiz_index + 1) + " of " + str(len(app.quiz_questions)), 13, GREY, 32)
        self.add_label(q["q"], 18, NAVY, 90, True)
        for option in q["options"]:
            self.add_button(option, lambda _, choice=option: self.answer(choice), LIGHT_BLUE, 48)

    def answer(self, choice):
        app = App.get_running_app()
        q = app.quiz_questions[app.quiz_index]
        correct = choice == q["answer"]
        if correct:
            app.quiz_score += 1
        app.quiz_answers.append({
            "question": q["q"], "chosen": choice,
            "correct_answer": q["answer"], "correct": correct
        })
        explanation = ("Correct! " if correct else "Not quite. Correct answer: " + q["answer"] + ". ") + q.get("why", "")
        if app.quiz_index + 1 < len(app.quiz_questions):
            app.quiz_index += 1
            app.message("Answer Feedback", explanation)
            self.refresh()
        else:
            app.message("Final Answer", explanation)
            app.record_quiz_result()


# ---------------- TEACHER DASHBOARD ----------------

class TeacherScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("TEACHER DASHBOARD", "Manage lessons and local registration.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        user = app.current_user or {}
        self.add_label("Welcome, " + user.get("name", "Teacher"), 20, BLUE, 50, True)
        self.add_button("ADD OR EDIT LESSON", lambda *_: setattr(self.manager, "current", "editor"), GREEN)
        self.add_button("VIEW REGISTRATION REQUESTS", lambda *_: self.view_requests(), BLUE)
        self.add_button("VIEW QUIZ RESULTS", lambda *_: setattr(self.manager, "current", "results"), GOLD)
        self.add_button("SIGN OUT", lambda *_: app.logout(), RED)

    def view_requests(self):
        app = App.get_running_app()
        requests = app.data.get("requests", [])
        if not requests:
            app.message("Registration Requests", "No requests have been received on this device.")
            return
        lines = []
        for req in requests[-20:]:
            lines.append(req.get("name", "") + " | " + req.get("student_id", "") +
                         "\n" + req.get("email", "") + "\n" +
                         req.get("course", "") + " — " + req.get("status", "Pending"))
        app.message("Recent Requests", "\n\n".join(lines))


# ---------------- LESSON EDITOR ----------------

class TeacherEditorScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("LESSON EDITOR", "Create or update learning materials.", **kwargs)
        self.subject_field = make_input("Subject name")
        self.title_field = make_input("Lesson title")
        self.notes_field = make_input("Write lesson notes here", multiline=True, height=250)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        if app.current_subject and not self.subject_field.text:
            self.subject_field.text = app.current_subject
        lesson = app.data["lessons"].get(self.subject_field.text.strip())
        if lesson and not self.title_field.text:
            self.title_field.text = lesson.get("title", "")
            self.notes_field.text = lesson.get("notes", "")
        self.add_label("SUBJECT", 13, NAVY, 30, True)
        self.add_input(self.subject_field)
        self.add_label("LESSON TITLE", 13, NAVY, 30, True)
        self.add_input(self.title_field)
        self.add_label("LESSON NOTES", 13, NAVY, 30, True)
        self.add_input(self.notes_field)
        self.add_button("SAVE LESSON", lambda *_: app.save_lesson(self.subject_field.text, self.title_field.text, self.notes_field.text), GREEN, 52)
        self.back("teacher")


# ---------------- ADMIN DASHBOARD ----------------

class AdminScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("ADMIN DASHBOARD", "Local device administration.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        users = app.data.get("users", [])
        requests = app.data.get("requests", [])
        pending = sum(1 for r in requests if r.get("status") == "Pending")
        self.add_label("AJTI ADMINISTRATION", 20, BLUE, 48, True)
        self.add_label("Registered accounts: " + str(len(users)), 14, DARK, 38)
        self.add_label("Registration requests: " + str(len(requests)), 14, DARK, 38)
        self.add_label("Pending requests: " + str(pending), 14, GREEN, 38)
        self.add_button("APPROVE NEXT STUDENT", lambda *_: app.approve_next_request(), GREEN, 52)
        self.add_button("VIEW QUIZ RESULTS", lambda *_: setattr(self.manager, "current", "results"), GOLD)
        self.add_button("SIGN OUT", lambda *_: app.logout(), RED)


# ---------------- RESULTS VIEW ----------------

class ResultsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__("QUIZ RESULTS", "Results stored on this device.", **kwargs)

    def refresh(self):
        self.body.clear_widgets()
        app = App.get_running_app()
        if not app.current_user or app.current_user.get("role") not in ("teacher", "admin"):
            self.add_label("Teacher/admin access required.", 14, RED, 50)
            self.back("welcome")
            return
        results = app.data.get("results", [])
        if not results:
            self.add_label("No quiz results yet.", 14, GREY, 50)
        else:
            for r in reversed(results[-100:]):
                self.add_label(
                    r.get("student_name", "Student") + " (" + r.get("student_id", "") + ")\n" +
                    r.get("subject", "Quiz") + ": " + str(r.get("score", 0)) + "/" +
                    str(r.get("total", 0)) + " — " + str(r.get("percent", 0)) + "%\n" +
                    r.get("date", ""),
                    13, DARK, 68
                )
        destination = "admin" if app.current_user.get("role") == "admin" else "teacher"
        self.back(destination)


# ---------------- RUN ----------------

if __name__ == "__main__":
    AJTIApp().run()
