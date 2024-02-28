# Data Engineer Take-Home Challenge: Mini ETL Pipeline.

### Objective

Develop a data processing pipeline that tranforms a large volume of text data from a Kinesis stream into a format suitable for the continuous training a text summarization model. The pipeline should leverage Python and be designed with enterprise-scale data processing tools in mind.

---

### Background

You're part of a dynamic team at a company specializing in NLP services dedicated to assisting news aggregators and content curators. The company's mission is to automate the summarization of articles and reports from diverse sources, enabling rapid access to distilled insights. This task is crucial for staying ahead in the fast-paced world of news and content curation, where the ability to quickly summarize and understand large volumes of text data can provide a significant competitive edge. 


### Overview

The NLP model must be trained on a regular schedule to keep up-to-date on the stylistic elements of modern journalism. Therefore in this challenge, you are entrusted with the development of a data pipeline capable of processing incoming text data efficiently. The ultimate goal is to enhance this data in ways that bolster machine learning (ML) training scenarios. This includes considering how the result is stored, ensuring that it supports efficient data access patterns suitable for large-scale processing and ML model training.

To kickstart your task, you are provided with a sample dataset alongside a foundational setup designed to simulate the ingestion of streaming text data. Your challenge is to extend and optimize this setup in a way explained below.

---

### Objective

Develop a data processing pipeline that retrieves each record from a Kinesis stream, enriches it by adding a calculated feature (e.g., word count) to every record, and computes the average of this metric for all records. The enriched records, now including the additional feature, should then be stored in an S3 bucket, ready for subsequent processing steps. Note that only the enriched records need to be stored; the calculated average does not require storage."


## **Getting Started**

### **Setup Instructions**

1. **Environment Setup**: Ensure Docker and Docker Compose are installed on your system. The provided **`docker-compose.yml`** includes services for LocalStack (simulating AWS S3 and Kinesis).
2. **Running the Pipeline**: Execute ```docker-compose up``` to launch the services. This command initiates a simulated AWS environment for your pipeline's operation. The setup involves starting two containers: one for simulating AWS services like S3 and Kinesis, and another for populating the Kinesis stream (named "MyStream") with approximately 1000 records and creating an S3 bucket ("my-bucket") for storage. The population script runs iteratively, simulating the continuous generation of data. 

### **Note to Candidates**
We understand that real-world data engineering projects often require dealing with incomplete information or making educated guesses about the best approach to a problem. In this challenge, should you encounter any ambiguities or feel that certain details are not specified, you are encouraged to make reasonable assumptions to fill in the gaps. Please document any such assumptions and the rationale behind them in your submission. This will help us understand your thought process and decision-making skills in navigating real-world scenarios.

## **Requirements**

- While not mandatory, you are encouraged to use an enterprise-scale data processing solution such as Metaflow, MLFlow, Spark, Apache Flink, or any other tool suitable for distributed processing of large datasets. Be prepared to justify your choice.
- Incorporate any new dependencies into the docker-compose environment, ensuring they can run locally and offline within Docker containers.
- Design your solution to facilitate machine learning training, focusing on data batching, storage, and retrieval for optimized access in large-scale ML model training.
- Provide documentation on how to set up and run your solution. Outline your design decisions, especially those related to the choice of data processing tools and storage for ML training.

## Submission Instructions

Clone this repository to download the boiler plate. Build your application based on this foundation and update the README accordingly. Submit your completed challenge via email.

## Notes from the submission:

- Run the same ```docker-compose up``` command. As observed in the logs, Metaflow will be triggerred by 'listener.py' in "process-stream" container. Each record will be read, processed, and saved to S3.

- Since each run of Metaflow is independent, the average word count is not calculated across all runs. However, since the result JSON files are saved in S3, we can use Athena to query them using SQL.   
```
CREATE EXTERNAL TABLE IF NOT EXISTS records_table (
  `article_id` string,
  `title` string,
  `author` string,
  `publish_date` string,
  `content` string,
  `word_count` int
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://my-bucket/';

SELECT AVG(word_count) as average_word_count FROM records_table;


