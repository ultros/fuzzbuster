import json
from typing import NoReturn
from fpdf import FPDF


class Report:

    def __init__(self, report_file_name: str, target_address: str, url_results_list: list):
        self.report_file_name = report_file_name
        self.target_address = target_address
        self.url_results_list = url_results_list


class PdfReport(Report):

    def generate_pdf_report(self) -> NoReturn:
        pdf = FPDF(orientation='P', unit='pt', format='A4')
        pdf.add_page()

        pdf.image("assets/images/cyber-tutorials-org-logo-small.png", w=76, h=96)
        pdf.set_font(family='Times', size=24, style='B')
        pdf.cell(w=0, h=80, txt=self.target_address, border=0, align="L", ln=1)

        pdf.set_font(family="Times", size=10)
        for url in self.url_results_list:
            pdf.cell(w=100, h=20, txt=f"{url}", border=0, ln=1)

        pdf.output(self.report_file_name + ".pdf")


class HtmlReport(Report):

    def generate_html_report(self) -> NoReturn:
        html_report = open(f"{self.report_file_name}.html", 'w+')
        html_report.write(f"<html>")
        html_report.write(f"<head>")
        html_report.write(f"<title>{self.target_address}</title>")
        html_report.write(f"<style>h1{{text-align: center;}}</style>")
        html_report.write(f"</head><body>")
        html_report.write(f"<h1>{self.target_address}</h1>")
        for url in self.url_results_list:
            html_report.write(f"<p>{url}\n</p>")
            html_report.write(f"----------------------------------------\n")
        html_report.write(f"</body></html>")


class JsonReport(Report):

    def generate_json(self) -> NoReturn:
        json_string = json.dumps(self.url_results_list)
        with open(f"{self.report_file_name}.json", 'w+') as file_obj:
            file_obj.write(json_string)
            file_obj.close()
