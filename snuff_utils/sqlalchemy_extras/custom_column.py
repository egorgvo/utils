from sqlalchemy import Column


class CustomColumn(Column):

    def icontains(self, substring):
        return self.ilike(f'%{substring}%')
