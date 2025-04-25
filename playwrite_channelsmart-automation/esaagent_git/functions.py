

##dropdown###


def select_dropdown(page, select_id: str, option_id: str):
    page.wait_for_selector(select_id).click()
    page.wait_for_selector(option_id).click()

def type_into_input(page, input_xpath: str, value: str):
    input_field = page.wait_for_selector(f"xpath={input_xpath}")
    input_field.fill("")  # optional: clear existing text
    input_field.type(value)

def click_button_with_icon(page, icon_text: str):
    page.wait_for_selector(f"button:has(mat-icon:text('{icon_text}'))").click()


def search_user(page, user):
    select_dropdown(page, "#mat-select-0", "#mat-option-0")
    type_into_input(
        page,
        "/html/body/app-root/app-admin/div/div/app-esa-user/div[2]/div/app-card/div/div[2]/div/mat-form-field[2]/div/div[1]/div/input",
        user['email_id']
    )
    click_button_with_icon(page, "search")
    page.wait_for_timeout(1000)

    ###login###


# def login_to_channelsmart(page, email: str, password: str):
#     #page.goto("http://channelsmart.eshipz.com/")
#     page.goto("http://bluedartstorageuat.z29.web.core.windows.net/auth/signin")
#     page.wait_for_timeout(1000)  # Optional: allow page animations to settle
#
#     page.wait_for_selector("input[formcontrolname='email']").type(email)
#     page.wait_for_selector("input[formcontrolname='password']").type(password)
#     page.wait_for_timeout(1000)
#     page.get_by_role("button", name="Sign In").click()
#     page.wait_for_timeout(10000)
def login_to_channelsmart(page, email: str, password: str):
    page.goto("http://channelsmart.eshipz.com/users", timeout=60000)
    #page.goto("http://bluedartstorageuat.z29.web.core.windows.net/users",timeout=60000)

    page.wait_for_selector("input[formcontrolname='email']", timeout=10000).fill("loadtest@gmail.com")
    page.wait_for_selector("input[formcontrolname='password']", timeout=10000).fill("password")
    page.click("button:has-text('Sign In')")

    # Wait for either success or failure
    page.wait_for_timeout(3000)

    # Check if login failed
    if "signin" in page.url:
        page.screenshot(path="login_failed.png", full_page=True)
        raise Exception("❌ Login failed. Check credentials or UI changes.")

    print("✅ Login succeeded. Current URL:", page.url)

    #page.wait_for_selector("//button[text()='Sign In']").click()


### subadmin dropdown###
import pandas as pd
def search_user_by_email_from_csv(page, csv_path: str):
    """
    Reads the first email from the CSV and performs search using Playwright.

    Args:
        page (Page): Playwright page object
        csv_path (str): Path to the CSV file
    """
    try:
        df = pd.read_csv(csv_path)
        email_column = "email_id[mandatory]"
        if email_column not in df.columns:
            print("❌ Email column not found in CSV.")
            return

        email_id = df.iloc[0][email_column]

        # Interact with dropdown
        page.wait_for_selector("#mat-select-0").click()
        page.wait_for_selector("#mat-option-0").click()

        # Input email
        input_field = page.wait_for_selector(
            "xpath=/html/body/app-root/app-admin/div/div/app-esa-user/div[2]/div/app-card/div/div[2]/div/mat-form-field[2]/div/div[1]/div/input"
        )
        input_field.type(email_id)
        print(f"✅ Successfully entered email: {email_id}")

        # Click search button
        page.wait_for_timeout(1000)
        page.locator("button:has(mat-icon:text('search'))").click()

    except Exception as e:
        print(f"⚠️ Error in searching user: {e}")



####pickup user dropdown####

def fill_contact_number_from_csv(page, csv_path: str = "playwrite_channelsmart-automation/esaagent_git/pickup_template.csv"):
    # Read CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return

    # Extract contact number
    contact_number = df.iloc[0].get("contact_number[mandatory]", None)

    if contact_number:
        contact_number = str(contact_number)

        try:
            # Select dropdown
            page.wait_for_selector("#mat-select-0").click()
            page.wait_for_timeout(1000)
            page.wait_for_selector("#mat-option-0").click()
            page.wait_for_timeout(1000)

            # Type in the input field
            input_field = page.wait_for_selector(
                "xpath=/html/body/app-root/app-admin/div/div/app-esa-user/div[2]/div/app-card/div/div[2]/div/mat-form-field[2]/div/div[1]/div/input"
            )
            input_field.type(contact_number)
            page.wait_for_timeout(1000)

            print(f"✅ Successfully entered contact_number: {contact_number}")

            # Click search
            page.locator("button:has(mat-icon:text('search'))").click()

        except Exception as e:
            print(f"❌ Error interacting with the page: {e}")
    else:
        print("❗ 'contact_number[mandatory]' column not found or value is empty in CSV.")



