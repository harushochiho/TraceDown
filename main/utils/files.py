import io
import json
from urllib.request import urlopen

import pandas as pd
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from openpyxl.chart import PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as OpenpyxlImage


class FilesProcessing:

    @staticmethod
    def read_files(file_paths: list[str]) -> list[str]:
        if not file_paths:
            raise ValueError("File paths list cannot be empty.")

        contents: list[str] = []
        for file_path in file_paths:
            with open(file_path, "r", encoding="utf-8") as file:
                print("Reading file:", file_path)
                contents.append(file.read())

        if not contents:
            raise ValueError("No content has been read yet.")

        return contents

    @staticmethod
    def write_files_with_time(path: str, content: str, time: str, line_end: str = "") -> None:
        if not path:
            raise ValueError("File path cannot be empty.")

        with open(path, "a", encoding="utf-8") as opening_file:
            print(f"{time} Logging {path}")
            opening_file.write(f"{time}-{content}{line_end}")

    @staticmethod
    def write_json_file(path: str, content: dict) -> None:
        if not path:
            raise ValueError("File path cannot be empty.")

        from pathlib import Path

        p = Path(path)
        # Ensure parent directory exists
        # p.parent.mkdir(parents=True, exist_ok=True)

        # Check if file exists and has content
        if p.exists() and p.stat().st_size > 0:
            try:
                # Read existing JSON
                with p.open('r', encoding='utf-8') as f:
                    current_json = json.load(f)

                # Ensure it's a list
                if not isinstance(current_json, list):
                    raise ValueError("Existing JSON is not an array. Expected a list of objects.")

                # Append new content to existing array
                current_json.append(content)
                print(f"Appended object to {path}. Total objects: {len(current_json)}")

            except json.JSONDecodeError:
                # File exists but is corrupted/invalid JSON; start fresh with new content
                print(f"Warning: File {path} contains invalid JSON. Starting fresh.")
                current_json = [content]
        else:
            # File doesn't exist or is empty; create new array with the content
            current_json = [content]
            print(f"Created new JSON array at {path}")

        # Write the updated array back to file (overwrite mode for atomicity)
        with p.open('w', encoding='utf-8') as f:
            json.dump(current_json, f, ensure_ascii=False, indent=4)
            print(f"Successfully saved {len(current_json)} object(s) to {path}")

    @staticmethod
    def export_to_excel(data: list[dict], file_path: str, sheet_name: str = "Sheet1", receipt_path: str = None) -> None:
        df = pd.DataFrame(data=data)
        pos_col_total = df.columns.get_loc("Total") + 1
        pos_col_tax = df.columns.get_loc("Tax") + 1
        pos_col_category = df.columns.get_loc("Category") + 1
        excel_buffer = io.BytesIO()
        
        # Use ExcelWriter with openpyxl engine
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            # Export DataFrame
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Access the openpyxl workbook and worksheet objects directly
            wb = writer.book
            ws = wb[sheet_name]
            data_end_row = ws.max_row
            data_end_col = len(df.columns)
            
            # Add formulas for subtotal
            row_subtotal = ws.max_row + 1
            cell_subtotal = f"A{row_subtotal}"  # Next empty row for subtotal
            ws[cell_subtotal] = "Sub Total"
            ws.cell(row=row_subtotal, column=2,
                    value=f"=ROUND(SUM({get_column_letter(pos_col_total)}2:{get_column_letter(pos_col_total)}{data_end_row}), 2)")
            ws.merge_cells(start_row=ws.max_row, start_column=2, end_row=ws.max_row, end_column=data_end_col)

            # Add formulas for tax
            row_tax = ws.max_row + 1
            cell_tax = f"A{row_tax}"  # Next empty row for tax
            ws[cell_tax] = "HST"
            print(f"=ROUND(SUMIF({get_column_letter(pos_col_tax)}2:{get_column_letter(pos_col_tax)}{data_end_row}, \"Y\",{get_column_letter(pos_col_total)}2:{get_column_letter(pos_col_total)}{data_end_row}) * 0.13, 2)")
            ws.cell(row=row_tax, column=2,
                    value=f"=ROUND(SUMIF({get_column_letter(pos_col_tax)}2:{get_column_letter(pos_col_tax)}{data_end_row}, \"Y\",{get_column_letter(pos_col_total)}2:{get_column_letter(pos_col_total)}{data_end_row}) * 0.13, 2)")
            ws.merge_cells(start_row=ws.max_row, start_column=2, end_row=ws.max_row, end_column=data_end_col)

            # Add formulas for total after tax
            row_after_tax = ws.max_row + 1
            cell_total_after_tax = f"A{ws.max_row + 1}"  # Next empty row for total after tax
            ws[cell_total_after_tax] = "Total after Tax"
            ws.cell(row=row_after_tax, column=2,
                    value=f"=ROUND(SUM(B{row_subtotal}:B{row_tax}), 2)")
            ws.merge_cells(start_row=ws.max_row, start_column=2, end_row=ws.max_row, end_column=data_end_col)

            # Add formulas for totals based on categories
            row_category_totals = ws.max_row + 2
            cell_category = f"A{row_category_totals}"
            cell_totals = f"B{row_category_totals}"

            ws[cell_category] = "Grouped Category"
            ws[cell_totals] = "Total"

            # Group by category and calculate totals
            category_list = list(df["Category"].unique())

            next_row = row_category_totals
            for category in category_list:
                next_row += 1
                cell_category = f"A{next_row}"
                cell_totals = f"B{next_row}"
    
                ws[cell_category] = category
                ws[cell_totals] = f"=SUMIF({get_column_letter(pos_col_category)}2:{get_column_letter(pos_col_category)}{data_end_row}, {cell_category}, {get_column_letter(pos_col_total)}2:{get_column_letter(pos_col_total)}{data_end_row})"

            # Insert a pie chart for category totals
            start_row_category = row_category_totals
            end_row_category = next_row
            pie_chart = PieChart()
            pie_chart.title = "Total"
            pie_chart.style = 11

            pie_chart.dataLabels = DataLabelList()
            pie_chart.dataLabels.showPercent = True
            pie_chart.dataLabels.showCatName = True
            pie_chart.dataLabels.showLeaderLines = True
            pie_chart.dataLabels.showLegendKey = False
            pie_chart.dataLabels.showVal = False
            pie_chart.dataLabels.showSerName = False
            
            pie_chart.dataLabels.separator = "\n"
            
            pie_chart.legend = None

            labels_ref = Reference(ws, min_col=1, min_row=start_row_category+1, max_row=end_row_category, max_col=1)
            data_ref = Reference(ws, min_col=2, min_row=start_row_category+1, max_row=end_row_category, max_col=2)

            pie_chart.add_data(data_ref, titles_from_data=True)
            pie_chart.set_categories(labels_ref)
            
            ws.add_chart(pie_chart, f"D{row_category_totals}")

            # Insert receipt image
            if not receipt_path:
                return
            
            with urlopen(f"http://127.0.0.1:8000/media/{receipt_path}") as response:
                img = OpenpyxlImage(io.BytesIO(response.read()))  # Ensure the image file is in the same directory or provide full path
               
                img.width = int(img.width * 0.25)
                img.height = int(img.height * 0.25)
                ws.add_image(img, f"{get_column_letter(ws.max_column+2)}1")

            center_alignment = Alignment(horizontal="center", vertical="center")
            
            for row in ws.iter_rows():
                for cell in row:
                    cell.alignment = center_alignment
            
        excel_buffer.seek(0)
        default_storage.save(file_path, ContentFile(excel_buffer.getvalue()))    