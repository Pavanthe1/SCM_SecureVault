# STATUS ACCOUNTING REPORT

**Project:** Secure-Vault – Web-Based File Encryption and Decryption System  
**Repository:** SCM_SecureVault  
**Repository Owner:** Pavanthe1  
**Version Control System:** Git  
**Repository Hosting Platform:** GitHub  
**Default Branch:** main  
**Baseline Version:** v1.0.0  
**Project Status:** Completed  
**Report Type:** Software Configuration Management – Status Accounting Report

---

# 1. INTRODUCTION

Status Accounting is an important Software Configuration Management (SCM) activity used to record and report information about software configuration items, their versions, modifications, and current status throughout the software development lifecycle.

This report presents the configuration status of the Secure-Vault project. It provides a consolidated record of the important project files, recorded changes, reasons for modifications, commit history, version identification, branch management, and configuration verification activities.

Git was used to maintain the version history of the project, while GitHub was used for remote repository management, issue tracking, and collaboration.

The purpose of this report is to provide traceability between the project configuration items and the changes recorded during development.

# 2. PROJECT CONFIGURATION INFORMATION

| Particular | Details |
|---|---|
| Project Name | Secure-Vault |
| Project Type | Web-Based File Encryption and Decryption System |
| Backend Technology | Python Flask |
| Frontend Technologies | HTML, CSS, JavaScript |
| Encryption Technologies | AES-256-GCM, ECC/ECDH and Hybrid AES-ECC |
| Database Support | PostgreSQL |
| Version Control | Git |
| Remote Repository | GitHub |
| Main Branch | main |
| Version Baseline | v1.0.0 |
| Repository Visibility | Public |
| Overall Status | Completed |

# 3. CONFIGURATION ITEM IDENTIFICATION

Configuration items are the important files and resources that are maintained and controlled throughout the project.

The following configuration items are included in the Secure-Vault repository.

| Configuration Item | Description | Status |
|---|---|---|
| app.py | Main Flask application, routes and application logic | Maintained |
| crypto_engine.py | Encryption and decryption implementation | Maintained |
| requirements.txt | Python libraries and project dependencies | Maintained |
| templates/ | HTML templates used for the application interface | Maintained |
| static/ | CSS, JavaScript and static resources | Maintained |
| tests/ | Test-related project files | Maintained |
| docs/ | Project documentation | Maintained |
| reports/ | Project and SCM reports | Maintained |
| scripts/ | Automation scripts for SCM reporting | Maintained |
| .gitignore | Defines files and folders excluded from Git tracking | Maintained |
| .env.example | Example environment configuration | Maintained |
| README.md | Project overview and setup instructions | Maintained |

These configuration items are stored in the GitHub repository to maintain a centralized record of the project.

# 4. VERSION HISTORY AND CHANGE RECORDS

Git commit history provides a record of modifications made to the project. Each commit contains an identifier, a commit message, an author, and a timestamp.

The following table summarizes the recorded project history.

| Commit ID | Change Description | Reason for Change |
|---|---|---|
| 34f66f2a29a | Initial SecureVault application | Established the initial project structure and application implementation. |
| a05b5e433eeb | Add Gunicorn for deployment | Added Gunicorn to support application deployment. |
| 660dc4aa5507 | Add PostgreSQL database support | Added PostgreSQL support for persistent database storage. |
| 9242bc6f1f02 | Update README.md | Updated project documentation and information. |
| 91f064d230e | Create status_accounting_report.md | Established the SCM status accounting report. |
| 5b2ca6cb05b2 | Update status_accounting_report.md | Expanded the report with configuration and change information. |
| 8597abf2b5a | Create .gitkeep | Established the scripts directory in the repository. |
| 917a6a1ba168 | Add files via upload | Added the automated report generation script. |
| 148c840af2f | Create status-accounting.yml | Added GitHub Actions workflow configuration. |

*Note: Commit identifiers are shown in shortened form. The full identifiers and timestamps are available in GitHub commit history.*

# 5. DETAILED CHANGE ACCOUNTING

This section explains the important changes made to the Secure-Vault project and the reasons behind those modifications.

## 5.1 Initial Application Development

**Commit:** 34f66f2a29a

**Configuration affected:** Application source code, templates, static resources and project structure.

**Reason for change:**

The initial application implementation was required to establish the foundation of the Secure-Vault system. The application structure was created to support user interaction and file encryption and decryption operations.

**Recorded outcome:**

The initial application implementation was committed to Git, establishing the starting point for subsequent project modifications.

## 5.2 Gunicorn Deployment Integration

**Commit:** a05b5e433eeb

**Configuration affected:** Deployment configuration and application dependencies.

**Reason for change:**

The Flask development server is primarily intended for development. Gunicorn was added to support running the Flask application using a production-oriented WSGI server.

**Recorded outcome:**

Gunicorn integration was recorded in the project repository.

## 5.3 PostgreSQL Database Integration

**Commit:** 660dc4aa5507

**Configuration affected:** Application database configuration and dependencies.

**Reason for change:**

PostgreSQL support was added to provide persistent database storage for application data and support the deployed application environment.

**Recorded outcome:**

PostgreSQL database support was incorporated into the project configuration and recorded through Git.

## 5.4 Documentation Update

**Commit:** 9242bc6f1f02

**Configuration affected:** README.md

**Reason for change:**

Project documentation was updated to maintain information about the application and its setup.

**Recorded outcome:**

The updated documentation was committed to the repository.

## 5.5 Status Accounting Report Preparation

**Commits:** 91f064d230e, 5b2ca6cb05b2

**Configuration affected:** reports/status_accounting_report.md

**Reason for change:**

A separate SCM report was created to document configuration items, project versions, recorded changes and the overall configuration status.

**Recorded outcome:**

The report was added to the repository and updated with project-specific SCM information.

## 5.6 Automated Status Accounting Implementation

**Commits:** 8597abf2b5a, 917a6a1ba168, 148c840af2f

**Configuration affected:** scripts/ and .github/workflows/

**Reason for change:**

Manual preparation of status accounting information can be time-consuming. Automation was introduced to collect repository information and generate a report.

**Recorded outcome:**

A Python script was added to collect GitHub repository information, and a GitHub Actions workflow was configured to execute the script and upload the generated report as a downloadable artifact.

The workflow was successfully executed, producing the following files:

- status_accounting_report.html
- status_accounting_commits.csv
- status_accounting_issues.csv

# 6. VERSION CONTROL AND BASELINE MANAGEMENT

Git was used to maintain the source-code history and record modifications to the project.

The project also uses Git tags to identify important versions.

**Baseline Version: v1.0.0**

The annotated Git tag v1.0.0 was created and pushed to the remote repository.

The tag points to commit 660dc4aa5507, which records the PostgreSQL database support change.

The baseline provides a reference point for identifying the configuration state of the project at that particular commit.

It also allows future modifications to be compared against an established version.

# 7. BRANCH MANAGEMENT

Branch management allows changes to be developed separately without directly modifying the main branch.

The repository contains the following branches:

| Branch | Purpose | Status |
|---|---|---|
| main | Main project development and stable source-code history | Default branch |
| feature/enhanced-status-report | Separate branch for improving the SCM status accounting report | Created |

The feature branch was created from main to maintain separation between the existing project version and the report enhancement.

Changes developed in the feature branch can be reviewed through a GitHub Pull Request before being merged into the main branch.

# 8. PULL REQUEST AND CHANGE REVIEW RECORD

Pull Requests provide a controlled method for reviewing modifications before merging them into the main branch.

For the status accounting report enhancement, the following change information is maintained:

| Particular | Details |
|---|---|
| Source Branch | feature/enhanced-status-report |
| Target Branch | main |
| Change Area | SCM status accounting documentation |
| Change Purpose | Improve report detail and configuration traceability |
| Review Method | GitHub Pull Request |
| Merge Status | To be recorded after the actual pull request is created and reviewed |

The Pull Request will provide a record of the proposed changes, review comments, approval and final merge status.

This helps maintain traceability and ensures that modifications are reviewed before becoming part of the main project version.

# 9. ISSUE TRACKING AND TASK ACCOUNTING

GitHub Issues were used to record and track SCM-related activities.

**Existing Issue:**

Issue #1 – Track SCM implementation and verification.

This issue provides a record of the SCM verification activity.

The repository's issue history can be used to identify reported problems, completed activities, discussions and their current status.

Issue status should be interpreted using the actual open or closed state displayed by GitHub.

# 10. AUTOMATED STATUS ACCOUNTING REPORT GENERATION

To reduce manual effort in preparing the status accounting report, an automated reporting mechanism was introduced.

The implementation uses:

- **GitHub REST API:** Retrieves repository information such as commits, issues, pull requests, tags and workflow runs.
- **Python:** Processes the retrieved information and generates report files.
- **GitHub Actions:** Executes the reporting script automatically.
- **HTML:** Presents the collected information in a readable report.
- **CSV:** Provides structured records that can be reviewed separately.

## 10.1 Automation Workflow

1. A change is pushed to the main branch or the workflow is manually triggered.
2. GitHub Actions checks out the repository.
3. The Python reporting script retrieves repository information.
4. The script generates HTML and CSV reports.
5. GitHub Actions uploads the generated files as workflow artifacts.
6. The generated report can be downloaded from the completed workflow run.

## 10.2 Generated Report Files

| Generated File | Purpose |
|---|---|
| status_accounting_report.html | Complete visual status accounting report |
| status_accounting_commits.csv | Commit history and change records |
| status_accounting_issues.csv | Issue information and task status |

## 10.3 Automation Execution Record

The GitHub Actions workflow named **Status Accounting Report** was successfully executed.

| Particular | Recorded Result |
|---|---|
| Workflow | Status Accounting Report |
| Execution Status | Success |
| Trigger | Manual workflow execution |
| Branch | main |
| Generated Artifact | SecureVault-Status-Accounting-Report |
| Artifact Availability | Successfully generated |

The generated artifact provides evidence that the automated status accounting process executed successfully.

# 11. CONFIGURATION VERIFICATION AND AUDIT STATUS

Configuration verification and auditing help determine whether project configuration records are maintained consistently.

The following SCM activities were performed or recorded.

| SCM Activity | Status |
|---|---|
| Configuration item identification | Completed |
| Git repository initialization | Completed |
| Source-code version tracking | Completed |
| Commit history maintenance | Completed |
| Remote repository management | Completed |
| Version tagging | Completed |
| Issue tracking setup | Completed |
| Configuration documentation | Completed |
| Branch creation | Completed |
| Automated report generation | Successfully executed |
| Report artifact generation | Successfully verified |

The successful GitHub Actions execution confirms that the reporting workflow ran and produced its artifact. It does not independently establish that every application feature passed functional testing.

# 12. CONFIGURATION STATUS SUMMARY

The Secure-Vault project configuration is maintained through Git and GitHub.

The following records provide the main sources of configuration information:

| Record | Information Provided |
|---|---|
| Git commits | Recorded source-code modifications |
| Git tags | Identified project versions and baselines |
| Git branches | Separate development and change-management activities |
| GitHub Issues | SCM tasks and issue history |
| GitHub Pull Requests | Proposed changes and review records |
| GitHub Actions | Automated execution history |
| Status Accounting Reports | Consolidated configuration information |

These records provide traceability between the project's configuration items, changes and versions.

# 13. CONCLUSION

The Status Accounting Report consolidates the configuration information of the Secure-Vault project.

Git was used to maintain source-code versions and record modifications, while GitHub provided centralized repository management, issue tracking, branch management and version visibility.

The recorded history includes the initial application implementation, Gunicorn deployment integration, PostgreSQL database support, documentation updates and the introduction of automated status accounting.

The v1.0.0 Git tag provides a reference baseline for the project. Branch management and Pull Requests provide a mechanism for controlled changes and review.

The Python reporting script and GitHub Actions workflow further reduce the effort required to collect and present SCM information.

Overall, the report provides a structured record of what configuration items exist, what changes were recorded, why those changes were made, and how the project versions and SCM activities are maintained.

**FINAL PROJECT STATUS: COMPLETED**
