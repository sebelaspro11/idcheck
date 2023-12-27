import streamlit as st
import subprocess
import json
import pandas as pd
import pwnedpasswords
import re
from streamlit_option_menu import option_menu

selected = option_menu(
    menu_title=None,
    options=["Check Credential", "Check Password", "About"],
    icons=["unlock", "key", "info-lg"], # https://icons.getbootstrap.com/
    orientation="horizontal",
)

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

if selected == "Check Credential":
    
    def run_curl_command(query):
        # Construct the curl command with the user input
        curl_command = f"curl https://api.proxynova.com/comb?query={query}"

        # Run the curl command and capture the output
        process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        # Check if the command was successful
        if process.returncode == 0:
            # Decode the output as JSON
            json_output = json.loads(output.decode('utf-8'))
            return json_output
        else:
            # Return an error message if the command failed
            return {"error": error.decode('utf-8')}
        
        
    def create_dataframe_from_json(json_data):
        # Extract lines from JSON data
        lines = json_data.get('lines', [])

        # Create a list of dictionaries
        data_list = [line.split(':', 1) for line in lines if ':' in line]
        data_dict_list = [{'Email': email.strip('"'), 'Password': password.strip('"')} for email, password in data_list]

        # Create a DataFrame with index starting from 1
        df = pd.DataFrame(data_dict_list, index=range(1, len(data_dict_list) + 1))
        return df

    def highlight_row(val, query):
        return 'background-color: #66bf86' if query.lower() in str(val).lower() else ''

    def main_credential():
        st.title("Credential Check")
        st.markdown(''' 
                    - If you see your username or password in the results, change your password immediately and, if possible, turn on Multi-Factor Authentication (MFA).
                    ### Disclaimer
                    - While the purpose of this service is to encourage enhanced security practices, it's essential to recognize the potential for misuse and we take no responsibility for any misuse.
                    - Individuals could exploit the service by researching and attempting to use compromised passwords on different platforms, especially considering the common practice of password reuse.
                    ''')
        # Create a form to handle the submission
        with st.form(key="credential_form"):
            # Get the query input from the user
            query = st.text_input("Enter your query:", key="query", placeholder='Insert email, username, or password')

            # Add a submit button
            submit_button = st.form_submit_button(label="Search")

        # Check if the form is submitted
        if submit_button:
            # Run the curl command
            result = run_curl_command(query)

            # Display the count
            st.markdown(f"<p style='font-size:30px; font-family: Arial, sans-serif; color: white;'>Count: {result.get('count', 0)}</p>",
                        unsafe_allow_html=True)

            # Display the result
            if "error" in result:
                st.error(f"{result['error']}")
            else:
                df = create_dataframe_from_json(result)

                if df.empty:
                    st.warning("No results found.")
                else:
                    st.markdown(' #### Top Results')

                    # Apply highlighting
                    df_styled = df.style.applymap(lambda x: highlight_row(x, query))

                    # Render the DataFrame with highlighting
                    st.markdown(df_styled.to_html(escape=False), unsafe_allow_html=True)

if selected == "Check Password":
    def check_password_strength(password):
        # Check character types
        uppercase_count = sum(1 for c in password if c.isupper())
        lowercase_count = sum(1 for c in password if c.islower())
        number_count = sum(1 for c in password if c.isdigit())
        symbol_count = sum(1 for c in password if c in "!@#$%^&*()-_+=<>?/{}[]|\~`")

        # Categorize based on character types
        if uppercase_count >= 1 and lowercase_count >= 1 and number_count >= 1 and symbol_count >= 1:
            strength = "VERY STRONG"
        elif uppercase_count >= 1 and lowercase_count >= 1 and (number_count >= 1 or symbol_count >= 1):
            strength = "STRONG"
        elif uppercase_count >= 1 and lowercase_count >= 1:
            strength = "MEDIUM"
        elif len(password) >= 8:
            strength = "WEAK"
        else:
            strength = "VERY WEAK"

        return strength




    def main_password():
        st.title("Password Check")
        st.markdown(''' 
                    ### Guidelines to Create a Strong Passwords
                    - Password must not contain the user’s account name or parts of the user’s full name
                    - It should be at least six characters in length
                    - It must contain characters of the following four categories:
                        - English uppercase characters (A through Z)
                        - English lowercase characters (a through z)
                        - Base 10 digits (0 through 9)
                        - Non-alphabetic characters (for example, !, $, #, %)''')
        with st.form(key="password_form"):
            # Get the query input from the user as a password field
            user_input = st.text_input("Enter Password:", type="password", key="user_input")

            # Add a submit button
            submit_button = st.form_submit_button(label="Check Password")

        # Check if the form is submitted
        if submit_button:
            # Check password strength
            password_strength = check_password_strength(user_input)
            st.markdown(f"<p style='font-size:18px;'><strong>Password Strength:</strong> <strong>{password_strength}</strong></p>", unsafe_allow_html=True)



            # Check if the password has been Checked
            result = pwnedpasswords.check(user_input)
            #st.write(f"Password: {user_input}")
            if result:
                st.markdown(f"<p style='font-size: 18px;'><strong>This password has been Checked</strong> <strong style='color: red;'>{result}</strong> <strong> times.</strong> <strong>Please change your password and setup Multi-Factor Authentication (MFA) if it's available.</strong></p>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='font-size: 18px;'><strong>This particular password hasn't been identified in the records of leaked passwords.</strong><br><strong>Nonetheless, consider enhancing your account security by enabling Multi-Factor Authentication (MFA) if it's available.</strong></p>", unsafe_allow_html=True)

def main():
    if selected == "Check Credential":
        main_credential()
    elif selected == "Check Password":
        main_password()

if __name__ == "__main__":
    main()
    
if selected == "About":
    st.write("# Welcome to ID Check! 🔒")


    st.markdown(
        """
        This web application is your shield against compromised online credentials. Stay one step ahead of data breaches – Check the security of your accounts effortlessly!
        
        ### Check Credential
        - In February 2021, COMB (Combination Of Many Breaches), the largest dataset of leaked credentials, containing over 3.2 billion usernames and passwords from various breaches, was publicly disclosed.
        - This tool enables easy searching of this massive dataset, allowing individuals to check if their credentials were exposed and promoting enhanced security practices. It emphasizes the importance of changing passwords promptly and enabling two-factor authentication when available. 
        - No search records are logged or stored on the servers. 
        - Datasource: https://www.proxynova.com/
        ### Check Password
        - Consist of hundreds of millions of real-world passwords that have been compromised in data breaches. 
        - Due to this exposure, using them for ongoing purposes poses a significantly higher risk of being exploited to compromise other accounts.
        - No search records are logged or stored on the servers. 
        
    """
    )
