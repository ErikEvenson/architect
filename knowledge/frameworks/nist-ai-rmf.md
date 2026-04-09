# NIST AI Risk Management Framework

## Scope

The NIST AI Risk Management Framework (AI RMF 1.0, released January 2023) is a voluntary framework for managing risks across the lifecycle of AI systems. It defines the core functions of trustworthy AI, the characteristics of trustworthy AI, and a cycle of activities (Govern, Map, Measure, Manage) for organizations developing, deploying, or using AI systems. AI RMF is the primary US framework reference for AI governance and is increasingly cited in customer security reviews, RFPs, and regulatory filings as the expected baseline for any organization shipping AI features. Covers the four core functions, the seven characteristics of trustworthy AI, the AI lifecycle stages, the relationship to the NIST Generative AI Profile, the EU AI Act mapping, and practical implementation patterns for organizations adopting AI features. Does not cover specific ML model architectures or vendor product comparisons.

## The Four Core Functions

AI RMF organizes activities into four functions, mirroring the structure of the NIST CSF:

### Govern

Establishes and maintains the organizational culture, risk management strategy, and oversight that allows the rest of the AI RMF activities to operate. Govern is the function that makes AI RMF actionable at the organizational level.

Key activities:
- **Risk management strategy** — defining acceptable risk levels for AI systems, including bias, fairness, robustness, and privacy risks
- **Roles and responsibilities** — naming who is accountable for AI risk decisions (AI ethics board, AI risk officer, model owners)
- **Policy** — written policies governing AI development, deployment, monitoring, and decommissioning
- **Stakeholder engagement** — ensuring affected stakeholders (users, customers, employees, regulators, the public) have a voice in AI governance
- **Documentation requirements** — what must be documented for every AI system (model card, data card, intended use, known limitations)

### Map

Identifies the context in which an AI system will be deployed, the categories of AI risk relevant to the system, and the impacts on different stakeholder groups.

Key activities:
- **Categorize the AI system** — what type of AI is it (generative, predictive, classification, recommendation), what is the use case, who are the users
- **Identify intended and unintended use cases** — the obvious uses and the foreseeable misuses
- **Map AI risks** — bias, fairness, privacy, security, safety, environmental impact, intellectual property
- **Stakeholder mapping** — who is affected by the system's outputs (direct users, affected third parties, society)
- **Document the system context** — model card, data card, intended use statement, known limitations

### Measure

Quantifies and evaluates AI risks using metrics, tests, and assessments. The Measure function is what distinguishes AI RMF from a purely document-based framework — it requires actual measurement, not just documentation.

Key activities:
- **Performance metrics** — accuracy, precision, recall, F1, ROC AUC for predictive models; perplexity, BLEU, ROUGE, human-eval for generative models
- **Bias and fairness metrics** — disparate impact, equal opportunity, calibration across protected groups
- **Robustness testing** — adversarial inputs, distribution shift, edge cases, prompt injection (for LLMs)
- **Privacy testing** — membership inference, model inversion, data extraction
- **Safety testing** — harmful content generation, safety boundary testing, red-teaming
- **Operational monitoring** — drift detection, performance monitoring, incident reporting

### Manage

Allocates resources to risks based on the assessed impact and prioritizes the risks for treatment. Manage is the function that turns measurement into action.

Key activities:
- **Risk treatment** — accept, mitigate, transfer, or avoid each identified risk
- **Resource allocation** — assigning people, tools, and budget to risk management activities
- **Incident response** — defined process for responding to AI-specific incidents (harmful output, bias finding, privacy breach, safety violation)
- **Continuous improvement** — feedback loop from operational monitoring back into the Govern, Map, and Measure functions

## The Seven Characteristics of Trustworthy AI

AI RMF defines seven characteristics that a trustworthy AI system should exhibit. These are not pillars to be checked off; they are properties to be balanced based on the system's context.

1. **Valid and Reliable** — the system's outputs are accurate, consistent, and produced by a process that has been tested and verified
2. **Safe** — the system does not, under defined conditions, lead to a state in which human life, health, property, or the environment is endangered
3. **Secure and Resilient** — the system is protected from adversarial manipulation, can withstand unexpected events, and can recover from failures
4. **Accountable and Transparent** — there is documentation of who built the system, what data trained it, what its known limitations are, and who is responsible for its outputs
5. **Explainable and Interpretable** — the system's behavior can be explained at a level appropriate to the audience (users, regulators, affected parties)
6. **Privacy-Enhanced** — the system protects the privacy of individuals whose data is used or affected
7. **Fair — with Harmful Bias Managed** — the system's outcomes are fair across relevant groups, and any harmful biases are identified and addressed

The characteristics are interrelated and sometimes in tension. Improving one (e.g., explainability) can degrade another (e.g., model accuracy). The balance is a contextual decision driven by the Govern function.

## The AI Lifecycle

AI RMF describes the AI lifecycle in stages:

1. **Plan and Design** — define the use case, the intended outcomes, the constraints, and the success criteria
2. **Collect and Process Data** — gather, clean, label, and document the training data
3. **Build and Use Model** — train, validate, and document the model
4. **Verify and Validate** — test against the success criteria; conduct fairness, robustness, and safety testing
5. **Deploy and Use** — operationalize the model, integrate with the application, train users
6. **Operate and Monitor** — observe performance in production, detect drift, respond to incidents
7. **Decommission** — retire the model, archive the documentation, ensure no residual risk

Each stage has its own AI RMF activities. The Govern function operates continuously across all stages.

## NIST Generative AI Profile (NIST AI 600-1)

In July 2024, NIST released the **AI 600-1 Generative AI Profile** as a companion to AI RMF, addressing the specific risks of generative AI systems. The profile identifies 12 risks that are unique to or particularly amplified by generative AI:

1. **CBRN Information** — generation of harmful chemical, biological, radiological, or nuclear information
2. **Confabulation** — fabricated information presented as factual
3. **Dangerous, Violent, or Hateful Content** — harmful generated content
4. **Data Privacy** — inadvertent disclosure of training data
5. **Environmental Impacts** — high energy and water consumption of training and inference
6. **Harmful Bias and Homogenization** — amplification of biases, reduction in output diversity
7. **Human-AI Configuration** — inappropriate reliance on AI outputs by humans
8. **Information Integrity** — AI-generated misinformation and disinformation
9. **Information Security** — adversarial attacks specific to AI systems
10. **Intellectual Property** — generation of content that infringes on existing IP
11. **Obscene, Degrading, or Abusive Content** — generation of offensive content
12. **Value Chain and Component Integration** — risks from third-party models, datasets, and tools

For each risk, the profile suggests Govern, Map, Measure, and Manage activities.

## Relationship to the EU AI Act

The EU AI Act (effective from August 2024 with phased application through 2026) is the first major regulatory framework specifically for AI systems. It is a regulation, not a voluntary framework, and applies to any AI system placed on the EU market or whose output is used in the EU.

Key alignment points between AI RMF and the EU AI Act:

- **Risk categorization** — both use a risk-based approach (EU AI Act: Unacceptable, High, Limited, Minimal; AI RMF: contextual)
- **Documentation requirements** — both require model documentation (model card, technical documentation)
- **Bias and fairness** — both require attention to fairness across protected groups
- **Human oversight** — both emphasize meaningful human oversight of high-risk AI systems
- **Post-market monitoring** — both require ongoing monitoring of deployed systems

Key differences:
- AI RMF is voluntary; EU AI Act is mandatory
- EU AI Act prohibits certain uses (social scoring, real-time biometric ID in public spaces) outright
- EU AI Act imposes specific conformity assessment procedures for high-risk systems

Organizations subject to the EU AI Act often use AI RMF as the implementation framework, with EU AI Act as the compliance overlay.

## Common Implementation Patterns

### Adopting AI RMF in a software organization shipping AI features

1. **Inventory** — identify every AI system in the product (LLM-powered features, ML models, recommendation systems, automated decisioning)
2. **Categorize by risk** — for each system, assess the impact category (high-impact: affects user safety, financial decisions, employment; medium: affects user experience; low: internal tooling)
3. **Document each high-impact system** — model card, data card, intended use, known limitations
4. **Establish governance** — name an AI risk owner, define the risk acceptance process, establish an incident response path
5. **Build measurement** — automated bias and fairness testing, drift monitoring, performance dashboards
6. **Continuous improvement** — quarterly review of AI risks, incidents, and system updates

### Reporting on AI RMF to leadership

A common dashboard shows:

- **Inventory** — count of AI systems by risk tier
- **Documentation completeness** — percentage of systems with complete model cards and data cards
- **Measurement coverage** — percentage of systems with current bias, fairness, and performance measurements
- **Open AI risks** — risks identified but not yet mitigated, with owners and deadlines
- **Recent AI incidents** — incidents in the last quarter, root causes, remediation status

### Model card and data card

The two key documentation artifacts are:

- **Model card** — describes the model itself: intended use, performance metrics, training procedure, known limitations, ethical considerations, biases identified during testing
- **Data card** — describes the training data: source, collection method, preprocessing, demographic characteristics, known biases, consent and licensing

Both should be written at a level appropriate for the audience — technical detail for ML practitioners, plain language for policy reviewers, and an executive summary for leadership.

## Common Decisions

- **AI RMF as the primary framework vs as a reference** — primary when AI is a strategic concern and the organization wants a single voluntary framework. Reference when the organization is subject to the EU AI Act or other regulatory regime that mandates specific practices.
- **Voluntary adoption vs customer-driven adoption** — many organizations adopt AI RMF because customers ask for it in security reviews, not because of internal initiative. This is fine, but the adoption should still be substantive (actual measurement and management) rather than just documentary.
- **Centralized AI governance vs distributed** — centralized (an AI risk team, AI ethics board) for organizations with many AI systems and high-impact use cases. Distributed (each product team owns its AI risk with central oversight) for organizations with smaller AI footprints. Most organizations end up somewhere in between.
- **Manual measurement vs automated measurement** — start manual to build the measurement methodology, then automate. Avoid the trap of "we will automate measurement when we have time" — automation is what makes continuous monitoring sustainable.
- **Generative AI Profile adoption** — adopt for any system that uses LLMs or generative AI specifically. The standard AI RMF is sufficient for predictive models alone.

## Reference Links

- [NIST AI Risk Management Framework (AI RMF 1.0)](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST AI RMF Playbook](https://airc.nist.gov/AI_RMF_Knowledge_Base/Playbook)
- [NIST AI 600-1 Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
- [EU AI Act official text](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [Model cards for model reporting (Mitchell et al.)](https://arxiv.org/abs/1810.03993)
- [Data cards (Pushkarna et al.)](https://arxiv.org/abs/2204.01075)

## See Also

- `frameworks/nist-csf-2.0.md` — CSF as a parallel cybersecurity framework
- `general/ai-ml-services.md` — general AI/ML service architecture
- `providers/aws/ai-ml-services.md` — AWS-specific AI/ML services
- `providers/azure/ai-ml-services.md` — Azure-specific AI/ML services
- `providers/gcp/ai-ml-services.md` — GCP-specific AI/ML services
- `compliance/gdpr.md` — GDPR overlap (data subject rights, automated decision-making)
- `general/data-classification.md` — data classification as input to AI risk assessment
