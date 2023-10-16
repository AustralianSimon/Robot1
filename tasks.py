from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=200,)
    open_robot_order_website()
    open_order_page()
    orders = get_orders()
    make_orders(orders)
    archive_receipts()

def open_robot_order_website():
        browser.goto('https://robotsparebinindustries.com/')

def open_order_page():
    page = browser.page()
    page.get_by_role('link', name='Order your robot!').click()
    close_annoying_modal()

def close_annoying_modal():
    page = browser.page()
    page.get_by_role('button', name='OK').click()

def get_orders():
    fileLink = 'https://robotsparebinindustries.com/orders.csv'
    http = HTTP()
    http.download(url=fileLink, overwrite=True)
    data = Tables()
    orders = data.read_table_from_csv(
        'orders.csv', header=True
    )
    return orders

def fill_in_form(row):
    page = browser.page()
    page.select_option('#head', str(row['Head']))

    page.click('//input[@value='+ row['Body']+']')

    page.get_by_placeholder('Enter the part number for the legs').fill(row['Legs'])

#    page.get_by_placeholder('Shipping address').fill(row['Address'])
    page.fill('#address', row['Address'])
    page.click('#preview')

    while not page.query_selector('#order-another'):
        page.click('#order')
    

def make_orders(orders):
    """Submits the orders from list"""
    page = browser.page()
    for row in orders:
        fill_in_form(row)
        receipt(row['Order number'])
        
        page.click('#order-another')
        close_annoying_modal()

def receipt(order_number):
    screenshot_robot(order_number)
    embed_screenshot_to_receipt(order_number, f"output/{order_number}.pdf")

def screenshot_robot(order_number):
    page = browser.page()
    page.screenshot(path=f'/output/{order_number}.png')

def embed_screenshot_to_receipt(order_number, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(files=[f'/output/{order_number}.png'], 
    target_document=f"output/{order_number}.pdf", append=False)

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip('output/', 'output/receipts.zip', include='*.pdf')