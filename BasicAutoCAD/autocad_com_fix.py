import win32com.client
 
acad = win32com.client.Dispatch("AutoCAD.Application")
acad.Visible = True
print(acad.Name)