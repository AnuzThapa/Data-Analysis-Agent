# from scout.graph import Agent
# from scout.prompts import prompts


# def main():
#     try:
#         # A config is required for memory. All graph checkpoints are saved to a thread_id.
#         config = {
#             "configurable": {
#                 "thread_id": "1"
#             }
#         }

#         agent = Agent(
#             name="Scout",
#             system_prompt=prompts.scout_system_prompt,
#             model="llama3.2:latest",
#             temperature=0.1
#         )

#         # Stream responses
#         while True:
#             user_input = input("User: ")
#             if user_input.lower() in ["exit", "quit"]:
#                 break

#             print(f"\n---- User ---- \n\n{user_input}\n")

#             print(f"---- Assistant ---- \n")
#             # Get the response using our simplified get_stream function
#             result = agent.stream(user_input, config=config)

#             for message_chunk in result:
#                 if message_chunk:
#                     print(message_chunk, end="", flush=True)

#             thread_state = agent.runnable.get_state(config=config)

#             if "chart_json" in thread_state.values:
#                 chart_json = thread_state.values["chart_json"]
#                 if chart_json:
#                     import plotly.io as pio
#                     fig = pio.from_json(chart_json)
#                     fig.show()
#             print("")

#     except Exception as e:
#         print(f"Error: {type(e).__name__}: {str(e)}")
#         raise


# if __name__ == "__main__":
#     print(f"\nGreetings!\n\nTry asking Scout to show you a preview of the data.\n\n{40*"="}\n\n")

#     main()


# import streamlit as st
# import plotly.io as pio
# from scout.graph import Agent
# from scout.prompts import prompts

# # Initialize session state
# if "agent" not in st.session_state:
#     st.session_state.agent = Agent(
#         name="Scout",
#         system_prompt=prompts.scout_system_prompt,
#         model="llama3.2:latest",
#         temperature=0.1
#     )
#     st.session_state.thread_id = "1"
#     st.session_state.config = {
#         "configurable": {
#             "thread_id": st.session_state.thread_id
#         }
#     }
#     st.session_state.messages = []

# agent = st.session_state.agent
# config = st.session_state.config

# st.set_page_config(page_title="Scout DB Agent", layout="wide")
# st.title("🔍 Scout: DB Query Agent")

# # Chat interface
# st.markdown("Ask a question about your database (e.g., *How many customers are there?*)")

# user_input = st.text_input("You:", key="input", placeholder="Type your question here and press Enter")

# if user_input:
#     st.session_state.messages.append(("user", user_input))

#     with st.spinner("Thinking..."):
#         response_container = st.empty()
#         response_text = ""

#         # Stream response
#         # for chunk in agent.stream(user_input, config=config):
#         #     if chunk:
#         #         response_text += chunk
#         #         response_container.markdown(f"**Scout:** {response_text}")
#         tool_call_text = ""

#         for chunk in agent.stream(user_input, config=config):
#             if chunk:
#                 if "< TOOL CALL:" in chunk:
#                     # This marks the beginning of a tool call (query)
#                     tool_call_text += f"\n\n🔧 {chunk.strip()}"
#                 elif chunk.startswith("{") or chunk.startswith("[") or "SELECT" in chunk.upper():
#                     # Likely part of the tool args (SQL or JSON)
#                     tool_call_text += f"\n```sql\n{chunk.strip()}\n```"
#                 else:
#                     # Natural language response
#                     response_text += chunk
#                 # Update display dynamically
#                 response_container.markdown(f"**Scout:** {response_text}\n{tool_call_text}")

#         # Save to message history
#         st.session_state.messages.append(("assistant", response_text))

#         # Check for chart and render it
#         thread_state = agent.runnable.get_state(config=config)
#         if "chart_json" in thread_state.values:
#             chart_json = thread_state.values["chart_json"]
#             if chart_json:
#                 fig = pio.from_json(chart_json)
#                 st.plotly_chart(fig, use_container_width=True)

# # Display chat history
# st.markdown("---")
# for role, message in st.session_state.messages:
#     if role == "user":
#         st.markdown(f"**You:** {message}")
#     elif role == "assistant":
#         st.markdown(f"**Scout:** {message}")
#         # st.markdown(f"**Query:**\n```sql\n{query}\n```\n\n**Result:**\n{result}")


import streamlit as st
import plotly.io as pio
from dbagent.graph import Agent
from dbagent.prompts import prompts

# Set up Streamlit page
st.set_page_config(page_title="MR.Lang DB Agent", layout="wide")
st.title("🔍 Mr.Lang: DB Query Agent")

# Session state initialization
if "agent" not in st.session_state:
    st.session_state.agent = Agent(
        name="Lang",
        system_prompt=prompts.lang_system_prompt,
        model="llama3.2:latest",
        temperature=0.1
    )
    st.session_state.thread_id = "1"
    st.session_state.config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }
    st.session_state.messages = []  # stores {"role": ..., "content": ...}

agent = st.session_state.agent
config = st.session_state.config

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input at the bottom
if user_input := st.chat_input("Ask something about your database..."):
    # Display user's message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Create assistant container
    with st.chat_message("assistant"):
        response_container = st.empty()
        response_text = ""
        tool_call_text = ""

        with st.spinner("Mr.Lang is thinking..."):
            for chunk in agent.stream(user_input, config=config):
                if chunk:
                    if "< TOOL CALL:" in chunk:
                        tool_call_text += f"\n\n🔧 {chunk.strip()}"
                    elif chunk.startswith("{") or chunk.startswith("[") or "SELECT" in chunk.upper():
                        tool_call_text += f"\n```sql\n{chunk.strip()}\n```"
                    else:
                        response_text += chunk

                    response_container.markdown(f"{response_text}\n\n{tool_call_text}")

        # Save assistant message
        st.session_state.messages.append({"role": "assistant", "content": f"{response_text}\n\n{tool_call_text}"})

        # Render chart if available
        thread_state = agent.runnable.get_state(config=config)
        if "chart_json" in thread_state.values:
            chart_json = thread_state.values["chart_json"]
            if chart_json:
                fig = pio.from_json(chart_json)
                st.plotly_chart(fig, use_container_width=True)
