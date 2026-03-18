import streamlit as st

st.title("Imprint")

st.markdown("## The Team behind this Project:")

col1, col2, col3, col4 = st.columns([0.4, 1, 0.4, 1])

with col2:
    st.markdown("""
    
        <br>
        <br>
        
        **Lenn Bartens**  
        Student of Business Informatics  
        Contact: stu247567@mail.uni-kiel.de
    """, unsafe_allow_html=True)

st.divider()

col1_2, col2_2, col3_2, col4_2 = st.columns([0.4, 1, 0.4, 1])

with col2_2:
    st.markdown("""
    
        <br>
        <br>
        
        **Felix Klinger**  
        Student of Business Informatics  
        Contact: stu246657@mail.uni-kiel.de
    """, unsafe_allow_html=True)

st.divider()

col1_3, col2_3, col3_3, col4_3 = st.columns([0.4, 1, 0.4, 1])

with col2_3:
    st.markdown("""
    
        <br>
        <br>
        
        **Moritz Hänsel**  
        Student of Business Informatics  
        Contact: stu244864@mail.uni-kiel.de
    """, unsafe_allow_html=True)

st.divider()

col1_4, col2_4, col3_4, col4_4 = st.columns([0.4, 1, 0.4, 1])

with col2_4:
    st.markdown("""
    
        <br>
        <br>
        
        **Anthime Willmann**  
        Student of Computer Science  
        Contact: stu247423@mail.uni-kiel.de
    """, unsafe_allow_html=True)

st.divider()
st.divider()

st.markdown("""
    ## University:

    This project was done as our Data-Science-Project as one of our mandatory modules at the Christian-Albrechts-University to Kiel.

    **Christian-Albrechts-University to Kiel**  
    Christian-Albrechts-Platz 4  
    24118 Kiel  
    Germany

    Contact: mail@uni-kiel.de
""")

st.divider()

col_left, col_middle, col_right = st.columns([1, 0.4, 1])

with col_middle:
    if st.button("Back to Homepage 🏠", width = "stretch"):
        st.switch_page("pages/homepage.py")