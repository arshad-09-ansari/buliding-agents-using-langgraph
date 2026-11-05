
from model import create_table, seed_movies, Base, engine, Movies, Bookings
from db import movies

from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from pydantic import BaseModel, Field
from typing import Optional, TypedDict, Literal


# ==========================================
# STEP 1: DATABASE INITIALIZATION
# ==========================================

create_table()
seed_movies(movies)


# ==========================================
# STEP 2: INITIALIZE GROQ LLM
# ==========================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


# ==========================================
# STEP 3: DEFINE INTENT SCHEMA
# ==========================================

class IntentSchema(BaseModel):

    intent: Literal[
        "book_info",
        "confirm_booking",
        "cancel_booking",
        "check_booking",
        "general",
        "list_movies",
        "movie_details",
        "return_tickets"
    ] = Field(
        description="Intent identified from the user message"
    )

    reasoning: str = Field(
        description="Reason for selecting this intent"
    )


# ==========================================
# STEP 4: DEFINE LANGGRAPH STATE
# ==========================================

class CinemaState(TypedDict):

    user_message: str
    intent: Optional[str]
    movie_id: Optional[int]
    movie_title: Optional[str]
    customer_name: Optional[str]
    seats: Optional[int]
    booking_id: Optional[int]
    total_amount: Optional[float]
    result: Optional[str]
    reasoning: Optional[str]


# ==========================================
# STEP 5: STRUCTURED OUTPUT
# ==========================================

classifier_llm = llm.with_structured_output(IntentSchema)


# ==========================================
# STEP 6: CLASSIFIER PROMPT
# ==========================================

CLASSIFIER_PROMPT = """
You are an intent classifier for a movie ticket
booking application.

Identify what the user wants to do.

Available intents:

1. book_info:
   User wants to book new movie tickets.

2. confirm_booking:
   User explicitly confirms a pending booking.

3. cancel_booking:
   User wants to cancel an existing booking.

4. check_booking:
   User wants to check booking status or details.

5. general:
   Greetings and general conversation.

6. list_movies:
   User wants to see available movies.

7. movie_details:
   User wants information about a particular movie.

8. return_tickets:
   User wants to return booked tickets or request a refund.

Rules:

- Select exactly one intent.
- Understand the meaning, not just keywords.
- Do not assume that "yes" means booking confirmation.
- Confirmation requires pending booking context.
"""


# ==========================================
# STEP 7: CLASSIFIER NODE
# ==========================================

def classify_intent_node(state: CinemaState):

    query = state["user_message"]

    intent_result = classifier_llm.invoke([
        {
            "role": "system",
            "content": CLASSIFIER_PROMPT
        },
        {
            "role": "user",
            "content": query
        }
    ])

    print("\n========== CLASSIFIER RESULT ==========")
    print("User Message:", query)
    print("Detected Intent:", intent_result.intent)
    print("Reasoning:", intent_result.reasoning)

    return {
        "intent": intent_result.intent,
        "reasoning": intent_result.reasoning
    }


# ==========================================
# STEP 8: CREATE LANGGRAPH
# ==========================================

graph = StateGraph(CinemaState)

graph.add_node("classifier", classify_intent_node)

graph.add_edge(START, "classifier")

graph.add_edge("classifier", END)


# ==========================================
# STEP 9: COMPILE GRAPH
# ==========================================

memory = InMemorySaver()

final_graph = graph.compile(
    checkpointer=memory
)


# ==========================================
# STEP 10: TEST GRAPH
# ==========================================

if __name__ == "__main__":

    initial_state = {
        "user_message": "List all the movies",
        "intent": None,
        "movie_id": None,
        "movie_title": None,
        "customer_name": None,
        "seats": None,
        "booking_id": None,
        "total_amount": None,
        "result": None,
        "reasoning": None
    }

    config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    response = final_graph.invoke(
        initial_state,
        config
    )

    print("\n========== FINAL GRAPH STATE ==========")
    print(response)



def list_movies_node(state:CinemaState)-> dict:
    with Session(engine) as db:
        movies  =  db.qurey(Movies).all()
        all_movies = []
        for m in movies:
            all_movies.append({
                "id": m.id,
                "title": m.title,
                "genre": m.genre,
                "show_time": m.show_time
                "price_per_seat": m.price,
                "available_seats": m.available,
                "total_seats": m.total_seats,
            })
    return {"data": {"all_movies": all_movies}}     




def movie_detail_node(state:CinemaState)-> dict:
       movie = None
       with Seassion(engine) as db:
           if state.movie_id:
               movie  = db.get(Movies, state.movie_id)
           elif state.movie_title:
               movie = db.qurey(Movies).filter(Movies.title.ilike(f"%{state.movie_title}%")).first()
       if not movie:
           return{"data": {"error":"please provode correct movice id or title and try  to list to movie list"}}
       
       movie =  {
                           "id": movie.id,
                           "title": movie.title,
                           "genre": movie.genre,
                           "show_time": movie.show_time,
                           "price_per_seat": movie.price,
                           "available_seats": movie.available,
                           "total_seats": movie.total_seats,
                           
                }
       return {"data": {"movie": movie}}
   
              
                  