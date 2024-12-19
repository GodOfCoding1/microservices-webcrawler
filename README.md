## Web Crawler Microservice

This microservice app will crawl https://search.sunbiz.org/Inquiry/CorporationSearch/ByName according to the query given by the user.

### Demo link

https://drive.google.com/file/d/1jSO4YeJ0oU6kyq7H6e31YhWR2uNRjS5k/view?usp=sharing

### Setup

- Clone the repo
  ```git clone https://github.com/GodOfCoding1/microservices-webcrawler.git```
- cd into the repo
  ```cd microservices-webcrawler```
- run: ```docker-compose up```
  initial run of above command may take time
- go to localhost:3000 to access the react app after all services are up and running

### Database Design

<img width="933" alt="image" src="https://github.com/user-attachments/assets/2fa422e7-ce90-4bed-b8af-536adab63f31" />

### Microservice Design

- Main backend api - responsible for saving to the database and invoking requests to crawler if needed. Has a queue system to enable asynchronous saving to database (users will get faster response as they are not waiting for save to database to finish)
- Crawler - responside for crawling the website accordin to the query given
- Postgresql Instance
- Frontend- Frontend made in react

### Assumptions 

- Assumes the data never changes after initial query. Would have been time consuming to impliment
