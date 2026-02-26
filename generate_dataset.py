#!/usr/bin/env python3
"""
Code Smell Detection Dataset Generator

Generates 400-500 structured prompts for code smell detection research,
following methodology from arXiv:2503.10666.
"""

import json
import csv
import random
from typing import List, Dict
from datetime import datetime

# High-token action keywords
ACTION_KEYWORDS = [
    "Analyze", "Recommend", "Write", "Measure", "Report",
    "List", "Compare", "Evaluate", "Implement", "Design"
]

# Domain contexts for diversity
DOMAINS = [
    "E-commerce",
    "Finance",
    "Healthcare",
    "Scientific Computing",
    "General Software"
]

# Prompt types (generation only as specified)
PROMPT_TYPES = ["generation"]

# Complexity levels
COMPLEXITY_LEVELS = ["basic", "intermediate", "advanced"]


def create_code_smell_definitions():
    """Define all 25 code smell categories with metadata."""
    return {
        "long_method": {
            "name": "Long Method",
            "description": "Methods that are too long and do too many things",
            "target_count": 20
        },
        "long_parameter_list": {
            "name": "Long Parameter List",
            "description": "Functions with too many parameters",
            "target_count": 20
        },
        "god_class": {
            "name": "God Class / Large Class",
            "description": "Classes that do too much and have too many responsibilities",
            "target_count": 20
        },
        "feature_envy": {
            "name": "Feature Envy",
            "description": "Methods that use other classes' data more than their own",
            "target_count": 18
        },
        "data_clumps": {
            "name": "Data Clumps",
            "description": "Groups of data that appear together frequently",
            "target_count": 18
        },
        "duplicated_code": {
            "name": "Duplicated Code",
            "description": "Similar code appearing in multiple places",
            "target_count": 20
        },
        "dead_code": {
            "name": "Dead Code",
            "description": "Code that is never executed",
            "target_count": 16
        },
        "speculative_generality": {
            "name": "Speculative Generality",
            "description": "Overly generic code written for hypothetical future needs",
            "target_count": 16
        },
        "primitive_obsession": {
            "name": "Primitive Obsession",
            "description": "Overuse of primitives instead of small objects",
            "target_count": 18
        },
        "switch_statements": {
            "name": "Switch Statements",
            "description": "Complex switch/if-else chains that should be polymorphism",
            "target_count": 18
        },
        "parallel_inheritance": {
            "name": "Parallel Inheritance Hierarchies",
            "description": "Hierarchies that must change together",
            "target_count": 16
        },
        "lazy_class": {
            "name": "Lazy Class",
            "description": "Classes that don't do enough to justify their existence",
            "target_count": 16
        },
        "temporary_field": {
            "name": "Temporary Field",
            "description": "Fields only used in certain circumstances",
            "target_count": 16
        },
        "message_chains": {
            "name": "Message Chains",
            "description": "Long chains of method calls (a.b().c().d())",
            "target_count": 16
        },
        "middle_man": {
            "name": "Middle Man",
            "description": "Classes that only delegate to other classes",
            "target_count": 16
        },
        "inappropriate_intimacy": {
            "name": "Inappropriate Intimacy",
            "description": "Classes that are too tightly coupled",
            "target_count": 18
        },
        "alternative_classes_different_interfaces": {
            "name": "Alternative Classes with Different Interfaces",
            "description": "Similar classes with different method signatures",
            "target_count": 16
        },
        "incomplete_library_class": {
            "name": "Incomplete Library Class",
            "description": "Library classes missing needed functionality",
            "target_count": 14
        },
        "data_class": {
            "name": "Data Class",
            "description": "Classes with only fields and getters/setters",
            "target_count": 16
        },
        "refused_bequest": {
            "name": "Refused Bequest",
            "description": "Subclasses that don't use inherited members",
            "target_count": 16
        },
        "comments_smell": {
            "name": "Comments (as smell indicator)",
            "description": "Excessive comments compensating for unclear code",
            "target_count": 14
        },
        "magic_numbers": {
            "name": "Magic Numbers/Strings",
            "description": "Unexplained literal values in code",
            "target_count": 18
        },
        "deep_nesting": {
            "name": "Deep Nesting",
            "description": "Excessive levels of nested conditionals or loops",
            "target_count": 18
        },
        "global_state": {
            "name": "Global State",
            "description": "Overuse of global variables",
            "target_count": 16
        },
        "shotgun_surgery": {
            "name": "Shotgun Surgery",
            "description": "Changes requiring modifications in many places",
            "target_count": 16
        }
    }


def generate_prompts_for_smell(smell_key: str, smell_info: Dict) -> List[Dict]:
    """Generate all prompts for a specific code smell."""
    prompts = []
    target = smell_info["target_count"]

    # Distribute across complexity levels
    basic_count = target // 3 + (1 if target % 3 > 0 else 0)
    intermediate_count = target // 3 + (1 if target % 3 > 1 else 0)
    advanced_count = target - basic_count - intermediate_count

    # Generate prompts using category-specific templates
    templates = get_templates_for_smell(smell_key)

    prompt_idx = 0
    for complexity, count in [("basic", basic_count), ("intermediate", intermediate_count), ("advanced", advanced_count)]:
        for i in range(count):
            domain = DOMAINS[prompt_idx % len(DOMAINS)]
            keywords = select_action_keywords(complexity)
            template = templates[complexity][i % len(templates[complexity])]

            prompt_text = template.format(
                domain=domain,
                domain_lower=domain.lower().replace(" ", "_"),
                keywords=", ".join(keywords)
            )

            prompt = {
                "id": f"{smell_key}_{complexity}_{i+1:03d}",
                "prompt": prompt_text,
                "code_smells": [smell_info["name"]],
                "complexity": complexity,
                "action_keywords": keywords,
                "domain": domain,
                "prompt_type": "generation",
                "expected_token_depth": get_token_depth(complexity),
                "synthetic": False
            }
            prompts.append(prompt)
            prompt_idx += 1

    return prompts


def select_action_keywords(complexity: str) -> List[str]:
    """Select appropriate action keywords based on complexity."""
    if complexity == "basic":
        return random.sample(ACTION_KEYWORDS, 1)
    elif complexity == "intermediate":
        return random.sample(ACTION_KEYWORDS, 2)
    else:
        return random.sample(ACTION_KEYWORDS, 3)


def get_token_depth(complexity: str) -> str:
    """Map complexity to expected token depth."""
    return {"basic": "low", "intermediate": "medium", "advanced": "high"}[complexity]


def get_templates_for_smell(smell_key: str) -> Dict[str, List[str]]:
    """Return prompt templates for each code smell category."""

    templates = {
        "long_method": {
            "basic": [
                "Write a Python function to process customer orders that validates input, calculates totals, applies discounts, updates inventory, generates invoice, sends confirmation email, and logs the transaction.",
                "Write a Python function for user registration that validates email format, checks password strength, verifies username availability, creates user record, sends welcome email, initializes user preferences, and logs registration event.",
                "Write a Python function to handle file uploads that validates file type, checks file size, scans for viruses, generates unique filename, stores file, creates database record, and sends notification.",
                "Write a Python function for report generation that queries database, filters records, performs calculations, formats data, generates charts, compiles PDF, and emails to recipients.",
                "Write a Python function to process payment that validates card details, checks account balance, applies fees, processes transaction, updates ledger, generates receipt, and sends confirmation.",
                "Write a Python function for inventory management that checks stock levels, calculates reorder points, generates purchase orders, updates supplier records, logs changes, and sends alerts.",
                "Write a Python function to handle customer complaints that validates ticket, categorizes issue, assigns priority, routes to agent, sends acknowledgment, logs interaction, and updates CRM."
            ],
            "intermediate": [
                "Write a comprehensive data ETL pipeline function that reads from multiple CSV sources, cleans and normalizes data, performs aggregations, handles missing values, validates against schema, transforms for target format, and exports to database.",
                "Write a Python function for e-commerce checkout that handles cart validation, inventory reservation, shipping calculation, tax computation, payment processing, order creation, email notification, and analytics tracking.",
                "Write a Python function for loan application processing that validates applicant info, pulls credit reports, calculates risk scores, determines rates, generates documents, submits for approval, and notifies applicant.",
                "Write a Python function for clinical trial data processing that validates patient records, checks eligibility, randomizes assignments, tracks adverse events, generates safety reports, and submits to regulatory database.",
                "Write a Python function for scientific experiment logging that captures sensor readings, validates data ranges, applies calibration, stores measurements, generates visualizations, and exports to research database.",
                "Write a Python function for multi-tenant user provisioning that validates organization, creates accounts, assigns roles, configures permissions, initializes workspaces, sends invitations, and logs audit trail."
            ],
            "advanced": [
                "Design and implement a complete patient record processing system as a single function that handles admission, diagnosis coding, treatment planning, insurance verification, billing calculation, appointment scheduling, prescription management, and discharge documentation.",
                "Write a comprehensive financial portfolio rebalancing function that analyzes current holdings, calculates target allocations, identifies trades needed, checks tax implications, validates against compliance rules, executes orders, updates records, and generates reports.",
                "Write an end-to-end machine learning pipeline function that loads data, performs feature engineering, trains multiple models, evaluates performance, selects best model, deploys to production, monitors predictions, and retrains on drift.",
                "Write a comprehensive supply chain optimization function that forecasts demand, optimizes inventory levels, plans production schedules, coordinates logistics, manages supplier relationships, tracks shipments, and generates performance dashboards.",
                "Write a complete healthcare claims adjudication function that validates claim format, verifies member eligibility, checks provider credentials, applies coverage rules, calculates payments, handles appeals, generates EOBs, and updates financial records.",
                "Write a comprehensive trading system function that receives market data, calculates indicators, generates signals, manages risk, executes orders, handles partial fills, reconciles positions, and produces compliance reports."
            ]
        },

        "long_parameter_list": {
            "basic": [
                "Write a Python function create_user(username, email, password, first_name, last_name, phone, address, city, state, zip_code, country, birth_date, gender) that creates a new user account.",
                "Write a Python function send_email(recipient, sender, subject, body, cc, bcc, reply_to, priority, attachments, tracking_id, template_id) that sends formatted emails.",
                "Write a Python function calculate_shipping(weight, length, width, height, origin_zip, dest_zip, carrier, service_type, insurance, signature_required, hazmat) that computes shipping cost.",
                "Write a Python function create_invoice(customer_id, items, tax_rate, discount_code, payment_terms, due_date, currency, notes, template, recurring, auto_send) that generates invoices.",
                "Write a Python function search_products(query, category, min_price, max_price, brand, color, size, rating, in_stock, sort_by, page, per_page) that searches product catalog.",
                "Write a Python function create_appointment(patient_id, provider_id, date, time, duration, type, location, notes, reminder, insurance_id, copay) that schedules appointments.",
                "Write a Python function generate_report(report_type, start_date, end_date, filters, grouping, metrics, format, recipients, schedule, timezone, include_charts) that creates reports."
            ],
            "intermediate": [
                "Write a Python function configure_server(hostname, port, ssl_enabled, ssl_cert, ssl_key, max_connections, timeout, buffer_size, log_level, log_path, cache_enabled, cache_size, cache_ttl, auth_required, auth_provider) that sets up server configuration.",
                "Write a Python function process_transaction(transaction_id, account_from, account_to, amount, currency, exchange_rate, fee_type, fee_amount, description, category, tags, recurring, schedule, notify_sender, notify_recipient, compliance_check) that handles financial transactions.",
                "Write a Python function create_clinical_study(study_name, protocol_id, sponsor, investigators, sites, start_date, end_date, enrollment_target, inclusion_criteria, exclusion_criteria, endpoints, randomization, blinding, data_management, monitoring_plan, regulatory_status) that initializes a clinical trial.",
                "Write a Python function configure_analysis(data_source, variables, transformations, filters, aggregations, statistical_tests, confidence_level, corrections, output_format, visualizations, export_path, validation_rules, missing_data_handling, outlier_treatment) that sets up statistical analysis.",
                "Write a Python function deploy_application(app_name, version, environment, region, instance_type, instance_count, auto_scaling, min_instances, max_instances, health_check_path, health_check_interval, load_balancer, ssl_termination, env_variables, secrets, rollback_enabled) that deploys applications."
            ],
            "advanced": [
                "Write a Python function create_marketing_campaign(campaign_name, campaign_type, start_date, end_date, budget, daily_limit, target_audience, demographics, interests, behaviors, locations, devices, platforms, ad_formats, creatives, landing_pages, conversion_goals, tracking_pixels, attribution_model, optimization_goal, bid_strategy, frequency_cap, dayparting, exclusions, compliance_flags) that creates comprehensive ad campaigns.",
                "Write a Python function configure_data_pipeline(pipeline_name, source_type, source_config, destination_type, destination_config, schema_mapping, transformations, validations, error_handling, retry_policy, batch_size, parallelism, scheduling, monitoring_enabled, alert_thresholds, alert_recipients, logging_level, audit_enabled, encryption_enabled, compression, partitioning, deduplication) that sets up ETL workflows.",
                "Write a Python function initialize_experiment(experiment_id, hypothesis, methodology, variables_independent, variables_dependent, variables_controlled, sample_size, power_analysis, randomization_method, blinding_type, data_collection_instruments, measurement_protocols, analysis_plan, stopping_rules, safety_monitoring, data_quality_checks, consent_process, ethics_approval, funding_source, collaboration_agreements, publication_plan) that initializes scientific experiments.",
                "Write a Python function create_insurance_policy(policy_type, policyholder_info, coverage_limits, deductibles, premium_amount, payment_frequency, effective_date, expiration_date, beneficiaries, riders, exclusions, conditions, underwriting_class, risk_factors, territory, agency, agent, commission_rate, reinsurance_treaty, regulatory_filing, document_templates, delivery_method, renewal_terms, cancellation_terms) that creates insurance policies.",
                "Write a Python function setup_trading_strategy(strategy_name, asset_class, instruments, data_feeds, timeframes, indicators, entry_conditions, exit_conditions, position_sizing, risk_per_trade, max_drawdown, correlation_limits, execution_algo, slippage_model, commission_model, margin_requirements, leverage_limits, hedging_rules, rebalancing_frequency, performance_metrics, backtesting_period, walk_forward_windows, optimization_method, paper_trading_period) that configures algorithmic trading."
            ]
        },

        "god_class": {
            "basic": [
                "Write a UserManager class that handles user registration, authentication, profile management, password reset, email verification, session handling, and activity logging.",
                "Write an OrderProcessor class that manages order creation, validation, pricing, inventory updates, payment processing, shipping coordination, and notification sending.",
                "Write a ProductCatalog class that handles product creation, categorization, pricing, inventory tracking, search functionality, recommendation engine, and analytics.",
                "Write a ReportGenerator class that creates financial reports, sales analytics, inventory summaries, customer insights, performance dashboards, and export functionality.",
                "Write a NotificationService class that handles email sending, SMS messaging, push notifications, in-app alerts, scheduled reminders, and delivery tracking.",
                "Write a FileManager class that handles file uploads, storage, retrieval, versioning, sharing, permissions, compression, and cleanup scheduling.",
                "Write a CustomerService class that manages tickets, chat support, email responses, knowledge base, satisfaction surveys, and escalation workflows."
            ],
            "intermediate": [
                "Implement an ApplicationController class that manages database connections, HTTP routing, request validation, business logic execution, template rendering, caching, error handling, API responses, and logging.",
                "Write a FinancialSystem class that handles accounts, transactions, reconciliation, reporting, tax calculations, audit trails, compliance checks, currency conversion, and statement generation.",
                "Write a HospitalManagement class that manages patients, appointments, medical records, billing, pharmacy, laboratory, staff scheduling, bed allocation, and emergency protocols.",
                "Write a ResearchPlatform class that handles experiment design, data collection, analysis pipelines, visualization, collaboration, publication workflow, data archival, and reproducibility tracking.",
                "Write a ContentManagement class that handles articles, media assets, workflows, publishing, versioning, localization, SEO optimization, analytics, and content recommendations."
            ],
            "advanced": [
                "Write a comprehensive ECommerceEngine class that controls product catalog, inventory management, shopping cart operations, checkout processing, payment handling, shipping logistics, customer service tickets, analytics tracking, and report generation.",
                "Write an EnterpriseResourcePlanning class that manages procurement, inventory, manufacturing, sales, finance, HR, project management, business intelligence, compliance, and integration with external systems.",
                "Write a HealthcareInformationSystem class that handles patient registration, clinical documentation, order management, pharmacy, laboratory, radiology, billing, insurance claims, quality metrics, and regulatory reporting.",
                "Write a TradingPlatform class that manages market data, order routing, execution, risk management, portfolio tracking, reporting, compliance monitoring, client management, fee calculation, and reconciliation.",
                "Write a ScientificWorkbench class that handles experiment configuration, data acquisition, signal processing, statistical analysis, machine learning, visualization, collaboration, publication, data management, and reproducibility.",
                "Write a SmartCityPlatform class that manages traffic systems, energy grid, water management, waste collection, emergency services, public transit, citizen services, environmental monitoring, and urban planning analytics."
            ]
        },

        "feature_envy": {
            "basic": [
                "Write a Python class OrderPrinter that has a method print_order_details which accesses customer.name, customer.email, customer.address, customer.phone to format a shipping label.",
                "Write a Python class ReportBuilder that has a method build_employee_report which heavily uses employee.salary, employee.department, employee.manager, employee.start_date, employee.reviews.",
                "Write a Python class InvoiceCalculator that has a method calculate_total which uses order.items, order.discount, order.tax_rate, order.shipping, order.customer.membership_level.",
                "Write a Python class NotificationFormatter that has a method format_user_notification accessing user.preferences, user.timezone, user.language, user.notification_settings.",
                "Write a Python class PaymentValidator that has a method validate_payment using card.number, card.expiry, card.cvv, card.holder_name, card.billing_address.",
                "Write a Python class ShippingCalculator that has a method calculate_rate using package.weight, package.dimensions, package.origin, package.destination, package.fragile."
            ],
            "intermediate": [
                "Write a Python class AnalyticsProcessor with a method generate_user_analytics that extensively uses user.orders, user.sessions, user.clicks, user.purchases, user.preferences, user.demographics to compute engagement scores.",
                "Write a Python class BillingManager with a method process_subscription_billing that heavily accesses subscription.plan, subscription.customer, subscription.payment_method, subscription.usage, subscription.discounts, subscription.billing_cycle.",
                "Write a Python class PatientReporter with a method generate_patient_summary that uses patient.demographics, patient.conditions, patient.medications, patient.allergies, patient.visits, patient.lab_results, patient.vitals.",
                "Write a Python class PortfolioAnalyzer with a method analyze_holdings that extensively uses account.positions, account.transactions, account.cash_balance, account.margin, account.performance_history.",
                "Write a Python class ExperimentReporter with a method generate_results that uses experiment.measurements, experiment.parameters, experiment.controls, experiment.subjects, experiment.timestamps."
            ],
            "advanced": [
                "Write a Python class ComplianceChecker with a method check_transaction_compliance that uses transaction.amount, transaction.parties, transaction.jurisdiction, transaction.type, customer.risk_rating, customer.documents, customer.history, regulations.thresholds, regulations.requirements.",
                "Write a Python class ClaimsAdjudicator with a method adjudicate_claim that heavily uses claim.services, claim.diagnosis, claim.provider, member.coverage, member.benefits, member.deductible, member.copay, policy.rules, policy.exclusions.",
                "Write a Python class RiskAssessor with a method assess_loan_risk using applicant.income, applicant.employment, applicant.credit_history, applicant.assets, applicant.debts, loan.amount, loan.term, market.rates, market.conditions.",
                "Write a Python class TreatmentPlanner with a method create_plan using patient.diagnosis, patient.history, patient.allergies, patient.preferences, treatment.protocols, treatment.contraindications, provider.specialties, insurance.coverage.",
                "Write a Python class CampaignOptimizer with a method optimize_targeting using campaign.performance, audience.demographics, audience.behaviors, audience.conversions, market.trends, competitor.activity, budget.constraints."
            ]
        },

        "data_clumps": {
            "basic": [
                "Write Python functions that repeatedly pass (street, city, state, zip_code, country) together as separate parameters for shipping, billing, and contact addresses.",
                "Write Python functions that pass (start_date, end_date, timezone) as separate parameters to multiple report generation and filtering functions.",
                "Write Python functions that use (latitude, longitude, altitude) as separate parameters for location tracking, distance calculation, and map rendering.",
                "Write Python functions that pass (width, height, depth) separately to multiple functions for volume calculation, shipping cost, and storage allocation.",
                "Write Python functions that repeatedly use (first_name, last_name, email, phone) as separate parameters for contact management.",
                "Write Python functions that pass (red, green, blue, alpha) as separate parameters to multiple image processing functions."
            ],
            "intermediate": [
                "Write a Python e-commerce module where (product_id, quantity, unit_price, discount_percent, tax_rate) are passed separately to cart operations, checkout, invoice generation, and inventory updates.",
                "Write a Python financial module where (account_number, routing_number, account_type, holder_name, bank_name) are passed separately to transfer, validation, and reporting functions.",
                "Write a Python healthcare module where (patient_id, provider_id, facility_id, appointment_date, appointment_time, appointment_type) are passed separately to scheduling, billing, and notification functions.",
                "Write a Python scientific module where (sample_id, measurement_value, measurement_unit, timestamp, instrument_id, operator_id) are passed separately to recording, validation, and analysis functions.",
                "Write a Python HR module where (employee_id, department_id, manager_id, job_title, salary, hire_date) are passed separately to payroll, reporting, and org chart functions."
            ],
            "advanced": [
                "Write a Python insurance module where claim information (claim_id, policy_number, incident_date, incident_type, incident_location_street, incident_location_city, incident_location_state, claimant_name, claimant_phone, claimant_email) is passed separately to submission, validation, adjustment, and payment functions.",
                "Write a Python trading module where order details (symbol, quantity, order_type, limit_price, stop_price, time_in_force, account_id, strategy_id, risk_params) are passed separately to validation, execution, reporting, and reconciliation functions.",
                "Write a Python clinical trial module where subject data (subject_id, site_id, visit_number, visit_date, investigator_id, protocol_version, randomization_code, consent_date, demographics) is passed separately to enrollment, data capture, monitoring, and reporting functions.",
                "Write a Python logistics module where shipment details (origin_address, origin_city, origin_country, dest_address, dest_city, dest_country, weight, dimensions, carrier, service_level, insurance_value) are passed separately to routing, tracking, billing, and customer notification functions."
            ]
        },

        "duplicated_code": {
            "basic": [
                "Write a Python module with separate functions validate_customer_email, validate_supplier_email, and validate_employee_email that each contain identical email validation logic.",
                "Write a Python module with calculate_order_tax, calculate_invoice_tax, and calculate_refund_tax functions that duplicate the same tax calculation algorithm.",
                "Write Python functions format_customer_report and format_vendor_report that contain nearly identical formatting and templating code.",
                "Write a Python module with save_user_to_db, save_product_to_db, and save_order_to_db functions that duplicate database connection and error handling logic.",
                "Write Python classes CustomerValidator and SupplierValidator that both contain identical input sanitization and validation methods.",
                "Write a Python module with export_orders_csv, export_customers_csv, and export_products_csv functions that duplicate CSV formatting logic."
            ],
            "intermediate": [
                "Write a Python e-commerce application with create_customer, create_vendor, and create_partner functions that each duplicate address validation, email verification, phone formatting, and database insertion code.",
                "Write a Python financial system with process_deposit, process_withdrawal, and process_transfer functions that duplicate validation, logging, notification, and audit trail code.",
                "Write a Python healthcare system with schedule_appointment, reschedule_appointment, and cancel_appointment functions that duplicate availability checking, notification, and calendar update logic.",
                "Write a Python analytics module with generate_sales_report, generate_inventory_report, and generate_customer_report functions that duplicate data retrieval, filtering, aggregation, and formatting code.",
                "Write a Python API with customer_api_handler, product_api_handler, and order_api_handler functions that duplicate authentication, validation, error handling, and response formatting code."
            ],
            "advanced": [
                "Write a Python trading platform with functions for stock_order_validation, options_order_validation, and futures_order_validation that duplicate complex validation logic including account verification, margin checks, risk assessment, and compliance rules.",
                "Write a Python insurance system with auto_claim_processor, home_claim_processor, and health_claim_processor that each duplicate eligibility verification, coverage calculation, fraud detection, and payment processing workflows.",
                "Write a Python clinical system with inpatient_admission, outpatient_registration, and emergency_intake functions that duplicate patient verification, insurance validation, consent collection, and record initialization logic.",
                "Write a Python ERP system with procurement_workflow, sales_workflow, and manufacturing_workflow functions that duplicate approval routing, notification, audit logging, and status tracking code.",
                "Write a Python research platform with experiment_setup, simulation_setup, and analysis_setup functions that duplicate parameter validation, resource allocation, logging configuration, and checkpoint management code."
            ]
        },

        "dead_code": {
            "basic": [
                "Write a Python class UserService with methods login, logout, and deprecated_authenticate that is never called but still maintained in the codebase.",
                "Write a Python module with calculate_total, calculate_subtotal, and an unused legacy_calculate function that was replaced but not removed.",
                "Write a Python class OrderProcessor with methods that include commented-out code blocks and unused helper methods from a previous implementation.",
                "Write a Python module with active functions and a DEBUG_MODE flag that enables unused debugging functions that are never executed in production.",
                "Write a Python class PaymentGateway with current payment methods and unused deprecated_payment_v1 methods that remain in the code."
            ],
            "intermediate": [
                "Write a Python e-commerce module with active order processing plus unused promotional code handlers, abandoned cart recovery, and legacy discount calculation methods.",
                "Write a Python financial system with working transaction processing alongside unused experimental trading algorithms, deprecated fee structures, and obsolete reporting methods.",
                "Write a Python healthcare module with functioning appointment scheduling plus unused telemedicine_v1 handlers, deprecated insurance verification methods, and legacy billing code.",
                "Write a Python analytics module with active reporting functions plus unused A/B testing framework code, deprecated visualization methods, and legacy data export functions.",
                "Write a Python CMS with working content management plus unused workflow_v1 handlers, deprecated template engine integration, and legacy media processing code."
            ],
            "advanced": [
                "Write a Python trading platform with active order execution plus extensive unused backtesting framework, deprecated strategy implementations, legacy market data handlers, and obsolete risk calculation modules.",
                "Write a Python insurance platform with functioning claims processing plus unused legacy adjudication rules, deprecated underwriting models, abandoned fraud detection algorithms, and obsolete policy migration code.",
                "Write a Python clinical trial system with active data capture plus unused electronic consent module v1, deprecated randomization algorithms, legacy adverse event reporting, and abandoned interim analysis code.",
                "Write a Python ERP system with working inventory management plus unused demand forecasting v1, deprecated supplier scoring models, legacy warehouse optimization code, and abandoned integration adapters."
            ]
        },

        "speculative_generality": {
            "basic": [
                "Write a Python AbstractDataProcessor base class with many abstract methods for future extensibility, but currently only one concrete JsonProcessor subclass exists.",
                "Write a Python PluginManager that supports loading, unloading, and managing plugins with a complex API, but the system only uses one hardcoded plugin.",
                "Write a Python configuration system with support for JSON, YAML, XML, INI, and TOML formats, environment variable overrides, and remote config servers when only JSON files are used.",
                "Write a Python NotificationFactory that can create email, SMS, push, webhook, and Slack notifications with a complex builder pattern, but only email is implemented.",
                "Write a Python CacheManager supporting Redis, Memcached, filesystem, and database caching with automatic failover, when only simple dictionary caching is needed."
            ],
            "intermediate": [
                "Write a Python e-commerce payment system with abstract interfaces for credit cards, PayPal, cryptocurrency, bank transfers, and buy-now-pay-later, with complex factory patterns, when only credit card payments are used.",
                "Write a Python reporting framework with extensible renderers for PDF, Excel, HTML, JSON, XML, and custom formats with plugin architecture, when only PDF export is required.",
                "Write a Python workflow engine with support for parallel execution, conditional branching, loops, timers, and external triggers, when only simple sequential workflows are needed.",
                "Write a Python multi-database ORM supporting PostgreSQL, MySQL, SQLite, MongoDB, and Cassandra with query optimization and connection pooling, when only PostgreSQL is used.",
                "Write a Python API gateway with support for REST, GraphQL, gRPC, WebSocket, and SOAP with protocol translation, when only REST endpoints are served."
            ],
            "advanced": [
                "Write a Python trading system with abstract strategy interfaces supporting technical, fundamental, sentiment, and ML-based strategies with backtesting, paper trading, and live modes, when only one simple moving average strategy runs.",
                "Write a Python healthcare integration engine supporting HL7v2, FHIR, CDA, X12, and custom formats with transformation pipelines, routing rules, and acknowledgment handling, when only basic HL7v2 ADT messages are processed.",
                "Write a Python ML pipeline framework with support for TensorFlow, PyTorch, scikit-learn, XGBoost, and custom models with hyperparameter tuning, distributed training, and model versioning, when only simple logistic regression is used.",
                "Write a Python enterprise service bus supporting synchronous calls, async messaging, event sourcing, saga pattern, and distributed transactions, when only simple request-response is needed."
            ]
        },

        "primitive_obsession": {
            "basic": [
                "Write a Python function process_order that uses strings for order_id, customer_id, product_id, and status instead of typed objects.",
                "Write a Python function that represents money amounts as floats and currency as strings instead of a Money class.",
                "Write a Python function that uses string phone numbers with separate country_code, area_code, and number variables instead of a PhoneNumber class.",
                "Write a Python function that represents dates as separate year, month, day integers instead of proper date objects.",
                "Write a Python function that uses email addresses as plain strings throughout with inline validation logic.",
                "Write a Python function that represents coordinates as separate latitude and longitude floats instead of a Coordinate class."
            ],
            "intermediate": [
                "Write a Python e-commerce module that uses strings and integers for order_id (string), total_amount (float), currency (string), status (string), shipping_address as multiple strings, and payment_status (string) instead of value objects.",
                "Write a Python financial module that represents transactions with primitive types: transaction_id (string), amount (float), currency (string), source_account (string), dest_account (string), type (string), status (string) instead of domain objects.",
                "Write a Python healthcare module that uses patient_mrn (string), diagnosis_codes as list of strings, medication_codes as list of strings, dosages as list of floats, units as list of strings instead of proper domain models.",
                "Write a Python scientific module that represents measurements with value (float), unit (string), uncertainty (float), timestamp (float), instrument_id (string) as primitives instead of a Measurement class.",
                "Write a Python HR module using employee_id (string), salary (float), currency (string), department (string), role (string), level (int), hire_date (string) as primitives instead of typed objects."
            ],
            "advanced": [
                "Write a Python trading system using primitive types throughout: symbol (string), price (float), quantity (int), order_type (string), side (string), time_in_force (string), limit_price (float), stop_price (float), status (string), filled_quantity (int), average_price (float) instead of Order and related domain objects.",
                "Write a Python insurance system representing policies with primitives: policy_number (string), effective_date (string), expiration_date (string), premium (float), coverage_limits as dict of strings to floats, deductibles as dict, status (string), policyholder_info as nested dicts of strings.",
                "Write a Python clinical trial system using primitives: subject_id (string), site_id (string), visit_window_start (string), visit_window_end (string), measurements as dict of string to float, adverse_events as list of dicts with string fields, protocol_deviations as list of string tuples.",
                "Write a Python logistics system using primitives for shipments: tracking_number (string), origin_coords (tuple of floats), dest_coords (tuple of floats), weight (float), weight_unit (string), dimensions as tuple, carrier_code (string), service_code (string), status_history as list of string tuples."
            ]
        },

        "switch_statements": {
            "basic": [
                "Write a Python function calculate_discount(customer_type) that uses if-elif chains to return different discount rates for 'regular', 'premium', 'vip', 'employee', and 'wholesale' customers.",
                "Write a Python function get_shipping_cost(shipping_method) with if-elif statements for 'standard', 'express', 'overnight', 'international', and 'freight' options.",
                "Write a Python function process_payment(payment_type) using if-elif to handle 'credit_card', 'debit_card', 'paypal', 'bank_transfer', and 'crypto' differently.",
                "Write a Python function format_message(message_type) with switch-like logic for 'email', 'sms', 'push', 'slack', and 'teams' notification formats.",
                "Write a Python function calculate_tax(state) using if-elif chains for different US state tax calculation rules.",
                "Write a Python function render_chart(chart_type) with if-elif for 'bar', 'line', 'pie', 'scatter', and 'histogram' rendering logic."
            ],
            "intermediate": [
                "Write a Python function process_order(order_type, customer_type, payment_method) with nested if-elif chains handling combinations of order types (standard, subscription, preorder), customer types (individual, business, government), and payment methods.",
                "Write a Python function handle_claim(claim_type, policy_type, jurisdiction) with complex if-elif logic for processing auto, home, health, and life insurance claims differently based on policy type and state regulations.",
                "Write a Python function execute_trade(asset_class, order_type, market_condition) with if-elif chains handling stocks, options, futures, and forex differently based on order type and market hours/conditions.",
                "Write a Python function process_lab_result(test_type, specimen_type, patient_category) with nested conditionals for different lab test processing logic based on test category and patient demographics.",
                "Write a Python function apply_transformation(data_type, source_format, target_format) with if-elif handling different transformation rules for various data type and format combinations."
            ],
            "advanced": [
                "Write a Python function calculate_premium(policy_type, coverage_level, risk_factors, state, age_bracket, credit_tier) with deeply nested if-elif chains calculating insurance premiums differently for each combination of factors.",
                "Write a Python function route_order(asset_class, order_size, urgency, market_maker, client_type, regulatory_status) with complex conditional logic selecting different execution venues and algorithms based on multiple factors.",
                "Write a Python function adjudicate_claim(claim_type, service_category, provider_type, member_plan, accumulator_status, prior_auth_status, network_status) with extensive if-elif chains implementing different adjudication rules for each combination.",
                "Write a Python function assign_protocol(diagnosis_category, severity, comorbidities, patient_preferences, resource_availability, insurance_coverage) with complex branching logic for treatment protocol selection.",
                "Write a Python function optimize_route(vehicle_type, cargo_type, time_constraints, weather_conditions, traffic_status, driver_preferences, regulatory_restrictions) with nested conditionals for logistics routing decisions."
            ]
        },

        "parallel_inheritance": {
            "basic": [
                "Write Python class hierarchies where Shape (Circle, Rectangle, Triangle) has a parallel Renderer hierarchy (CircleRenderer, RectangleRenderer, TriangleRenderer).",
                "Write Python class hierarchies where Document (Invoice, Receipt, Quote) requires parallel Printer classes (InvoicePrinter, ReceiptPrinter, QuotePrinter).",
                "Write Python class hierarchies where Payment (CreditCard, BankTransfer, Crypto) has parallel Validator classes (CreditCardValidator, BankTransferValidator, CryptoValidator).",
                "Write Python class hierarchies where Report (SalesReport, InventoryReport, FinancialReport) requires parallel Exporter classes for each type.",
                "Write Python class hierarchies where Notification (Email, SMS, Push) has parallel Template classes (EmailTemplate, SMSTemplate, PushTemplate)."
            ],
            "intermediate": [
                "Write Python class hierarchies for an e-commerce system where Order types (StandardOrder, SubscriptionOrder, PreOrder) each require parallel Fulfillment, Billing, and Notification class hierarchies.",
                "Write Python class hierarchies for a financial system where Account types (Checking, Savings, Investment) require parallel Statement, InterestCalculator, and FeeCalculator hierarchies.",
                "Write Python class hierarchies for a healthcare system where Encounter types (Inpatient, Outpatient, Emergency) require parallel Billing, Documentation, and Scheduling hierarchies.",
                "Write Python class hierarchies for an analytics platform where DataSource types (Database, API, File) require parallel Connector, Transformer, and Validator hierarchies.",
                "Write Python class hierarchies for a CMS where Content types (Article, Video, Podcast) require parallel Editor, Publisher, and Analytics hierarchies."
            ],
            "advanced": [
                "Write Python class hierarchies for a trading platform where Instrument types (Stock, Option, Future, Forex) each require parallel OrderHandler, RiskCalculator, MarginCalculator, SettlementProcessor, and ReportGenerator class hierarchies.",
                "Write Python class hierarchies for an insurance system where Policy types (Auto, Home, Health, Life) require parallel Underwriter, ClaimProcessor, PremiumCalculator, RenewalHandler, and ComplianceChecker hierarchies.",
                "Write Python class hierarchies for a clinical system where Study types (Phase1, Phase2, Phase3, Phase4) require parallel EnrollmentManager, DataCollector, SafetyMonitor, StatisticalAnalyzer, and RegulatoryReporter hierarchies.",
                "Write Python class hierarchies for an ERP system where Entity types (Customer, Vendor, Employee, Partner) require parallel Validator, Synchronizer, AuditLogger, ReportGenerator, and AccessController hierarchies."
            ]
        },

        "lazy_class": {
            "basic": [
                "Write a Python class StringHelper with only one method capitalize_first that wraps str.capitalize().",
                "Write a Python class DateFormatter with only one method format_date that wraps strftime with a hardcoded format.",
                "Write a Python class EmailValidator with only one method is_valid that contains a single regex match.",
                "Write a Python class Config with only one method get that wraps dictionary access.",
                "Write a Python class Logger with only one method log that wraps print().",
                "Write a Python class Counter with only one attribute and increment/decrement methods."
            ],
            "intermediate": [
                "Write a Python e-commerce module with OrderIdGenerator class that only generates sequential IDs, PriceRounder class that only rounds to 2 decimals, and SkuFormatter class that only uppercases strings.",
                "Write a Python financial module with AccountNumberFormatter class that only adds dashes, BalanceChecker class that only compares two values, and CurrencySymbolMapper class that only does dictionary lookup.",
                "Write a Python healthcare module with MrnFormatter class that only pads with zeros, DateOfBirthValidator class that only checks if date is in past, and GenderMapper class that only maps M/F to full words.",
                "Write a Python analytics module with PercentageCalculator class that only divides and multiplies by 100, RoundingHelper class with one method, and NullChecker class that only checks for None.",
                "Write a Python API module with ResponseWrapper class that only wraps data in a dict, StatusMapper class that only maps codes to messages, and TimestampAdder class that only adds current time to dict."
            ],
            "advanced": [
                "Write a Python trading system with minimal classes: TickerNormalizer (uppercases symbols), QuantityValidator (checks positive), PriceFormatter (rounds to tick size), SideMapper (maps buy/sell to 1/-1), and TimeInForceValidator (checks against list).",
                "Write a Python insurance system with trivial classes: PolicyNumberFormatter (adds prefix), CoverageAmountRounder (rounds to nearest 1000), DeductibleValidator (checks within range), PremiumCalculatorWrapper (calls external service), and EffectiveDateChecker (compares dates).",
                "Write a Python clinical system with minimal classes: SubjectIdGenerator (formats UUID), VisitNumberFormatter (pads digits), ConsentDateValidator (checks not future), RandomizationCodeGenerator (wraps random), and AgeCalculator (subtracts dates).",
                "Write a Python logistics system with trivial classes: TrackingNumberFormatter (adds carrier prefix), WeightConverter (multiplies by constant), DimensionCalculator (multiplies three values), ZipCodeValidator (regex match), and CarrierCodeMapper (dictionary lookup)."
            ]
        },

        "temporary_field": {
            "basic": [
                "Write a Python class ReportGenerator with fields summary_data, chart_config, and export_path that are only set and used during the generate_report method.",
                "Write a Python class OrderProcessor with fields validation_errors, calculated_tax, and applied_discounts that are only populated during process_order.",
                "Write a Python class DataImporter with fields parsed_rows, error_log, and mapping_config that are only used during the import_file method.",
                "Write a Python class PaymentHandler with fields transaction_id, auth_response, and retry_count that are only used during process_payment.",
                "Write a Python class EmailSender with fields attachments, recipients_list, and template_data that are only populated when sending specific email types."
            ],
            "intermediate": [
                "Write a Python class InvoiceProcessor with instance fields line_item_totals, tax_breakdowns, discount_applications, subtotal, adjustment_log, and validation_messages that are only set during invoice generation and are meaningless otherwise.",
                "Write a Python class ClaimAdjudicator with fields coverage_results, deductible_applied, copay_calculated, coinsurance_amount, provider_discount, and member_responsibility that exist only during adjudication.",
                "Write a Python class TradeExecutor with fields order_book_snapshot, available_liquidity, slippage_estimate, execution_venue, partial_fills, and final_average_price populated only during execution.",
                "Write a Python class PatientAdmission with fields bed_assignment, attending_physician, insurance_verification_result, consent_status, and initial_orders only set during the admission workflow.",
                "Write a Python class ExperimentRunner with fields current_iteration, accumulated_results, convergence_metrics, resource_usage, and checkpoint_data only meaningful during experiment execution."
            ],
            "advanced": [
                "Write a Python class PortfolioRebalancer with many temporary fields: current_allocations, target_allocations, drift_calculations, trade_candidates, tax_lot_selections, wash_sale_checks, order_generation_state, execution_status, reconciliation_data, and performance_attribution that are only valid during rebalancing operation.",
                "Write a Python class InsuranceRenewalProcessor with temporary fields: policy_history_cache, claims_experience, rate_factors, territory_adjustments, tier_placement, surcharge_calculations, discount_eligibility, premium_components, comparison_quotes, and renewal_recommendation only set during renewal processing.",
                "Write a Python class ClinicalTrialEnrollment with temporary fields: screening_results, eligibility_criteria_evaluation, randomization_factors, stratification_data, site_capacity_check, investigator_availability, consent_documentation, baseline_assessments, and enrollment_confirmation only populated during enrollment workflow.",
                "Write a Python class SupplyChainOptimizer with temporary fields: demand_forecast_cache, inventory_positions, lead_time_estimates, supplier_capacity, transportation_costs, constraint_evaluations, optimization_iterations, solution_candidates, and implementation_plan only valid during optimization run."
            ]
        },

        "message_chains": {
            "basic": [
                "Write a Python function that accesses customer.account.billing.address.zip_code to get billing information.",
                "Write a Python function that navigates order.customer.preferences.notification.email.frequency to update notification settings.",
                "Write a Python function that reads company.department.team.manager.contact.phone to get manager phone numbers.",
                "Write a Python function that accesses config.database.connection.pool.settings.max_size to configure database pools.",
                "Write a Python function that traverses user.profile.settings.privacy.sharing.contacts to check sharing permissions."
            ],
            "intermediate": [
                "Write a Python e-commerce function that accesses order.customer.account.payment_methods.primary.card.billing_address.validation_status to verify payment method.",
                "Write a Python financial function that navigates portfolio.accounts.primary.holdings.equity.positions.largest.current_value.currency to report values.",
                "Write a Python healthcare function that reads patient.medical_record.encounters.latest.diagnoses.primary.coding.icd10.code to get diagnosis codes.",
                "Write a Python analytics function that traverses dashboard.widgets.charts.performance.data_source.connection.query.results.latest to fetch data.",
                "Write a Python CMS function that accesses site.pages.home.sections.hero.content.media.images.featured.url to get featured image."
            ],
            "advanced": [
                "Write a Python trading function that chains through order.execution.fills.primary.venue.market_maker.liquidity_pool.pricing.spread.historical.average to analyze execution quality.",
                "Write a Python insurance function that navigates claim.policy.coverage.benefits.medical.services.allowed.procedure.reimbursement.schedule.rates.contracted to determine payment.",
                "Write a Python clinical function that traverses study.sites.primary.investigators.principal.credentials.certifications.board.specialty.subspecialty.effective_date for compliance checking.",
                "Write a Python ERP function that accesses purchase_order.vendor.contracts.active.terms.payment.schedule.milestones.first.conditions.documents.required to check requirements.",
                "Write a Python IoT function that chains device.network.gateway.cluster.region.data_center.storage.time_series.metrics.temperature.readings.latest.value to get sensor data."
            ]
        },

        "middle_man": {
            "basic": [
                "Write a Python class OrderService that has methods like get_order_total, get_order_items, get_order_status that all just call corresponding methods on self.order_repository.",
                "Write a Python class UserManager that delegates all operations (create, update, delete, find) directly to self.user_dao without adding any logic.",
                "Write a Python class PaymentGateway that simply forwards all method calls to self.payment_processor without any additional processing.",
                "Write a Python class ConfigManager that only delegates get and set operations to self.config_store.",
                "Write a Python class NotificationService that forwards send_email, send_sms, send_push directly to respective provider classes."
            ],
            "intermediate": [
                "Write a Python class CustomerFacade that has 15+ methods all delegating to CustomerRepository, each method just calling the corresponding repository method with same parameters.",
                "Write a Python class TradingService that delegates order_create, order_modify, order_cancel, position_get, balance_get directly to TradingApi without transformation.",
                "Write a Python class PatientService that forwards all CRUD operations plus search, filter, and export methods directly to PatientRepository.",
                "Write a Python class ReportManager that delegates generate, schedule, export, email for each report type directly to ReportEngine.",
                "Write a Python class DataAccessLayer that provides entity-specific methods all forwarding to generic DatabaseConnector methods."
            ],
            "advanced": [
                "Write a Python class ApplicationService layer where OrderService, CustomerService, InventoryService, PaymentService, and ShippingService each have 10+ methods that all delegate directly to corresponding repositories without business logic.",
                "Write a Python class TradingFacade that delegates to OrderManagement, RiskManagement, PortfolioManagement, and ReportingService with each method being a simple forward to underlying service.",
                "Write a Python class HealthcareCoordinator that forwards to PatientService, EncounterService, BillingService, ClinicalService, and SchedulingService with no coordination logic.",
                "Write a Python class AnalyticsBroker that delegates to DataWarehouse, ReportEngine, DashboardService, and ExportService with methods that only pass parameters through.",
                "Write a Python class IntegrationHub that forwards to each external system adapter (ERP, CRM, Billing, Shipping) without any transformation or orchestration."
            ]
        },

        "inappropriate_intimacy": {
            "basic": [
                "Write Python classes Order and Customer where Order directly accesses Customer._internal_credit_score and Customer._private_notes fields.",
                "Write Python classes Invoice and Payment where each class directly modifies the other's private state variables.",
                "Write Python classes User and Session where Session accesses User._password_hash and User._security_questions directly.",
                "Write Python classes Product and Inventory where Product directly manipulates Inventory._reserved_stock and Inventory._warehouse_locations.",
                "Write Python classes Employee and Payroll where each reads and writes the other's internal accounting fields."
            ],
            "intermediate": [
                "Write Python classes OrderProcessor and InventoryManager where OrderProcessor directly manipulates InventoryManager._stock_levels, _reserved_items, _reorder_triggers, and _supplier_queues bypassing public API.",
                "Write Python classes Patient and MedicalRecord where Patient directly accesses MedicalRecord._diagnosis_history, _medications, _allergies, and _provider_notes, and MedicalRecord modifies Patient._insurance_details.",
                "Write Python classes Account and Transaction where Transaction reads Account._balance, _overdraft_limit, _pending_holds and Account inspects Transaction._authorization_code, _fraud_score.",
                "Write Python classes Campaign and Analytics where Campaign directly queries Analytics._user_segments, _conversion_funnels, _attribution_data and Analytics modifies Campaign._budget_allocation.",
                "Write Python classes Experiment and DataCollector where each class has detailed knowledge of the other's internal data structures and directly manipulates them."
            ],
            "advanced": [
                "Write a Python trading system where Order, Execution, RiskManager, and Position classes all have direct access to each other's private fields, with Order modifying Position._unrealized_pnl, RiskManager accessing Order._internal_routing, and Execution updating RiskManager._exposure_cache.",
                "Write a Python healthcare system where Patient, Encounter, Claim, and Provider classes are deeply intertwined, each accessing private fields of the others for efficiency rather than using proper interfaces.",
                "Write a Python e-commerce system where Cart, Checkout, Inventory, and Payment classes bypass encapsulation, with Cart modifying Inventory._holds, Checkout accessing Payment._tokenized_cards, and Payment updating Cart._applied_promotions.",
                "Write a Python insurance system where Policy, Claim, Underwriting, and Billing classes share intimate knowledge, each accessing internal state of others including _risk_scores, _claim_reserves, _premium_calculations.",
                "Write a Python scientific system where Experiment, Measurement, Analysis, and Publication classes directly access each other's private data stores, caches, and internal computation states."
            ]
        },

        "alternative_classes_different_interfaces": {
            "basic": [
                "Write Python classes JsonFileReader with method load_json(path) and XmlFileReader with method parse_xml(filename) that do the same thing but have different interfaces.",
                "Write Python classes EmailNotifier with send(recipient, message) and SmsNotifier with dispatch(phone_number, text_content) for sending notifications.",
                "Write Python classes MySqlDatabase with execute_query(sql) and PostgresDatabase with run_statement(query_string) for database operations.",
                "Write Python classes FileLogger with write_log(message) and DatabaseLogger with insert_log_entry(log_data) for logging.",
                "Write Python classes RestApiClient with get_data(endpoint) and GraphqlClient with query(operation) for API calls."
            ],
            "intermediate": [
                "Write Python payment classes StripePayment with charge(amount, card_token), PayPalPayment with create_payment(value, payer_id), and SquarePayment with process(payment_info) all doing similar operations with different signatures.",
                "Write Python storage classes S3Storage with upload_file(bucket, key, data), AzureBlob with put_blob(container, name, content), and GcsStorage with write_object(bucket_name, object_path, payload) for cloud storage.",
                "Write Python classes HttpClient with request(method, url, body), AxiosWrapper with call(config_object), and FetchService with fetch(url, options) for HTTP operations.",
                "Write Python classes PdfGenerator with create_pdf(content, options), ReportBuilder with build_report(data, template), and DocumentWriter with write_document(sections, format) for document generation.",
                "Write Python classes SqlAlchemyRepo with find_by_id(entity_class, id), DjangoOrmRepo with get(model, pk), and PeeweeRepo with fetch_one(model_class, identifier) for data access."
            ],
            "advanced": [
                "Write Python trading APIs TradingViewApi with place_order(symbol, qty, side), InteractiveBrokersApi with submit_order(contract, order_details), and AlpacaApi with create_order(ticker, quantity, direction, type) with similar functionality but completely different interfaces.",
                "Write Python healthcare integration classes Hl7Parser with parse_message(raw_hl7), FhirClient with read_resource(resource_type, id), and CdaProcessor with extract_document(cda_xml) for clinical data with incompatible interfaces.",
                "Write Python analytics classes GoogleAnalytics with track_event(category, action, label), MixpanelClient with send_event(event_name, properties), and AmplitudeTracker with log_event(event_type, event_properties) with different signatures.",
                "Write Python ML frameworks TensorFlowModel with predict(input_tensor), PyTorchModel with forward(x), and SklearnModel with predict_proba(X) for inference with incompatible interfaces.",
                "Write Python messaging classes KafkaProducer with send(topic, message), RabbitMqPublisher with publish(exchange, routing_key, body), and SqsClient with send_message(queue_url, message_body) with different APIs."
            ]
        },

        "incomplete_library_class": {
            "basic": [
                "Write a Python function that extends the datetime library by adding utility functions for business day calculations that datetime doesn't provide.",
                "Write a Python class that wraps json library to add support for serializing custom objects that json.dumps can't handle.",
                "Write a Python module that extends the csv library with functions for handling malformed CSV files and automatic encoding detection.",
                "Write a Python utility that wraps requests library to add retry logic, circuit breaker, and caching that it doesn't provide natively.",
                "Write a Python helper that extends pathlib with batch operations and recursive pattern matching that Path doesn't support."
            ],
            "intermediate": [
                "Write a Python e-commerce module that wraps decimal.Decimal with currency-aware arithmetic, rounding rules, and formatting that the standard library lacks.",
                "Write a Python financial module that extends pandas DataFrame with financial calculations, time series analysis, and market data specific operations.",
                "Write a Python healthcare module that wraps datetime with medical-specific date handling including gestational age, dosing intervals, and clinical time windows.",
                "Write a Python scientific module that extends numpy with domain-specific operations for signal processing, uncertainty propagation, and unit handling.",
                "Write a Python analytics module that wraps matplotlib/seaborn with business chart templates, branding, and automated annotations they don't provide."
            ],
            "advanced": [
                "Write a Python trading module that extensively wraps pandas, numpy, and datetime with financial market specific functionality including trading calendars, corporate actions, time zone handling, and market data alignment.",
                "Write a Python clinical data module that extends multiple libraries (datetime, pandas, json) with healthcare-specific validations, HIPAA-compliant transformations, and clinical terminology mappings.",
                "Write a Python ERP integration module that wraps requests, xml.etree, and json with enterprise-specific message handling, EDI formatting, and business document transformations.",
                "Write a Python research module that extends scipy, statsmodels, and pandas with reproducibility features, experiment tracking, and scientific metadata handling the base libraries lack."
            ]
        },

        "data_class": {
            "basic": [
                "Write a Python class Customer with only fields (name, email, phone, address) and getter/setter methods, no business logic.",
                "Write a Python class Product with attributes (id, name, price, description, category) and only property accessors.",
                "Write a Python class Order with fields (order_id, items, total, status, date) and just getters and setters.",
                "Write a Python class Employee with only data (id, name, department, salary, hire_date) and accessor methods.",
                "Write a Python class Configuration with settings fields and only get/set methods, no behavior."
            ],
            "intermediate": [
                "Write a Python class Invoice with extensive fields (invoice_number, customer_info, line_items, subtotal, tax_amount, discounts, total, payment_status, dates) and only getters/setters/to_dict methods.",
                "Write a Python class PatientRecord with fields (mrn, demographics, insurance, conditions, medications, allergies, vitals, providers) and only accessor and serialization methods.",
                "Write a Python class TradeOrder with fields (order_id, symbol, side, quantity, price, order_type, status, timestamps, fills) and only property methods.",
                "Write a Python class CampaignData with fields (campaign_id, name, settings, targeting, creatives, budget, schedule, performance_metrics) and only accessors.",
                "Write a Python class ExperimentRecord with fields (experiment_id, parameters, measurements, metadata, results, status, timestamps) and only get/set/serialize methods."
            ],
            "advanced": [
                "Write a Python class ComprehensiveOrder with 30+ fields covering order details, customer info, shipping, billing, items, pricing, status, audit trail, and only getter/setter/serialization methods with no business logic.",
                "Write a Python class FullPatientProfile with extensive fields for demographics, medical history, current conditions, medications, allergies, immunizations, family history, social history, insurance, providers, and only accessors.",
                "Write a Python class DetailedTradeExecution with fields for order info, routing, execution venues, fills, timing, costs, compliance data, settlement info, and only property methods.",
                "Write a Python class InsurancePolicy with comprehensive fields for policy details, coverages, limits, deductibles, premiums, endorsements, claims history, billing, and only getters/setters.",
                "Write a Python class ClinicalStudyRecord with fields for study info, protocol, sites, investigators, subjects, visits, data points, adverse events, deviations, and only accessor methods."
            ]
        },

        "refused_bequest": {
            "basic": [
                "Write a Python class Stack that inherits from list but doesn't use most list methods like insert, remove, or slice operations.",
                "Write a Python class ReadOnlyConfig inheriting from dict but raising exceptions for __setitem__, update, and pop.",
                "Write a Python class LimitedUser inheriting from FullUser but disabling premium_features, admin_actions, and advanced_settings methods.",
                "Write a Python class RestrictedAccount inheriting from Account but blocking withdraw, transfer, and close methods.",
                "Write a Python class BasicReport inheriting from AdvancedReport but not implementing export_pdf, schedule, and email methods."
            ],
            "intermediate": [
                "Write a Python class GuestCustomer inheriting from Customer but raising NotImplementedError for save_payment_method, view_order_history, access_loyalty_program, and manage_subscriptions.",
                "Write a Python class TrialAccount inheriting from PremiumAccount but disabling advanced_analytics, api_access, custom_integrations, and priority_support methods.",
                "Write a Python class ViewOnlyDashboard inheriting from Dashboard but blocking edit_layout, add_widget, configure_data_source, and share methods.",
                "Write a Python class BasicPatient inheriting from Patient but not implementing upload_documents, request_prescription_refill, schedule_telehealth, and access_portal methods.",
                "Write a Python class SimpleExperiment inheriting from Experiment but ignoring parallel_execution, distributed_computing, advanced_visualization, and automated_reporting capabilities."
            ],
            "advanced": [
                "Write a Python class RestrictedBrokerageAccount inheriting from FullBrokerageAccount but disabling margin_trading, options_trading, futures_trading, forex_trading, and short_selling while only allowing basic stock purchases.",
                "Write a Python class LimitedPolicy inheriting from ComprehensivePolicy but raising NotImplementedError for add_rider, increase_coverage, file_claim, request_loan, and change_beneficiary methods.",
                "Write a Python class ObservationalStudy inheriting from ClinicalTrial but not implementing randomization, blinding, intervention_assignment, and placebo_control methods.",
                "Write a Python class BasicERPUser inheriting from ERPAdmin but blocking module_configuration, user_management, workflow_customization, integration_setup, and audit_access.",
                "Write a Python class ReadOnlyAnalytics inheriting from AnalyticsPlatform but disabling create_dashboard, modify_reports, export_data, schedule_jobs, and manage_data_sources."
            ]
        },

        "comments_smell": {
            "basic": [
                "Write a Python function with extensive comments explaining what each line does, including obvious operations like 'increment counter by 1' and 'check if value is None'.",
                "Write a Python class with docstrings and comments that are longer than the actual code, explaining every variable assignment.",
                "Write a Python function with TODO comments, FIXME notes, and commented-out code blocks that have been there for 'future reference'.",
                "Write a Python function where comments apologize for the code or warn other developers about confusing logic instead of clarifying the code.",
                "Write a Python module with header comments in every function restating the function name and parameters that are already self-documenting."
            ],
            "intermediate": [
                "Write a Python e-commerce order processor with comments explaining business rules that should be extracted into well-named functions, including multi-paragraph explanations of discount logic.",
                "Write a Python financial calculation module with extensive comments explaining formulas that could be self-documenting code, including ASCII diagrams in comments.",
                "Write a Python healthcare data processor with comments explaining HIPAA compliance that should be in documentation, plus warnings about edge cases in the code.",
                "Write a Python API handler with comments documenting the protocol instead of using proper API documentation tools, including request/response examples in code comments.",
                "Write a Python analytics function with historical comments explaining why changes were made, referenced bug tickets, and names of developers who modified sections."
            ],
            "advanced": [
                "Write a Python trading algorithm with extensive comments explaining market microstructure that belong in documentation, commented-out alternative implementations, warnings about race conditions, and explanations of magic numbers.",
                "Write a Python claims processor with multi-page comment blocks explaining insurance regulations, commented-out legacy code paths, TODO items from years ago, and apologies for complex conditional logic.",
                "Write a Python clinical decision support function with comments containing medical references, regulatory citations, implementation history, performance warnings, and explanations that compensate for unclear variable names.",
                "Write a Python ETL pipeline with comments explaining data lineage that should be metadata, warnings about data quality issues, historical notes about source system changes, and explanations of workarounds.",
                "Write a Python scientific simulation with comments containing mathematical derivations, literature references, assumptions documentation, validation notes, and explanations for numerical precision choices."
            ]
        },

        "magic_numbers": {
            "basic": [
                "Write a Python function that uses 0.0825 for tax rate, 86400 for seconds in day, 1024 for buffer size without named constants.",
                "Write a Python function that checks if value > 100 and value < 10000 without explaining what these thresholds represent.",
                "Write a Python function that uses 7, 30, 365 for day calculations without constants explaining they're week, month, year.",
                "Write a Python function that applies discounts of 0.05, 0.10, 0.15, 0.20 based on quantity thresholds without named values.",
                "Write a Python function that uses HTTP status codes 200, 400, 401, 403, 404, 500 as literal numbers in conditionals."
            ],
            "intermediate": [
                "Write a Python e-commerce function that uses literals like 5.99 for shipping, 0.0875 for tax, 25 for free shipping threshold, 10 for max items, 30 for return days, 2.5 for weight multiplier without constants.",
                "Write a Python financial function using 0.0725 for interest rate, 360 for day count, 12 for periods, 10000 for minimum balance, 0.025 for fee rate, 250000 for FDIC limit without named values.",
                "Write a Python healthcare function with values like 120/80 for blood pressure, 98.6 for temperature, 7.35-7.45 for pH, 70-100 for glucose without clinical constants.",
                "Write a Python analytics function using 0.05 for significance, 0.8 for power, 1.96 for z-score, 30 for minimum sample, 0.3 for effect size without statistical constants.",
                "Write a Python scheduling function with 9, 17 for work hours, 480 for minutes, 5 for workdays, 2080 for annual hours, 0.5 for lunch duration without named values."
            ],
            "advanced": [
                "Write a Python trading function using 0.02 for stop loss, 0.06 for take profit, 0.25 for position size, 10 for ADR multiple, 20/50/200 for MA periods, 14 for RSI period, 2.0 for Bollinger bands, 0.5 for Kelly fraction without named constants.",
                "Write a Python insurance function with limits like 250000, 500000, 1000000 for coverage, 500, 1000, 2500 for deductibles, 0.8 for coinsurance, 6250 for out-of-pocket max, rates like 0.0234, 0.0156, 0.0089 without named values.",
                "Write a Python clinical function with thresholds like 140/90, 126, 6.5, 200, 1.7, 40/50, 130 for diagnostic criteria, 7, 14, 21, 30, 90 for follow-up intervals, 0.5, 1.0, 2.0 for dosing without clinical constants.",
                "Write a Python ML function using 0.001 for learning rate, 32 for batch size, 100 for epochs, 0.2 for dropout, 0.0001 for weight decay, 0.5 for threshold, 42 for random seed, 0.8 for train split without named hyperparameters.",
                "Write a Python logistics function with weights 50, 150, 2000 for categories, dimensions 12, 24, 48 for packages, rates 5.99, 12.99, 29.99 for shipping, zones 1-8 with multipliers 1.0, 1.2, 1.5, 2.0, 2.5 without named values."
            ]
        },

        "deep_nesting": {
            "basic": [
                "Write a Python function to calculate shipping costs where if domestic then if weight > 10 then if express shipping then if member discount applies then calculate final rate.",
                "Write a Python function that checks if user exists then if user is active then if user has permission then if resource is available then perform action.",
                "Write a Python function with nested loops: for each category, for each product, for each variant, for each price tier, apply calculation.",
                "Write a Python function with try inside try inside try blocks for handling different levels of exceptions.",
                "Write a Python function where validation checks are nested 5 levels deep before reaching the actual business logic."
            ],
            "intermediate": [
                "Write a Python order validation function that checks if order exists, then if customer is active, then if payment is verified, then if items are in stock, then if shipping address is valid, then if no fraud flags, then process the order.",
                "Write a Python data processing function with nested loops iterating files, then sheets, then rows, then cells, then applying transformations with conditionals at each level.",
                "Write a Python permission checker that nests through organization level, then department level, then team level, then role level, then specific permission level.",
                "Write a Python report generator with nested conditionals for report type, then date range, then grouping, then filtering, then formatting at each section level.",
                "Write a Python API handler with nested try-except for connection, then authentication, then authorization, then validation, then execution, then response formatting."
            ],
            "advanced": [
                "Write a Python claims processing function with deeply nested conditionals: if claim type then if policy active then if coverage applies then if deductible met then if within limits then if provider in network then if service authorized then if no exclusions then process payment.",
                "Write a Python trading validation with nesting: if market open then if instrument tradeable then if account active then if sufficient margin then if within risk limits then if no restrictions then if order valid then if venue available then route order.",
                "Write a Python clinical decision function nested as: if patient eligible then if diagnosis confirmed then if contraindications checked then if interactions cleared then if dosing appropriate then if consent obtained then if resources available then initiate treatment.",
                "Write a Python ETL pipeline with deeply nested loops and conditionals: for each source, for each table, for each partition, for each record, checking schema, validating data, applying transforms, handling errors, with conditionals at each level.",
                "Write a Python eligibility checker with nesting: if application complete then if identity verified then if employment confirmed then if income validated then if credit checked then if debt ratio acceptable then if collateral valued then if underwriting approved then issue decision."
            ]
        },

        "global_state": {
            "basic": [
                "Write a Python module using global variables current_user, db_connection, config, logger, and cache that are accessed throughout multiple functions.",
                "Write a Python module with a global SETTINGS dictionary that multiple functions read from and write to without synchronization.",
                "Write a Python module using global counters request_count, error_count, success_count that are incremented by various functions.",
                "Write a Python module with global STATE variable that tracks application state and is modified by functions throughout the codebase.",
                "Write a Python module using globals for api_client, session, rate_limiter that are initialized once and used everywhere."
            ],
            "intermediate": [
                "Write a Python e-commerce module using globals: current_cart, active_session, user_preferences, applied_promotions, inventory_cache that are read and modified by order processing, checkout, and inventory functions.",
                "Write a Python financial module using global variables: market_data_cache, position_tracker, trade_log, risk_metrics, account_balances accessed and modified throughout trading, reporting, and risk functions.",
                "Write a Python healthcare module using globals: current_patient, active_encounter, medication_list, clinical_context, user_permissions shared across scheduling, documentation, and billing functions.",
                "Write a Python analytics module using globals: data_cache, computed_metrics, active_queries, report_state, user_filters modified by dashboard, reporting, and data access functions.",
                "Write a Python API module using globals: rate_limit_state, auth_tokens, request_context, response_cache, circuit_breaker_state shared across handlers."
            ],
            "advanced": [
                "Write a Python trading system using extensive globals: order_book_cache, position_state, risk_exposure, pnl_tracker, execution_state, market_status, connection_pool, subscription_state, strategy_parameters, and audit_log accessed and modified by order management, execution, risk, and reporting modules.",
                "Write a Python clinical system using globals: patient_context, encounter_state, medication_orders, allergy_alerts, clinical_decision_support_state, billing_context, scheduling_state, provider_context, and audit_trail shared across registration, clinical, pharmacy, and billing modules.",
                "Write a Python ERP system using globals: transaction_context, inventory_state, procurement_cache, manufacturing_queue, sales_pipeline, financial_period, integration_status, workflow_state, and notification_queue modified by procurement, manufacturing, sales, and finance modules.",
                "Write a Python research platform using globals: experiment_context, data_pipeline_state, computation_cache, result_accumulator, resource_allocation, collaboration_state, publication_queue, and reproducibility_tracker shared across experiment, analysis, and publication modules."
            ]
        },

        "shotgun_surgery": {
            "basic": [
                "Write a Python module where changing the date format requires modifying display_date, store_date, parse_date, format_report_date, export_date functions across multiple files.",
                "Write a Python module where adding a new user field requires changes in User class, UserForm, UserSerializer, UserValidator, UserRepository, and user templates.",
                "Write a Python module where changing tax calculation logic requires updates in Order, Invoice, Cart, Checkout, Receipt, and Report classes.",
                "Write a Python module where modifying logging format requires changes in api_handler, data_processor, scheduler, notifier, and reporting modules.",
                "Write a Python module where updating error codes requires modifications across exception classes, handlers, responses, documentation, and client libraries."
            ],
            "intermediate": [
                "Write a Python e-commerce system where adding a new payment method requires changes in Payment model, PaymentForm, PaymentProcessor, CheckoutFlow, OrderConfirmation, Receipt, RefundHandler, ReportGenerator, and payment templates across 10+ files.",
                "Write a Python financial system where adding a new currency requires modifications in Amount class, ExchangeService, Transaction model, Statement generator, Report formatter, API serializers, and UI components.",
                "Write a Python healthcare system where adding a new insurance type requires updates in Coverage model, EligibilityChecker, ClaimProcessor, BillingCalculator, StatementGenerator, and multiple report classes.",
                "Write a Python analytics system where adding a new metric requires changes in DataCollector, MetricCalculator, Dashboard, Report, Export, Alert, and API response classes.",
                "Write a Python CMS where adding a content field requires updates in Model, Form, Serializer, Template, Search indexer, Export handler, and API views."
            ],
            "advanced": [
                "Write a Python trading system where adding a new order type requires modifications in Order model, OrderValidator, OrderRouter, ExecutionHandler, RiskCalculator, PositionTracker, SettlementProcessor, ComplianceChecker, ReportGenerator, AuditLogger, and client API across 20+ files.",
                "Write a Python insurance system where adding a new coverage type requires changes in Policy model, Quote engine, Underwriting rules, Premium calculator, Claim processor, Billing system, Renewal handler, Compliance reporter, Agent portal, and Customer portal.",
                "Write a Python clinical system where adding a new vital sign requires updates in Measurement model, DataCapture, Validation rules, Clinical displays, Trending charts, Alerts, Documentation, Billing codes, Quality measures, and Research exports.",
                "Write a Python ERP system where adding a new entity status requires modifications in Entity model, StatusTransitions, Workflow engine, Notification handlers, Report filters, API responses, UI components, Export handlers, and Audit logging.",
                "Write a Python research platform where adding a new data type requires changes in DataModel, ValidationRules, StorageAdapter, ProcessingPipeline, VisualizationEngine, ExportFormats, MetadataSchema, SearchIndexer, and ComplianceChecker."
            ]
        }
    }

    # Add default templates for any missing smell keys
    default_templates = {
        "basic": [
            f"Write a Python function demonstrating {{domain_lower}} {smell_key.replace('_', ' ')} patterns.",
            f"Implement a {{domain}} module that exhibits {smell_key.replace('_', ' ')} characteristics.",
            f"Write Python code for {{domain_lower}} that shows {smell_key.replace('_', ' ')} smell patterns."
        ],
        "intermediate": [
            f"Write a comprehensive Python {{domain_lower}} system that demonstrates {smell_key.replace('_', ' ')} across multiple components.",
            f"Implement a {{domain}} application showing complex {smell_key.replace('_', ' ')} patterns in business logic."
        ],
        "advanced": [
            f"Design and implement an enterprise-scale Python {{domain_lower}} platform exhibiting significant {smell_key.replace('_', ' ')} in architecture.",
            f"Write a comprehensive {{domain}} system demonstrating advanced {smell_key.replace('_', ' ')} patterns across the entire codebase."
        ]
    }

    if smell_key not in templates:
        return default_templates

    return templates[smell_key]


def generate_core_dataset():
    """Generate the core dataset of 450 prompts."""
    all_prompts = []
    smell_definitions = create_code_smell_definitions()

    for smell_key, smell_info in smell_definitions.items():
        prompts = generate_prompts_for_smell(smell_key, smell_info)
        all_prompts.extend(prompts)

    return all_prompts


def generate_synthetic_expansions(core_prompts: List[Dict], target_count: int = 50) -> List[Dict]:
    """Generate synthetic prompt expansions through controlled variations."""
    synthetic_prompts = []

    # Domain swapping variations
    for prompt in core_prompts[:target_count]:
        new_domain = DOMAINS[(DOMAINS.index(prompt["domain"]) + 1) % len(DOMAINS)]

        # Create domain-swapped variant
        new_prompt = prompt.copy()
        new_prompt["id"] = f"synthetic_{prompt['id']}"
        new_prompt["domain"] = new_domain
        new_prompt["synthetic"] = True

        # Update prompt text with new domain context
        domain_replacements = {
            "E-commerce": ["e-commerce", "online store", "shopping", "retail", "marketplace"],
            "Finance": ["financial", "banking", "trading", "investment", "accounting"],
            "Healthcare": ["healthcare", "medical", "clinical", "patient", "hospital"],
            "Scientific Computing": ["scientific", "research", "laboratory", "experiment", "analysis"],
            "General Software": ["application", "system", "software", "platform", "service"]
        }

        old_terms = domain_replacements.get(prompt["domain"], [])
        new_terms = domain_replacements.get(new_domain, [])

        new_text = prompt["prompt"]
        for old, new in zip(old_terms[:3], new_terms[:3]):
            new_text = new_text.replace(old, new)

        new_prompt["prompt"] = new_text
        synthetic_prompts.append(new_prompt)

    return synthetic_prompts


def create_metadata(prompts: List[Dict]) -> Dict:
    """Create metadata summary for the dataset."""
    metadata = {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "methodology": "Based on arXiv:2503.10666",
        "total_prompts": len(prompts),
        "code_smell_categories": list(create_code_smell_definitions().keys()),
        "complexity_levels": COMPLEXITY_LEVELS,
        "domains": DOMAINS,
        "action_keywords": ACTION_KEYWORDS,
        "prompt_types": PROMPT_TYPES,
        "statistics": {
            "by_complexity": {},
            "by_domain": {},
            "by_smell": {},
            "synthetic_count": 0,
            "core_count": 0
        }
    }

    # Calculate statistics
    for prompt in prompts:
        # By complexity
        complexity = prompt["complexity"]
        metadata["statistics"]["by_complexity"][complexity] = \
            metadata["statistics"]["by_complexity"].get(complexity, 0) + 1

        # By domain
        domain = prompt["domain"]
        metadata["statistics"]["by_domain"][domain] = \
            metadata["statistics"]["by_domain"].get(domain, 0) + 1

        # By smell
        for smell in prompt["code_smells"]:
            metadata["statistics"]["by_smell"][smell] = \
                metadata["statistics"]["by_smell"].get(smell, 0) + 1

        # Synthetic vs core
        if prompt["synthetic"]:
            metadata["statistics"]["synthetic_count"] += 1
        else:
            metadata["statistics"]["core_count"] += 1

    return metadata


def export_to_csv(prompts: List[Dict], filepath: str):
    """Export prompts to CSV format."""
    if not prompts:
        return

    fieldnames = ["id", "prompt", "code_smells", "complexity", "action_keywords",
                  "domain", "prompt_type", "expected_token_depth", "synthetic"]

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for prompt in prompts:
            row = prompt.copy()
            # Convert lists to semicolon-separated strings for CSV
            row["code_smells"] = ";".join(row["code_smells"])
            row["action_keywords"] = ";".join(row["action_keywords"])
            writer.writerow(row)


def main():
    """Main function to generate the complete dataset."""
    random.seed(42)  # For reproducibility

    dataset_dir = "/Users/rosawu/Documents/code-smell/dataset"

    print("Generating core dataset...")
    core_prompts = generate_core_dataset()
    print(f"Generated {len(core_prompts)} core prompts")

    print("Generating synthetic expansions...")
    synthetic_prompts = generate_synthetic_expansions(core_prompts)
    print(f"Generated {len(synthetic_prompts)} synthetic prompts")

    # Save core prompts
    print("Saving core prompts...")
    with open(f"{dataset_dir}/prompts_core.json", 'w', encoding='utf-8') as f:
        json.dump(core_prompts, f, indent=2, ensure_ascii=False)
    export_to_csv(core_prompts, f"{dataset_dir}/prompts_core.csv")

    # Save synthetic prompts
    print("Saving synthetic prompts...")
    with open(f"{dataset_dir}/prompts_synthetic.json", 'w', encoding='utf-8') as f:
        json.dump(synthetic_prompts, f, indent=2, ensure_ascii=False)
    export_to_csv(synthetic_prompts, f"{dataset_dir}/prompts_synthetic.csv")

    # Create and save metadata
    print("Creating metadata...")
    all_prompts = core_prompts + synthetic_prompts
    metadata = create_metadata(all_prompts)
    with open(f"{dataset_dir}/metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "="*50)
    print("DATASET GENERATION COMPLETE")
    print("="*50)
    print(f"Total prompts: {len(all_prompts)}")
    print(f"  - Core prompts: {len(core_prompts)}")
    print(f"  - Synthetic prompts: {len(synthetic_prompts)}")
    print(f"\nFiles created in {dataset_dir}:")
    print("  - prompts_core.json")
    print("  - prompts_core.csv")
    print("  - prompts_synthetic.json")
    print("  - prompts_synthetic.csv")
    print("  - metadata.json")
    print("\nDistribution by complexity:")
    for level, count in metadata["statistics"]["by_complexity"].items():
        print(f"  - {level}: {count}")
    print("\nDistribution by domain:")
    for domain, count in metadata["statistics"]["by_domain"].items():
        print(f"  - {domain}: {count}")


if __name__ == "__main__":
    main()
