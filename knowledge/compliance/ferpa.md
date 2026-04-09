# FERPA — Family Educational Rights and Privacy Act

## Scope

The Family Educational Rights and Privacy Act (FERPA, 20 USC §1232g) is a US federal law that protects the privacy of student education records. It applies to **educational agencies and institutions that receive funds from the US Department of Education** — which is essentially every public K-12 school, every public college and university, and most private and non-profit higher education institutions in the US. FERPA also applies to **third-party providers** that schools share student data with (edtech vendors, learning management systems, payment processors, transcript services). Covers FERPA's core requirements (the rights of parents and eligible students, the directory information exception, the school official exception, the audit/study exception), the typical edtech vendor scenario, the cloud service mapping for K-12 and higher education workloads, the relationship to COPPA and state-level student privacy laws, and the practical implementation patterns for SaaS vendors selling into education. Does not cover state-level student privacy laws in detail (California SOPIPA, New York Education Law 2-d, Illinois SOPPA, etc.).

## Applicability

FERPA applies to:

- **Educational agencies and institutions** that receive funds from the US Department of Education — public K-12 schools, public colleges and universities, most private K-12 and higher education
- **Third parties that act on behalf of the school** under the "school official" exception (edtech vendors, hosting providers, contractors performing institutional functions)

FERPA does not apply directly to:

- **Schools that do not receive Department of Education funds** (rare in practice)
- **Edtech vendors that do not act under the school official exception** — these vendors collect data directly from students/parents under their own privacy policy and are not bound by FERPA, though COPPA and state laws may apply
- **General-purpose cloud providers** when they only provide infrastructure (the cloud provider is a sub-processor; FERPA flows through the school-to-vendor contract)

The most common confusion is whether a SaaS vendor selling into K-12 or higher education is subject to FERPA. The answer depends on the contract:

- If the school engages the vendor as a "school official" performing an institutional service, the vendor is bound by FERPA and must handle student data accordingly (limited use, no further disclosure, return/destroy on contract end)
- If the vendor sells directly to students or parents without a school contract, the vendor is not bound by FERPA but is subject to general consumer privacy laws

## Education Records

FERPA defines "education records" as records that are:

- Directly related to a student
- Maintained by an educational agency or institution or by a party acting for the agency or institution

The definition is broad and includes:

- Grades and transcripts
- Class schedules
- Attendance records
- Disciplinary records
- Health records (with overlap to HIPAA — see below)
- Financial aid records
- Most categories of student-specific information

The definition does NOT include:

- **Sole possession records** — personal notes by an instructor that are not shared
- **Law enforcement unit records** — created and maintained by the school's law enforcement unit for law enforcement purposes
- **Employment records** — for students who are also employees, employment records are not education records
- **Treatment records** — health/counseling records made or maintained by professionals in their professional capacity (these fall under HIPAA in some cases)
- **Post-attendance records** — records about an individual after they are no longer a student

## Core Requirements

### Right to Inspect and Review

Parents (for students under 18) and eligible students (18+ or attending postsecondary) have the right to:

- **Inspect and review** the student's education records within 45 days of a request
- **Request amendment** of records they believe to be inaccurate, misleading, or in violation of privacy rights
- **Have a hearing** if the request to amend is denied

### Right to Consent to Disclosure

Generally, the school must obtain **written consent** before disclosing personally identifiable information from a student's education records. There are several **exceptions**:

1. **School officials with legitimate educational interest** — including third parties acting on behalf of the school under contract
2. **Other schools to which the student is transferring**
3. **Specified officials for audit or evaluation purposes**
4. **Appropriate parties in connection with financial aid** to the student
5. **Organizations conducting studies** for, or on behalf of, the school
6. **Accrediting organizations**
7. **Compliance with a judicial order or subpoena**
8. **Health or safety emergencies**
9. **State and local authorities** under specific state laws
10. **Directory information** (see below)

### Directory Information

Schools may designate certain categories of information as "directory information" that can be disclosed without consent:

- Name
- Address
- Telephone number
- Email address
- Date and place of birth
- Major field of study
- Participation in officially recognized activities and sports
- Dates of attendance
- Degrees and awards received
- Most recent previous educational agency or institution attended

Parents and eligible students must be given the opportunity to **opt out** of directory information disclosure. Schools that disclose directory information must give annual notice of the opt-out right.

### School Official Exception (the cloud-relevant one)

This is the exception that lets schools share student data with edtech vendors and cloud providers without obtaining individual consent. To qualify:

- The third party performs a service or function for which the school would otherwise use its own employees
- The third party is under the **direct control** of the school regarding the use and maintenance of the records
- The third party uses the records only for the purpose for which they were disclosed
- The third party does not redisclose the information to others without consent

The key requirement is "direct control", which is operationalized through contract terms:

- Specific limited purpose for which the data may be used
- Prohibition on further disclosure
- Requirements for security and confidentiality
- Return or destruction of data at contract end
- Cooperation with the school's audits

A contract that does not meet these requirements does not qualify the vendor for the school official exception, which means the vendor cannot legally receive education records without parent/student consent for each individual.

## Cloud Service Mapping

| FERPA Requirement | AWS | Azure | GCP |
|---|---|---|---|
| Encryption at rest | KMS, S3 SSE, EBS encryption | Key Vault, Storage SSE, Disk Encryption | Cloud KMS, Cloud Storage CMEK, Persistent Disk CMEK |
| Encryption in transit | ACM, ELB TLS | Front Door TLS, App Gateway TLS | Cloud Load Balancing TLS |
| Access controls | IAM with PIM-equivalent | Azure RBAC with PIM | Cloud IAM with conditional bindings |
| Audit logging | CloudTrail with data events for S3 | Activity Log + Diagnostic Settings | Cloud Audit Logs (Admin Activity + Data Access) |
| Data deletion | S3 lifecycle, RDS delete | Storage lifecycle, SQL delete | Storage lifecycle, BigQuery delete |
| Data residency | Regional services | Regional services + data residency add-ons | Regional services |
| Vendor data processing addendum | AWS Data Processing Addendum | Microsoft DPA | Google Cloud DPA |

The cloud providers themselves are sub-processors under FERPA — the school-to-vendor contract makes the vendor a "school official" and the vendor's contract with the cloud provider extends the obligations downstream.

## Architect Checklist

- [ ] **[Critical]** **Determine if FERPA applies**. If selling into K-12 or higher education, FERPA almost certainly applies via the school official exception.
- [ ] **[Critical]** **Review the contract with each school customer** for school official exception language. The contract must include the four required elements (limited purpose, no further disclosure, security requirements, return/destroy on termination).
- [ ] **[Critical]** **Maintain education records separately** from other data, with explicit access controls. The records must be inventoried and the access must be auditable.
- [ ] **[Critical]** **Implement data deletion procedures** that can return or destroy education records at the end of the contract. Test the deletion path; "deleted" must mean actually deleted, not soft-deleted with the data still recoverable.
- [ ] **[Critical]** **Restrict access to education records** to staff who need it for the contracted service. Document the access policy and the access list.
- [ ] **[Critical]** **Maintain audit logs** of access to education records. Logs should capture who accessed what, when, and from where. Retain for the duration the school requires (typically the duration of the contract plus some buffer).
- [ ] **[Critical]** **Establish a process for parent / student access requests**. While the school is the primary contact for access requests, the vendor must be able to support the school in producing the data within the FERPA timeline (45 days).
- [ ] **[Recommended]** **Implement a data classification system** that distinguishes education records from other data. This makes the access controls and audit logs scoped correctly.
- [ ] **[Recommended]** **Document the data flow** from the school to the vendor, within the vendor's systems, and back to the school. The data flow is the artifact that demonstrates compliance with the limited purpose requirement.
- [ ] **[Recommended]** **Use customer-managed encryption keys** for any storage of education records, with the key managed by the vendor (or by the school in some advanced configurations).
- [ ] **[Recommended]** **Avoid using education records for vendor product improvement** unless the contract explicitly permits it. The default is "no use beyond the contracted service".
- [ ] **[Optional]** **Pursue Student Data Privacy Consortium (SDPC) Resource Registry** listing for transparency and to streamline contract negotiations with school districts.

## Relationship to COPPA

The Children's Online Privacy Protection Act (COPPA) applies to operators of online services directed at children under 13. There is overlap with FERPA when an edtech vendor serves K-12 students:

- **FERPA** applies because the school is sharing education records with the vendor under the school official exception
- **COPPA** applies because the service is directed at children under 13 and collects personal information from them

The school official exception under FERPA includes the school's role as the parent/guardian for COPPA consent purposes — the school can consent on behalf of parents under specific conditions. This is the basis for the FTC's "schools as proxy for parental consent" guidance for edtech.

For higher education vendors, COPPA does not apply (students are 18+).

## Relationship to State Student Privacy Laws

Many US states have student privacy laws that go beyond FERPA. The most prominent:

- **California SOPIPA** (Student Online Personal Information Protection Act, 2014) — prohibits targeted advertising, prohibits sale of student data, requires data protection
- **New York Education Law §2-d** — requires parental opt-in for some data uses, requires public posting of vendor data agreements
- **Illinois SOPPA** (Student Online Personal Protection Act) — similar to SOPIPA with additional notification requirements
- **Connecticut Public Act 16-189** — requires data protection addenda for school contracts with edtech vendors

State laws are typically stricter than FERPA. For a vendor selling nationally, the practical approach is to comply with the strictest applicable state law (often California or Illinois) and apply that standard universally.

## Penalties

FERPA does not have a private right of action, and the penalty regime is unusual:

- **Loss of federal funding** — the Department of Education can withdraw federal funding from an institution that has a policy or practice of violating FERPA. This is an existential threat for most schools but has rarely been invoked.
- **No direct fines** — FERPA does not impose monetary fines on schools or third parties
- **Reputational and contractual consequences** — vendors that violate FERPA risk losing school contracts and being publicly reported

The lack of direct fines is partially compensated for by state laws (which often do impose fines) and by contractual remedies in vendor agreements with schools.

## Common Decisions (ADR Triggers)

- **School official exception vs direct relationship** — school official is the standard for selling into schools. Direct relationship is appropriate for consumer-facing services where students or parents are the customer.
- **Multi-tenant vs single-tenant for school customers** — multi-tenant is operationally simpler but requires careful per-school data isolation. Single-tenant is sometimes required by school RFPs or by district policy.
- **Data deletion at contract end** — return to the school vs destroy in place. Most schools prefer destruction in place with a verification certificate; some require return of the data first.
- **Subprocessor management** — every subprocessor (cloud provider, monitoring vendor, support tool) that touches education records must be flowed through the FERPA contract terms. Maintain a subprocessor list and notify schools of changes.
- **State law alignment** — comply with the strictest applicable state law universally vs per-state. Universal alignment is operationally simpler.

## Reference Links

- [FERPA (20 USC §1232g)](https://www.law.cornell.edu/uscode/text/20/1232g)
- [FERPA regulations (34 CFR Part 99)](https://www.ecfr.gov/current/title-34/subtitle-A/part-99)
- [Department of Education Student Privacy Policy Office](https://studentprivacy.ed.gov/)
- [FTC COPPA guidance for ed tech](https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions)
- [Student Data Privacy Consortium](https://privacy.a4l.org/)

## See Also

- `compliance/hipaa.md` — HIPAA, which sometimes overlaps with FERPA for student health records
- `compliance/gdpr.md` — GDPR, which applies if any students are EU residents
- `compliance/ccpa.md` — CCPA, which has limited applicability to education but may apply to non-school-related processing
- `compliance/pipeda-lgpd.md` — PIPEDA / LGPD for Canadian and Brazilian students
- `frameworks/nist-csf-2.0.md` — NIST CSF as the underlying security framework
- `failures/compliance.md` — compliance failure patterns
