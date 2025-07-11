from graph.graph import app

url = "https://developers.hubspot.com/docs/reference/api/overview"
print(app.invoke(input={"service":url})["service"])
print(app.invoke(input={"service":url})["mapping"])