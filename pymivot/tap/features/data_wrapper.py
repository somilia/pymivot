
class DataWrapper:
    """
    DataWrapper is a class that wraps the data got from the database and offer getter.
    """
    def __init__(self, data, columns=None):
        """
        Parameters
        ----------
        data : list
            The data got from the database
        columns : list
            The columns of the mapped_table
        """
        self.data = data
        self.columns = columns

    def get(self, element):
        """
        Get the data of the element in the row(s).

        Parameters
        ----------
        element : str
            The element to get the data from
        """
        elm_index = self.columns.index(element)
        if len(self.data) == 1:
            return self.data[0][elm_index]
        else:
            return [row[elm_index] for row in self.data]

    def show_rows(self, row=None, nb_rows=None):
        """
        Show the rows of the data.
        """
        print("-----Data in the table:-----")
        print("- Columns:")
        print("- ",self.columns)
        if row is not None:
            print("- Row", row, ":")
            print("- ", self.data[row-1])
        elif nb_rows is not None:
            print("- Rows:")
            for row in self.data[:nb_rows]:
                print("- ", row)
        else:
            print("- Rows:")
            for row in self.data:
                print("- ", row)
        print("-----------------------------")
