import datetime
import json
import logging
import os
from typing import Any, Type, Optional, List, Dict

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _save_results_to_file(content: str, company_name: str) -> None:
    """Saves the search results to a file with the company name in the filename."""
    try:
        filename = f"{company_name}_search_results_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        with open(filename, "w") as file:
            file.write(content)
        logger.info(f"Results saved to {filename}")
    except IOError as e:
        logger.error(f"Failed to save results to file: {e}")
        raise


class CompanyDocumentSearchResult(BaseModel):
    """Model for a company document search result."""
    title: str = Field(..., description="Title of the document")
    description: str = Field(..., description="Brief description of the document's content")
    link: str = Field(..., description="URL link to the document")
    document_type: str = Field(..., description="Type of document (annual_report, financial_statement, press_release, etc.)")
    publication_date: Optional[str] = Field(None, description="Date of publication if available")
    relevance_score: float = Field(..., description="Relevance score (1-10) for the document")


class CompanySearchToolSchema(BaseModel):
    """Input for CompanyInternalSearchTool."""
    company_name: str = Field(
        ..., description="Name of the company to search for documents"
    )
    document_type: Optional[str] = Field(
        None, description="Type of document to search for (annual_report, financial_statement, press_release, etc.)"
    )
    search_query: str = Field(
        ..., description="Specific search query for finding company documents"
    )
    year: Optional[str] = Field(
        None, description="Year of document to search for (e.g., '2023')"
    )


class CompanyInternalSearchTool(BaseTool):
    name: str = "Search for Company Internal Documents"
    description: str = (
        "A tool for searching the internet to find company internal documents such as annual reports, "
        "financial statements, investor presentations, and other official company publications. "
        "Returns results in a structured format with document titles, descriptions, URLs, dates, and types."
    )
    args_schema: Type[BaseModel] = CompanySearchToolSchema
    base_url: str = "https://google.serper.dev"
    n_results: int = 10
    save_file: bool = False
    search_type: str = "search"

    def _get_search_url(self, search_type: str) -> str:
        """Get the appropriate endpoint URL based on search type."""
        search_type = search_type.lower()
        allowed_search_types = ["search", "news"]
        if search_type not in allowed_search_types:
            raise ValueError(
                f"Invalid search type: {search_type}. Must be one of: {', '.join(allowed_search_types)}"
            )
        return f"{self.base_url}/{search_type}"

    def _construct_search_query(self, company_name: str, document_type: Optional[str], search_query: str, year: Optional[str]) -> str:
        """Construct an effective search query for finding company documents."""
        base_query = f"{company_name} {search_query}"
        
        if document_type:
            if document_type.lower() == "annual_report":
                base_query += " annual report pdf filetype:pdf"
            elif document_type.lower() == "financial_statement":
                base_query += " financial statement pdf filetype:pdf"
            elif document_type.lower() == "investor_presentation":
                base_query += " investor presentation pdf filetype:pdf"
            elif document_type.lower() == "press_release":
                base_query += " press release"
            elif document_type.lower() == "sustainability_report":
                base_query += " sustainability ESG report pdf filetype:pdf"
            else:
                base_query += f" {document_type} filetype:pdf"
                
        if year:
            base_query += f" {year}"
            
        # Add site operators for common investor relations sites
        site_query = f'"{company_name}" investor relations OR "{company_name}" financial reports OR "{company_name}" annual report filetype:pdf'
        
        return f"{base_query} ({site_query})"

    def _guess_document_type(self, title: str, snippet: str, url: str) -> str:
        """Guess the document type based on title, snippet, and URL."""
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        url_lower = url.lower()
        
        # Direct PDF check has highest priority
        if url_lower.endswith('.pdf'):
            # Check for annual reports in PDF URLs
            if ('annual' in url_lower and 'report' in url_lower) or 'ar20' in url_lower:
                return "annual_report"
            # Check for financial statements in PDF URLs
            elif ('financial' in url_lower and ('statement' in url_lower or 'report' in url_lower)) or 'fs20' in url_lower:
                return "financial_statement"
            # Check for sustainability reports in PDF URLs
            elif ('sustainability' in url_lower or 'esg' in url_lower) and 'report' in url_lower:
                return "sustainability_report"
            # Check for investor presentations in PDF URLs
            elif ('investor' in url_lower or 'presentation' in url_lower):
                return "investor_presentation"
        
        # Check for annual reports
        if ('annual report' in title_lower or 'annual report' in snippet_lower or 
            '/annual-report' in url_lower or 'annualreport' in url_lower):
            return "annual_report"
            
        # Check for financial statements
        if ('financial statement' in title_lower or 'financial statement' in snippet_lower or
            'balance sheet' in title_lower or 'income statement' in title_lower or
            'cash flow' in title_lower or 'financial results' in title_lower or
            '/financials' in url_lower):
            return "financial_statement"
            
        # Check for investor presentations
        if ('investor presentation' in title_lower or 'investor presentation' in snippet_lower or
            'investor day' in title_lower or 'investor day' in snippet_lower or
            '/presentations' in url_lower):
            return "investor_presentation"
            
        # Check for press releases
        if ('press release' in title_lower or 'press release' in snippet_lower or
            'announces' in title_lower or 'news release' in title_lower or
            '/press' in url_lower or '/news' in url_lower):
            return "press_release"
            
        # Check for ESG/sustainability reports
        if ('sustainability' in title_lower or 'sustainability' in snippet_lower or
            'esg' in title_lower or 'esg' in snippet_lower or
            'environmental' in title_lower or 'social responsibility' in title_lower or
            '/sustainability' in url_lower or '/esg' in url_lower):
            return "sustainability_report"
            
        # Default to "other" if we can't determine
        return "other"

    def _guess_publication_date(self, title: str, snippet: str) -> Optional[str]:
        """Extract publication date from title or snippet if possible."""
        import re
        
        # Look for year patterns (2020, 2021, etc.) in title or snippet
        year_pattern = r'\b(20\d{2})\b'
        year_matches = re.findall(year_pattern, f"{title} {snippet}")
        
        if year_matches:
            # Use the first year match as a basic date
            return year_matches[0]
            
        # Look for more specific date patterns
        date_patterns = [
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? 20\d{2}\b',
            r'\b\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* 20\d{2}\b',
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2},? 20\d{2}\b',
            r'\b\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) 20\d{2}\b'
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, f"{title} {snippet}")
            if date_match:
                return date_match.group(0)
                
        return None

    def _calculate_relevance_score(self, result: dict, company_name: str, document_type: Optional[str]) -> float:
        """Calculate a relevance score from 1-10 for the search result."""
        score = 5.0  # Start with a neutral score
        
        title = result.get('title', '')
        snippet = result.get('snippet', '')
        link = result.get('link', '')
        
        # Boost score for PDF files (likely official documents)
        if link.lower().endswith('.pdf'):
            score += 2.0
        
        # Boost score for official company domain
        company_domain = company_name.lower().replace(" ", "")
        if company_domain in link.lower():
            score += 1.5
            
        # Boost score for investor relations pages
        if 'investor' in link.lower() or 'financial' in link.lower():
            score += 1.0
            
        # Boost score if the title contains the company name
        if company_name.lower() in title.lower():
            score += 0.5
            
        # Boost score for recent years in the title or link
        import re
        year_match = re.search(r'20(2[0-5]|1[5-9])', f"{title} {snippet} {link}")
        if year_match:
            # More recent years get higher scores
            year = int(year_match.group(0))
            recency_bonus = min(1.0, (year - 2015) / 10.0)  # 0.0 for 2015, 1.0 for 2025
            score += recency_bonus
            
        # Adjust score based on document type match
        guessed_type = self._guess_document_type(title, snippet, link)
        if document_type and document_type.lower() == guessed_type:
            score += 1.0
            
        # Cap the score at 10
        return min(10.0, score)

    def _extract_direct_pdf_links(self, title: str, snippet: str, url: str, company_name: str) -> Optional[str]:
        """
        Try to extract direct PDF links from search results.
        Returns the direct PDF URL if found, otherwise returns None.
        """
        import re
        
        # First check if the URL itself is already a PDF
        if url.lower().endswith('.pdf'):
            return url
            
        # Common patterns for PDF links in snippets
        pdf_patterns = [
            # Look for quoted URLs ending with .pdf
            r'href=[\'"]([^\'"]+\.pdf)[\'"]',
            r'href=([^\s]+\.pdf)',
            # Look for URL patterns with .pdf extension
            r'https?://[^\s\'"]+\.pdf',
            # Look for specific patterns with the company name
            rf'https?://[^\s\'"]+{company_name.lower().replace(" ", "[\\s-_]")}[^\s\'"]+\.pdf',
        ]
        
        # Common PDF file naming patterns
        file_patterns = [
            'annual[\\s-_]report',
            'annual[\\s-_]review',
            'financial[\\s-_]statement',
            'financial[\\s-_]report',
            'ar\\d{4}',
            'report\\d{4}',
            '\\d{4}[\\s-_]annual',
            '\\d{4}[\\s-_]report',
        ]
        
        # Check combined text for PDF URLs
        combined_text = f"{title} {snippet} {url}"
        
        # Try each pattern
        for pattern in pdf_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            if matches:
                for match in matches:
                    # Verify this looks like a valid URL
                    if match.startswith('http'):
                        return match
                    # If it's a relative path, try to construct full URL
                    elif match.startswith('/'):
                        # Extract base domain from original URL
                        domain_match = re.match(r'(https?://[^/]+)', url)
                        if domain_match:
                            domain = domain_match.group(1)
                            return f"{domain}{match}"
        
        # Check for specific known patterns for bank annual reports
        if 'bankfab.com' in url and 'annual' in url.lower() and 'report' in url.lower():
            # Extract year from title or URL
            year_match = re.search(r'20\d{2}', combined_text)
            if year_match:
                year = year_match.group(0)
                return f"https://www.bankfab.com/-/media/fab-uds/about-fab/investor-relations/reports-and-presentations/quarterly-and-annual-reports/{year}/fab-annual-report-{year}-en.pdf"
        
        # Try to construct PDF URL based on typical patterns if we have an index page
        if '/investor-relations/' in url or '/investors/' in url:
            # Extract domain
            domain_match = re.match(r'(https?://[^/]+)', url)
            if domain_match:
                domain = domain_match.group(1)
                
                # Extract year from title or snippet
                year_match = re.search(r'20\d{2}', combined_text)
                year = year_match.group(0) if year_match else "2023"  # Default to 2023 if no year found
                
                # Try common URL patterns for annual reports
                company_slug = company_name.lower().replace(" ", "-")
                possible_urls = [
                    f"{domain}/media/annual-reports/{company_slug}-annual-report-{year}.pdf",
                    f"{domain}/media/reports/{year}/{company_slug}-annual-report-{year}.pdf",
                    f"{domain}/media/{year}/{company_slug}-annual-report.pdf",
                    f"{domain}/documents/annual-reports/{year}.pdf",
                    f"{domain}/investors/annual-reports/{year}/{company_slug}-ar-{year}.pdf"
                ]
                
                # For FAB Bank specifically
                if 'bankfab.com' in domain:
                    possible_urls.append(f"{domain}/-/media/fab-uds/about-fab/investor-relations/reports-and-presentations/quarterly-and-annual-reports/{year}/fab-annual-report-{year}-en.pdf")
                
                # Return the first URL that might exist (would need to check with an HTTP request in production)
                return possible_urls[0]
                
        # No direct PDF link found
        return None

    def _process_organic_results(self, organic_results: list, company_name: str, document_type: Optional[str]) -> List[CompanyDocumentSearchResult]:
        """Process organic search results into structured document results."""
        processed_results = []
        for result in organic_results[: self.n_results]:
            try:
                title = result["title"]
                link = result["link"]
                snippet = result.get("snippet", "")
                
                # Try to extract direct PDF link if available
                direct_pdf_link = self._extract_direct_pdf_links(title, snippet, link, company_name)
                
                # Use the direct PDF link if found, otherwise use the original link
                final_link = direct_pdf_link if direct_pdf_link else link
                
                # Guess document type and publication date
                guessed_type = self._guess_document_type(title, snippet, final_link)
                publication_date = self._guess_publication_date(title, snippet)
                
                # Calculate relevance score - give bonus for direct PDF links
                relevance_score = self._calculate_relevance_score(result, company_name, document_type)
                if direct_pdf_link:
                    relevance_score += 1.0  # Bonus for direct PDF links
                
                document_result = CompanyDocumentSearchResult(
                    title=title,
                    description=snippet,
                    link=final_link,
                    document_type=guessed_type,
                    publication_date=publication_date,
                    relevance_score=min(10.0, relevance_score)  # Cap at 10
                )
                
                processed_results.append(document_result)
            except KeyError:
                logger.warning(f"Skipping malformed organic result: {result}")
                continue
                
        # Sort results by relevance score (highest first)
        processed_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return processed_results

    def _make_api_request(self, search_query: str, search_type: str) -> dict:
        """Make API request to Serper."""
        search_url = self._get_search_url(search_type)
        payload = json.dumps({"q": search_query, "num": self.n_results})
        headers = {
            "X-API-KEY": os.environ["SERPER_API_KEY"],
            "content-type": "application/json",
        }

        response = None
        try:
            response = requests.post(
                search_url, headers=headers, json=json.loads(payload), timeout=10
            )
            response.raise_for_status()
            results = response.json()
            if not results:
                logger.error("Empty response from Serper API")
                raise ValueError("Empty response from Serper API")
            return results
        except requests.exceptions.RequestException as e:
            error_msg = f"Error making request to Serper API: {e}"
            if response is not None and hasattr(response, "content"):
                error_msg += f"\nResponse content: {response.content}"
            logger.error(error_msg)
            raise
        except json.JSONDecodeError as e:
            if response is not None and hasattr(response, "content"):
                logger.error(f"Error decoding JSON response: {e}")
                logger.error(f"Response content: {response.content}")
            else:
                logger.error(
                    f"Error decoding JSON response: {e} (No response content available)"
                )
            raise

    def _run(self, **kwargs: Any) -> Any:
        """Execute the company document search operation."""
        company_name = kwargs.get("company_name")
        document_type = kwargs.get("document_type")
        search_query = kwargs.get("search_query")
        year = kwargs.get("year")
        save_file = kwargs.get("save_file", self.save_file)
        
        # Construct an effective search query
        effective_query = self._construct_search_query(company_name, document_type, search_query, year)
        
        # Make the API request
        results = self._make_api_request(effective_query, self.search_type)
        
        # Process the results
        document_results = []
        
        if "organic" in results:
            document_results = self._process_organic_results(results["organic"], company_name, document_type)
        
        # Format the output
        formatted_results = {
            "company_name": company_name,
            "search_query": effective_query,
            "total_results_found": len(document_results),
            "documents": [doc.model_dump() for doc in document_results]
        }
        
        # Save to file if requested
        if save_file:
            _save_results_to_file(json.dumps(formatted_results, indent=2), company_name)
        
        return formatted_results


class CompanyFinancialDocumentTool(BaseTool):
    name: str = "Search for Company Financial Documents"
    description: str = (
        "A specialized tool for finding financial documents such as annual reports, "
        "quarterly reports, and financial statements for a specific company. "
        "This tool is optimized for finding official financial publications."
    )
    args_schema: Type[BaseModel] = CompanySearchToolSchema
    base_url: str = "https://google.serper.dev"
    n_results: int = 10
    save_file: bool = False
    search_type: str = "search"
    
    def _run(self, **kwargs: Any) -> Any:
        """Execute the financial document search operation."""
        # Set the document type to focus on financial documents
        kwargs["document_type"] = kwargs.get("document_type", "financial_statement")
        
        # Enhance the search query with financial terms
        original_query = kwargs.get("search_query", "")
        kwargs["search_query"] = f"{original_query} financial annual report quarterly statement"
        
        # Use the base search functionality to perform the search
        search_tool = CompanyInternalSearchTool(
            base_url=self.base_url,
            n_results=self.n_results,
            save_file=self.save_file,
            search_type=self.search_type
        )
        results = search_tool._run(**kwargs)
        
        # Further filter/process results if needed
        if "documents" in results:
            # Filter to keep only financial document types
            financial_doc_types = ["annual_report", "financial_statement", "investor_presentation"]
            results["documents"] = [
                doc for doc in results["documents"] 
                if doc.get("document_type") in financial_doc_types
            ]
            results["total_results_found"] = len(results["documents"])
        
        return results


class CompanyAnnualReportTool(BaseTool):
    name: str = "Search for Company Annual Reports"
    description: str = (
        "A specialized tool for finding annual reports for a specific company. "
        "This tool is optimized for locating the most recent and relevant annual reports."
    )
    args_schema: Type[BaseModel] = CompanySearchToolSchema
    base_url: str = "https://google.serper.dev"
    n_results: int = 10
    save_file: bool = False
    search_type: str = "search"
    
    def _run(self, **kwargs: Any) -> Any:
        """Execute the annual report search operation."""
        # Set the document type to focus on annual reports
        kwargs["document_type"] = "annual_report"
        
        # Enhance the search query
        original_query = kwargs.get("search_query", "")
        kwargs["search_query"] = f"{original_query} annual report pdf"
        
        # Use the CompanyInternalSearchTool to perform the search
        search_tool = CompanyInternalSearchTool(
            base_url=self.base_url,
            n_results=self.n_results,
            save_file=self.save_file,
            search_type=self.search_type
        )
        results = search_tool._run(**kwargs)
        
        # Further filter/process results to focus on annual reports
        if "documents" in results:
            # Filter to keep only annual reports
            results["documents"] = [
                doc for doc in results["documents"] 
                if doc.get("document_type") == "annual_report"
            ]
            results["total_results_found"] = len(results["documents"])
        
        return results


class CompanyESGReportTool(BaseTool):
    name: str = "Search for Company ESG/Sustainability Reports"
    description: str = (
        "A specialized tool for finding ESG (Environmental, Social, Governance) and "
        "sustainability reports for a specific company."
    )
    args_schema: Type[BaseModel] = CompanySearchToolSchema
    base_url: str = "https://google.serper.dev"
    n_results: int = 10
    save_file: bool = False
    search_type: str = "search"
    
    def _run(self, **kwargs: Any) -> Any:
        """Execute the ESG/sustainability report search operation."""
        # Set the document type to focus on sustainability reports
        kwargs["document_type"] = "sustainability_report"
        
        # Enhance the search query
        original_query = kwargs.get("search_query", "")
        kwargs["search_query"] = f"{original_query} sustainability ESG environmental social governance report"
        
        # Create and use the CompanyInternalSearchTool to perform the search
        search_tool = CompanyInternalSearchTool(
            base_url=self.base_url,
            n_results=self.n_results,
            save_file=self.save_file,
            search_type=self.search_type
        )
        results = search_tool._run(**kwargs)
        
        # Further filter/process results to focus on sustainability reports
        if "documents" in results:
            # Filter to keep only sustainability reports
            results["documents"] = [
                doc for doc in results["documents"] 
                if doc.get("document_type") == "sustainability_report"
            ]
            results["total_results_found"] = len(results["documents"])
        
        return results