# Service Level Agreement (SLA)
## Coast to Coast Journeys - Travel Booking Platform

---

### Agreement Details

| Field | Value |
|-------|-------|
| **Project Name** | Coast to Coast Journeys (C2C Journeys) |
| **Document Version** | 1.0 |
| **Effective Date** | January 26, 2026 |
| **Parties** | Priyesh Srivastava, Khushi |
| **Review Period** | Quarterly |

---

## 1. Purpose

This Service Level Agreement (SLA) defines the expected service levels, responsibilities, and commitments for the Coast to Coast Journeys travel booking platform operated by the project team.

---

## 2. Scope of Services

### 2.1 Platform Services
| Service | Description |
|---------|-------------|
| **Hotel Booking** | Search, compare, and book hotels worldwide via ETG/RateHawk API |
| **Flight Booking** | Flight search and booking services |
| **Visa Assistance** | Visa application support and documentation |
| **Payment Processing** | Secure payments via Razorpay and PayPal |
| **User Management** | Account creation, authentication, booking history |

### 2.2 Technical Infrastructure
- **Backend**: Flask Python API Server
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML/CSS/JavaScript
- **APIs**: ETG Hotels, Razorpay, PayPal, Google Maps

---

## 3. Service Level Targets

### 3.1 Availability

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Platform Uptime** | 99.5% | Monthly |
| **API Response Time** | < 3 seconds | 95th percentile |
| **Scheduled Maintenance** | Max 4 hours/month | Off-peak hours |

### 3.2 Support Response Times

| Priority | Description | Response Time | Resolution Time |
|----------|-------------|---------------|-----------------|
| **Critical (P1)** | Complete service outage, payment failures | 1 hour | 4 hours |
| **High (P2)** | Major feature unavailable, booking errors | 4 hours | 24 hours |
| **Medium (P3)** | Minor bugs, UI issues | 24 hours | 72 hours |
| **Low (P4)** | Feature requests, enhancements | 48 hours | Next release |

---

## 4. Roles & Responsibilities

### 4.1 Priyesh Srivastava
- Technical architecture and backend development
- API integrations (Hotels, Payments, Maps)
- Database management and security
- Server deployment and maintenance
- Bug fixes and technical support

### 4.2 Khushi
- Frontend development and UI/UX design
- Content management and updates
- Customer support coordination
- Marketing and social media
- User feedback collection and reporting

### 4.3 Shared Responsibilities
- Code reviews and quality assurance
- Documentation updates
- Emergency response and incident management
- Feature planning and roadmap decisions

---

## 5. Payment Processing SLA

### 5.1 Transaction Processing

| Metric | Target |
|--------|--------|
| Payment success rate | > 98% |
| Refund processing | Within 5-7 business days |
| Payment gateway uptime | 99.9% (as per provider SLA) |

### 5.2 Payment Partners
- **Razorpay** (Live) - Primary for Indian transactions
- **PayPal** (Live) - International transactions

---

## 6. Data & Security

### 6.1 Data Protection
- All customer data encrypted at rest and in transit
- PCI-DSS compliance for payment data
- Regular security audits (quarterly)
- Automated backups (daily)

### 6.2 Privacy Compliance
- GDPR compliant data handling
- Clear privacy policy published
- Opt-in consent for marketing
- Customer data deletion upon request

---

## 7. Incident Management

### 7.1 Incident Response Process

```
1. Detection → 2. Classification → 3. Response → 4. Resolution → 5. Post-mortem
```

### 7.2 Escalation Matrix

| Level | Contact | Trigger |
|-------|---------|---------|
| L1 | On-call team member | All incidents |
| L2 | Tech Lead (Priyesh) | P1/P2 unresolved > 2 hrs |
| L3 | Both parties | Critical business impact |

### 7.3 Communication
- Incident notifications via WhatsApp group
- Status updates every 2 hours during active incidents
- Post-incident report within 48 hours

---

## 8. Maintenance Windows

| Type | Schedule | Notice Period |
|------|----------|---------------|
| **Planned Maintenance** | Sundays 2:00 AM - 6:00 AM IST | 48 hours |
| **Emergency Maintenance** | As needed | Best effort notification |
| **Feature Deployments** | Weekdays after 10:00 PM IST | 24 hours |

---

## 9. Service Credits

In case of SLA breach, the following credits apply:

| Uptime Achieved | Service Credit |
|-----------------|----------------|
| 99.0% - 99.5% | 10% of monthly operating cost |
| 95.0% - 99.0% | 25% of monthly operating cost |
| Below 95.0% | 50% of monthly operating cost |

---

## 10. Exclusions

This SLA does not apply to:
- Third-party API outages (ETG, Razorpay, PayPal, Supabase)
- Force majeure events
- Scheduled maintenance windows
- Customer-caused issues
- Beta features explicitly marked as such

---

## 11. Review & Amendment

- This SLA will be reviewed quarterly
- Amendments require written agreement from both parties
- Performance metrics reviewed monthly

---

## 12. Signatures

| Party | Signature | Date |
|-------|-----------|------|
| **Priyesh Srivastava** | _________________________ | ____________ |
| **Khushi** | _________________________ | ____________ |

---

## Appendix A: Contact Information

| Role | Name | Contact |
|------|------|---------|
| Technical Lead | Priyesh Srivastava | priyesh@c2cjourneys.com |
| Operations Lead | Khushi | khushi@c2cjourneys.com |
| Support Email | - | sales@c2cjourneys.com |
| Emergency Hotline | - | +91 8237216173 |

---

## Appendix B: Third-Party SLAs

| Service | Provider SLA | Impact on C2C |
|---------|--------------|---------------|
| **ETG/RateHawk** | 99.9% uptime | Hotel search/booking |
| **Supabase** | 99.99% uptime | Database, Auth |
| **Razorpay** | 99.99% uptime | Indian payments |
| **PayPal** | 99.9% uptime | International payments |

---

*Document generated on January 26, 2026*
*Coast to Coast Journeys © 2026*
