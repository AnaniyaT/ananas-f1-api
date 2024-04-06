import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models import Race
from .Parser import Parser
from typing import List
import asyncio


class Scraper:
    parser = Parser()
    
    async def getAllRaces(self, year: int, getResults: bool = True) -> List[Race]:
        urls = await self.parser.getRaceUrls(year)
        
        tasks = [self.parser.getRace(url, idx + 1, getResults=getResults) for idx, url in enumerate(urls[1:])]
            
        result = await asyncio.gather(*tasks)
    
        return result            
        
        
    