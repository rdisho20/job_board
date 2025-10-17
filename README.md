# A Flask Job Board

## Features
**Post a Job**
- Title
- Date & Time Posted (generated)
- Company
- Type of Job (Fulltime, Parttime, Contract, Seasonal, Temporary)
- Category (list of categories to choose from)
- Location (On-site, Hybrid, Remote)
- About the Company
- About the Job
- Requirements / Nice to Have
- Pay range
- Apply

**Employee Dashboard**
- Upload Company Logo
- Post a Job (link)
- Your Jobs (display job cards, sorted by most recent)

**Your Company's Jobs Postings**
- Edit
- Delete

## Links
Employer Login / Employer Sign Up  
Recent Job Postings  
Category Job Postings (dropdown menu)  
Search  
Employers (list)

## About Main Styles
- Body → soft grey bg, natural dark-blue text.
- Headings → natural strong blue, bold, readable.
- Links → purple theme, hover darkens.
- Buttons → light blue base, darker hover.
- Search bar → clean, with rounded edges.
- Job cards → white background, soft borders, hover lift effect.
- Lists → clean bullet points for requirements, responsibilities, etc.
- Footer → muted, simple.

## About Nav Styles
- Centered layout → clean & balanced.
- Hover effect → soft grey + purple highlight.
- Active link → light blue pill-style highlight.
- Easy swap → just change links / add class="active" where you need.

---

## Database Schema
Compay
- id
- name
- contact email
- password
- about company

Job Postings
- id
- position title
- description - no more than 5000 characters
- date and time posted, default now()
- pay range
- company id

Job types
- id
- job type
- job id

Industry Categories
- id
- industry category
- job id

company - jobs
one to many
modality:
- company -> job, not required
- job -> company, required (company is required for a job to exist)

jobs - job_type
many to many
modality:
- job -> job_type (job requires a job type)
- job_type -> job (job_type requires a job)

jobs - industry_type
many to many
modality:
- job -> industry_type (job requires an industry type)
- industry_type -> job (industry_type requires a job)