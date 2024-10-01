# Documentation on Legal Hold

## Summary
The Legal Hold feature in Wire provides a mechanism for securely recording communications of designated users for compliance and legal purposes. The system includes a Legal Hold service comprising three essential sub-services: Collector, Exporter, and Hold. These services work together to ensure that conversations are properly archived and can be accessed when necessary. A legal hold device is tied to a user account, managed by the Legal Hold service, and can only be added or removed by team administrators with user consent. Notifications and status updates about legal holds are communicated clearly to all relevant parties.

## Detailed Analysis

### Overview of Legal Hold Service
- **Legal Hold Service**: Enables the recording of communications for specific users within a Wire installation, ensuring compliance with legal obligations.
- **Components**:
  - **Collector**: Gathers conversations from users.
  - **Exporter**: Handles the export of stored conversations.
  - **Hold**: Temporarily stores conversations between the Collector and Exporter processes.

### Installation and Setup
Detailed instructions for setting up the Legal Hold service on a designated server (preferably Ubuntu 18.04) include the following steps:

1. **Install PostgreSQL**:
    ```bash
    sudo apt update
    sudo apt install postgresql
    ```
   
2. **Set Database Password**:
    ```bash
    sudo -u postgres psql
    ALTER USER postgres PASSWORD '<your-postgresql-password>';
    ```

3. **Create Legal Hold Database**:
    ```sql
    CREATE DATABASE legalhold;
    ```

4. **Configure and Run Legal Hold Service**:
   Ensure Docker is installed and use a random secret token for configuration.
   ```bash
   docker run -e DB_URL=<your-database-url> <legal-hold-container-image>
   ```

5. **Configure DNS**: 
   Point a subdomain (e.g., `legal.<your-domain>`) to the Legal Hold service.

### User Consent and Status Management
Before a user can have a legal hold device added to their account, consent is mandatory:
- Users receive a prompt for their consent before being subjected to legal holds. Only upon granting consent can the legal hold devices be assigned.

#### API Endpoints for Legal Hold Operations
- **Request a user to be put under legal hold**:
    ```http
    POST /teams/{tid}/legalhold/{uid}
    ```
    Responds with `201 Created` if successful.

- **User Approval Process**:
    ```http
    PUT /teams/{tid}/legalhold/{uid}/approve
    {
      "password": "<user's password>"  // optional for password-less users
    }
    ```
    Responds with `200 OK`.

- **Deletion of Legal Hold by Admin**:
    ```http
    DELETE /teams/{tid}/legalhold/{uid}
    {
      "password": "<admin's password>"  // optional for password-less admins
    }
    ```
    Responds with `200 OK`.

- **Get Legal Hold Status**:
    ```http
    GET /team/{tid}/members
    ```
    The response includes a `legalhold_status` field indicating if legal hold is enabled or disabled for team members.

### Events Related to Legal Holds
Various events are triggered in response to actions regarding legal holds:
- New legal hold request:
    ```json
    { "type": "user.legalhold-request", "id": UserID, ... }
    ```
- Legal hold enabled:
    ```json
    { "type": "user.legalhold-enable", "id": UserID }
    ```
- Legal hold disabled:
    ```json
    { "type": "user.legalhold-disable", "id": UserID }
    ```

## Contradictions
While analyzing the documents, certain elements mentioned in different documents may appear repetitive rather than directly contradictory. The latest documentation dated 2023-01-25 aligns consistently in the following aspects:

### Key Contradictions:
1. **Device Management**:
   - The notion of adding legal hold devices is consistent: team admins can add devices only with user consent. However, in different documents, the way in which this user consent is sought or presented may vary slightly.

2. **User Notification**:
   - Some documents state explicit methods (e.g., red dots on the UI) to indicate active legal holds, whereas others imply general notifications without specifying UI elements.

3. **Database and Service Installation**:
   - Various undocumented steps such as the necessity of Docker installations or specific command structures were echoed throughout; however, the latest version is the go-to source for accurate instructions.

By ensuring that programmers and users follow the details in the 2023-01-25 documentation, potential confusion created by outdated or varying descriptions in documents without dates should be minimized. 

This document consolidates comprehensive legal hold information and provides a relevant view for its implementation, while also highlighting any inconsistencies that could affect usability and comprehension.