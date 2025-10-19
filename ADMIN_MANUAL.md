# REIMS Admin User Manual

## 👤 Admin Overview

As a REIMS administrator, you have full access to system management, property operations, tenant management, financial tracking, and analytics. This manual covers all administrative tasks and responsibilities.

## 🚀 Getting Started

### System Access
1. **Start the System**: Follow the [Startup Guide](STARTUP_GUIDE.md)
2. **Access Admin Dashboard**: http://localhost:5175/admin
3. **API Documentation**: http://localhost:8000/docs

### Admin Credentials
- **Development**: No authentication required
- **Production**: Contact system administrator for credentials

## 🏢 Property Management

### Adding New Properties

#### Step-by-Step Process
1. **Navigate to Properties**: http://localhost:5175/properties
2. **Click "Add Property"**
3. **Fill Required Information**:
   - Property Code (unique identifier)
   - Property Name
   - Complete Address
   - Property Type (Residential, Commercial, Industrial, etc.)
   - Square Footage
   - Number of Bedrooms/Bathrooms
   - Monthly Rent Amount

#### API Endpoint
```bash
POST /properties
Content-Type: application/json

{
  "property_code": "PROP001",
  "name": "Sunset Apartments Unit 1A",
  "address": "123 Main Street",
  "city": "Downtown",
  "state": "CA",
  "zip_code": "90210",
  "country": "USA",
  "property_type": "residential",
  "status": "available",
  "square_footage": 1200.5,
  "bedrooms": 2,
  "bathrooms": 2.0,
  "parking_spaces": 1,
  "monthly_rent": 2500.00,
  "description": "Modern 2BR apartment with city views"
}
```

### Property Status Management

#### Available Statuses
- **Available**: Ready for new tenants
- **Occupied**: Currently leased
- **Maintenance**: Under repair/renovation
- **Unavailable**: Temporarily off-market

#### Updating Property Status
```bash
PUT /properties/{property_id}
{
  "status": "occupied",
  "monthly_rent": 2600.00
}
```

### Property Analytics
- **Access**: http://localhost:5175/analytics/properties
- **Performance Metrics**: Revenue, occupancy rates, maintenance costs
- **Individual Property Reports**: `/analytics/property/{property_id}/performance`

## 👥 Tenant Management

### Adding New Tenants

#### Required Information
- Personal Details (Name, Email, Phone)
- Emergency Contact Information
- Employment Details
- Income Verification
- Credit Score (if available)
- Background Check Status

#### Create Tenant Profile
```bash
POST /tenants
{
  "tenant_code": "TEN001",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@email.com",
  "phone": "555-123-4567",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "555-987-6543",
  "emergency_contact_relationship": "Spouse",
  "employer": "Tech Corp Inc",
  "monthly_income": 5000.00,
  "credit_score": 750
}
```

### Tenant Screening Process
1. **Application Review**: Verify all submitted information
2. **Background Check**: Run credit and criminal background checks
3. **Income Verification**: Confirm employment and income
4. **Reference Check**: Contact previous landlords
5. **Approval Decision**: Approve or deny application

### Tenant Communication
- **Email Notifications**: Rent reminders, lease renewals
- **Maintenance Requests**: Track and respond to tenant requests
- **Document Sharing**: Lease agreements, notices, receipts

## 📋 Lease Management

### Creating New Leases

#### Lease Setup Process
1. **Select Property**: Choose available property
2. **Select Tenant**: Choose approved tenant
3. **Set Lease Terms**:
   - Start and End Dates
   - Monthly Rent Amount
   - Security Deposit
   - Late Fees
   - Pet Deposits (if applicable)
   - Auto-renewal Terms

#### Create Lease Agreement
```bash
POST /leases
{
  "lease_number": "LEASE001",
  "property_id": 1,
  "tenant_id": 1,
  "start_date": "2025-11-01",
  "end_date": "2026-10-31",
  "monthly_rent": 2500.00,
  "security_deposit": 2500.00,
  "late_fee": 50.00,
  "pet_deposit": 300.00,
  "lease_type": "fixed_term",
  "auto_renewal": true,
  "notice_period_days": 30,
  "rent_due_day": 1
}
```

### Lease Renewal Process
1. **Review Current Lease**: 60 days before expiration
2. **Market Analysis**: Check current rental rates
3. **Tenant Communication**: Discuss renewal terms
4. **New Lease Creation**: Update terms and extend dates
5. **Documentation**: Sign and file new lease agreement

### Lease Termination
1. **Notice Period**: Ensure proper notice given
2. **Property Inspection**: Schedule move-out inspection
3. **Security Deposit**: Calculate return amount
4. **Final Accounting**: Process final bills and payments
5. **Property Preparation**: Ready for next tenant

## 🔧 Maintenance Management

### Maintenance Request Workflow

#### Creating Maintenance Requests
```bash
POST /maintenance
{
  "request_number": "MAINT001",
  "property_id": 1,
  "title": "Kitchen Faucet Leak",
  "description": "Kitchen faucet has been dripping for 3 days",
  "category": "Plumbing",
  "priority": "medium",
  "tenant_id": 1,
  "estimated_cost": 150.00
}
```

#### Priority Levels
- **Emergency**: Safety hazards, major systems failure
- **High**: Significant impact on habitability
- **Medium**: Standard repairs and improvements
- **Low**: Cosmetic issues, non-urgent items

#### Maintenance Categories
- Plumbing
- Electrical
- HVAC
- Appliances
- Structural
- Cosmetic
- Landscaping
- Security

### Vendor Management
1. **Vendor Database**: Maintain approved contractor list
2. **Work Orders**: Assign requests to appropriate vendors
3. **Quality Control**: Inspect completed work
4. **Cost Tracking**: Monitor maintenance expenses
5. **Performance Reviews**: Rate vendor performance

### Preventive Maintenance
- **HVAC Systems**: Quarterly inspections
- **Plumbing**: Annual pipe inspections
- **Electrical**: Bi-annual safety checks
- **Appliances**: Regular servicing schedules
- **Fire Safety**: Monthly alarm tests

## 💰 Financial Management

### Recording Financial Transactions

#### Transaction Types
- **Income**: Rent payments, deposits, fees
- **Expenses**: Maintenance, utilities, insurance
- **Refunds**: Security deposit returns
- **Transfers**: Between properties or accounts

#### Create Financial Transaction
```bash
POST /financial
{
  "transaction_number": "TXN001",
  "property_id": 1,
  "transaction_type": "income",
  "category": "rent_payment",
  "amount": 2500.00,
  "description": "November 2025 rent payment",
  "transaction_date": "2025-11-01",
  "payment_method": "bank_transfer",
  "reference_number": "BT123456"
}
```

### Rent Collection
1. **Monthly Invoicing**: Generate rent invoices
2. **Payment Tracking**: Monitor payment status
3. **Late Fee Assessment**: Apply late fees automatically
4. **Collection Actions**: Follow up on overdue payments
5. **Payment Processing**: Record all payments

### Financial Reporting
- **Monthly P&L**: Property-wise profit and loss
- **Cash Flow**: Track incoming and outgoing funds
- **Expense Analysis**: Categorize and analyze expenses
- **Tax Reporting**: Generate tax-ready reports
- **Budget vs Actual**: Compare planned vs actual expenses

## 📊 Analytics & Reporting

### Dashboard Overview
**Access**: http://localhost:5175/analytics/dashboard

#### Key Metrics
- Total Properties
- Occupied vs Vacant Units
- Monthly Revenue
- Outstanding Maintenance Requests
- Tenant Satisfaction Scores
- Average Rent per Unit

### Financial Analytics
```bash
GET /analytics/dashboard
```

#### Available Reports
- **Occupancy Rates**: Track vacancy trends
- **Revenue Analysis**: Monthly and annual revenue
- **Expense Breakdown**: Maintenance, utilities, other costs
- **Property Performance**: ROI and cash flow by property
- **Market Analysis**: Rent comparisons and trends

### Document Analytics
```bash
GET /api/analytics/documents
```

#### Document Metrics
- Total Documents Uploaded
- Processing Status
- Document Types
- Storage Usage
- Processing Time Analytics

## 📄 Document Management

### Document Upload Process
1. **Access Upload Portal**: http://localhost:5175/documents
2. **Select Files**: Choose documents to upload
3. **Add Metadata**: Property ID, document type, description
4. **Process Documents**: AI extraction of key information
5. **Review Results**: Verify extracted data accuracy

### Document Organization
- **Property Documents**: Leases, inspections, photos
- **Tenant Documents**: Applications, background checks
- **Financial Documents**: Receipts, invoices, statements
- **Legal Documents**: Notices, court documents
- **Maintenance Documents**: Work orders, receipts

### AI Document Processing
```bash
POST /process/{document_id}
```

#### Automated Extraction
- **Lease Information**: Dates, amounts, terms
- **Financial Data**: Invoice amounts, dates, vendors
- **Property Details**: Square footage, amenities
- **Contact Information**: Names, phone numbers, emails

## ⚙️ System Administration

### User Management
- **Create Admin Accounts**: Add new administrators
- **Role Assignment**: Define user permissions
- **Access Control**: Manage feature access
- **Password Policies**: Enforce security standards

### System Monitoring
#### Health Checks
```bash
GET /health
GET /analytics/health
GET /queue/health
GET /storage/health
```

#### Performance Monitoring
- **Response Times**: API endpoint performance
- **Queue Status**: Background job processing
- **Storage Usage**: Database and file storage
- **Error Rates**: System error monitoring

### Backup & Recovery
1. **Database Backup**: Regular SQLite database backups
2. **Document Backup**: File storage backups
3. **Configuration Backup**: System settings backup
4. **Recovery Testing**: Regular backup validation

### System Updates
1. **Update Planning**: Schedule maintenance windows
2. **Backup Creation**: Pre-update system backup
3. **Update Execution**: Apply system updates
4. **Testing**: Verify system functionality
5. **Rollback Plan**: Ready rollback procedures

## 🔒 Security Management

### Data Protection
- **Sensitive Information**: Secure handling of personal data
- **Document Security**: Encrypted document storage
- **Access Logging**: Track user access and actions
- **Data Retention**: Implement retention policies

### Compliance
- **Privacy Laws**: GDPR, CCPA compliance
- **Financial Regulations**: SOX compliance for financial data
- **Housing Laws**: Fair housing act compliance
- **Data Security**: Industry security standards

## 📞 Support & Troubleshooting

### Common Admin Tasks
1. **Reset Tenant Portal**: Help tenants with login issues
2. **Maintenance Tracking**: Update request statuses
3. **Report Generation**: Create custom reports
4. **Data Import**: Bulk import property/tenant data
5. **System Configuration**: Adjust system settings

### Emergency Procedures
1. **System Outage**: Contact technical support
2. **Data Loss**: Initiate backup recovery
3. **Security Breach**: Follow incident response plan
4. **Payment Issues**: Process manual payments
5. **Tenant Emergencies**: 24/7 contact procedures

### Support Contacts
- **Technical Support**: IT department
- **Vendor Support**: Maintenance contractors
- **Legal Support**: Property law attorneys
- **Financial Support**: Accounting department

## 📋 Best Practices

### Daily Tasks
- [ ] Review new maintenance requests
- [ ] Check rent payment status
- [ ] Monitor system health
- [ ] Respond to tenant communications
- [ ] Update property statuses

### Weekly Tasks
- [ ] Generate financial reports
- [ ] Review analytics dashboard
- [ ] Process vendor invoices
- [ ] Conduct property inspections
- [ ] Update lease information

### Monthly Tasks
- [ ] Generate monthly P&L reports
- [ ] Review maintenance costs
- [ ] Analyze occupancy rates
- [ ] Update market rent analysis
- [ ] Backup system data

### Annual Tasks
- [ ] Lease renewal reviews
- [ ] Tax report generation
- [ ] System security audit
- [ ] Vendor performance review
- [ ] Insurance policy reviews