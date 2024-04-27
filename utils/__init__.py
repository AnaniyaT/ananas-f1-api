import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from typing import Any
from models import BaseModel


class Utils:
    @staticmethod
    def editDistance(word1: str, word2: str) -> int:
        '''
        Calculates the minimum number of operations required to convert word1 to word2
        '''
        m = len(word1)
        n = len(word2)

        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            dp[i][0] = i

        for j in range(1, n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1]) + 1

        return dp[m][n]
    
    @staticmethod
    def toJson(obj):
        if isinstance(obj, type(BaseModel)):
            return obj.toJson()
        return str(obj)
    
    
    @staticmethod
    def clean(value: Any):
        if isinstance(value, str):
            return value.replace("'", "''")
        return value
    
    
    @staticmethod
    def createSetStatement(**kwargs) -> str:
        """
        Creates a SET statement for an UPDATE query
        """
        statement = ", ".join([f"{key} = '{Utils.clean(value)}'" for key, value in kwargs.items() if value is not None])
        
        return f"SET {statement}"
    
    
    @staticmethod
    def getNameAndShortName(name: str) -> tuple[str, str]:
        """
        Returns the name and short name of a driver or constructor
        """
        name = name.split()
        shortName = name[-1]
        name = " ".join(name[:-1])
        
        return name, shortName