# aws-bedrock
Aws Bedrock Related Info and Demo

Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon with a single API

Amazon Bedrock is a HIPAA eligible service and can be used in compliance with GDPR, allowing even more customers to benefit from generative AI

#### Infusing knowledge into LLM-powered systems

We have two primary types of knowledge for LLMs:
- Parametric knowledge: refers to everything the LLM learned during training and acts as a frozen snapshot of the world for the LLM.
- Source knowledge: covers any information fed into the LLM via the input prompt.

Fine-tuning, explored in other workshops, deals with elevating the parametric knowledge through fine-tuning. Since fine-tuning is a resouce intensive operation, this option is well suited for infusing static domain-specific information like domain-specific langauage/writing styles (medical domain, science domain, ...) or optimizing performance towards a very specific task (classification, sentiment analysis, RLHF, instruction-finetuning, ...).

Targeting the source knowledge for domain-specific performance uplift is very well suited for all kinds of dynamic information, from knowledge bases in structured and unstructured form up to integration of information from live systems. 

Retrieval-augmented generation, a common design pattern for ingesting domain-specific information through the source knowledge. It is particularily well suited for ingestion of information in form of unstructured text with semi-frequent update cycles. [rag](https://arxiv.org/pdf/2005.11401.pdf)

RAG Process

- Prepare documents Embeddings
  - Before being able to answer the questions, the documents must be processed and a stored in a document store index
    - Load the documents
    - Process and split them into smaller chunks
    - Create a numerical vector representation of each chunk using Amazon Bedrock Titan Embeddings model
    - Create an index using the chunks and the corresponding embeddings

- Ask question
  - When the documents index is prepared, you are ready to ask the questions and relevant documents will be fetched based on the question being asked. Following steps will be executed.
    - Create an embedding of the input question
    - Compare the question embedding with the embeddings in the index
    -  the (top N) relevant document chunks
    - Add those chunks as part of the context in the prompt
    - Send the prompt to the model under Amazon Bedrock
    - Get the contextual answer based on the documents retrieved

- Question Answering
  - Quick way
    You have the possibility to use the wrapper provided by LangChain which wraps around the Vector Store and takes input the LLM. This wrapper performs the following steps behind the scences:

      -  Takes input the question
      -  Create question embedding
      -  Fetch relevant documents
      -  Stuff the documents and the question into a prompt
      -  Invoke the model with the prompt and generate the answer in a human readable manner.

#### Generate embeddings
Use text embeddings to convert text into meaningful vector representations. You input a body of text and the output is a (1 x n) vector. You can use embedding vectors for a wide variety of applications. Bedrock currently offers Titan Embeddings for text embedding that supports text similarity (finding the semantic similarity between bodies of text) and text retrieval (such as search).
you can use amazon.titan-embed-g1-text-02 as embedding model via the API. The input text size is 8192 tokens and the output vector length is 1536.

##### Service Endpoints

- com.amazonaws.{REGION}.bedrock

- com.amazonaws.{REGION}.bedrock-runtime

##### Inference Parameters 

- Randomness and diversity

  - Temperature: LLMs use probability to construct the words in a sequence. For any given sequence, there is a probability distribution of options for the next word in the sequence. When you set the temperature closer to zero, the model tends to select the higher-probability words. When you set the temperature further away from zero, the model might select a lower-probability word.

  - Top P: Top P defines a cutoff based on the sum of probabilities of the potential choices. If you set Top P below 1.0, the model considers the most probable options and ignores the less probable ones.

- Length

  - Response length: Configures the maximum number of tokens to use in the generated response.

  - Stop sequences: A stop sequence is a sequence of characters. If the model encounters a stop sequence, it stops generating further tokens. Different models support different types of characters in a stop sequence, different maximum sequence lengths, and may support the definition of multiple stop sequences.

##### Inference Parameters - Stable Diffusion

- Prompt strength: This controls how strongly Stable Diffusion weights your prompt when it's generating images. It's a number between 1 and 30 (the default appears to be around 15). In the image above, you can see the prompt strength set to 1 (top) and 30 (bottom).

- Generation steps: This controls how many diffusion steps the model takes. More is generally better, though you do get diminishing returns. 

- Seed: This controls the random seed used as the base of the image. It's a number between 1 and 4,294,967,295. If you use the same seed with the same settings, you'll get similar results each time. 

##### Links

- [workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/en-US)

- [langchain](https://python.langchain.com/docs/get_started/introduction)

- [bedrock-pricing]( https://aws.amazon.com/jp/bedrock/pricing/)

- [blog-ga](https://aws.amazon.com/blogs/aws/amazon-bedrock-is-now-generally-available-build-and-scale-generative-ai-applications-with-foundation-models/?trk=55dc591c-143b-4ecb-898e-fa3dcd67469e&sc_channel=el)

- [embedding](https://docs.aws.amazon.com/bedrock/latest/userguide/embeddings.html)

- [workshop](https://github.com/aws-samples/amazon-bedrock-workshop)

- [rag](https://arxiv.org/pdf/2005.11401.pdf)

- https://qdrant.tech/

- https://explore.skillbuilder.aws/learn/course/external/view/elearning/17508/amazon-bedrock-getting-started

- https://aws.amazon.com/generative-ai/

- https://aws.amazon.com/bedrock/knowledge-bases/

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock.html

- https://huggingface.co/

##### Todo

- [ ] Test Claude Antropic 

- [ ] Retrieval Augmented Generation (RAG)
Privately customize FMs, RAG [link](https://aws.amazon.com/bedrock/knowledge-bases/)
You can deliver more contextual and relevant responses by incorporating organization-specific data through a process known as Retrieval Augmented Generation (RAG). With agents for Amazon Bedrock (in preview), you can create secure integration with your organization’s data sources by adding knowledge bases without retraining the FM.

You can quickly add a knowledge base by specifying a data source to ingest, such as Amazon S3, and an FM to convert the data to vector format such as Amazon Titan Embeddings. You can also specify a destination vector database to store vector data, such as the vector engine for Amazon OpenSearch Serverless, Pinecone, or Redis Enterprise Cloud.

Agents for Amazon Bedrock use knowledge bases to identify the appropriate data sources. The agents also retrieve relevant information based on user input, incorporate the retrieved information context into the user query, and provide a response. All of the information retrieved from knowledge bases comes with source attribution to improve transparency and minimize hallucinations.

- [ ] Fine Tune FM
You can fine-tune an FM for a particular task without having to annotate large volumes of data. Point Amazon Bedrock at a few labeled examples in Amazon Simple Storage Service (Amazon S3). Then, the service makes a separate copy of the base FM that is accessible only to you and trains this private copy of the FM. None of your data is used to train the original base FMs.


- [ ] Search and Embeddings
You can use the Amazon Titan Embeddings FM to create a vector of your organization’s data for semantic search. Vector embeddings are numerical representations of text, image, audio, and video data that can be used to understand the relationship between sentences or words. This helps find more relevant and contextual information for a user query. The embeddings can be stored in a vector database to use for streamlined, accurate searches.