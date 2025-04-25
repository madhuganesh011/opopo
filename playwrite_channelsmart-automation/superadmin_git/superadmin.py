import pytest
import json
from datetime import datetime
from functions import login_to_channelsmart, search_user
from playwright.sync_api import sync_playwright
import os

@pytest.mark.parametrize("headless_mode", [True])  # Change to False for debugging locally
def test_full_flow(headless_mode):
    with open("playwrite_channelsmart-automation/superadmin_git/data_offers.json") as file:
    #with open("data_offers.json") as f:
        offer = json.load(file)
    with open("playwrite_channelsmart-automation/superadmin_git/data_users.json") as file:
    #with open("data_users.json") as f:
        user = json.load(file)
    with open("playwrite_channelsmart-automation/superadmin_git/data_report.json") as file:
    #with open("data_report.json") as f:
        reports = json.load(file)
    video_dir = "videos"
    os.makedirs(video_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless_mode)
        context = browser.new_context(record_video_dir=video_dir)
        page = context.new_page()

        #page = browser.new_page()

        # Login
        login_to_channelsmart(page, "superadminuat@gmail.com", "password")
        page.wait_for_timeout(4000)

        # ---------------- Offers ----------------
        page.get_by_role("link", name="Offers").click()
        page.wait_for_selector("//span[text()='Offers']").click()
        page.wait_for_selector("//button[contains(., 'Add Offer')]").click()

        page.fill("//input[@formcontrolname='offer_code']", offer["offer_code"])
        page.fill("//input[@formcontrolname='offer_description']", offer["offer_description"])
        page.fill("//input[@formcontrolname='bd_packtype']", offer["package_value"])
        start_date = datetime.strptime(offer["start_date"], "%d-%m-%Y").strftime("%Y-%m-%d")
        end_date = datetime.strptime(offer["end_date"], "%d-%m-%Y").strftime("%Y-%m-%d")

        page.fill("//input[@formcontrolname='start_date']", start_date)
        page.fill("//input[@formcontrolname='end_date']", end_date)
        #page.fill("//input[@formcontrolname='start_date']", offer["start_date"])
        #page.fill("//input[@formcontrolname='end_date']", offer["end_date"])
        page.fill("//input[@formcontrolname='created_by']", offer["created_by"])

        page.click('mat-select[formcontrolname="offer_regions"]')
        page.locator("mat-option span.mat-option-text", has_text=offer["offer_regions"]).click()
        page.locator("h2.mat-dialog-title", has_text="Add Offer").click(force=True)
        page.wait_for_timeout(3000)

        page.click('mat-select[formcontrolname="services"]')
        page.locator("span.mat-option-text", has_text=offer["services"]).click()
        page.locator("h2.mat-dialog-title", has_text="Add Offer").click(force=True)
        page.wait_for_timeout(3000)
        page.get_by_role("button", name="Add").click()
        page.wait_for_timeout(3000)
        success_message = page.locator("mat-dialog-content >> text=Offer Added Successfully.")
        if success_message.is_visible(timeout=5000):
            print("✅ Offer created successfuly by super_admin")
        else:
            print("❌ Offer creation dialog not found in the console")

        page.click("#offer-added-confirm")

        # Edit Offer
        page.click("xpath=/html/body/app-root/app-admin/div/div/app-offers/div[2]/div/div/div[2]/table/tbody/tr[1]/td[7]")
        field = page.locator("//input[@formcontrolname='offer_code']")
        field.fill("alumelumam")
        page.get_by_role("button", name="Update").click()
        page.wait_for_timeout(3000)
        success_message1 = page.locator("mat-dialog-content >>text=Offer Updated Successfully.")
        page.wait_for_timeout(1000)

        if success_message1.is_visible(timeout=5000):
            print("✅ Offer updated successfully by super_admin")
        else:
            print("❌ Offer updation dialog not found .")
        page.wait_for_selector("#offer-updated-confirm").click()
        page.wait_for_timeout(3000)

        # Deactivate Offer
        toggle = page.locator("mat-slide-toggle#mat-slide-toggle-1")
        input_el = toggle.locator("input")
        if input_el.is_checked():
            toggle.locator(".mat-slide-toggle-thumb-container").click()
            page.wait_for_timeout(3000)
        success_message2 = page.locator("mat-dialog-content >>text=Offer Deactivated")
        page.wait_for_timeout(1000)

        if success_message2.is_visible(timeout=5000):
            print("✅ Offer de-activated successfully by super_admin")
        else:
            print("❌ Offer de-activation dialog not found.")
        page.wait_for_selector("#toggle-confirm").click()

        # Deactivate Offer
        page.wait_for_timeout(3000)
        input_el = page.locator("mat-slide-toggle input[type='checkbox']").first
        is_checked = input_el.is_checked()

        if not is_checked:
            page.locator("mat-slide-toggle").first.click()
        success_message3 = page.locator("mat-dialog-content >>text=Offer Activated")
        page.wait_for_timeout(1000)

        if success_message3.is_visible(timeout=5000):
            print("✅ Offer activated successfully by super_admin")
        else:
            print("❌ Offer activation dialog not found.")
        page.wait_for_selector("#toggle-confirm").click()
        page.wait_for_timeout(10000)

        # ---------------- Users ----------------
        page.get_by_role("link", name="Users").click()
        page.click("//button[contains(., 'Add User')]")

        page.fill("//input[@formcontrolname='first_name']", user["first_name"])
        page.fill("//input[@formcontrolname='last_name']", user["last_name"])
        page.fill("//input[@formcontrolname='password']", user["password"])
        page.fill("//input[@formcontrolname='contact_number']", user["contact_number"])
        page.fill("//input[@formcontrolname='email_id']", user["email_id"])
        page.wait_for_selector('mat-select[formcontrolname="region"]').click()
        page.locator("mat-option span.mat-option-text", has_text=user["region"]).click()
        page.get_by_role("button", name="Add").click()
        page.wait_for_timeout(5000)

        success_message4 = page.locator("mat-dialog-content >> text=Added User Successfully.")
        page.wait_for_timeout(3000)

        if success_message4.is_visible(timeout=5000):
            print("✅ sub_admin created successfully by super_admin")
        else:
            print("❌ user creation dialog not found.")
        page.wait_for_timeout(3000)
        page.wait_for_selector("#added-user-confirm", timeout=60000).click()
        page.wait_for_timeout(3000)

        # Edit User
        search_user(page, user)
        page.click("xpath=/html/body/app-root/app-admin/div/div/app-esa-user/div[2]/div/app-card/div/div[2]/div/table/tbody/tr/td[5]")
        last_name_field = page.locator("//input[@formcontrolname='last_name']")
        last_name_field.fill("alumelumam")
        page.get_by_role("button", name="Update").click()
        page.wait_for_timeout(3000)

        # Deactivate User
        search_user(page, user)
        toggle_input = page.locator("mat-slide-toggle input[type='checkbox']").nth(0)
        if toggle_input.get_attribute("aria-checked") == "true":
            page.locator("mat-slide-toggle label").nth(0).click()
            page.wait_for_timeout(3000)
        success_message4 = page.locator("mat-dialog-content >> text=Deactivated Successfully")
        page.wait_for_timeout(1000)

        # Wait up to 5 seconds for the dialog to appear
        if success_message4.is_visible(timeout=5000):
            print("✅ sub_admin de-activated successfully by super_admin")
        else:
            print("❌ user de-activated dialog not found.")
        page.wait_for_selector("#toggle-confirm").click()
        page.wait_for_selector("#toggle-confirm")


        # Activate User
        page.wait_for_timeout(3000)
        page.wait_for_selector("button:has(mat-icon:text('search'))").click()
        toggle = page.locator("mat-slide-toggle").nth(0)

        # Wait for toggle to be visible
        toggle.wait_for(state="visible")

        # Click to toggle
        toggle.click()
        print("Toggle clicked!")
        success_message5 = page.locator("mat-dialog-content >> text=Activated Successfully")
        page.wait_for_timeout(1000)

        # Wait up to 5 seconds for the dialog to appear
        if success_message5.is_visible(timeout=5000):
            print("✅ sub_admin activated successfully by super_admin")
        else:
            print("❌ user activated dialog not found.")
        page.wait_for_selector("#toggle-confirm").click()

        # ---------------- Reports ----------------
        # ---------------- Reports ----------------
        page.wait_for_timeout(3000)
        page.get_by_role("link", name="Reports").click()

        # Wait for inputs to show
        page.wait_for_selector("//input[@formcontrolname='fromday']")

        # Safely parse dates
        def parse_date_safe(date_str):
            for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%m-%d-%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
            raise ValueError(f"Unsupported date format: {date_str}")

        report_start_date = parse_date_safe(reports["start_date"])
        report_end_date = parse_date_safe(reports["end_date"])

        page.fill("//input[@formcontrolname='fromday']", report_start_date)
        page.fill("//input[@formcontrolname='today']", report_end_date)
        page.fill("//input[@formcontrolname='email_id']", reports["email_id"])

        page.get_by_role("button", name='Generate Report').click()
        page.wait_for_timeout(5000)

        success_message6 = page.locator("mat-dialog-content >> text=Generated Report Shared To Your Email.")
        page.wait_for_timeout(1000)

        # Wait up to 5 seconds for the dialog to appear
        if success_message6.is_visible(timeout=5000):
            print("✅ Report generated successfully.")
        else:
            print("❌ Report generation dialog not found.")
        page.click("#generated-report-confirm")
        context.close()
        browser.close()
