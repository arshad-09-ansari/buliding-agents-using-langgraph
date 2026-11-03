from dotenv import load_dotenv
from prompt_toolkit import prompt

load_dotenv()  # Load environment variables from .env file

 ###import all importats packages,
from langchain_groq  import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field
from typing import Annotated, Literal


### define llm objects
llm  = ChatGroq(model="openai/gpt-oss-120b")

###SGlobal State
class EmailState(BaseModel):
    question: str = ""
    mail_reason: str = ""
    recipient_name: str = ""
    recipiennt_email: str = ""
    subject: str = ""
    body: str = ""
    feedback: str = ""
    feedback_count: int = 0
    response: str = ""
    
###Node define 
class UserDetails(BaseModel):
    mail_reason: str= Field(description="Reason of the email like why user want to send this email ")
    recipient_name: str=Field(description="Name of the recipient of the name if avalile ")
    recipiennt_email: str=Field(description="Email address of the recipient of the email")



def retriever_node(state:EmailState) -> EmailState:
    llm_for_user_details = llm.with_structured_output(UserDetails)
    userDetails = llm_for_user_details.invoke("Retriefve the usr details from this qurey: {state.question}")
    
    
    if not userDetails.mail_reason or not userDetails.recipient_email:
       pass
    state.recipient_name = userDetails.recipient_name
    state.recipiennt_email = userDetails.recipiennt_email
    state.mail_reason = userDetails.mail_reason
    
    return state

### draft Node


class DraftEmail(BaseModel):
    subject: str= Field(description="Email subject within 40 words ")
    body: str=Field(description="Email body including proper details, reason and greeting and others ")


class EmailReview(BaseModel):
    approved: bool = Field(description="Whether the email draft is ready to send")
    feedback: str = Field(description="Actionable changes needed, or an empty string if approved")


def draft_node(state:EmailState) -> EmailState:
    "Draft a email"
    Dram_Email= llm.with_structured_output(UserDetails)
    
    prompt = """write a email with these details:
    To:{stae.recipient_name}, 
    Request:{state.mail_reason}
    
    
    please write a poer mail body andn subject withour extra test, Mail body max size will be 200 words.
    """
    draftEmail: DraftEmail = Dram_Email.invoke(prompt)
    state.subject = draftEmail.subject
    state.body = draftEmail.body
    return state


def review_node(state: EmailState) -> EmailState:
    print("\n")
    print("-"*50)
    print("suject: ", state.subject,"\n")
    print("body: ", state.body)
    print("-"*50)
    
    response = interrupt({
         "message":"Do you want to approve this or re-write the  email draft? (yes/no)"  
    })
    if response  == "yes":
        state.feedback == ""
    else:
        state.feedback = response
        state.feedback_count = state.feedback + 1
        
    
    
    return state
 
    
    
    def router(state:EmailState)-> Literal["draft","send", "cancel"]:
        if not state.feedback or state.feedback.strip() == "":
            return "send"
        
        if state.feedback_count >= 2:
            return "cancel"
        
        return "draft"
    
    ### cancel node
    def cancel_node(state:EmailState) -> EmailState:
        "cancel the email sending process"
        state.response = "email sending process cancelled"
        return state
    
    
    
    
    ### send node
    def send_node(state:EmailState) -> EmailState:
        "send final email" 
        state.response = "email sent succesfully"
        return state
        
    
    ### subject and body
    
    
    ### define the graph
    graph = StateGraph(EmailState)
    graph.add_node("retriever", retriever_node)
    graph.add_node("draft", draft_node)
    graph.add_node("send", send_node)
    graph.add_node("review", review_node)
    graph.add_node("cancel", cancel_node)
    
    
    ### define the edges
    graph.add_edge(START, "retriever" )
    graph.add_edge("retriever", "draft")
    graph.add_edge("draft", "review")
    graph.add_conditional_edges("review", router)
    graph.add_edge("send", END)
    graph.add_edge("cancel", END)
    
    final_graph = graph.compile(checkpointer = InmemorySaver())
    
    
    