import pytest
from selenium import webdriver
from time import sleep
from selenium.webdriver.support.select import Select
import sqlite3

# Global variable
# Prepare the user and password for test
username_test = "test111"
password_test = "Aa123456!!"
institution_test = "SCE_Test"
faculty_test = "Chemistry_Test"
instID = 0
facID = 0

@pytest.fixture
def fill_db():
    global instID, facID

    # Prepare the institution
    db_name = "database.db"

    # connect to db to clean the created user
    con = sqlite3.connect(db_name)
    cursor=con.cursor()

    # Check if institution exists
    sqlQueryCheckExist = "SELECT * FROM Institutions WHERE InstitutionName = (?)"
    sqlRes = con.execute(sqlQueryCheckExist, (institution_test,))
    record = sqlRes.fetchone()
    
    # If institution does not exists create it
    if record == None:
        sqtInsertInst = "INSERT INTO Institutions (InstitutionName) VALUES (?)"
        cursor.execute(sqtInsertInst, (institution_test,))
        instID = cursor.lastrowid
    else:
        instID = record[0]
    
    # Check if faculty exists
    sqlQueryCheckExist = "SELECT * FROM Faculties WHERE FacultyName = (?)"
    sqlRes = con.execute(sqlQueryCheckExist, (faculty_test,))
    record = sqlRes.fetchone()
    
    # If faculty does not exists create it
    if record == None:
        sqlInsertFac = "INSERT INTO Faculties (FacultyName) VALUES (?)"
        cursor.execute(sqlInsertFac, (faculty_test,))
        facID = cursor.lastrowid
    else:
        facID = record[0]

    # Check if institution and faculty exists in FacIn table
    sqlQueryCheckExist = "SELECT * FROM FacIn WHERE InstitutionID = (?) AND FacultyID = (?)"
    sqlRes = con.execute(sqlQueryCheckExist, (instID, facID))
    record = sqlRes.fetchone()
    
    # If institution and faculty does not exists create it
    if record == None:
        sqtInsertInstFac = "INSERT INTO FacIn VALUES (?, ?)"
        con.execute(sqtInsertInstFac, (instID, facID))
    
    # Commit the changes in users table
    con.commit()

    # CLose connection to DB
    con.close()

def db_cleaner():
    # connect to db to clean the created user
    con = sqlite3.connect("database.db")

    # Check if user exists
    sqlQueryCheckExist = "SELECT * FROM Users WHERE UserName = (?)"
    sqlRes = con.execute(sqlQueryCheckExist, (username_test,))
    record = sqlRes.fetchone()
    
    # If user exists delete the user from DB
    if record != None:
        sqlDelete = "DELETE FROM Users WHERE UserName = (?)"
        sqlRes = con.execute(sqlDelete, (username_test,))

    # Check if institution and faculty exists in FacIn table
    sqlQueryCheckExist = "SELECT * FROM FacIn WHERE InstitutionID = (?) AND FacultyID = (?)"
    sqlRes = con.execute(sqlQueryCheckExist, (instID, facID))
    record = sqlRes.fetchone()
    
    # If faculty in institution exists delete it
    if record != None:
        sqtDelInstFac = "DELETE FROM FacIn WHERE InstitutionID = (?) AND FacultyID = (?)"
        con.execute(sqtDelInstFac, (instID, facID))

    # Check if faculty exists
    sqlQueryCheckExist = "SELECT * FROM Faculties WHERE FacultyName = (?)"
    sqlRes = con.execute(sqlQueryCheckExist, (faculty_test,))
    record = sqlRes.fetchone()
    
    # If faculty exists delete it
    if record != None:
        sqlDelFac = "DELETE FROM Faculties WHERE FacultyID = (?)"
        con.execute(sqlDelFac, (facID,))

    # Check if institution exists
    sqlQueryCheckExist = "SELECT * FROM Institutions WHERE InstitutionName = (?)"
    sqlRes = con.execute(sqlQueryCheckExist, (institution_test,))
    record = sqlRes.fetchone()
    
    # If institution exists create it
    if record != None:
        sqtDelInst = "DELETE FROM Institutions WHERE InstitutionID = (?)"
        con.execute(sqtDelInst, (instID,))

    # Commit the changes in users table
    con.commit()

    # CLose connection to DB
    con.close()
    

class TestIntegrationRegister:

    def test_register_page(self, application: str, ff_browser: webdriver.Firefox, fill_db):
        """Opening main page."""
        ff_browser.get(application)

        # Get the register button element
        btnRegister = ff_browser.find_element_by_xpath("/html/body/div[1]/div[2]/a[4]")

        # Click on login button
        btnRegister.click()

        # Get login screen header
        strRegisterHeader = ff_browser.find_element_by_xpath("/html/body/div[2]/h1")

        # Get message from login screen
        strMsg = strRegisterHeader.text

        assert (strMsg == "Register")

    def test_register_success(self, application: str, ff_browser: webdriver.Firefox):
        """Opening register page."""
        ff_browser.get(application + "/register")
        
        # Prepare the user and password for test
        fname_test = "test1"
        lname_test = "test1"
        year_test = 2

        # Get all elements on register page
        username = ff_browser.find_element_by_name("username")
        fname = ff_browser.find_element_by_name("fName")
        lname = ff_browser.find_element_by_name("lName")
        password = ff_browser.find_element_by_name("password")
        institution = Select(ff_browser.find_element_by_name("institution"))
        faculty = Select(ff_browser.find_element_by_name("faculty"))
        studyYear = ff_browser.find_element_by_name("year")

        # Get submit button element
        btnSubmit = ff_browser.find_element_by_xpath("/html/body/div[2]/form/input")

        # Inject username and password of test user
        username.send_keys(username_test)
        fname.send_keys(fname_test)
        lname.send_keys(lname_test)
        password.send_keys(password_test)
        institution.select_by_visible_text(institution_test)
        sleep(1)
        faculty.select_by_visible_text(faculty_test)
        studyYear.send_keys(year_test)

        # Click on submit button
        btnSubmit.click()

        # Get the welocme message element
        welcomeMsg = ff_browser.find_element_by_xpath("/html/body/div[1]/div[2]/b")

        assert welcomeMsg.text == ("Welcome " + username_test + "!")

class TestIntegrationLogin:
    
    def test_login_page(self, application: str, ff_browser: webdriver.Firefox):
        
        # Run logout to clean session
        ff_browser.get(application + "/logout")

        # Open the main page
        ff_browser.get(application)

        # Get the login button element
        btnLogin = ff_browser.find_element_by_xpath("/html/body/div[1]/div[2]/a[3]")

        # Click on login button
        btnLogin.click()

        # Get login screen header
        strLoginHeader = ff_browser.find_element_by_xpath("/html/body/div[2]/h1")

        # Get message from login screen
        strMsg = strLoginHeader.text

        assert (strMsg == "Login")

    def test_login_success(self, application: str, ff_browser: webdriver.Firefox):
        # Open the login page
        ff_browser.get(application + "/login")

        # Get username and password elements on page
        username = ff_browser.find_element_by_name("username")
        password = ff_browser.find_element_by_name("password")

        # Get submit button element
        btnSubmit = ff_browser.find_element_by_xpath("/html/body/div[2]/form/input")

        # Inject username and password of test user
        username.send_keys(username_test)
        password.send_keys(password_test)

        # Click on submit button
        btnSubmit.click()

        # Get the welocme message element
        welcomeMsg = ff_browser.find_element_by_xpath("/html/body/div[1]/div[2]/b")
        
        assert welcomeMsg.text == ("Welcome " + username_test + "!")
    
    def test_logout_success(self, application: str, ff_browser: webdriver.Firefox):
        """Performing logout from main screen"""
        ff_browser.get(application)
        
        # Get the logout button element
        btnLogout = ff_browser.find_element_by_xpath("/html/body/div[1]/div[2]/a[3]")

        # Click on logout button
        btnLogout.click()

        # Get buttons login and register that exist only if the user was not logged in
        btnLogin = ff_browser.find_element_by_xpath("/html/body/div[1]/div[2]/a[3]")
        btnRegister = ff_browser.find_element_by_xpath("/html/body/div[1]/div[2]/a[4]")

        # Save text of buttons
        strLogin = btnLogin.text
        strRegister = btnRegister.text
        
        assert ((strLogin == "Login") and (strRegister == "Register"))

        # Clean DB after end of all tests
        db_cleaner()