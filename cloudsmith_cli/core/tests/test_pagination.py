from ..pagination import PageInfo


class TestPageInfo:
    def test_str_with_valid_page_info(self):
        info = PageInfo.from_headers(
            {
                "X-Pagination-Count": "42",
                "X-Pagination-Page": "2",
                "X-Pagination-PageSize": "10",
                "X-Pagination-PageTotal": "5",
            }
        )
        assert str(info) == "Valid: True, Count: 42, Page: 2, Size: 10, Total: 5"

    def test_str_with_invalid_page_info(self):
        assert (
            str(PageInfo())
            == "Valid: False, Count: None, Page: None, Size: None, Total: None"
        )
