from xhtml2pdf import pisa

#get the directory of the current file 
import os
current_dir = os.path.dirname(os.path.abspath(__file__))


def html_to_pdf(html_content: str, output_filename: str):
    try:
        output_filename = os.path.join(current_dir, output_filename)
        print("Output filename: ", output_filename)

        with open(output_filename, "wb") as pdf_file:
            pisa.CreatePDF(html_content, dest=pdf_file)

        return "Success generating PDF: " + output_filename
    
    except Exception as e:
        return "Error generating PDF: " + str(e)



#define a main function
if __name__ == "__main__":
    # Example usage
    html_content = """
    <html>
    <head>
        <title>Test PDF</title>
    </head>
    <body>
        <h1>Hello, PDF!</h1>
        <p>This is a test PDF generated from HTML.</p>
    </body>
    </html>
    """
    result = html_to_pdf(html_content, "report_out.pdf")
    print(result)
    