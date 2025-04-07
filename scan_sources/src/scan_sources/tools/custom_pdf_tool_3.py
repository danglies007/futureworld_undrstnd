import os
import logging
from typing import Any, Optional, Type, List, Union
from pydantic import BaseModel, Field, model_validator
from embedchain.models.data_type import DataType
from .rag.rag_tool import RagTool

logger = logging.getLogger(__name__)

# Define reference directory path - same level as main.py
REFERENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reference")

class FixedPDFSearchToolSchema(BaseModel):
    """Input for PDFSearchTool."""
    query: str = Field(
        ..., 
        description="Mandatory query you want to use to search the PDF's content"
    )

class PDFSearchToolSchema(FixedPDFSearchToolSchema):
    """Input for PDFSearchTool."""
    pdf: Optional[str] = Field(
        None,
        description="Optional pdf path to search in a specific document. If not provided, will search across all loaded PDFs."
    )

class CustomPDFSearchTool3(RagTool):
    """Tool for searching through PDF documents using embedchain."""
    name: str = "Search PDF tool"
    description: str = "A tool that can be used to semantic search queries across PDF content using embedchain."
    args_schema: Type[BaseModel] = PDFSearchToolSchema

    def __init__(self, pdf: Optional[Union[str, List[str]]] = None, auto_load: bool = True, **kwargs):
        """Initialize the tool with optional PDF path(s).
        
        Args:
            pdf: Optional PDF path or list of paths
            auto_load: If True, automatically load PDFs from reference directory
            **kwargs: Additional arguments passed to RagTool
        """
        # Set default chunker configuration if not provided
        if not kwargs.get('config'):
            kwargs['config'] = {
                "chunker": {
                    "chunk_size": 500,
                    "chunk_overlap": 50,
                    "min_chunk_size": 100,  # Added min_chunk_size > chunk_overlap
                    "length_function": "len"
                }
            }
        super().__init__(**kwargs)
        self._loaded_pdfs = set()
        
        # Ensure reference directory exists
        os.makedirs(REFERENCE_DIR, exist_ok=True)
        logger.info(f"Using reference directory: {REFERENCE_DIR}")
        
        # Log available PDFs
        pdfs = [f for f in os.listdir(REFERENCE_DIR) if f.lower().endswith('.pdf')]
        if pdfs:
            logger.info(f"Available PDFs in reference directory:")
            for pdf_file in pdfs:
                logger.info(f"- {pdf_file}")
        else:
            logger.warning(f"No PDFs found in reference directory: {REFERENCE_DIR}. " 
                          f"Please add PDF files to this directory for document scanning functionality. "
                          f"The flow will continue but document scanning tasks may not produce meaningful results.")
        # Handle provided PDFs
        if pdf is not None:
            pdfs_to_load = [pdf] if isinstance(pdf, str) else pdf
            for pdf_path in pdfs_to_load:
                self._load_pdf(pdf_path)
                
        # Auto-load PDFs from reference directory if requested
        if auto_load:
            self._load_reference_pdfs()
            
        if self._loaded_pdfs:
            self._update_description()

    def _load_pdf(self, pdf_path: Optional[str]) -> None:
        """Load a single PDF file."""
        if pdf_path is None:
            logger.error("PDF path is None")
            return
            
        try:
            if not os.path.isabs(pdf_path):
                logger.debug(f"Converting relative path to absolute: {pdf_path}")
                full_path = os.path.join(REFERENCE_DIR, pdf_path)
                logger.debug(f"Absolute path: {full_path}")
                pdf_path = full_path
            
            if not os.path.exists(pdf_path):
                logger.error(f"PDF not found at path: {pdf_path}")
                logger.info(f"Reference directory contents: {os.listdir(REFERENCE_DIR) if os.path.exists(REFERENCE_DIR) else 'REFERENCE_DIR does not exist'}")
                return
                
            if pdf_path in self._loaded_pdfs:
                logger.warning(f"PDF already loaded: {pdf_path}")
                return
                
            logger.info(f"Loading PDF: {os.path.basename(pdf_path)}")
            logger.debug(f"Full path: {pdf_path}")
            logger.debug(f"File size: {os.path.getsize(pdf_path)} bytes")
            
            try:
                self.add(pdf_path, data_type=DataType.PDF_FILE)
                logger.info(f"Successfully added PDF: {os.path.basename(pdf_path)}")
                self._loaded_pdfs.add(pdf_path)
            except Exception as e:
                logger.error(f"Failed to add PDF {os.path.basename(pdf_path)}: {str(e)}", exc_info=True)
                raise

        except Exception as e:
            logger.error(f"Unexpected error in _load_pdf for {pdf_path}: {str(e)}", exc_info=True)
            raise

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute the search query using embedchain."""
        try:
            # Log the input parameters
            logger.info(f"Running query: {query}")
            logger.info(f"Additional kwargs: {kwargs}")
            
            self._before_run(query, **kwargs)
            
            if not self.adapter:
                error_msg = "Adapter not initialized. Please provide PDF path(s) or ensure PDFs exist in the reference directory."
                logger.error(error_msg)
                return error_msg
            
            if not hasattr(self.adapter, 'embedchain_app'):
                error_msg = "Invalid adapter configuration: embedchain_app not found"
                logger.error(error_msg)
                return error_msg
            
            # Log loaded PDFs before query
            logger.info(f"Currently loaded PDFs: {[os.path.basename(p) for p in self._loaded_pdfs]}")
            
            # Use the embedchain app's query method
            results = self.adapter.embedchain_app.query(query)
            if not results:
                return "No relevant information found in the PDFs."
            
            # Format the result into a coherent response
            response = f"Search Results:\n{results}\n"
            
            # Add sources information
            sources = sorted([os.path.basename(pdf) for pdf in self._loaded_pdfs])
            if sources:
                response += f"\nSources consulted: {', '.join(sources)}"
            
            return response
            
        except Exception as e:
            error_msg = f"Error searching PDFs: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg

    def _load_reference_pdfs(self) -> None:
        """Load all PDFs from the reference directory."""
        try:
            logger.info(f"Scanning reference directory: {REFERENCE_DIR}")
            pdfs = [f for f in os.listdir(REFERENCE_DIR) if f.lower().endswith('.pdf')]
            
            if pdfs:
                logger.info(f"Found {len(pdfs)} PDFs in reference directory: {', '.join(pdfs)}")
                for pdf in pdfs:
                    try:
                        self._load_pdf(pdf)
                    except Exception as e:
                        logger.error(f"Failed to load PDF {pdf}: {str(e)}", exc_info=True)
            else:
                logger.warning("No PDFs found in reference directory")
                
        except Exception as e:
            logger.error(f"Error scanning reference directory: {str(e)}", exc_info=True)
            raise

    @model_validator(mode="after")
    def _set_default_adapter(self):
        """Set up the default embedchain adapter if none provided."""
        if isinstance(self.adapter, RagTool._AdapterPlaceholder):
            from embedchain import App
            from crewai_tools.adapters.pdf_embedchain_adapter import PDFEmbedchainAdapter
            
            app = App.from_config(config=self.config) if self.config else App()
            self.adapter = PDFEmbedchainAdapter(
                embedchain_app=app,
                summarize=self.summarize
            )
        return self

    def add(self, *args, **kwargs):
        """Add data to the embedchain app."""
        try:
            logger.info(f"Attempting to add data to embedchain: {args}")
            logger.debug(f"Add kwargs: {kwargs}")
            super().add(*args, **kwargs)
            logger.info("Successfully added data to embedchain")
        except ValueError as ve:
            if "No data found" in str(ve):
                logger.error(f"Embedchain could not extract data from PDF: {args[0]}")
                # Try to get more info about the PDF
                try:
                    import PyPDF2
                    with open(args[0], 'rb') as f:
                        pdf = PyPDF2.PdfReader(f)
                        logger.info(f"PDF Info - Pages: {len(pdf.pages)}, Metadata: {pdf.metadata}")
                except Exception as e:
                    logger.error(f"Could not read PDF with PyPDF2: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error adding data to embedchain: {str(e)}", exc_info=True)
            raise

    def _before_run(self, query: str, **kwargs: Any) -> Any:
        if "pdf" in kwargs:
            self._load_pdf(kwargs["pdf"])
        return super()._before_run(query, **kwargs)

    def _update_description(self) -> None:
        """Update tool description with current PDFs."""
        if self._loaded_pdfs:
            pdf_names = [os.path.basename(p) for p in sorted(self._loaded_pdfs)]
            self.description = f"Search through PDFs using embedchain: {', '.join(pdf_names)}"

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute the search query using embedchain."""
        try:
            self._before_run(query, **kwargs)
            
            if not self.adapter:
                raise ValueError("Adapter not initialized. Please provide PDF path(s) or ensure PDFs exist in the reference directory.")
            
            if not hasattr(self.adapter, 'embedchain_app'):
                raise ValueError("Invalid adapter configuration: embedchain_app not found")
            
            # Use the embedchain app's query method
            results = self.adapter.embedchain_app.query(query)
            if not results:
                return "No relevant information found in the PDFs."
            
            # Format the result into a coherent response
            response = f"Search Results:\n{results}\n"
            
            # Add sources information
            sources = sorted([os.path.basename(pdf) for pdf in self._loaded_pdfs])
            if sources:
                response += f"\nSources consulted: {', '.join(sources)}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching PDFs: {str(e)}")
            return f"Error searching PDFs: {str(e)}"

    async def _arun(self, query: str, **kwargs: Any) -> str:
        """Async implementation of the tool."""
        return self._run(query, **kwargs)
