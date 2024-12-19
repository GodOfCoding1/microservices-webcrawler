from playwright.sync_api import sync_playwright
 
 
def extractCompaniesWithQuery(query_string: str):
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the page
        page.goto("https://search.sunbiz.org/Inquiry/CorporationSearch/ByName")  # Replace with the actual URL

        # Locate the input box by ID and input a sample string
        search_box = page.locator('input#SearchTerm')
        search_box.fill(query_string)
        # Press Enter
        search_box.press("Enter")

        # Optional: wait for navigation or results to load
        page.wait_for_load_state("networkidle")
        # Extract all tables with rows and headers

        tables = page.locator("table")
        extracted_table_data = None
        document_id_set = set()

        for table in tables.element_handles():
            table_data = {"headers": [], "rows": []}

            # Extract headers (th elements)
            headers = table.query_selector_all("th")
            table_data["headers"] = [header.inner_text() for header in headers]
            if ("###".join(['Corporate Name', 'Document Number', 'Status']) != "###".join(table_data["headers"])): #check if the table has the structure we expect (can be moved to a config file)
                continue
            # Extract rows (tr elements)
            rows = table.query_selector_all("tr")
            for row in rows[1:]:
                row_data = []
                row_links = []

                # Extract cell text and href
                cells = row.query_selector_all("td")
                for cell in cells:
                    # Get cell text
                    row_data.append(cell.inner_text())

                    # Check if the cell contains an anchor tag
                    anchor = cell.query_selector("a")
                    if anchor:
                        row_links.append(anchor.get_attribute("href"))

                table_data["rows"].append({
                    "text": row_data,
                    "links": row_links
                })

            extracted_table_data = table_data
            break #exit once we got the table we want

        if not extracted_table_data:
            return ([],set())
        id_to_link={}
        id_to_details={}
        for row in extracted_table_data['rows']:
            id = row['text'][1]
            id_to_details[id] = { "Corporate Name":row['text'][0], "Document Number":row['text'][1], "Status":row['text'][2] } # ideally these keys should be a Constant defined somewhere higher up like a config file
            if len(row['links'])>0:
                id_to_link[id]=row['links'][0]

        for id in id_to_link:
            page.goto("https://search.sunbiz.org"+id_to_link[id])
            try:
                container = page.locator("div.detailSection.filingInformation div")
                # Extract label-span pairs
                label_span_dict = {}
                labels = container.locator("label").element_handles()
                spans = container.locator("span").element_handles()

                # Match each label with its corresponding span
                for label, span in zip(labels, spans):
                    label_text = label.inner_text()
                    span_text = span.inner_text()
                    label_span_dict[label_text] = span_text
            except:
                # skip the row if main details are not found
                continue
            
            try:
                # Extract principal address
                principal_address_element = page.locator('div.detailSection:has(span:text("Principal Address")) div')
                principal_address = principal_address_element.inner_html().replace("<br>", "\n").strip()
                id_to_details[id]["Principal Address"]=principal_address.replace('\n','')
            except:
                id_to_details[id]["Principal Address"]=""

            try:
                # Extract mailing address
                mailing_address_element = page.locator('div.detailSection:has(span:text("Mailing Address")) div')
                mailing_address = mailing_address_element.inner_html().replace("<br>", "\n").strip()
                id_to_details[id]["Mailing Address"]= mailing_address.replace('\n','')
            except:
                id_to_details[id]["Mailing Address"]=""

            # Store in a dict
            for key in label_span_dict:
                id_to_details[id][key]=label_span_dict[key]
            document_id_set.add(id)

        # Close browser
        browser.close()
        return (list(id_to_details.values()),document_id_set)
 
 
if __name__ == '__main__':
    extractCompaniesWithQuery("Apple")

# handle if link is not found