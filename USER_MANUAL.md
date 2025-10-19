# REIMS End User Manual

## 👤 End User Overview

As a REIMS end user (tenant, property owner, or general user), you have access to document management, property information, maintenance requests, and reporting features. This manual guides you through all available features.

## 🚀 Getting Started

### System Access
1. **Access Application**: http://localhost:5175
2. **Login**: Use provided credentials (development mode has no login)
3. **Dashboard**: Your main hub for all activities

### User Interface Overview
- **Navigation Menu**: Access main features
- **Dashboard**: Quick overview of your information
- **Search Bar**: Find properties, documents, or data
- **Notifications**: Important updates and alerts

## 📄 Document Management

### Uploading Documents

#### Supported File Types
- **PDF**: Property documents, leases, reports
- **Images**: JPG, PNG property photos, receipts
- **CSV**: Financial data, property listings
- **Excel**: Spreadsheets, financial reports

#### Upload Process
1. **Navigate to Documents**: http://localhost:5175/documents
2. **Click "Upload Documents"**
3. **Select Files**: Choose files from your computer
4. **Add Information**:
   - Document title
   - Document type
   - Property association (if applicable)
   - Description or notes
5. **Upload**: Click "Upload" to start processing

#### API Upload (Advanced Users)
```bash
curl -X POST -F "file=@document.pdf" \
     -F "title=Property Lease" \
     -F "type=lease" \
     http://localhost:8000/api/documents/upload
```

### Document Processing

#### AI-Powered Features
- **Text Extraction**: Automatically extract text from PDFs and images
- **Data Recognition**: Identify key information (dates, amounts, names)
- **Property Matching**: Link documents to relevant properties
- **Financial Data**: Extract financial information from receipts/invoices

#### Processing Status
- **Uploading**: File is being transferred
- **Processing**: AI is analyzing the document
- **Completed**: Processing finished, data available
- **Error**: Processing failed (check file format)

#### Viewing Processed Data
1. **Go to Documents List**
2. **Click on Document**
3. **View "Processed Data" Tab**
4. **Review Extracted Information**
5. **Make Corrections if Needed**

### Document Search & Organization

#### Search Features
- **Text Search**: Search within document content
- **Filter by Type**: Leases, receipts, photos, etc.
- **Date Range**: Find documents by upload/creation date
- **Property Filter**: Show documents for specific properties

#### Organization
- **Folders**: Organize by property, type, or date
- **Tags**: Add custom tags for easy finding
- **Favorites**: Mark important documents
- **Recent**: Quick access to recently viewed documents

## 🏠 Property Information

### Property Search

#### Search Options
- **Location**: Search by address, city, or ZIP code
- **Property Type**: Residential, commercial, industrial
- **Price Range**: Filter by rent or purchase price
- **Features**: Bedrooms, bathrooms, square footage
- **Availability**: Available, occupied, maintenance

#### Property Details
- **Basic Information**: Address, type, size
- **Financial**: Rent amount, deposits, fees
- **Features**: Amenities, parking, utilities
- **Photos**: Property images and virtual tours
- **Documents**: Associated leases, inspections
- **History**: Previous tenants, maintenance records

### Property Comparison
1. **Select Properties**: Choose multiple properties
2. **Compare Features**: Side-by-side comparison
3. **Analyze Costs**: Compare total costs
4. **Review Locations**: Map view with property markers
5. **Generate Report**: Export comparison data

## 🔧 Maintenance Requests

### Submitting Maintenance Requests

#### Request Categories
- **Emergency**: Safety hazards, major system failures
- **Urgent**: Significant impact on daily life
- **Standard**: Regular repairs and maintenance
- **Cosmetic**: Non-essential improvements

#### Request Process
1. **Access Maintenance Portal**: http://localhost:5175/maintenance
2. **Click "New Request"**
3. **Fill Out Form**:
   - Property address
   - Issue category (plumbing, electrical, etc.)
   - Priority level
   - Detailed description
   - Photos (if applicable)
   - Preferred contact method
4. **Submit Request**
5. **Receive Confirmation**: Request number and timeline

#### Request Form Example
```
Property: 123 Main Street, Apt 1A
Category: Plumbing
Priority: Urgent
Subject: Kitchen faucet leak
Description: Kitchen faucet has been leaking for 2 days. 
Water is dripping constantly and getting worse.
Best time to contact: Weekdays 9 AM - 5 PM
Phone: 555-123-4567
```

### Tracking Maintenance Requests

#### Request Status
- **Submitted**: Request received, awaiting review
- **Assigned**: Technician assigned, work scheduled
- **In Progress**: Technician working on issue
- **Completed**: Work finished, ready for review
- **Closed**: Issue resolved, request closed

#### Status Updates
- **Email Notifications**: Automatic status updates
- **SMS Alerts**: Optional text message updates
- **Portal Updates**: Real-time status in your dashboard
- **Technician Contact**: Direct communication with assigned worker

### Work Order Management
1. **Receive Work Order**: Details of scheduled work
2. **Confirm Access**: Arrange property access
3. **Be Present**: Be available during scheduled time
4. **Inspect Work**: Review completed repairs
5. **Provide Feedback**: Rate service quality

## 📊 Personal Dashboard

### Dashboard Widgets

#### Property Information
- **My Properties**: Properties you own or rent
- **Rent Status**: Current rent payment status
- **Lease Information**: Lease terms and renewal dates
- **Property Value**: Current market estimates

#### Document Summary
- **Recent Uploads**: Your latest documents
- **Processing Status**: Documents being processed
- **Storage Usage**: How much storage you're using
- **Quick Actions**: Upload, search, organize

#### Maintenance Overview
- **Active Requests**: Current maintenance issues
- **Request History**: Past maintenance records
- **Upcoming Inspections**: Scheduled property visits
- **Emergency Contacts**: Important phone numbers

#### Financial Summary
- **Payment History**: Rent and fee payments
- **Outstanding Balances**: Any amounts due
- **Expense Tracking**: Your property-related expenses
- **Tax Documents**: Important financial documents

### Customizing Your Dashboard
1. **Widget Selection**: Choose which widgets to display
2. **Layout Options**: Arrange widgets as preferred
3. **Data Preferences**: Select what information to show
4. **Notification Settings**: Configure alert preferences

## 📋 Reports & Analytics

### Available Reports

#### Personal Financial Reports
- **Payment History**: All your payments and dates
- **Expense Summary**: Breakdown of property costs
- **Tax Summary**: Tax-relevant information
- **Budget Analysis**: Compare planned vs actual expenses

#### Property Reports
- **Property Performance**: Rental income and expenses
- **Market Analysis**: Comparable property data
- **Maintenance History**: All repairs and costs
- **Occupancy Reports**: Vacancy and rental periods

#### Document Reports
- **Document Inventory**: List of all your documents
- **Processing Summary**: AI processing results
- **Storage Usage**: File sizes and storage consumption
- **Recent Activity**: Document upload and access history

### Generating Reports
1. **Go to Reports Section**: http://localhost:5175/reports
2. **Select Report Type**: Choose from available options
3. **Set Parameters**:
   - Date range
   - Property selection
   - Data categories
   - Output format (PDF, Excel, CSV)
4. **Generate Report**: Click "Create Report"
5. **Download**: Save report to your computer

### Scheduled Reports
- **Setup Automation**: Receive reports automatically
- **Frequency Options**: Daily, weekly, monthly, quarterly
- **Email Delivery**: Reports sent to your email
- **Custom Filters**: Only include relevant data

## 🔍 Search & Discovery

### Global Search

#### Search Capabilities
- **Document Content**: Search inside document text
- **Property Information**: Find properties by features
- **Financial Data**: Search transactions and payments
- **Maintenance Records**: Find specific repair issues
- **Contact Information**: Search for people and vendors

#### Advanced Search
- **Boolean Operators**: Use AND, OR, NOT
- **Date Ranges**: Specify time periods
- **Property Filters**: Limit to specific properties
- **Document Types**: Filter by file type
- **Amount Ranges**: Search financial data by amount

#### Search Examples
```
Search: "lease agreement" AND 2025
Search: rent amount:2000..3000
Search: maintenance plumbing urgent
Search: date:2025-01-01..2025-12-31
```

### Filters & Sorting
- **Sort Options**: Date, amount, relevance, alphabetical
- **Filter Categories**: Type, status, property, date
- **Save Searches**: Bookmark frequently used searches
- **Search History**: Access previous searches

## 📱 Mobile Access

### Mobile Features
- **Responsive Design**: Works on phones and tablets
- **Touch Optimization**: Finger-friendly interface
- **Photo Upload**: Take photos directly from mobile
- **GPS Integration**: Location-based property search
- **Offline Access**: View cached information

### Mobile Best Practices
1. **Use WiFi**: For large file uploads
2. **Photo Quality**: Use good lighting for document photos
3. **Backup Data**: Ensure information is saved
4. **Regular Updates**: Keep browser updated
5. **Security**: Use secure networks

## 🔐 Privacy & Security

### Data Protection
- **Personal Information**: Your data is encrypted
- **Document Security**: Files are securely stored
- **Access Control**: Only you can see your data
- **Audit Trail**: Track who accessed what and when

### Best Practices
1. **Strong Passwords**: Use complex, unique passwords
2. **Regular Logout**: Close sessions when finished
3. **Secure Networks**: Use trusted internet connections
4. **Update Software**: Keep browsers and devices updated
5. **Report Issues**: Contact support for security concerns

### Privacy Controls
- **Data Sharing**: Control who can see your information
- **Email Preferences**: Manage notification settings
- **Document Visibility**: Set sharing permissions
- **Account Settings**: Update personal information

## 📞 Support & Help

### Getting Help

#### Self-Service Options
- **Help Center**: In-app help articles
- **Video Tutorials**: Step-by-step video guides
- **FAQ**: Frequently asked questions
- **User Community**: Community forums and discussions

#### Contact Support
- **Email Support**: support@reims.company.com
- **Phone Support**: 1-800-REIMS-HELP
- **Live Chat**: Available during business hours
- **Support Tickets**: Submit detailed issue reports

### Common Tasks

#### Upload Problems
1. **Check File Size**: Maximum 50MB per file
2. **Verify Format**: Ensure supported file type
3. **Clear Browser Cache**: Refresh and try again
4. **Check Connection**: Ensure stable internet
5. **Contact Support**: If problems persist

#### Search Issues
1. **Check Spelling**: Verify search terms
2. **Use Simpler Terms**: Try broader search
3. **Clear Filters**: Remove restrictive filters
4. **Try Categories**: Use category navigation
5. **Check Permissions**: Ensure access rights

#### Performance Issues
1. **Close Other Tabs**: Free up browser memory
2. **Update Browser**: Use latest browser version
3. **Check Internet**: Verify connection speed
4. **Clear Cache**: Clear browser cache and cookies
5. **Restart Browser**: Close and reopen browser

## 📋 Tips & Tricks

### Efficiency Tips
1. **Keyboard Shortcuts**: Learn common shortcuts
2. **Bulk Operations**: Process multiple items at once
3. **Templates**: Use templates for common tasks
4. **Bookmarks**: Save frequently used pages
5. **Automation**: Set up automatic notifications

### Organization Tips
1. **Consistent Naming**: Use clear, consistent file names
2. **Regular Cleanup**: Delete unnecessary documents
3. **Tag Everything**: Use tags for easy searching
4. **Create Folders**: Organize by property or date
5. **Regular Backups**: Download important documents

### Quality Tips
1. **High-Quality Scans**: Use good resolution for documents
2. **Complete Information**: Fill out all relevant fields
3. **Regular Updates**: Keep information current
4. **Verify Data**: Check AI-extracted information
5. **Provide Feedback**: Help improve the system

## 🎯 Quick Reference

### Essential URLs
- **Main Application**: http://localhost:5175
- **Document Upload**: http://localhost:5175/documents
- **Maintenance Requests**: http://localhost:5175/maintenance
- **Property Search**: http://localhost:5175/properties
- **Personal Dashboard**: http://localhost:5175/dashboard
- **Reports**: http://localhost:5175/reports

### Emergency Contacts
- **Technical Support**: IT Department
- **Property Management**: Your property manager
- **Emergency Maintenance**: 24/7 emergency line
- **Account Issues**: Customer service

### File Upload Limits
- **Maximum File Size**: 50MB
- **Supported Formats**: PDF, JPG, PNG, CSV, XLSX
- **Concurrent Uploads**: Up to 10 files at once
- **Processing Time**: 1-5 minutes per document