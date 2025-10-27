# -*- coding: utf-8 -*-
"""
Full-Stack COCOMO Estimation Tool (Python Flask Web Application)

This single file contains the complete Flask server, COCOMO calculation logic,
and the HTML/CSS/JavaScript required for the interactive frontend.

To run this:
1. Ensure you have Python installed.
2. Install Flask: pip install Flask
3. Save this code as 'app.py'.
4. Run: python app.py
5. Open your web browser to http://127.0.0.1:5000/
"""
from flask import Flask, request, render_template_string
import math

# --- 1. COCOMO CONSTANTS AND CORE LOGIC ---

# [a, b, c, d] for E = a * (KLOC)^b and D = c * (E)^d
COCOMO_PARAMS = {
    'organic': [2.4, 1.05, 2.5, 0.38],
    'semidetached': [3.0, 1.12, 2.5, 0.35],
    'embedded': [3.6, 1.20, 2.5, 0.32],
}

# Effort Multipliers (Cost Drivers) Data
COST_DRIVERS_DATA = {
    'RELY': {'name': 'Required Software Reliability', 'levels': {'VL': 0.75, 'L': 0.88, 'N': 1.00, 'H': 1.15, 'VH': 1.40}, 'default': 1.00},
    'DATA': {'name': 'Database Size/Program Size', 'levels': {'L': 0.94, 'N': 1.00, 'H': 1.08, 'VH': 1.16}, 'default': 1.00},
    'CPLX': {'name': 'Product Complexity', 'levels': {'VL': 0.70, 'L': 0.85, 'N': 1.00, 'H': 1.15, 'VH': 1.30, 'EH': 1.65}, 'default': 1.00},
    'TOOL': {'name': 'Use of Software Tools', 'levels': {'VL': 1.24, 'L': 1.10, 'N': 1.00, 'H': 0.91, 'VH': 0.82}, 'default': 1.00},
    'VIRT': {'name': 'Virtual Machine Volatility', 'levels': {'L': 0.87, 'N': 1.00, 'H': 1.15, 'VH': 1.30}, 'default': 1.00},
}

def calculate_cocomo(kloc, mode, drivers, salary):
    """Performs the full COCOMO Intermediate Model calculation in Python (Backend)."""
    
    # --- 1. Calculate Effort Adjustment Factor (EAF) ---
    eaf = 1.0
    for value in drivers.values():
        eaf *= float(value)
        
    # Get COCOMO parameters
    try:
        a, b_exp, c, d_exp = COCOMO_PARAMS[mode]
    except KeyError:
        return None, "Invalid project mode selected."

    # --- 2. Calculate Estimated Effort (E) in Person-Months (PM) ---
    # E = a * (KLOC)^b * EAF
    effort_pm = a * (float(kloc) ** b_exp) * eaf

    # --- 3. Development Time (D) in Months ---
    # D = c * (E)^d
    duration_months = c * (effort_pm ** d_exp)

    # --- 4. Average Staffing (P) in People ---
    # P = E / D
    avg_people = effort_pm / duration_months
    
    # --- 5. Total Cost (C) ---
    # C = Effort * Salary
    total_cost = effort_pm * float(salary)

    return {
        'effort_pm': round(effort_pm, 2),
        'duration_months': round(duration_months, 2),
        'avg_people': round(avg_people, 2),
        'total_cost': round(total_cost, 0),
        'eaf': round(eaf, 3),
        'kloc': float(kloc),
        'mode': mode.capitalize()
    }, None

# --- 2. FLASK APP SETUP AND ROUTING ---

app = Flask(__name__)

# Main route handling both form display (GET) and calculation (POST)
@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    error = None

    if request.method == 'POST':
        try:
            # Gather inputs from the web form
            kloc = float(request.form.get('kloc'))
            salary = float(request.form.get('salary'))
            mode = request.form.get('mode')
            
            # Gather cost driver inputs
            drivers = {}
            for key in COST_DRIVERS_DATA:
                drivers[key] = request.form.get(key)
                
            # Perform calculation in the Python backend
            if kloc <= 0 or salary <= 0:
                error = "KLOC and Salary must be positive numbers."
            else:
                results, error = calculate_cocomo(kloc, mode, drivers, salary)

        except (ValueError, TypeError):
            error = "Please ensure all numerical fields are filled correctly."
        except Exception as e:
            error = f"A server error occurred: {e}"

    # Render the HTML template, passing results and constants
    return render_template_string(HTML_TEMPLATE, 
                                  cost_drivers_data=COST_DRIVERS_DATA,
                                  results=results,
                                  error=error)

# --- 3. HTML TEMPLATE (Frontend) ---

# This multi-line string holds the entire, responsive HTML frontend.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COCOMO Web Estimation Tool</title>
    <!-- Tailwind CSS CDN for modern styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root {
            --primary-color: #059669; /* Emerald Green */
            --secondary-color: #f59e0b;
        }
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f0fdfa; /* Lightest Emerald */
        }
        .mode-radio:checked + label {
            border-color: var(--primary-color);
            background-color: #d1fae5; /* Light Green */
            font-weight: 700;
        }
        .result-card {
            border-left: 6px solid var(--primary-color);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .chart-bar {
            background-color: var(--primary-color);
            height: 1.25rem;
            border-radius: 0.25rem;
            transition: width 1s ease-out;
        }
        .form-input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
            transition: border-color 0.2s;
        }
        .form-input:focus {
            border-color: var(--primary-color);
            outline: none;
            box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.2);
        }
    </style>
</head>
<body class="p-4 md:p-8">

    <div class="w-full max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">

        <!-- Input Form (Left/Center Column) -->
        <div class="lg:col-span-2 bg-white p-6 md:p-10 rounded-2xl shadow-2xl border border-gray-100 h-fit">
            <h1 class="text-3xl font-extrabold text-gray-900 mb-2">COCOMO Software Estimation</h1>
            <p class="text-sm text-gray-500 mb-6 border-b pb-4">Intermediate COCOMO '81 Model using Python (Flask) Backend</p>

            <form method="POST" action="/" class="space-y-8">

                <!-- Primary Inputs -->
                <div class="grid md:grid-cols-2 gap-6">
                    <div>
                        <label for="kloc" class="block mb-2 text-sm font-medium text-gray-700">Project Size (KLOC)</label>
                        <input type="number" step="0.1" id="kloc" name="kloc" value="{{ request.form.kloc if request.form.kloc else '10' }}" 
                               class="form-input" required min="0.1">
                        <p class="text-xs text-gray-400 mt-1">Kilo Lines of Code (thousands).</p>
                    </div>
                    <div>
                        <label for="salary" class="block mb-2 text-sm font-medium text-gray-700">Avg. Monthly Salary (USD)</label>
                        <input type="number" id="salary" name="salary" value="{{ request.form.salary if request.form.salary else '8000' }}" 
                               class="form-input" required min="1000" step="100">
                        <p class="text-xs text-gray-400 mt-1">Cost for 1 Person-Month.</p>
                    </div>
                </div>

                <!-- Project Mode Selection -->
                <div>
                    <h2 class="text-xl font-semibold text-gray-800 mb-4 pt-4 border-t">Project Mode</h2>
                    <div class="grid md:grid-cols-3 gap-4">
                        {% for mode in ['organic', 'semidetached', 'embedded'] %}
                        <div>
                            <input id="mode-{{ mode }}" type="radio" name="mode" value="{{ mode }}" class="hidden mode-radio" 
                                   {% if request.form.mode == mode or not request.form.mode and loop.first %}checked{% endif %}>
                            <label for="mode-{{ mode }}" class="flex items-center justify-center p-4 cursor-pointer border-2 border-gray-200 rounded-lg text-center transition duration-150 shadow-md hover:border-primary-color/50">
                                <span class="text-base text-gray-800">{{ mode.capitalize() }}</span>
                            </label>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <!-- Effort Multipliers (Cost Drivers) -->
                <div>
                    <h2 class="text-xl font-semibold text-gray-800 mb-4 pt-4 border-t">Effort Multipliers (Cost Drivers)</h2>
                    <p class="text-sm text-gray-500 mb-6">These factors adjust the base effort based on project constraints and skills.</p>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        {% for key, driver in cost_drivers_data.items() %}
                        <div>
                            <label for="{{ key }}" class="block mb-2 text-sm font-medium text-gray-700">{{ driver.name }} ({{ key }})</label>
                            <select id="{{ key }}" name="{{ key }}" class="form-input bg-white">
                                {% for level, value in driver.levels.items() %}
                                <option value="{{ value }}" 
                                    {% if request.form[key] == value|string or (not request.form and value == driver.default) %}selected{% endif %}>
                                    {{ level }} ({{ value }})
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div class="pt-4 border-t">
                    <button type="submit" class="w-full py-3 px-4 bg-primary-color text-white font-bold rounded-lg shadow-lg hover:bg-primary-color/90 transition duration-150 ease-in-out transform hover:scale-[1.01]">
                        Calculate COCOMO Estimate
                    </button>
                </div>
            </form>
        </div>

        <!-- Output and Chart Card (Right Column) -->
        <div class="lg:col-span-1">
            <div class="bg-white p-6 md:p-8 rounded-2xl shadow-2xl border border-gray-100 h-full sticky top-8">
                <h2 class="text-2xl font-extrabold text-primary-color mb-4 border-b pb-2">Calculation Results</h2>
                
                <!-- Error Display -->
                {% if error %}
                    <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50" role="alert">
                        {{ error }}
                    </div>
                {% endif %}

                {% if results %}
                <div id="results-display" class="space-y-4 mb-8">
                    <!-- Effort -->
                    <div class="result-card p-4 bg-primary-color/5 rounded-lg shadow-md" style="--primary-color: #059669;">
                        <p class="text-sm text-primary-color font-medium">Estimated Effort</p>
                        <p class="text-3xl font-bold text-gray-900">{{ "{:,.2f}".format(results.effort_pm) }} PM</p>
                        <p class="text-sm text-gray-500 italic">Person-Months</p>
                    </div>
                    <!-- Duration -->
                    <div class="result-card p-4 bg-blue-50 rounded-lg shadow-md" style="--primary-color: #3b82f6;">
                        <p class="text-sm text-blue-600 font-medium">Development Time</p>
                        <p class="text-3xl font-bold text-gray-900">{{ "{:,.2f}".format(results.duration_months) }} Months</p>
                        <p class="text-sm text-gray-500 italic">Time to completion</p>
                    </div>
                    <!-- Cost -->
                    <div class="result-card p-4 bg-yellow-50 rounded-lg shadow-md" style="--primary-color: #f59e0b;">
                        <p class="text-sm text-secondary-color font-medium">Total Cost</p>
                        <p class="text-3xl font-bold text-gray-900">${{ "{:,.0f}".format(results.total_cost) }}</p>
                        <p class="text-sm text-gray-500 italic">Estimated Budget</p>
                    </div>
                </div>

                <!-- Summary -->
                <p class="text-lg font-semibold text-gray-700 mt-6 pt-4 border-t">Summary</p>
                <p class="text-sm text-gray-600">
                    Your **{{ results.mode }}** project ({{ "{:,.0f}".format(results.kloc) }} KLOC) requires an average staffing of 
                    <span class="font-bold text-primary-color">{{ "{:,.2f}".format(results.avg_people) }} people</span> 
                    to complete the work in <span class="font-bold text-primary-color">{{ "{:,.2f}".format(results.duration_months) }} months.</span>
                </p>
                <p class="text-xs text-gray-500 mt-2">
                    Effort Adjustment Factor (EAF): <span class="font-semibold">{{ results.eaf }}</span>
                </p>

                <!-- Visualization/Chart (Simple Text-based for Flask) -->
                <div class="mt-6 pt-4 border-t">
                    <h3 class="text-base font-semibold text-gray-700 mb-2">Effort vs. Time Ratio</h3>
                    <div class="w-full bg-gray-200 rounded-lg overflow-hidden">
                        {% set total = results.effort_pm + results.duration_months %}
                        {% set effort_width = (results.effort_pm / total) * 100 %}
                        {% set duration_width = (results.duration_months / total) * 100 %}
                        
                        <div class="flex h-6 text-xs font-medium">
                            <div style="width:{{ effort_width }}%;" class="bg-primary-color text-white text-center p-1">
                                {{ "{:,.0f}".format(results.effort_pm) }} PM
                            </div>
                            <div style="width:{{ duration_width }}%;" class="bg-blue-500 text-white text-center p-1">
                                {{ "{:,.0f}".format(results.duration_months) }} M
                            </div>
                        </div>
                    </div>
                </div>
                {% endif %}

            </div>
        </div>
    </div>

</body>
</html>
"""

# --- 4. RUN SERVER ---

if __name__ == '__main__':
    # Setting debug=True allows for automatic code reloading during development.
    # It should be set to False in a production environment.
    app.run(debug=True)

