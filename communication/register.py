class ReadFile():

        def getContent(file):
                content = open(file,"r")
                return content.read()

        def getContentNoDupLn(self,file):
                content = open(file,"a+")
                values = content.read().split('\n')
                output = []
                seen = set()
                for value in values:
                        if value not in seen:
                                output.append(value)
                                seen.add(value)
                return output

class WriteFile():

        def __init__(self,file):
                self.file = file
                
        def println(self,content):
                file = open(self.file,"a+")
                IP_list =  file.readlines()
                if not content+'\n' in IP_list:
                        file.write(content+'\n')
                file.close()
