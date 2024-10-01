# Comprehensive Documentation on Team Size and Server Management in Wire

## Introduction

This documentation aims to provide a detailed overview of the infrastructure configuration options available for Wire, particularly for handling teams exceeding 500 users. It will explore the limits imposed on team sizes and conversation memberships, the necessary configurations for managing connections and resources, and best practices for server usage with extensive user bases. The information presented stems entirely from the extracted documents provided, ensuring clarity on how to optimize Wire for larger teams.

### Objectives of This Documentation:
- Describe the maximum user limits within teams and conversations.
- Explain configurations needed for handling larger teams in Brigade (Brig).
- Provide guidance on file descriptor management for active connections.
- Offer troubleshooting tips and strategies for effective server management.

## Table of Contents
1. [Maximum Team Sizes](#maximum-team-sizes)
2. [Managing Large Teams](#managing-large-teams)
   - 2.1 [Configuring Team Size](#configuring-team-size)
   - 2.2 [Team Updates and WebSocket Notifications](#team-updates-and-websocket-notifications)
3. [Conversation Membership Limits](#conversation-membership-limits)
4. [File Descriptor Management](#file-descriptor-management)
5. [Recap and Conclusions](#recap-and-conclusions)

## Maximum Team Sizes

By default, the maximum number of users in a team within Wire is capped at **500**. However, this limit can be modified. The configuration in the Brig settings allows you to increase this limit through the following setting:

```yaml
optSettings:
  setMaxTeamSize: 501
```

This adjustment permits the creation of teams with user counts higher than the standard limit. 

### Important Notes:
- If your team surpasses **2000 members**, some real-time team update events, such as notifications regarding new members joining, will not be delivered via WebSocket connections. However, this limitation does not significantly obstruct the overall functioning of the application.
- Individual conversations, regardless of team size, maintain a strict upper limit of **2000** members. This cannot be overridden due to backend constraints that only support fan-out messaging to a maximum of 2000 recipients, which is an ongoing area for enhancement in future updates.

## Managing Large Teams

### Configuring Team Size
To modify the maximum size of teams within your Wire infrastructure, follow these steps:
1. Access the Brig configuration file.
2. Locate the `optSettings` section.
3. Insert or edit the `setMaxTeamSize` option as shown previously.

### Team Updates and WebSocket Notifications
When handling a team that exceeds **2000** members, you should be aware:
- Clients will not receive live websocket notifications for certain updates.
- Despite this, regular functionality should remain intact for most applications.

## Conversation Membership Limits

While teams can have flexible member limits beyond 500, it’s critical to note that conversation memberships are still restricted to **2000** participants. The backend architecture only permits sending a message to a maximum of 2000 recipients at a time, which is why this limit cannot be increased arbitrarily. Adjustments in this area are an ongoing endeavor.

## File Descriptor Management

For servers hosting connections with many users, managing file descriptors becomes vital. Wire’s Restund server (used for TURN connections) requires careful monitoring of allocations associated with active participant connections. Each allocation between a participant requires **1 or 2 file descriptors.**

### Recommendations:
- Ensure your server's file descriptor limits are adequately increased if you operate with a larger user base. 
- Currently, a single Restund server supports up to **64,000** allocations. If you anticipate exceeding this number during active calls, deploying additional Restund servers is necessary to maintain performance.

## Recap and Conclusions

In summary, managing larger teams in Wire encompasses adjusting maximum team size settings, addressing limitations in conversation membership, and effectively managing file descriptors for connections. For infrastructure managers, maintaining these configurations ensures that user experiences remain seamless and efficient, even with rising numbers in team memberships.

Key takeaways include:
- Default team limit is 500, extendable to 2000 with specific configurations.
- Conversations capped at 2000 members, with backend limitations on message fan-out.
- Monitoring and adjusting file descriptor allocations are essential for handling many active participants.

This documentation serves as a foundational guide for those looking to optimize their use of Wire for larger collaborative environments.