class MarkdownTable:
    @staticmethod
    def render(data, headers):
        if len(headers) == 0:
            return ''
        output = '| '
        headerDivider = '| '
        for header in headers:
            output += header + ' | '
            headerDivider += '--- | '
        output += '\n' + headerDivider
        for row in data:
            rowData = '| '
            for col in row:
                rowData += str(col).replace('|', '<code>&#124;</code>') + ' | '
            output += '\n' + rowData
        return output
