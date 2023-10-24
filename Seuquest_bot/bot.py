import faiss,random, spacy
from langchain.vectorstores import FAISS,Qdrant
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.prompts import HumanMessagePromptTemplate,SystemMessagePromptTemplate,ChatPromptTemplate
from qdrant_client import QdrantClient
from qdrant_client.http import models as QdrantModel
from qdrant_client.http import models as qdrant_models

class SeuQuest:
    """

    Methods
    -----
        * load_vectordb  (Don't takes any parameters)
        * text_splitter  (Takes only one string parameter)
        * csv_splitter   (Takes only path of the document)
        * train          (Takes two parameters one is training data and another one is data type if data type is document pass True else False)
        * marge_vectordb (takes vector store as parameter and marge with default vector store)
        * set_as_default_vectordb (It only take a vector store as parameter and the vector as set default vector store)
        * make_conversation (Don't takes any parameters it helps to create conversation chains)
        * generate_answer (It takes two parameters conversation chain and human quey)


    """
    __kyes = ["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","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"]
    embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")

    def __init__(self):
        self.vectordb = None
        self.__message_template()


    class Faiss:
        """
        manage faiss vector store
        The Faiss class is a Python class that provides methods for loading, training, merging, and
        saving vector databases using the Faiss library.
        """
        def __init__(self,instance,path):
            self.instance = instance
            self.path = path

        def load(self):
            """
            The function loads a local FAISS database and assigns it to the instance's vectordb
            attribute if it is None.
            :return: The `load` function is returning the `load_db` variable.
            """
            load_db = FAISS.load_local(self.path,embeddings=self.instance.embeddings)
            if self.instance.vectordb is None:
                self.instance.vectordb = load_db
            return load_db

        def train(self ,data,document=False):
            """
            The function `train` trains a vector database using either a list of documents or a list of
            texts.

            :param data: The `data` parameter is the input data that will be used to train the vector
            database. It can be either a list of documents or a list of texts, depending on the value of
            the `document` parameter
            :param document: The `document` parameter is a boolean flag that indicates whether the input
            data is in document format or not. If `document` is set to `True`, it means that the input
            data is a list of documents. If `document` is set to `False`, it means that the input data,
            defaults to False (optional)
            :return: the created vector database.
            """
            try:
                if document:
                    create_vectordb = FAISS.from_documents(data,embedding=self.instance.embeddings)
                else:
                    create_vectordb = FAISS.from_texts(data,embedding=self.instance.embeddings)

                return create_vectordb
            except:
                print("Failed to train")

        def marge(self,db,*args,**kwargs):
            """
            The function "marge" merges a given database with the current database and returns the
            merged database.

            :param db: The "db" parameter is a database object that is being passed into the "marge"
            method
            :return: the merged `vectordb` object.
            """
            new_vectordb = self.vectordb.merge_from(db)
            return new_vectordb

        def save(self,db,path):
            """
            The function saves a vectorstore to a specified path and prints a confirmation message.

            :param db: The "db" parameter is likely an instance of a database object or a data structure
            that contains the vectorstore data. It is used to access and manipulate the data in the
            vectorstore
            :param path: The `path` parameter is a string that represents the file path where the
            vectorstore will be saved
            """
            db.save_local(path)
            print("Saved new vectorstore to"+path)



    class QDRANT:
        """
        The `QDRANT` class is a Python class that provides methods for interacting with the QDRANT
        vector database, including loading collections, training collections with data, and overwriting
        payload for specific points in a collection.
        """
        def __init__(self,instance,url,api_key):
            self.instance = instance
            self.url = url
            self.api_key = api_key
            self.client_ = self.client()

        def client(self):
            """
            The function creates and returns a QdrantClient object with the specified URL and API key.
            :return: an instance of the QdrantClient class.
            """
            client_ = QdrantClient(

                url=self.url,
                api_key=self.api_key,
            )
            return client_

        def load(self,collection_name):
            """
            The function loads a collection from a Qdrant database and returns the loaded collection.

            :param collection_name: The `collection_name` parameter is the name of the collection in the
            Qdrant database where you want to load the vectors
            :return: The `load` function returns the `vectordb` object.
            """
            vectordb = Qdrant(
                    client=self.client_,
                    collection_name=collection_name,
                    embeddings=self.instance.embeddings
                )
            if self.instance.vectordb is None:
                self.instance.vectordb = vectordb

            return vectordb

        def new_collection(self,collection_name,data,document=False):
            collection_config = QdrantModel.VectorParams(
                size=768, # 768 for instructor-xl, 1536 for OpenAI
                distance=QdrantModel.Distance.COSINE
            )

            self.client_.recreate_collection(
                collection_name=collection_name,
                vectors_config=collection_config
            )
            create_vectordb = self.load(collection_name)
            if document:
                create_vectordb.add_documents(data)
            else:
                create_vectordb.add_texts(data)
            return create_vectordb

        def train(self,data,metadata):
            """
            The train function takes in data and metadata, cleans the text, splits it into multiple
            texts, adds the texts and metadata to a vector database, and returns the vector database.

            :param data: The "data" parameter is the input text data that you want to train the model
            on. It could be a single string or a list of strings, depending on how you want to structure
            your training data
            :param metadata: The metadata parameter is a piece of additional information associated with
            each text in the data. It can be any relevant information that you want to store and
            associate with the texts
            :return: The code is returning the instance of the vectordb object.
            """
            clean_text =  SeuQuest.text_cleaner(data)
            texts = SeuQuest.text_splitter(clean_text)
            metadata_list = [metadata for i in range(len(texts))]
            self.instance.vectordb.add_texts(texts=texts,metadatas=metadata_list)
            return self.instance.vectordb

        def overwrite_payload(self,collection_name:str,points:list[str,int],payload:dict):
            """
            The function `overwrite_payload` takes in a collection name, a list of points, and a payload
            dictionary, and calls a method to overwrite the payload for the specified points in the
            specified collection.

            :param collection_name: The name of the collection where the payload will be overwritten
            :type collection_name: str
            :param points: The "points" parameter is a list of strings and integers. It represents the
            points or coordinates in the collection that you want to overwrite with the new payload.
            Each element in the list should be a string or an integer
            :type points: list[str,int]
            :param payload: The `payload` parameter is a dictionary that contains the data you want to
            overwrite for the specified points in the collection. It should have key-value pairs where
            the keys represent the fields in the collection and the values represent the new values you
            want to set for those fields
            :type payload: dict
            :return: The result of the `overwrite_payload` method is being returned.
            """
            result = self.client_.overwrite_payload(collection_name=collection_name,points=points,payload=payload)
            return result


    @staticmethod
    def text_splitter(text):
        """
        The function `text_splitter` takes in a text and splits it into chunks of a specified size, with
        a specified overlap, using a character separator.

        :param text: The input text that you want to split into chunks
        :return: the split text.
        """
        spliter = CharacterTextSplitter(separator="\n",chunk_size=4080,chunk_overlap=50)
        split_text = spliter.split_text(text)
        return split_text

    @staticmethod
    def text_cleaner(text_data):
        """
        The function `text_cleaner` takes in a string of text data, removes stop words and punctuation
        using the spaCy library, and returns the cleaned text as a string.

        :param text_data: The `text_data` parameter is a string that represents the input text that you
        want to clean
        :return: The function `text_cleaner` returns the cleaned text data after removing stop words and
        punctuation.
        """
        nlp = spacy.load("en_core_web_md")
        doc = nlp(text_data)
        clean_tokens = [token.text for token in doc if (token.text == "." or token.text == ":") or (not token.is_stop and not token.is_punct)]
        cleaned_text = " ".join(clean_tokens)
        return cleaned_text

    @staticmethod
    def csv_splitter(file):
        """
        The function `csv_splitter` takes a file as input, loads the CSV data from the file using a
        CSVLoader object, and returns the extracted data.

        :param file: The "file" parameter is the path or name of the CSV file that you want to split
        :return: the extracted data from the CSV file.
        """
        load_csv = CSVLoader(file)
        extract_data = load_csv.load()
        return extract_data


    def set_as_default_vectordb(self,db):
        """
        The function sets a given database as the default vectordb.

        :param db: The "db" parameter is the database that you want to set as the default vectordb
        """
        self.vectordb = db

    def __message_template(self):
        """
        The function defines a message template for a chat prompt in a Python program.
        """
        self.__system_message_template = ''''
        You are SeuQuest Ai bot. crafted by Tanjim Abubokor for help students with Southeast University info. Use the following pieces of context to answer the question.
        ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
        {context}

        '''
        self.__user_question_template = "{question}"

        messages = [
            SystemMessagePromptTemplate.from_template(self.__system_message_template),
            HumanMessagePromptTemplate.from_template(self.__user_question_template)
        ]
        qa_prompt = ChatPromptTemplate.from_messages(messages)
        self.__qa_prompt = qa_prompt

    def qdrant_metadata_filtering(metadatas):
        # qdrant filtering (must)
        must:dict = metadatas.get("must",None)
        filter_must = []
        if must is not None:
            for key,values in must.items():
                for value in values:
                    condition = qdrant_models.FieldCondition(
                                        key="metadata."+str(key),
                                        match=qdrant_models.MatchValue(value=str(value))
                                    )
                    filter_must.append(condition)

        # qdrant filtering (must_not)
        must_not:dict = metadatas.get("must_not",None)
        filter_must_not = []
        if must_not is not None:
            for key,values in must_not.items():
                for value in values:
                    condition = qdrant_models.FieldCondition(
                                    key="metadata."+str(key),
                                    match=qdrant_models.MatchValue(value=str(value))
                                )
                    filter_must_not.append(condition)

        # qdrant filtering (should)
        should:dict = metadatas.get("should",None)
        filter_should = []
        if should is not None:
            for key,values in should.items():
                for value in values:
                    condition = qdrant_models.FieldCondition(
                                    key="metadata."+str(key),
                                    match=qdrant_models.MatchValue(value=str(value))
                                )
                    filter_should.append(condition)

        filter_ = qdrant_models.Filter(
                must=[must_ for must_ in filter_must],
                must_not=[must_not_ for must_not_ in filter_must_not],
                should = [should_ for should_ in filter_should]
                )

        return filter_

    def make_conversation(self,metadatas:dict[dict[list]]=None):
        """
        The `make_conversation` function creates a conversation object for conversational retrieval
        using Qdrant filtering and OpenAI's ChatGPT model.

        :param metadatas: The `metadatas` parameter is a dictionary that contains filtering conditions
        for the conversation. It has three keys: `must`, `must_not`, and `should`. Each key corresponds
        to a list of metadata conditions that need to be satisfied for a conversation to be included in
        the search results
        :type metadatas: dict[dict[list]]
        :return: The function `make_conversation` returns a `ConversationalRetrievalChain` object.
        """
        openai_api_key = random.choice(SeuQuest.__kyes)

        if metadatas is not None:
            filter_ = SeuQuest.qdrant_metadata_filtering(metadatas)

            retriever = self.vectordb.as_retriever(
                    search_kwargs=dict(
                        k=4,
                        filter=filter_
                    )
                )
        else:
            retriever = self.vectordb.as_retriever()

        llm = ChatOpenAI(openai_api_key=openai_api_key)
        memory = ConversationBufferMemory(memory_key="chat_history",return_messages=True)
        conversation = ConversationalRetrievalChain.from_llm(llm=llm, memory=memory, verbose=False,
                                                      retriever=retriever,
                                                      max_tokens_limit=4000,
                                                      chain_type="stuff",
                                                      combine_docs_chain_kwargs={"prompt":self.__qa_prompt}
                                                      )
        return conversation

    def generate_answer(self,question,metadatas:dict[dict[str]]=None):
        """
        The function `generate_answer` takes a question and optional metadata as input, creates a
        conversation using the metadata, and returns the answer to the question.

        :param question: The "question" parameter is a string that represents the question you want to
        ask. It is the input to the function and will be used to generate the answer
        :param metadatas: The `metadatas` parameter is a dictionary that contains additional information
        or context related to the conversation. It is an optional parameter, so it can be set to `None`
        if not needed
        :type metadatas: dict[dict[str]]
        :return: The function `generate_answer` returns the answer to the given question.
        """
        conversation = self.make_conversation(metadatas=metadatas)
        response = conversation({"question":question})
        answer = response['answer']
        return answer

