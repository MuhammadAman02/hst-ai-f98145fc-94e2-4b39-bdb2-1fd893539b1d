import os
import sys
from nicegui import ui, app
from datetime import datetime
import uuid
from enum import Enum

# Add the current directory to the path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import validation services and models
from app.models.document import Document, DocumentType, ValidationResult
from app.services.validation_engine import validate_document, get_validation_rules

# Configure app
app.title = "Document Validation System - Credit Union Fraud Detection"
app.favicon = "🔍"

# Set up static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static')
app.add_static_files('/static', static_dir)

# Global state
current_documents = []
validation_results = []

# Define UI components
@ui.page('/')
def index():
    with ui.column().classes('w-full max-w-screen-xl mx-auto p-4'):
        # Header
        with ui.row().classes('w-full justify-between items-center'):
            ui.image('/static/img/logo.png').classes('h-12')
            ui.label('Document Validation System').classes('text-2xl font-bold text-blue-800')
            ui.label('Credit Union Fraud Detection').classes('text-lg text-gray-600')
        
        ui.separator()
        
        # Main content
        with ui.tabs().classes('w-full') as tabs:
            upload_tab = ui.tab('Document Upload')
            validation_tab = ui.tab('Validation Rules')
            results_tab = ui.tab('Validation Results')
        
        with ui.tab_panels(tabs, value=upload_tab).classes('w-full'):
            # Upload Panel
            with ui.tab_panel(upload_tab):
                with ui.card().classes('w-full'):
                    ui.label('Upload Documents for Validation').classes('text-xl font-bold mb-4')
                    
                    # Document type selection
                    doc_type = ui.select(
                        label='Document Type',
                        options=[
                            {'label': 'Bank Statement', 'value': DocumentType.BANK_STATEMENT},
                            {'label': 'Payslip', 'value': DocumentType.PAYSLIP},
                            {'label': 'Irish Residency Permit (IRP)', 'value': DocumentType.IRP},
                            {'label': 'PPSN Document', 'value': DocumentType.PPSN},
                            {'label': 'Tax Record', 'value': DocumentType.TAX_RECORD}
                        ],
                        value=DocumentType.BANK_STATEMENT
                    ).classes('w-full mb-4')
                    
                    # Mock document data inputs
                    with ui.column().classes('w-full gap-4'):
                        customer_name = ui.input(label='Customer Name').classes('w-full')
                        customer_dob = ui.date(label='Date of Birth').classes('w-full')
                        customer_address = ui.input(label='Address').classes('w-full')
                        
                        # Conditional fields based on document type
                        bank_fields = ui.column().classes('w-full gap-4')
                        payslip_fields = ui.column().classes('w-full gap-4')
                        irp_fields = ui.column().classes('w-full gap-4')
                        ppsn_fields = ui.column().classes('w-full gap-4')
                        tax_fields = ui.column().classes('w-full gap-4')
                        
                        with bank_fields:
                            ui.label('Bank Statement Details').classes('font-bold')
                            account_number = ui.input(label='Account Number (IBAN)').classes('w-full')
                            opening_balance = ui.number(label='Opening Balance (€)', format='%.2f').classes('w-full')
                            closing_balance = ui.number(label='Closing Balance (€)', format='%.2f').classes('w-full')
                            statement_date = ui.date(label='Statement Date').classes('w-full')
                        
                        with payslip_fields:
                            ui.label('Payslip Details').classes('font-bold')
                            employer_name = ui.input(label='Employer Name').classes('w-full')
                            gross_pay = ui.number(label='Gross Pay (€)', format='%.2f').classes('w-full')
                            net_pay = ui.number(label='Net Pay (€)', format='%.2f').classes('w-full')
                            pay_date = ui.date(label='Pay Date').classes('w-full')
                            
                        with irp_fields:
                            ui.label('IRP Details').classes('font-bold')
                            irp_number = ui.input(label='IRP Number').classes('w-full')
                            nationality = ui.input(label='Nationality').classes('w-full')
                            expiry_date = ui.date(label='Expiry Date').classes('w-full')
                            
                        with ppsn_fields:
                            ui.label('PPSN Details').classes('font-bold')
                            ppsn_number = ui.input(label='PPSN Number').classes('w-full')
                            issue_date = ui.date(label='Issue Date').classes('w-full')
                            
                        with tax_fields:
                            ui.label('Tax Record Details').classes('font-bold')
                            tax_year = ui.input(label='Tax Year').classes('w-full')
                            total_income = ui.number(label='Total Income (€)', format='%.2f').classes('w-full')
                            tax_paid = ui.number(label='Tax Paid (€)', format='%.2f').classes('w-full')
                    
                    # Show/hide relevant fields based on document type
                    def update_visible_fields():
                        doc_type_value = doc_type.value
                        bank_fields.visible = doc_type_value == DocumentType.BANK_STATEMENT
                        payslip_fields.visible = doc_type_value == DocumentType.PAYSLIP
                        irp_fields.visible = doc_type_value == DocumentType.IRP
                        ppsn_fields.visible = doc_type_value == DocumentType.PPSN
                        tax_fields.visible = doc_type_value == DocumentType.TAX_RECORD
                    
                    doc_type.on_change(update_visible_fields)
                    update_visible_fields()
                    
                    # Add document button
                    def add_document():
                        doc_id = str(uuid.uuid4())
                        doc_type_value = doc_type.value
                        
                        # Common document data
                        doc_data = {
                            'id': doc_id,
                            'type': doc_type_value,
                            'customer_name': customer_name.value,
                            'customer_dob': customer_dob.value.isoformat() if customer_dob.value else None,
                            'customer_address': customer_address.value,
                            'upload_date': datetime.now().isoformat()
                        }
                        
                        # Add document-specific data
                        if doc_type_value == DocumentType.BANK_STATEMENT:
                            doc_data.update({
                                'account_number': account_number.value,
                                'opening_balance': opening_balance.value,
                                'closing_balance': closing_balance.value,
                                'statement_date': statement_date.value.isoformat() if statement_date.value else None
                            })
                        elif doc_type_value == DocumentType.PAYSLIP:
                            doc_data.update({
                                'employer_name': employer_name.value,
                                'gross_pay': gross_pay.value,
                                'net_pay': net_pay.value,
                                'pay_date': pay_date.value.isoformat() if pay_date.value else None
                            })
                        elif doc_type_value == DocumentType.IRP:
                            doc_data.update({
                                'irp_number': irp_number.value,
                                'nationality': nationality.value,
                                'expiry_date': expiry_date.value.isoformat() if expiry_date.value else None
                            })
                        elif doc_type_value == DocumentType.PPSN:
                            doc_data.update({
                                'ppsn_number': ppsn_number.value,
                                'issue_date': issue_date.value.isoformat() if issue_date.value else None
                            })
                        elif doc_type_value == DocumentType.TAX_RECORD:
                            doc_data.update({
                                'tax_year': tax_year.value,
                                'total_income': total_income.value,
                                'tax_paid': tax_paid.value
                            })
                        
                        # Create document object
                        document = Document(**doc_data)
                        current_documents.append(document)
                        
                        # Update document list
                        update_document_list()
                        
                        # Show success notification
                        ui.notify(f'{doc_type_value.value} added successfully', type='positive')
                    
                    ui.button('Add Document', on_click=add_document).classes('bg-blue-500 text-white')
                
                # Document list
                with ui.card().classes('w-full mt-4'):
                    ui.label('Uploaded Documents').classes('text-xl font-bold mb-4')
                    documents_container = ui.column().classes('w-full')
                    
                    def update_document_list():
                        documents_container.clear()
                        
                        if not current_documents:
                            with documents_container:
                                ui.label('No documents uploaded yet').classes('text-gray-500 italic')
                        else:
                            for doc in current_documents:
                                with documents_container:
                                    with ui.card().classes('w-full mb-2 bg-gray-50'):
                                        with ui.row().classes('justify-between items-center'):
                                            ui.label(f"{doc.type.value}: {doc.customer_name}").classes('font-bold')
                                            
                                            with ui.row().classes('gap-2'):
                                                ui.button('View', on_click=lambda d=doc: view_document(d)).classes('bg-blue-500 text-white')
                                                ui.button('Remove', on_click=lambda d=doc: remove_document(d)).classes('bg-red-500 text-white')
                    
                    def view_document(doc):
                        ui.notify(f'Viewing document: {doc.id}')
                        # In a full implementation, this would show document details
                    
                    def remove_document(doc):
                        current_documents.remove(doc)
                        update_document_list()
                        ui.notify(f'Document removed', type='warning')
                    
                    update_document_list()
                
                # Validation button
                with ui.card().classes('w-full mt-4'):
                    ui.label('Run Validation').classes('text-xl font-bold mb-4')
                    
                    def run_validation():
                        if not current_documents:
                            ui.notify('No documents to validate', type='negative')
                            return
                        
                        # Clear previous results
                        validation_results.clear()
                        
                        # Run validation on each document
                        for doc in current_documents:
                            result = validate_document(doc)
                            validation_results.append(result)
                        
                        # Switch to results tab
                        tabs.set_value(results_tab)
                        update_results_display()
                        
                        ui.notify(f'Validation completed for {len(validation_results)} documents', type='positive')
                    
                    ui.button('Validate All Documents', on_click=run_validation).classes('bg-green-600 text-white')
            
            # Validation Rules Panel
            with ui.tab_panel(validation_tab):
                with ui.card().classes('w-full'):
                    ui.label('Document Validation Rules').classes('text-xl font-bold mb-4')
                    
                    # Display validation rules for each document type
                    with ui.tabs().classes('w-full') as rule_tabs:
                        for doc_type in DocumentType:
                            ui.tab(doc_type.value)
                    
                    with ui.tab_panels(rule_tabs).classes('w-full'):
                        for doc_type in DocumentType:
                            with ui.tab_panel(ui.tab(doc_type.value)):
                                rules = get_validation_rules(doc_type)
                                
                                with ui.table().classes('w-full').style('border-collapse: collapse'):
                                    ui.table.header(('Rule Category', 'Description', 'Severity'))
                                    for rule in rules:
                                        ui.table.row((
                                            rule['category'],
                                            rule['description'],
                                            rule['severity']
                                        ))
            
            # Results Panel
            with ui.tab_panel(results_tab):
                results_container = ui.column().classes('w-full')
                
                def update_results_display():
                    results_container.clear()
                    
                    if not validation_results:
                        with results_container:
                            ui.label('No validation results yet').classes('text-gray-500 italic')
                    else:
                        with results_container:
                            # Summary card
                            with ui.card().classes('w-full mb-4 bg-blue-50'):
                                ui.label('Validation Summary').classes('text-xl font-bold mb-2')
                                
                                total_issues = sum(len(result.issues) for result in validation_results)
                                high_severity = sum(1 for result in validation_results for issue in result.issues if issue.severity == 'HIGH')
                                medium_severity = sum(1 for result in validation_results for issue in result.issues if issue.severity == 'MEDIUM')
                                low_severity = sum(1 for result in validation_results for issue in result.issues if issue.severity == 'LOW')
                                
                                with ui.row().classes('gap-4'):
                                    with ui.card().classes('bg-white'):
                                        ui.label('Documents').classes('font-bold')
                                        ui.label(str(len(validation_results)))
                                    
                                    with ui.card().classes('bg-white'):
                                        ui.label('Total Issues').classes('font-bold')
                                        ui.label(str(total_issues))
                                    
                                    with ui.card().classes('bg-red-100'):
                                        ui.label('High Severity').classes('font-bold text-red-700')
                                        ui.label(str(high_severity)).classes('text-red-700')
                                    
                                    with ui.card().classes('bg-yellow-100'):
                                        ui.label('Medium Severity').classes('font-bold text-yellow-700')
                                        ui.label(str(medium_severity)).classes('text-yellow-700')
                                    
                                    with ui.card().classes('bg-blue-100'):
                                        ui.label('Low Severity').classes('font-bold text-blue-700')
                                        ui.label(str(low_severity)).classes('text-blue-700')
                            
                            # Individual results
                            for result in validation_results:
                                with ui.card().classes('w-full mb-4'):
                                    with ui.row().classes('justify-between items-center'):
                                        ui.label(f"{result.document_type.value}: {result.customer_name}").classes('text-lg font-bold')
                                        
                                        # Status indicator
                                        status_color = 'bg-green-500' if not result.issues else 'bg-red-500'
                                        status_text = 'VALID' if not result.issues else 'ISSUES DETECTED'
                                        ui.label(status_text).classes(f'{status_color} text-white px-2 py-1 rounded')
                                    
                                    ui.separator()
                                    
                                    if not result.issues:
                                        ui.label('No issues detected').classes('text-green-600')
                                    else:
                                        ui.label(f'Issues Detected: {len(result.issues)}').classes('font-bold mt-2')
                                        
                                        with ui.table().classes('w-full').style('border-collapse: collapse'):
                                            ui.table.header(('Severity', 'Category', 'Description', 'Recommendation'))
                                            
                                            for issue in result.issues:
                                                severity_class = {
                                                    'HIGH': 'bg-red-100 text-red-800',
                                                    'MEDIUM': 'bg-yellow-100 text-yellow-800',
                                                    'LOW': 'bg-blue-100 text-blue-800'
                                                }.get(issue.severity, '')
                                                
                                                ui.table.row((
                                                    ui.html(f'<span class="px-2 py-1 rounded {severity_class}">{issue.severity}</span>'),
                                                    issue.category,
                                                    issue.description,
                                                    issue.recommendation
                                                ))
                
                update_results_display()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Document Validation System", port=8000)