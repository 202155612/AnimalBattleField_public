from typing import List, Sequence, Tuple, Union

class QueryBuilder:
    def __init__(self) -> None:
        self._sql: str = ""
        self._params: List[object] = []

    def __str__(self) -> str:
        return self._sql

    def __iter__(self):
        yield self._sql
        yield self._params

    def _append(self, chunk: str) -> None:
        if self._sql and not self._sql.endswith(" "):
            self._sql += " "
        self._sql += chunk

    def WITH(self, cte: str):
        self._append("WITH " + cte)
        return self

    def SELECT(self, *cols: str):
        if not cols:
            raise ValueError("SELECT requires at least one column string.")
        self._append("SELECT " + ", ".join(cols))
        return self

    def FROM(self, tables: Union[str, Sequence[str]]):
        if isinstance(tables, (list, tuple)):
            self._append("FROM " + ", ".join(tables))
        else:
            self._append("FROM " + tables)
        return self

    def WHERE(self, condition: str, *values: object):
        self._append("WHERE " + condition)
        if values:
            self._params.extend(values)
        return self

    def HAVING(self, condition: str, *values: object):
        self._append("HAVING " + condition)
        if values:
            self._params.extend(values)
        return self

    def GROUP_BY(self, cols: Sequence[str]):
        if not cols:
            raise ValueError("GROUP_BY requires at least one column string.")
        self._append("GROUP BY " + ", ".join(cols))
        return self

    def ORDER_BY(self, items: Sequence[Union[str, Tuple[str, str]]]):
        if not items:
            raise ValueError("ORDER_BY requires at least one item.")
        parts: List[str] = []
        for it in items:
            if isinstance(it, (list, tuple)) and len(it) >= 1:
                col = str(it[0])
                direction = (str(it[1]) if len(it) >= 2 else "ASC").upper()
            else:
                col = str(it)
                direction = "ASC"
            if direction not in ("ASC", "DESC"):
                direction = "ASC"
            parts.append(f"{col} {direction}")
        self._append("ORDER BY " + ", ".join(parts))
        return self

    def LIMIT(self, x: Union[int, str], *values: object):
        if isinstance(x, int):
            self._append("LIMIT %s")
            self._params.append(x)
        else:
            self._append("LIMIT " + x)
            if values:
                self._params.extend(values)
        return self

    def OFFSET(self, x: Union[int, str], *values: object):
        if isinstance(x, int):
            self._append("OFFSET %s")
            self._params.append(x)
        else:
            self._append("OFFSET " + x)
            if values:
                self._params.extend(values)
        return self
    
    def build(self) -> Tuple[str, List[object]]:
        return self._sql, list(self._params)
