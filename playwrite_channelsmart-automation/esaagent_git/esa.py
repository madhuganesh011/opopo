import pytest
import json
import pandas as pd
from functions import login_to_channelsmart, fill_contact_number_from_csv
from playwright.sync_api import sync_playwright

@pytest.mark.parametrize("headless_mode", [True])
def test_full_customer_and_user_flow(headless_mode):
    with open("playwrite_channelsmart-automation/esaagent_git/data_report.json") as file:
        reports = json.load(file)

    with open("playwrite_channelsmart-automation/esaagent_git/data_credit.json") as file:
        customer = json.load(file)

    with open("playwrite_channelsmart-automation/esaagent_git/data_pickupuser.json") as file:
        user = json.load(file)

    with sync_playwright() as m:
        browser = m.chromium.launch(headless=headless_mode)
        page = browser.new_page()

        login_to_channelsmart(page, "loadtest@gmail.com", "password")
        page.wait_for_timeout(2000)

        # ---------------- Report Generation ----------------
        page.get_by_role("link", name="Reports").click()
        page.wait_for_selector("//input[@formcontrolname='fromday']").type(reports["start_date"])
        page.wait_for_selector("//input[@formcontrolname='today']").type(reports["end_date"])
        page.wait_for_selector("//input[@formcontrolname='email_id']").type(reports["email_id"])
        page.get_by_role("button", name='Generate Report').click()
        page.wait_for_timeout(5000)
        success_message1 = page.locator("mat-dialog-content >> text=Generated Report Shared To Your Email.")
        page.wait_for_timeout(1000)

        # Wait up to 5 seconds for the dialog to appear
        if success_message1.is_visible(timeout=5000):
            print("✅ Report generated successfully by ESA_agent")
        else:
            print("❌ Report generation dialog not found.")
        page.click("#generated-report-confirm")

        # ---------------- Customer Creation ----------------
        page.get_by_role("link", name="Customers").click()
        page.click("//button[contains(., 'Add Customer')]")
        for key in [
            "pancard_number", "aadhaar_number", "customer_code", "username",
            "addressline1", "addressline2", "addressline3", "company_name",
            "city", "pincode", "state", "phone_number", "email"
        ]:
            page.wait_for_selector(f"//input[@formcontrolname='{key}']").type(customer[key])
        page.click('mat-select[formcontrolname="services"]')
        page.locator("mat-option span.mat-option-text", has_text=customer["services"]).click()
        page.locator("h2.mat-dialog-title", has_text="Add Customer").click(force=True)
        page.locator('mat-checkbox:has-text("Same As Billing Address")').click()
        page.get_by_role("button", name="Add").click()
        page.wait_for_timeout(5000)
        success_message = page.locator("mat-dialog-content >> text=Added Customer Successfully.")

        # Wait up to 5 seconds for the dialog to appear
        if success_message.is_visible(timeout=5000):
            print("✅ credit customer created successfully by ESA_agent")
        else:
            print("❌ user creation dialog not found.")
        page.wait_for_timeout(3000)
        page.wait_for_selector("#added-customer-confirm").click()
        page.wait_for_timeout(3000)

        # ---------------- Bulk Customer Upload ----------------
        page.click("//button[contains(., 'Bulk Upload Customer')]")
        file_input = page.locator("#file")
        file_input.wait_for(state="visible", timeout=60000)
        file_input.wait_for(state="attached", timeout=60000)

        # Upload the file
        file_input.set_input_files("playwrite_channelsmart-automation/esaagent_git/customer_template.csv")
        print("✅ File upload triggered.")
        page.wait_for_timeout(3000)

        #page.set_input_files("#file", './customer_template.csv')
        page.locator("button.btn.btn-primary", has_text="Upload").click()
        page.wait_for_timeout(2000)

        # Wait for either success or any mat-dialog to appear
        dialog = page.locator("mat-dialog-content")
        try:
            dialog.wait_for(state="visible", timeout=10000)
            if "Customers Created Successfully." in dialog.inner_text():
                print("✅ bulk credit customer created successfully by ESA_agent")
            else:
                print("⚠️ Dialog appeared but did not contain expected text.")
        except:
            print("❌ No confirmation dialog appeared after bulk upload.")

        # Try to confirm if confirm button appears
        try:
            confirm = page.wait_for_selector("#bulk-upload-customer-confirm", timeout=3000)
            confirm.click()
            page.wait_for_timeout(3000)
        except:
            print("⚠️ Confirm button (#bulk-upload-customer-confirm) not found.")
        # page.locator("button.btn.btn-primary", has_text="Upload").click()
        # page.wait_for_timeout(5000)
        # success_message3 = page.locator("mat-dialog-content >> text=Customers Created Successfully.")
        # if success_message3.is_visible(timeout=5000):
        #     print("✅ bulk credit customer created successfully by ESA_agent")
        # else:
        #     print("❌ bulk-customer creation dialog not found.")
        # page.wait_for_timeout(5000)
        # page.wait_for_selector("#bulk-upload-customer-confirm").click()
        # page.wait_for_timeout(3000)


        csv_path = "playwrite_channelsmart-automation/esaagent_git/customer_template.csv"  # Uploaded file
        df = pd.read_csv(csv_path)
        email_id = df.iloc[0]["BILLING_EMAIL[MANDATORY]"] if "BILLING_EMAIL[MANDATORY]" in df.columns else None
        if email_id:
            page.wait_for_selector("#mat-select-0").click()
            page.wait_for_selector("#mat-option-2").click()
            input_field = page.wait_for_selector(
                "xpath=/html/body/app-root/app-admin/div/div/app-esa-customers/div[2]/div/app-card/div/div[2]/div/mat-form-field[2]/div/div[1]/div/input")
            input_field.type(email_id)
            print(f"Successfully entered email: {email_id}")
        else:
            print("Email column not found in CSV.")
        page.wait_for_timeout(1000)
        page.locator("button:has(mat-icon:text('search'))").click()
        page.wait_for_timeout(3000)

        # ---------------- Customer Edit ----------------
        page.wait_for_selector(
            "xpath=/html/body/app-root/app-admin/div/div/app-esa-customers/div[2]/div/app-card/div/div[2]/div/table/tbody/tr/td[6]/mat-icon").click()
        data_field1 = page.wait_for_selector("//input[@formcontrolname='pincode']")
        data_field1.fill("")
        data_field1.fill("560098")
        page.get_by_role("button", name="Update").click()
        page.wait_for_timeout(1000)
        print("user update sucessfull")
        page.wait_for_timeout(1000)
        page.wait_for_selector("#cash-customer-service-error").click()
        page.wait_for_selector("button:has-text('Cancel')", timeout=5000)
        page.click("button:has-text('Cancel')")



        # ---------------- Customer Deactivation ----------------
        page.locator("mat-slide-toggle label").first.click()
        page.wait_for_timeout(1000)
        success_message2 = page.locator("mat-dialog-content >>text=Deactivated Successfully")
        page.wait_for_timeout(1000)

        if success_message2.is_visible(timeout=5000):
            print("✅ credit customer de-activated successfully by ESA_agent")
        else:
            print("❌ customer de-activation dialog not found.")
        page.wait_for_selector("#toggle-confirm").click()
        page.wait_for_timeout(1000)
        # if page.locator("mat-dialog-content >>text=Deactivated Successfully").is_visible(timeout=5000):
        #     print("✅ customer de-activated successfully.")
        # page.click("#toggle-confirm")

        # ---------------- Customer Activation ----------------
        page.click("button:has(mat-icon:text('search'))")
        toggle = page.locator("mat-slide-toggle input[type='checkbox']").first
        if toggle.get_attribute("aria-checked") == "false":
            page.wait_for_timeout(30000)
            page.locator("mat-slide-toggle label").first.click()

        if page.locator("mat-dialog-content >>text=Activated Successfully").is_visible(timeout=5000):
            print("✅ credit customer activated successfully by ESA_agent")
        page.click("#toggle-confirm")

        # ---------------- Pickup User Creation ----------------
        page.get_by_role("link", name="Users").click()
        page.click("//button[contains(., 'Add User')]")
        for key in ["first_name", "last_name", "email_id", "contact_number", "password"]:
            page.fill(f"//input[@formcontrolname='{key}']", user[key])
        page.click('mat-select[formcontrolname="services"]')
        page.locator("mat-option span.mat-option-text", has_text=user["services"]).click()
        page.locator("h2.mat-dialog-title", has_text="Add Pickup User").click(force=True)
        page.get_by_role("button", name="Add").click()
        page.wait_for_timeout(3000)
        success_message = page.locator("mat-dialog-content >> text=Added User Successfully.")
        # Wait up to 5 seconds for the dialog to appear
        if success_message.is_visible(timeout=5000):
            print("✅ pickup-user created successfully by ESA_agent")
        else:
            print("❌ pickup-user creation dialog not found.")
        page.wait_for_timeout(3000)
        page.wait_for_selector("#added-user-confirm").click()
        page.wait_for_timeout(3000)

        # ---------------- Pickup User Bulk Upload ----------------
        page.click("//button[contains(., 'Bulk Upload User')]")
        file_input = page.locator("#file")
        file_input.wait_for(state="visible", timeout=60000)
        file_input.wait_for(state="attached", timeout=60000)

        # Upload the file
        file_input.set_input_files("playwrite_channelsmart-automation/esaagent_git/pickup_template.csv")
        print("✅ File upload triggered.")
        page.wait_for_timeout(3000)

        #page.set_input_files("#file", './pickup_template.csv')
        page.locator("button.btn.btn-primary", has_text="Upload").click()
        page.wait_for_timeout(3000)
        success_message1 = page.locator("mat-dialog-content >> text=Uploaded Successfully.")
        if success_message1.is_visible(timeout=5000):
            print("✅ bulk-pickup_user created successfully by ESA_agent")
        else:
            print("❌ bulk-pickup_user creation dialog not found.")
        page.wait_for_timeout(3000)
        page.wait_for_selector("#bulk-upload-user-confirm").click()
        page.wait_for_timeout(3000)


        # ---------------- Pickup User Edit ----------------
        fill_contact_number_from_csv(page)
        page.wait_for_timeout(3000)
        ###function###
        ###update###
        page.wait_for_selector("xpath=/html/body/app-root/app-admin/div/div/app-esa-user/div[2]/div/app-card/div/div[2]/div/table/tbody/tr/td[5]/mat-icon").click(force=True)

        #page.wait_for_selector("xpath=/html/body/app-root/app-admin/div/div/app-esa-user/div[2]/div/app-card/div/div[2]/div/table/tbody/tr/td[5]/mat-icon").click()
        data_field1 = page.wait_for_selector("//input[@formcontrolname='last_name']")
        data_field1.fill("")
        data_field1.fill("raki09")
        page.get_by_role("button", name="Update").click()
        page.wait_for_timeout(1000)
        print("pickup_user update sucessfully by ESA_agent")
        page.wait_for_timeout(1000)
        # ---------------- Pickup User Deactivation ----------------
        fill_contact_number_from_csv(page)
        page.locator("mat-slide-toggle label").first.click()
        page.wait_for_timeout(3000)
        if page.locator("mat-dialog-content >>text=Deactivated Successfully").is_visible(timeout=5000):
            print("✅ pickup_user de-activated successfully by ESA_agent")
        page.click("#toggle-confirm")
        page.wait_for_timeout(1000)

        # ---------------- Pickup User Activation ----------------
        page.locator("button:has(mat-icon:text('search'))").click()
        page.wait_for_timeout(1000)
        toggle_input = page.locator("mat-slide-toggle input[type='checkbox']").first

        # Wait for it to be attached
        toggle_input.wait_for(state="attached")

        # Check if the toggle is OFF (disabled)
        if toggle_input.get_attribute("aria-checked") == "false":
            toggle_label = page.locator("mat-slide-toggle label").first
            toggle_label.wait_for(state="visible")
            toggle_label.click()
            print("✅ Toggle was OFF, now enabled.")
        else:
            print("ℹ️ Toggle is already ON. No action needed.")

        success_message3 = page.locator("mat-dialog-content >>text=Activated Successfully")
        page.wait_for_timeout(1000)

        if success_message3.is_visible(timeout=5000):
            print("✅ pick_up user activated successfully by ESA_agent")
        else:
            print("❌ user activation dialog not found.")
        page.wait_for_selector("#toggle-confirm").click()
        page.wait_for_timeout(1000)

        browser.close()
