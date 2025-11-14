import arxiv
import pandas as pd

def fetch_ai_papers():
    """
    Lấy các bài báo mới nhất về AI (cs.AI) và Computer Science (cs.LG - Machine Learning) 
    từ arXiv.
    """
    try:
        # Tìm kiếm 10 bài báo mới nhất thuộc danh mục cs.AI và cs.LG
        # Sắp xếp theo ngày gửi (SubmittedDate)
        search = arxiv.Search(
            query = "cat:cs.AI OR cat:cs.LG",
            max_results = 10,
            sort_by = arxiv.SortCriterion.SubmittedDate
        )
        
        papers_data = []
        
        print("Đang lấy các bài báo AI/CS mới nhất từ arXiv...")
        
        for result in search.results():
            print(f"Tiêu đề: {result.title}")
            papers_data.append({
                'Tiêu đề': result.title,
                'Tác giả': ", ".join([author.name for author in result.authors]),
                'Ngày xuất bản': result.published.strftime('%Y-%m-%d'),
                'Link': result.pdf_url,
                'Tóm tắt': result.summary.replace('\n', ' ')
            })
            
        # Lưu vào DataFrame
        df = pd.DataFrame(papers_data)
        
        # Lưu ra file CSV
        df.to_csv('data/ai_papers.csv', index=False)
        print("\nĐã lấy và lưu tin AI/CS thành công!")
        return df

    except Exception as e:
        print(f"Đã xảy ra lỗi khi lấy dữ liệu từ arXiv: {e}")

if __name__ == "__main__":
    fetch_ai_papers()