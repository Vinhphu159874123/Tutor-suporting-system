import pdfplumber

pdf_path = r"c:\Users\Acer\Documents\HK251\Công nghệ phần mềm\Tutor support system\BTL_SE_251.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}\n")
    print("="*80)
    
    for i, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        print(f"\n--- PAGE {i} ---\n")
        print(text)
        print("\n" + "="*80)
