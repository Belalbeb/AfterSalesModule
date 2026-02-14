{
    "name": "After Sales",
    "version": "1.0",
    "description": "This module offers after sales services",
    "author": "Bebo",
    "category": "Services",
    "license": "LGPL-3",
    "depends": ["base", "product", "stock", "hr", "sale", "purchase","product_family","model", "mail"],
    "data": [
        "data/sequence_data.xml",
        "data/device_status_data.xml",
        "data/email_template_data.xml",
        "views/Maintenance_Ticket.xml",
        "views/product_assigned.xml",
        "views/wizard.xml",
        "views/maintenance_visit.xml",
    
    ],
    "installable": True,
    "application": True
}