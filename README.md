### Distributed Systems Project

## EMERGENCY SERVICE DISPATCHER

#### Introduction
The Emergency Service Dispatcher project aims to enhance emergency response systems through a robust Client-Server architecture integrated with the Google Maps API. The system manages incoming emergency requests, identifies the nearest emergency dispatcher, calculates estimated arrival times (ETA), and coordinates effective response efforts.

#### Problem Statement
Existing emergency dispatch systems often lack real-time data integration and efficient resource allocation mechanisms, leading to delays and inefficiencies. Manual coordination and disparate communication channels further exacerbate these challenges. Our system addresses these issues by providing a streamlined, automated solution.

#### Motivation
The motivation behind developing the Emergency Service Dispatcher system is to improve the efficiency and effectiveness of emergency responses. By leveraging modern technologies, the system aims to optimize resource allocation, reduce response times, and enhance overall emergency management.

#### Project Overview
The Emergency Service Dispatcher system includes the following core functionalities:

1. Database Management:
   - Utilizes an SQLite database to store dispatcher information and emergency logs.

2. Google Maps Integration:
   - Integrates with the Google Maps API for geocoding addresses and calculating routes and ETAs.

3. Nearest Dispatcher Logic:
   - An algorithm to identify the nearest dispatcher based on emergency type and location.

4. Server-Client Communication:
   - Employs socket programming to establish communication between the server and clients.

5. Twilio API Integration:
   - Notifies first responders using the Twilio API, ensuring prompt communication and coordination.

 #### Prerequisites
- Python 3.x
- SQLite
- Google Maps API key
- Twilio API account

#### Discussion
The Emergency Service Dispatcher system significantly improves emergency response coordination and efficiency. By integrating modern technologies and providing real-time data and notifications, the system enhances the effectiveness of emergency services.

#### Conclusion & Future Works
The project represents a significant advancement in emergency response coordination. Future enhancements could include refining the nearest dispatcher algorithm, integrating additional communication channels (SMS, email), and developing a real-time dashboard for monitoring emergency response performance.

#### References
1. Google Maps Geocoding API
2. Google Maps Services Python
3. Twilio Python GitHub
4. Computer Networking: A Top-Down Approach, Jim Kurose
5. Operating System Concepts, Abraham Silberschatz, Greg Gagne, Peter Baer Galvin
6. Distributed Systems, Coulouris G., Dollimore J., and Kindberg T., Pearson
