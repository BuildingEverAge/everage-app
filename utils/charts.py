import matplotlib.pyplot as plt
import streamlit as st

def show_progress_chart(data):
    if not data:
        st.info("No check-in data yet.")
        return
    labels = [d["date"] for d in data]
    values = [sum(d["checked"]) for d in data]
    plt.figure(figsize=(8, 4))
    plt.bar(labels, values, color='green')
    plt.ylabel("Habits Completed")
    plt.title("Weekly Habit Progress")
    st.pyplot(plt)
