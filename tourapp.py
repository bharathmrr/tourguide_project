import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END, START
from langchain.tools import tool
from datetime import datetime
from langchain_community.retrievers import wikipedia
from langchain_community.tools import TavilySearchResults
from langchain_core.tools import Tool
from langchain.agents import AgentType, initialize_agent
from typing import TypedDict
import re

# Define the agent state
class AgentState(TypedDict):
    user_requments: str
    location: str
    overallinfo: str
    hotel_info: str
    final: str



wiki = wikipedia.WikipediaRetriever(
    language="en",
    include_summary=True,
    max_results=10
)

sercah = TavilySearchResults(
    tavily_api_key="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",
    max_results=10
)

llm = ChatGoogleGenerativeAI(api_key="AIzaSyAw8ZwA9d_T97JvC3xSAQB93cC_T53PShk", model="gemini-2.0-flash")

# Define tools
tools = [
   
    Tool(name="wikipedia_search", description="Search Wikipedia for information", func=wiki.get_relevant_documents),
    Tool(name="tavily_search", description="Search Tavily for information", func=sercah.run)
]

locationproppt = """You are a travel assistant specialized in weather-based location recommendations.
Given a user query describing their travel preferences, your job is to:
1. Understand their intent and weather preferences.
2. Suggest 2-3 candidate locations.
3. Check the past 30 days and upcoming 7-day forecast.
4. Recommend one best location and a few surrounding places.
Respond with:
- location:[location name]
- weather:[weather summary for past + next 7 days]
- surronding places:[names]
- why this place matches user preferences.
so query is: 
"""

hotel_serach_prompt = """You are a smart travel assistant. Based on the user’s request, find 3 to 5 hotels or hostels that best match their needs.
Include:
- 🏨 Hotel/Hostel name
- 💰 Price per night (approx.)
- ⭐ Review rating
- ✅ Key features (Wi-Fi, AC, views, etc.)
- 🔗 Booking or website link (if available)
- 📍 Location
- ⏱ Timing
User query:
"""

location_agent = initialize_agent(tools=tools, llm=llm, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION)
HOTEL_agent = initialize_agent(tools=tools, llm=llm, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION)

def location_node(state: AgentState) -> AgentState:
    query = locationproppt + state['user_requments']
    res = location_agent.invoke(query)
    location_extract_prompt = PromptTemplate.from_template(
        "Extract only the location name from the following travel recommendation:\n\n{res}"
    )
    extract_chain = location_extract_prompt | llm | StrOutputParser()
    location_name = extract_chain.invoke({'res': res})
    state['location'] = location_name.strip()
    state['overallinfo'] = res
    return state

def hotol_place(state: AgentState) -> AgentState:
    query = hotel_serach_prompt + state['location']
    state['hotel_info'] = HOTEL_agent.invoke(query)
    return state

def final_part(state: AgentState) -> AgentState:
    final_p = PromptTemplate(
        template="""You are a smart travel advisor. Based on the user’s query, generate a full travel suggestion:
📍 Recommended Destination: {location}
🌤 Weather Summary: Past 30 days & Next 7-day forecast
🏨 Hotel Options:
{hotel}
🏱 Surprise Nearby Place: Suggest one hidden gem based on the location {location}. Keep it relevant to the user's interests.
✅ Why this trip is perfect: Combine all elements including weather and comfort.
""",
        input_variables=["location", "hotel"]
    )
    ai = final_p | llm | StrOutputParser()
    result = ai.invoke({"location": state['location'], "hotel": state['hotel_info']})
    state['final'] = result
    return state

def user_ok(state: AgentState) -> dict:
    if 'streamlit_feedback' in state:
        if state['streamlit_feedback'] == 'ok':
            return {'__end__': True, 'final': state['final']}
        else:
            return {'user_requments': f"The suggested location {state['location']} wasn't liked. Reconsider for: {state['user_requments']}"}
    else:
        return state

graph = StateGraph(AgentState)
graph.add_node('location finder', location_node)
graph.add_node('hotels', hotol_place)
graph.add_node('final summary', final_part)
graph.add_node('user decide', user_ok)

graph.add_edge(START, 'location finder')
graph.add_edge('location finder', 'hotels')
graph.add_edge('hotels', 'final summary')
graph.add_edge('final summary', 'user decide')

graph.add_conditional_edges('user decide', lambda x: 'ok' if x.get('__end__') else 'no', {'ok': END, 'no': 'location finder'})
graph.set_entry_point('location finder')

tour = graph.compile()

# Streamlit Interface
st.title("🌞 AI Travel Planner")
user_query = st.text_input("Where would you like to travel? (e.g. very sunny place in North India)")

if user_query:
    inputs = {"user_requments": user_query}
    stream = tour.stream(inputs)

    final_result = None
    feedback_state = None

    for event in stream:
        if isinstance(event, dict) and 'final' in event:
            final_result = event['final']
            break

    if final_result:
        st.subheader("🧳 Suggested Travel Plan")
        st.markdown(final_result)
        feedback = st.radio("Do you like this suggestion?", ["ok", "no"], key="feedback")

        if st.button("Submit Feedback"):
            state = {
                "user_requments": user_query,
                "streamlit_feedback": feedback
            }
            stream = tour.stream(state)
            for event in stream:
                if isinstance(event, dict) and event.get("__end__"):
                    st.success("✅ Final Travel Plan Confirmed")
                    st.markdown(event["final"])
                    break
