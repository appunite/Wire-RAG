# Comprehensive Documentation on Legal Hold

## Introduction

Legal Hold is a vital service offered within the Wire communication platform, aimed primarily at recording all communications from designated users in a secure environment for legal compliance purposes. This documentation details the structure, installation, configuration, and operational characteristics of the Legal Hold service, ensuring a thorough understanding of its functions, including its sub-services: Collector, Exporter, and Hold. 

The objective of this documentation is to serve as a comprehensive guide for system administrators and users, outlining the necessary steps for installation, configuration, and usage of the Legal Hold feature within a Wire installation. The information will be divided into logical sections that cover installation prerequisites, setup procedures, technical details about the sub-services, as well as usage and operational details.

## Main Sections

### 1. Overview of Legal Hold

Legal Hold is designed to ensure that specific communications from users within a Wire installation are maintained securely, particularly for engagements involving potential legal scrutiny. The service is particularly structured as follows:

- **Collector**: This sub-service is responsible for gathering conversations from individual users.
- **Exporter**: This component takes care of exporting the collected conversations for storage.
- **Hold**: The Hold service temporarily retains conversations until they are exported, ensuring that no data is lost.

#### Installation Workflow

A typical setup of the Legal Hold involved in a Wire installation follows these steps:

1. Installation of the Legal Hold service on a dedicated server.
2. Configuration of Team Settings to integrate the Legal Hold service.
3. Selection of specific users to enable Legal Hold.
4. Confirmation from these users acknowledging their awareness of the data collection.
5. Activation of the Legal Hold service for these users, followed by the initiation of information collection.

### 2. Installing Legal Hold

The process for installing and running the Legal Hold service is adequately detailed. It begins with requirements for a server, which will support the service. In this documentation, Ubuntu 18.04 is used as the primary installation environment, although other operating systems could also be feasible.

#### Installation Requirements

- PostgreSQL database: This is used for storing the collected data.
- Git and Docker: These tools are essential for pulling the necessary code components.

##### Step-by-step Installation Process

1. **Install PostgreSQL**:
   ```bash
   sudo apt update
   sudo apt install postgresql
   ```

2. **Change the Database Password**:
   Enter the PostgreSQL console to change the password:
   ```bash
   sudo -u postgres psql
   ```
   Then execute the following command:
   ```sql
   ALTER USER postgres PASSWORD '<your-postgresql-password>';
   ```

3. **Create the legalhold Database**:
   ```sql
   CREATE DATABASE legalhold;
   ```

4. **Install Git and Docker**:
   The commands for installation will depend on the specific environments being utilized.

5. **Generate a Service Token**:
   Example command for generating a service token (`SERVICE_TOKEN`):
   ```bash
   openssl rand -base64 32
   ```

6. **Run the Docker Container**:
   You will finally run the actual Docker container for the Legal Hold service. An example command might look like this:
   ```bash
   docker run -d --name legalhold -e DB_URL=postgresql://<username>:<password>@localhost/legalhold legalhold-image
   ```

7. **Configure DNS**:
   Setup DNS for your domain, directing `legal.<yourdomain>` to point to this service. Enabling HTTPS and maintaining TLS with your public key in PEM format is critically important in this configuration.

### 3. Configuration of Legal Hold

#### User Consent Mechanism

Once a user accepts a legal hold request, the system adds a device, referred to as a **legal hold device**, to that user's account. Only team admins have the permission to remove this from a user's account. 

##### API Requests for Managing Legal Hold

1. **Request for legal hold by Admin**:
   ```http
   POST /teams/{tid}/legalhold/{uid}
   ```
   - Response: `201 Created`

2. **User Approval**:
   ```http
   PUT /teams/{tid}/legalhold/{uid}/approve
   {
     "password": <user's password> // optional if no password
   }
   ```
   - Response: `200 OK`

3. **Admin Deletion of Legal Hold**:
   ```http
   DELETE /teams/{tid}/legalhold/{uid}
   {
     "password": <admin's password> // optional if no password
   }
   ```
   - Response: `200 OK`

4. **Get Legal Hold Status for Team Members**:
   ```http
   GET /team/{tid}/members
   ```

### 4. Event Handling for Legal Hold

Legal Hold operates through specific events that are triggered within the Wire platform:
  - **New legal hold request**:
    ```json
    {
      "type": "user.legalhold-request",
      "id": "UserID of the one for whom LH is being requested",
      "last_prekey": "Last-prekey of the legal hold device",
      "client": {"id": "Client ID of the legalhold device"}
    }
    ```
  - **New legal hold enabled event**:
    ```json
    {
      "type": "user.legalhold-enable",
      "id": "UserID for whom LH was enabled"
    }
    ```
  - **New legal hold disabled event**:
    ```json
    {
      "type": "user.legalhold-disable",
      "id": "UserID for whom LH was disabled"
    }
    ```

These events are crucial for maintaining transparency and compliance among all team members.

### 5. Conclusion

The Legal Hold service within Wire serves as a comprehensive solution for ensuring that vital communication records are preserved for potential legal scrutiny, enhancing organizational compliance with corporate regulations. The process outlined in this documentation should enable administrators and users to effectively install, configure, and use the Legal Hold functionality.

### 6. Unresolved Conflicts

While multiple documents provided information regarding the setup and workflow of Legal Hold, it was noted that several sections repeated similar content. There were no explicit contradictions; rather, the information was largely redundant across sources.

Documentation pertaining to updates and versioning processes was found in varying contexts but did not contradict previously established guidelines, suggesting that any new features or updates will likely adhere to the structures outlined here. 

---

This documentation aims to provide clarity and in-depth understanding to users and administrators involved with the Legal Hold service on the Wire platform. The structured approach ensures that all pertinent details are captured, allowing for efficient implementation and management of the service.