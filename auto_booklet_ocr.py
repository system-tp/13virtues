print("RUNNING:", __file__)
import fitz  # PyMuPDF

def split_and_reorder_from_center():
    input_pdf = "booklet_raw.pdf"
    output_pdf = "booklet_ordered_perfect.pdf"
    
    doc = fitz.open(input_pdf)
    num_viewing_pages = len(doc)
    total_a5_pages = num_viewing_pages * 2
    
    # ページスロット(0〜59)を用意
    ordered_pages_data = [None] * total_a5_pages
    
    print(f"🚀 内側スタート丁合モード（全 {total_a5_pages} ページ）...")

    # 真ん中のページ（例：60ページなら30と31）を特定
    center_l = (total_a5_pages // 2)
    center_r = (total_a5_pages // 2) + 1

    for i in range(num_viewing_pages):
        # 1枚目が真ん中、2枚目がその外側...と広がっていくロジック
        # i=0: [30P, 31P]
        # i=1: [32P, 29P]
        # i=2: [28P, 33P]
        
        p_inner_left = (total_a5_pages // 2) - i
        p_inner_right = (total_a5_pages // 2) + 1 + i
        
        if i % 2 == 0:
            # 偶数枚目（1, 3, 5枚目...）
            idx_l = p_inner_left - 1
            idx_r = p_inner_right - 1
        else:
            # 奇数枚目（2, 4, 6枚目...）
            idx_l = p_inner_right - 1
            idx_r = p_inner_left - 1
            
        page = doc[i]
        mid_x = page.rect.width / 2
        
        ordered_pages_data[idx_l] = {"view_idx": i, "rect": fitz.Rect(0, 0, mid_x, page.rect.height)}
        ordered_pages_data[idx_r] = {"view_idx": i, "rect": fitz.Rect(mid_x, 0, page.rect.width, page.rect.height)}

    # 2. 書き出し
    out_doc = fitz.open()
    for p_idx in range(total_a5_pages):
        data = ordered_pages_data[p_idx]
        if data is None:
            continue
            
        view_page = doc[data["view_idx"]]
        new_p = out_doc.new_page(width=view_page.rect.width / 2, 
                                 height=view_page.rect.height)
        new_p.show_pdf_page(new_p.rect, doc, data["view_idx"], clip=data["rect"])

    out_doc.save(output_pdf, garbage=3)
    out_doc.close()
    doc.close()
    
    print(f"✅ 修正完了！: {output_pdf}")

if __name__ == "__main__":
    split_and_reorder_from_center()