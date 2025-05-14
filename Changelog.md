* 2.0.1 - Added agents.yaml file which was accidentally deleted
* 2.0.2
  * **Issues faced**

    * Mckinsey HTML is causing a problem with scraping using selenium - try webscrape tool for mckinsey
    * With the reports Claude reaches a context limit and stops the report halfway through.  Also hit rate limits
    * 
  * **New Features**
  * * Add in Market force implications report
    * Looking at adding image generation
  * **Improvements required**

    * [ ] Review how sources are managed and final sources are generated.  Maybe this should be simplified
    * [ ] Add the more detailed version of the Potential Sources again - based on alternative pydantic model
    * [X] Updated Models.py to incldue strap line into market forces analysis
      * [X] Included into the MarketForce(BaseModel):
        ```
           strap_line: str = Field(..., description="Brief summary of the market force, captured in 2 sentences")
           takeout: str = Field(..., description="Key takeout of the market force, what is the 'so what?' of this market force?")
        ```
    * [ ]
