"""Dashboard displaying information about plant data."""
import streamlit as st

if __name__ == "__main__":
    url = "https://liverpool-museums.shorthandstories.com/rise-of-liverpool-botanical-trust/assets/tObQ2mJ4vA/green-jade-vine-liverpool-express-thumbnail.jpg"
    left_co, cent_co, last_co = st.columns([1, 3, 1])
    with cent_co:
        st.header("LNHM Conservatory Sensor Checks")

        st.write("")
        st.write("")

        st.image(url)

        st.write("")
        st.write("")

        st.write("""
        This dashboard provides a comprehensive overview
        on data collected from the sensors at the conservatory
        for each plant. 

        
        Every recording represents key details like when the recording
        was taken, the plant name and id, soil moisture (%), time of 
        last watering and temperature (°C).

        
        There are two dashboards which can be viewed on separate 
        pages (see LHS menu)—one for live data, which is best for low granularity
        (e.g., mins/hours) or historical data that summarises the 
        live data into longer timeframes, which is best for analysing patterns. 

        
        Overall this project aims to provide gardeners with detailed reports on the
        health of each plant at the LNHM conservatory so that they can
        optimise their care and potentially increase visitor satisfaction 
        in the process.  
        """)
